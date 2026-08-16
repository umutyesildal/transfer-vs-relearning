from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.study.adapters.m0_evaluation import build_lm_eval_command
from transfer_vs_relearning.study.adapters.m0_probing import build_project_probe_command
from transfer_vs_relearning.utils.io import sha256_file, sha256_text, write_json


ALLOWED_ADAPTERS = {
    "lm_eval",
    "project_factual",
    "project_generation_integrity",
    "project_corpus_perplexity",
}
REQUIRED_FAMILIES = {
    "factual_access",
    "english_retention",
    "english_capability",
    "turkish_capability",
    "generation_integrity",
    "statistical_uncertainty",
}


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _strings(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
    ):
        raise ValueError(f"{label} must be a non-empty string list")
    return value


def _placeholder_paths(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            found.extend(_placeholder_paths(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_placeholder_paths(item, f"{prefix}[{index}]"))
    elif isinstance(value, str) and value.startswith("__") and value.endswith("__"):
        found.append(prefix)
    return found


def _scientific_cache_paths(plan: dict[str, Any], output_root: Path) -> dict[str, Path]:
    preflight = plan["data_preflight"]
    if preflight.get("mode") == "frozen_offline_reuse":
        cache_root = Path(str(preflight["source_cache_root"])).resolve()
    else:
        cache_root = output_root / "cache"
    return {
        "root": cache_root,
        "hf_home": cache_root / "huggingface",
        "datasets": cache_root / "huggingface_datasets",
        "xdg": cache_root,
    }


def _verified_content_manifest(preflight: dict[str, Any]) -> tuple[Path, list[dict[str, Any]]]:
    manifest_path = Path(str(preflight["source_content_manifest"])).resolve()
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Frozen dataset content manifest is missing: {manifest_path}")
    if sha256_file(manifest_path) != str(preflight["source_content_manifest_sha256"]):
        raise ValueError("Frozen dataset content manifest SHA-256 mismatch")
    rows: list[dict[str, Any]] = []
    with manifest_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            path = Path(str(row.get("path", ""))).resolve()
            if not path.is_file():
                raise FileNotFoundError(
                    f"Frozen dataset cache file is missing at manifest row {line_number}: {path}"
                )
            if path.stat().st_size != int(row.get("bytes", -1)):
                raise ValueError(f"Frozen dataset cache byte mismatch: {path}")
            if sha256_file(path) != str(row.get("sha256", "")):
                raise ValueError(f"Frozen dataset cache SHA-256 mismatch: {path}")
            rows.append(row)
    expected_files = int(preflight["source_cache_files"])
    expected_bytes = int(preflight["source_cache_bytes"])
    if len(rows) != expected_files or sum(int(row["bytes"]) for row in rows) != expected_bytes:
        raise ValueError("Frozen dataset cache manifest count/byte totals do not match")
    return manifest_path, rows


def load_m0_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _mapping(payload, "M0 evaluation config")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, path)


def build_m0_parallel_plan(config_path: Path, *, repo_root: Path) -> dict[str, Any]:
    config_path = config_path.resolve()
    repo_root = repo_root.resolve()
    config = load_m0_config(config_path)
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported M0 evaluation schema_version")
    if config.get("classification") not in {"qualification_only", "scientific_evaluation"}:
        raise ValueError("Unsupported M0 evaluation classification")
    model = _mapping(config.get("model"), "model")
    if model.get("backend") != "hf" or model.get("apply_chat_template") is not False:
        raise ValueError("M0 requires the frozen base HF backend without a chat template")
    if model.get("system_instruction") is not None:
        raise ValueError("M0 must not use a system instruction")

    parallel = _mapping(config.get("parallel_evaluation"), "parallel_evaluation")
    supported_topologies = {
        "preflight_then_single_slurm_array_plus_afterany_finalizer",
        "gpu_route_selection_then_preflight_then_single_slurm_array_plus_afterany_finalizer",
        "gpu_route_selection_per_lane_then_preflight_then_independent_jobs_plus_afterany_finalizer",
    }
    if parallel.get("topology") not in supported_topologies:
        raise ValueError(
            "M0 parallel topology must use data preflight, GPU-routed lane jobs and an "
            "afterany finalizer"
        )
    lanes = parallel.get("lanes")
    if not isinstance(lanes, list) or not lanes:
        raise ValueError("parallel_evaluation.lanes must be non-empty")
    normalized_lanes: list[dict[str, Any]] = []
    lane_ids: set[str] = set()
    task_ids: list[str] = []
    families: set[str] = set()
    for index, raw_lane in enumerate(lanes):
        lane = _mapping(raw_lane, f"lanes[{index}]")
        lane_id = str(lane.get("id", ""))
        if not lane_id or lane_id in lane_ids:
            raise ValueError(f"Lane ID is missing or duplicated: {lane_id!r}")
        adapter = str(lane.get("adapter", ""))
        if adapter not in ALLOWED_ADAPTERS:
            raise ValueError(f"Lane {lane_id} uses an unregistered adapter: {adapter}")
        lane_families = _strings(lane.get("families"), f"{lane_id}.families")
        families.update(lane_families)
        normalized = {**lane, "index": index, "id": lane_id, "adapter": adapter}
        if adapter == "lm_eval":
            tasks = _strings(lane.get("task_ids"), f"{lane_id}.task_ids")
            duplicates = set(tasks).intersection(task_ids)
            if duplicates:
                raise ValueError(f"Harness tasks occur in multiple lanes: {sorted(duplicates)}")
            task_ids.extend(tasks)
            if not isinstance(lane.get("fewshot"), int) or lane["fewshot"] < 0:
                raise ValueError(f"Lane {lane_id} needs a non-negative fewshot count")
        else:
            for key in (
                "evaluator_config",
                "evaluator_config_sha256",
                "expected_output_root",
            ):
                if not isinstance(lane.get(key), str) or not lane[key]:
                    raise ValueError(f"Lane {lane_id} is missing {key}")
        lane_ids.add(lane_id)
        normalized_lanes.append(normalized)

    expected_tasks = _strings(config.get("required_task_discovery"), "required_task_discovery")
    if set(task_ids) != set(expected_tasks) or len(task_ids) != len(expected_tasks):
        raise ValueError("Parallel Harness lanes must cover every required task exactly once")
    missing_families = REQUIRED_FAMILIES - families
    if missing_families:
        raise ValueError(f"Parallel lanes are missing required families: {sorted(missing_families)}")

    max_parallel = parallel.get("max_parallel_lanes")
    if not isinstance(max_parallel, int) or not 1 <= max_parallel <= len(normalized_lanes):
        raise ValueError("max_parallel_lanes must be between one and the lane count")
    if config["classification"] == "scientific_evaluation" and any(
        lane.get("limit") is not None for lane in normalized_lanes
    ):
        raise ValueError("Scientific M0 evaluation cannot use --limit")
    runtime = _mapping(parallel.get("runtime"), "parallel_evaluation.runtime")
    slurm = _mapping(parallel.get("slurm"), "parallel_evaluation.slurm")
    route_policy = slurm.get(
        "gpu_route_selection_policy", "earliest_test_only_start_then_declared_order"
    )
    if route_policy not in {
        "earliest_test_only_start_then_declared_order",
        "earliest_start_window_then_declared_slots_per_lane",
    }:
        raise ValueError("M0 requires the scheduler-probed GPU route selection policy")
    max_route_start_skew_seconds = slurm.get("max_route_start_skew_seconds", 900)
    if not isinstance(max_route_start_skew_seconds, int) or max_route_start_skew_seconds < 0:
        raise ValueError("max_route_start_skew_seconds must be a non-negative integer")
    raw_gpu_routes = slurm.get("gpu_routes")
    if raw_gpu_routes is None and all(
        isinstance(slurm.get(key), str) and slurm[key]
        for key in ("partition", "gres", "memory")
    ):
        raw_gpu_routes = [
            {
                "id": "legacy_frozen_route",
                "partition": slurm["partition"],
                "gres": slurm["gres"],
                "memory": slurm["memory"],
            }
        ]
    if not isinstance(raw_gpu_routes, list) or not raw_gpu_routes:
        raise ValueError("parallel_evaluation.slurm.gpu_routes must be non-empty")
    gpu_route_ids: set[str] = set()
    gpu_routes: list[dict[str, str]] = []
    for index, raw_route in enumerate(raw_gpu_routes):
        route = _mapping(raw_route, f"parallel_evaluation.slurm.gpu_routes[{index}]")
        route_id = str(route.get("id", ""))
        if not route_id or route_id in gpu_route_ids:
            raise ValueError(f"GPU route ID is missing or duplicated: {route_id!r}")
        normalized_route: dict[str, Any] = {"id": route_id}
        for key in ("partition", "gres", "memory"):
            value = route.get(key)
            if not isinstance(value, str) or not value:
                raise ValueError(f"GPU route {route_id} is missing {key}")
            normalized_route[key] = value
        parallel_slots = route.get("parallel_slots", 1)
        if not isinstance(parallel_slots, int) or parallel_slots < 1:
            raise ValueError(f"GPU route {route_id} parallel_slots must be a positive integer")
        normalized_route["parallel_slots"] = parallel_slots
        gpu_route_ids.add(route_id)
        gpu_routes.append(normalized_route)
    slurm = {
        **slurm,
        "gpu_route_selection_policy": route_policy,
        "max_route_start_skew_seconds": max_route_start_skew_seconds,
        "gpu_routes": gpu_routes,
    }
    environment_preparation = _mapping(
        parallel.get("environment_preparation"),
        "parallel_evaluation.environment_preparation",
    )
    data_preflight = _mapping(
        parallel.get("data_preflight"),
        "parallel_evaluation.data_preflight",
    )
    data_mode = data_preflight.get("mode", "network_materialize")
    if data_mode not in {"network_materialize", "frozen_offline_reuse"}:
        raise ValueError("Unsupported M0 data preflight mode")
    if config["classification"] == "scientific_evaluation":
        if data_mode != "frozen_offline_reuse":
            raise ValueError("Scientific M0 requires frozen_offline_reuse data mode")
        if data_preflight.get("network_retrieval_authorized") is not False:
            raise ValueError("Scientific M0 frozen input reuse must forbid network retrieval")
        for key in (
            "source_cache_root",
            "source_content_manifest",
            "source_content_manifest_sha256",
            "source_cache_files",
            "source_cache_bytes",
        ):
            if data_preflight.get(key) in {None, ""}:
                raise ValueError(f"Scientific M0 data preflight is missing {key}")
    seeds = _mapping(config.get("seeds"), "seeds")
    if set(seeds) != {"python", "numpy", "torch", "fewshot"}:
        raise ValueError("M0 requires exactly four named deterministic seeds")

    run_classification = (
        _mapping(config.get("test_only_policy"), "test_only_policy").get(
            "limited_run_classification"
        )
        if config["classification"] == "qualification_only"
        else "scientific"
    )
    if run_classification == "scientific" and any(
        lane.get("limit") is not None for lane in normalized_lanes
    ):
        raise ValueError("Scientific M0 evaluation cannot use --limit")

    identity = {
        "config_sha256": sha256_file(config_path),
        "model": [model.get("repository"), model.get("revision")],
        "run_classification": run_classification,
        "lanes": [
            (lane["id"], lane["adapter"], lane.get("task_ids", []))
            for lane in normalized_lanes
        ],
    }
    return {
        "schema_version": 1,
        "plan_id": sha256_text(json.dumps(identity, sort_keys=True))[:16],
        "name": config["name"],
        "contract_status": config["status"],
        "classification": config["classification"],
        "run_classification": run_classification,
        "execution_ready": config.get("execution_ready") is True,
        "execution_authorized": config.get("execution_authorized") is True,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "repo_root": str(repo_root),
        "model": {
            "repository": model["repository"],
            "revision": model["revision"],
            "manifest_path": model["historical_manifest_path"],
            "manifest_sha256": model["historical_manifest_sha256"],
        },
        "harness": config["harness"],
        "seeds": seeds,
        "runtime": runtime,
        "slurm": slurm,
        "environment_preparation": environment_preparation,
        "data_preflight": data_preflight,
        "storage": config["storage"],
        "topology": parallel["topology"],
        "max_parallel_lanes": max_parallel,
        "lane_count": len(normalized_lanes),
        "lanes": normalized_lanes,
        "placeholders": _placeholder_paths(config),
    }


def assess_m0_parallel_readiness(
    config_path: Path,
    *,
    repo_root: Path,
    project_state_path: Path,
    output_root: Path | None = None,
) -> dict[str, Any]:
    plan = build_m0_parallel_plan(config_path, repo_root=repo_root)
    state = load_m0_config(project_state_path)
    readiness = _mapping(state.get("readiness"), "project readiness")
    output = (output_root or Path(plan["storage"]["proposed_root"])).resolve()
    checks: list[dict[str, str]] = []

    def record(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"id": check_id, "status": "pass" if passed else "blocked", "detail": detail})

    record(
        "qualification_contract_frozen",
        plan["contract_status"] == "frozen",
        plan["contract_status"],
    )
    record("qualification_execution_ready", plan["execution_ready"], str(plan["execution_ready"]))
    record(
        "qualification_execution_authorized",
        plan["execution_authorized"],
        str(plan["execution_authorized"]),
    )
    record(
        "parallel_bindings_resolved",
        not plan["placeholders"],
        ", ".join(plan["placeholders"]) or "resolved",
    )
    if plan["classification"] == "scientific_evaluation":
        record(
            "project_ready_to_measure",
            readiness.get("ready_to_measure") is True,
            str(readiness.get("ready_to_measure")),
        )
        record(
            "project_eval_contract_frozen",
            readiness.get("evaluation_contract") == "frozen",
            str(readiness.get("evaluation_contract")),
        )
    else:
        record("project_measurement_gate", True, "not required for non-scientific qualification")
    record("output_namespace_fresh", not output.exists(), str(output))
    record(
        "scratch_output_policy",
        str(output).startswith("/vol/tmp2/yesildau/"),
        str(output),
    )
    if plan["classification"] == "scientific_evaluation":
        try:
            _, content_rows = _verified_content_manifest(plan["data_preflight"])
            cache_identity_ok = True
            cache_detail = (
                f"files={len(content_rows)}, "
                f"bytes={sum(int(row['bytes']) for row in content_rows)}"
            )
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            cache_identity_ok = False
            cache_detail = str(exc)
        record("frozen_dataset_cache_identity", cache_identity_ok, cache_detail)

    if plan["placeholders"]:
        record("runtime_and_artifact_identity", False, "cannot validate unresolved bindings")
    else:
        runtime = plan["runtime"]
        python = Path(runtime["python"])
        lock_path = Path(runtime["environment_lock_path"])
        runtime_ok = python.is_file() and os.access(python, os.X_OK)
        lock_ok = (
            lock_path.is_file()
            and sha256_file(lock_path) == runtime["environment_lock_sha256"]
        )
        manifest_path = Path(plan["model"]["manifest_path"])
        manifest_ok = (
            manifest_path.is_file()
            and sha256_file(manifest_path) == plan["model"]["manifest_sha256"]
        )
        project_configs_ok = True
        for lane in plan["lanes"]:
            if lane["adapter"] == "lm_eval":
                continue
            path = Path(lane["evaluator_config"])
            if not path.is_absolute():
                path = repo_root / path
            project_configs_ok = (
                project_configs_ok
                and path.is_file()
                and sha256_file(path) == lane["evaluator_config_sha256"]
            )
        try:
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            dirty = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            head = "unavailable"
            dirty = "unavailable"
        try:
            commit_ok = subprocess.run(
                [
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    str(runtime["implementation_commit"]),
                    head,
                ],
                cwd=repo_root,
                check=False,
            ).returncode == 0
        except OSError:
            commit_ok = False
        worktree_ok = dirty == ""
        implementation_files = _mapping(
            runtime.get("implementation_files"), "runtime implementation_files"
        )
        implementation_files_ok = True
        for relative, expected_sha256 in implementation_files.items():
            path = repo_root / str(relative)
            implementation_files_ok = (
                implementation_files_ok
                and path.is_file()
                and sha256_file(path) == str(expected_sha256)
            )
        task_overlay_files = _mapping(
            plan["harness"].get("task_overlay_files") or {}, "harness task_overlay_files"
        )
        task_overlay_files_ok = True
        for relative, expected_sha256 in task_overlay_files.items():
            path = repo_root / str(relative)
            task_overlay_files_ok = (
                task_overlay_files_ok
                and path.is_file()
                and sha256_file(path) == str(expected_sha256)
            )
        harness_ok = False
        if runtime_ok:
            identity_code = (
                "import importlib.metadata,json;"
                "d=importlib.metadata.distribution('lm-eval');"
                "u=json.loads(d.read_text('direct_url.json') or '{}');"
                "print(json.dumps({'version':d.version,'commit':u.get('vcs_info',{}).get('commit_id','')}))"
            )
            try:
                observed = json.loads(
                    subprocess.run(
                        [str(python), "-c", identity_code],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout
                )
                harness_ok = (
                    observed.get("version") == str(plan["harness"]["release"]).removeprefix("v")
                    and observed.get("commit") == plan["harness"]["git_commit"]
                )
            except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
                harness_ok = False
        record(
            "runtime_and_artifact_identity",
            runtime_ok
            and lock_ok
            and manifest_ok
            and project_configs_ok
            and commit_ok
            and worktree_ok
            and implementation_files_ok
            and task_overlay_files_ok
            and harness_ok,
            (
                f"python={runtime_ok}, environment_lock={lock_ok}, model_manifest={manifest_ok}, "
                f"project_configs={project_configs_ok}, commit={commit_ok}, "
                f"worktree_clean={worktree_ok}, implementation_files={implementation_files_ok}, "
                f"task_overlays={task_overlay_files_ok}, harness={harness_ok}"
            ),
        )

    blockers = [row["id"] for row in checks if row["status"] != "pass"]
    return {
        "schema_version": 1,
        "scope": "m0_parallel_evaluation_preflight",
        "status": "ready" if not blockers else "blocked_pre_scoring",
        "scientific_work_started": False,
        "plan_id": plan["plan_id"],
        "output_root": str(output),
        "lane_count": plan["lane_count"],
        "max_parallel_lanes": plan["max_parallel_lanes"],
        "checks": checks,
        "blockers": blockers,
    }


def prepare_m0_environment(plan: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    preparation = plan["environment_preparation"]
    if preparation.get("authorized") is not True:
        raise PermissionError("Dedicated M0 environment preparation is not authorized")
    environment_root = Path(str(preparation["root"])).resolve()
    if not str(environment_root).startswith("/vol/tmp2/yesildau/"):
        raise ValueError(f"Dedicated environment is outside approved scratch: {environment_root}")
    if environment_root.exists():
        raise FileExistsError(f"Dedicated environment root already exists: {environment_root}")
    base_python = Path(os.path.abspath(str(preparation["base_python"])))
    if not base_python.is_file() or not os.access(base_python, os.X_OK):
        raise FileNotFoundError(f"Base Python is missing or not executable: {base_python}")
    identity_code = (
        "import importlib.metadata,json,platform,torch,transformers,datasets,accelerate;"
        "d=next((x for x in importlib.metadata.distributions() if "
        "(x.metadata.get('Name') or '').lower().replace('_','-')=='lm-eval'),None);"
        "u=json.loads(d.read_text('direct_url.json') or '{}') if d else {};"
        "print(json.dumps({'python':platform.python_version(),'torch':torch.__version__,"
        "'cuda':torch.version.cuda,'transformers':transformers.__version__,"
        "'datasets':datasets.__version__,'accelerate':accelerate.__version__,"
        "'lm_eval_version':d.version if d else None,"
        "'lm_eval_commit':u.get('vcs_info',{}).get('commit_id','')}))"
    )
    base_observed = json.loads(
        subprocess.run(
            [str(base_python), "-c", identity_code],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    expected_base = _mapping(
        preparation.get("expected_base_identity"), "expected_base_identity"
    )
    base_mismatches = {
        key: {"expected": expected, "observed": base_observed.get(key)}
        for key, expected in expected_base.items()
        if base_observed.get(key) != expected
    }
    if base_mismatches:
        raise ValueError(f"V100 compatibility base identity mismatch: {base_mismatches}")
    compat_site_packages = Path(str(preparation["compat_site_packages"]))
    if not compat_site_packages.is_dir():
        raise FileNotFoundError(
            f"V100 compatibility site-packages is missing: {compat_site_packages}"
        )
    requirements = _strings(preparation.get("requirements"), "environment requirements")
    environment_root.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    subprocess.run(
        [str(base_python), "-m", "venv", "--system-site-packages", str(environment_root)],
        check=True,
    )
    python = environment_root / "bin/python"
    pip = [str(python), "-m", "pip"]
    install_environment = os.environ.copy()
    install_environment["PIP_CACHE_DIR"] = str(environment_root / "cache/pip")
    subprocess.run(
        [*pip, "install", "--disable-pip-version-check", *requirements],
        check=True,
        env=install_environment,
    )
    harness_spec = (
        "git+https://github.com/EleutherAI/lm-evaluation-harness.git@"
        + str(plan["harness"]["git_commit"])
    )
    subprocess.run(
        [*pip, "install", "--disable-pip-version-check", "--no-deps", harness_spec],
        check=True,
        env=install_environment,
    )
    subprocess.run(
        [*pip, "install", "--disable-pip-version-check", "--no-deps", "-e", str(repo_root)],
        check=True,
        env=install_environment,
    )
    purelib = Path(
        subprocess.run(
            [
                str(python),
                "-c",
                "import sysconfig; print(sysconfig.get_paths()['purelib'])",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    compatibility_path = purelib / "00_v100_compat_parent.pth"
    compatibility_path.write_text(
        f"{compat_site_packages}\n",
        encoding="utf-8",
    )
    subprocess.run([*pip, "check"], check=True, env=install_environment)
    freeze = subprocess.run(
        [*pip, "freeze", "--all"],
        check=True,
        capture_output=True,
        text=True,
        env=install_environment,
    ).stdout
    lock_path = environment_root / "environment.lock.txt"
    temporary = lock_path.with_suffix(".txt.tmp")
    temporary.write_text(freeze, encoding="utf-8")
    os.replace(temporary, lock_path)
    observed = json.loads(
        subprocess.run(
            [str(python), "-c", identity_code],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    expected_runtime = {
        **_mapping(preparation.get("expected_runtime_identity"), "expected_runtime_identity"),
        "lm_eval_version": str(plan["harness"]["release"]).removeprefix("v"),
        "lm_eval_commit": plan["harness"]["git_commit"],
    }
    runtime_mismatches = {
        key: {"expected": expected, "observed": observed.get(key)}
        for key, expected in expected_runtime.items()
        if observed.get(key) != expected
    }
    if runtime_mismatches:
        raise ValueError(f"Installed M0 runtime identity mismatch: {runtime_mismatches}")
    environment_files = [path for path in environment_root.rglob("*") if path.is_file()]
    environment_bytes = sum(path.stat().st_size for path in environment_files)
    if environment_bytes > int(preparation["max_environment_bytes"]):
        raise ValueError(
            f"Dedicated environment exceeds byte bound: {environment_bytes} > "
            f"{preparation['max_environment_bytes']}"
        )
    payload = {
        "schema_version": 1,
        "status": "complete",
        "started_at": started,
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "base_python": str(base_python),
        "base_identity": base_observed,
        "compat_site_packages": str(compat_site_packages),
        "compatibility_path_file": str(compatibility_path),
        "environment_root": str(environment_root),
        "python": str(python),
        "environment_lock_path": str(lock_path),
        "environment_lock_sha256": sha256_file(lock_path),
        "environment_file_count": len(environment_files),
        "environment_bytes": environment_bytes,
        "max_environment_bytes": int(preparation["max_environment_bytes"]),
        "identity": observed,
        "base_environment_mutated": False,
    }
    write_json(environment_root / "environment_identity.json", payload)
    return payload


def run_m0_data_preflight(plan: dict[str, Any], *, output_root: Path) -> dict[str, Any]:
    preflight = plan["data_preflight"]
    offline_reuse = preflight.get("mode") == "frozen_offline_reuse"
    if not offline_reuse and preflight.get("network_retrieval_authorized") is not True:
        raise PermissionError("M0 task-data retrieval is not authorized")
    if offline_reuse and preflight.get("network_retrieval_authorized") is not False:
        raise PermissionError("Frozen scientific cache reuse must keep network retrieval disabled")
    preflight_root = output_root / "preflight"
    if preflight_root.exists():
        raise FileExistsError(f"M0 data preflight output already exists: {preflight_root}")
    preflight_root.mkdir()
    cache_paths = _scientific_cache_paths(plan, output_root)
    cache_root = cache_paths["root"]
    tasks = [task for lane in plan["lanes"] for task in lane.get("task_ids", [])]
    environment = os.environ.copy()
    environment.update(
        {
            "HF_HOME": str(cache_paths["hf_home"]),
            "HF_DATASETS_CACHE": str(cache_paths["datasets"]),
            "XDG_CACHE_HOME": str(cache_paths["xdg"]),
            "HF_HUB_DISABLE_TELEMETRY": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    if offline_reuse:
        environment.update(
            {
                "HF_HUB_OFFLINE": "1",
                "HF_DATASETS_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1",
            }
        )
    else:
        for name in ("HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "TRANSFORMERS_OFFLINE"):
            environment.pop(name, None)
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    project_rows: list[dict[str, Any]] = []
    for lane in plan["lanes"]:
        if lane["adapter"] == "lm_eval":
            continue
        build_project_probe_command(plan, lane, repo_root=Path(plan["repo_root"]))
        project_rows.append(
            {
                "lane_id": lane["id"],
                "evaluator_config": lane["evaluator_config"],
                "evaluator_config_sha256": lane["evaluator_config_sha256"],
                "status": "verified_pre_model_load",
            }
        )
    _write_jsonl(output_root / "project_input_resolution.jsonl", project_rows)
    tasks_json = json.dumps(tasks)
    raw_include_path = plan["harness"].get("include_path")
    include_path = (
        Path(plan["repo_root"]) / str(raw_include_path)
        if raw_include_path is not None
        else None
    )
    if include_path is not None and not include_path.is_dir():
        raise FileNotFoundError(f"M0 Harness include path is missing: {include_path}")
    include_args = ["--include_path", str(include_path)] if include_path is not None else []
    task_manager_args = f"include_path={str(include_path)!r}" if include_path is not None else ""
    materialize_code = (
        "import json;from lm_eval.tasks import TaskManager;"
        f"d=TaskManager({task_manager_args}).load_task_or_group("
        f"json.loads({tasks_json!r}));"
        "print(json.dumps({'loaded_entry_count':len(d)}))"
    )
    commands = {
        "task_list": [
            plan["runtime"]["python"],
            "-m",
            "lm_eval",
            "ls",
            "tasks",
            *include_args,
        ],
        "task_validate": [
            plan["runtime"]["python"],
            "-m",
            "lm_eval",
            "validate",
            "--tasks",
            ",".join(tasks),
            *include_args,
        ],
    }
    if not offline_reuse:
        commands["task_materialize"] = [plan["runtime"]["python"], "-c", materialize_code]
    completed: dict[str, subprocess.CompletedProcess[str]] = {}
    for label, command in commands.items():
        result = subprocess.run(
            command,
            cwd=Path(plan["repo_root"]),
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        (preflight_root / f"{label}.stdout.log").write_text(result.stdout, encoding="utf-8")
        (preflight_root / f"{label}.stderr.log").write_text(result.stderr, encoding="utf-8")
        completed[label] = result
    offline_environment = environment.copy()
    offline_environment.update(
        {
            "HF_HUB_OFFLINE": "1",
            "HF_DATASETS_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
        }
    )
    offline_result = subprocess.run(
        [plan["runtime"]["python"], "-c", materialize_code],
        cwd=Path(plan["repo_root"]),
        env=offline_environment,
        capture_output=True,
        text=True,
        check=False,
    )
    (preflight_root / "task_offline_reload.stdout.log").write_text(
        offline_result.stdout, encoding="utf-8"
    )
    (preflight_root / "task_offline_reload.stderr.log").write_text(
        offline_result.stderr, encoding="utf-8"
    )
    completed["task_offline_reload"] = offline_result
    discovered = {
        line.split("|")[1].strip()
        for line in completed["task_list"].stdout.splitlines()
        if line.startswith("|") and len(line.split("|")) >= 3
    }
    rows = [
        {
            "task_id": task,
            "discovered": task in discovered,
            "validation_returncode": completed["task_validate"].returncode,
            "materialization_returncode": (
                None
                if offline_reuse
                else completed["task_materialize"].returncode
            ),
            "offline_reload_returncode": completed["task_offline_reload"].returncode,
            "status": (
                "complete"
                if task in discovered
                and all(result.returncode == 0 for result in completed.values())
                else "failed_pre_scoring"
            ),
            "run_classification": plan["run_classification"],
        }
        for task in tasks
    ]
    if offline_reuse:
        source_manifest, content_rows = _verified_content_manifest(preflight)
        cache_files = [Path(str(row["path"])) for row in content_rows]
        cache_bytes = sum(int(row["bytes"]) for row in content_rows)
    else:
        source_manifest = None
        cache_files = [path for path in sorted(cache_root.rglob("*")) if path.is_file()]
        cache_bytes = sum(path.stat().st_size for path in cache_files)
        content_rows = [
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in cache_files
        ]
    within_bounds = (
        len(cache_files) <= int(preflight["max_cache_files"])
        and cache_bytes <= int(preflight["max_cache_bytes"])
    )
    cache_materialized = (
        len(cache_files) >= int(preflight["min_cache_files"])
        and cache_bytes >= int(preflight["min_cache_bytes"])
    )
    _write_jsonl(output_root / "task_resolution.jsonl", rows)
    if source_manifest is None:
        _write_jsonl(output_root / "dataset_content_manifest.jsonl", content_rows)
    else:
        shutil.copyfile(source_manifest, output_root / "dataset_content_manifest.jsonl")
    status = (
        "complete"
        if all(row["status"] == "complete" for row in rows)
        and within_bounds
        and cache_materialized
        else "failed_pre_scoring"
    )
    payload = {
        "schema_version": 1,
        "status": status,
        "run_classification": plan["run_classification"],
        "started_at": started_at,
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": time.monotonic() - started,
        "task_count": len(tasks),
        "resolved_task_count": sum(row["status"] == "complete" for row in rows),
        "cache_file_count": len(cache_files),
        "cache_bytes": cache_bytes,
        "max_cache_files": int(preflight["max_cache_files"]),
        "max_cache_bytes": int(preflight["max_cache_bytes"]),
        "within_bounds": within_bounds,
        "cache_materialized": cache_materialized,
        "offline_reload_passed": completed["task_offline_reload"].returncode == 0,
        "project_input_lane_count": len(project_rows),
        "data_mode": preflight.get("mode", "network_materialize"),
        "source_content_manifest_sha256": (
            preflight.get("source_content_manifest_sha256") if offline_reuse else None
        ),
        "network_retrieval_used": False if offline_reuse else cache_materialized,
    }
    write_json(preflight_root / "preflight_result.json", payload)
    if status != "complete":
        raise RuntimeError(f"M0 task-data preflight failed: {payload}")
    return payload


def initialize_m0_namespace(output_root: Path, plan: dict[str, Any]) -> Path:
    if output_root.exists():
        raise FileExistsError(f"M0 evaluation namespace already exists: {output_root}")
    output_root.mkdir(parents=True)
    (output_root / "logs").mkdir()
    (output_root / "cache").mkdir()
    for lane in plan["lanes"]:
        (output_root / "lanes" / lane["id"]).mkdir(parents=True)
    write_json(output_root / "parallel_plan.json", plan)
    write_json(
        output_root / "bundle_status.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "status": "planned_not_run",
            "run_classification": plan["run_classification"],
            "lanes": {lane["id"]: "not_run" for lane in plan["lanes"]},
        },
    )
    return output_root


def load_initialized_plan(
    output_root: Path, config_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    planned = json.loads((output_root / "parallel_plan.json").read_text(encoding="utf-8"))
    current = build_m0_parallel_plan(config_path, repo_root=repo_root)
    if (
        planned.get("plan_id") != current["plan_id"]
        or planned.get("config_sha256") != current["config_sha256"]
    ):
        raise ValueError("M0 evaluation plan/config identity changed after submission")
    if not current["execution_ready"] or not current["execution_authorized"]:
        raise PermissionError("M0 evaluation config is not execution-ready and authorized")
    return current


def _inventory_files(root: Path) -> list[dict[str, Any]]:
    return [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name not in {"lane_result.json"}
    ]


def _summary_documents(result: dict[str, Any], lane_root: Path) -> list[dict[str, Any]]:
    artifact_root = Path(str(result.get("artifact_root", lane_root))).resolve()
    try:
        artifact_root.relative_to(lane_root.resolve())
    except ValueError:
        return []
    candidates = [
        path
        for path in sorted(artifact_root.rglob("*.json"))
        if path.name.startswith("results_")
        or path.name in {"summary.json", "summary_metrics.json", "errors.json", "run_manifest.json"}
    ]
    documents: list[dict[str, Any]] = []
    for path in candidates:
        if path.stat().st_size > 10 * 1024 * 1024:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        documents.append(
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "payload": payload,
            }
        )
    return documents


def run_m0_lane(plan: dict[str, Any], lane_index: int, *, output_root: Path) -> dict[str, Any]:
    if not 0 <= lane_index < plan["lane_count"]:
        raise IndexError(f"M0 lane index is out of range: {lane_index}")
    lane = plan["lanes"][lane_index]
    lane_root = output_root / "lanes" / lane["id"]
    result_path = lane_root / "lane_result.json"
    raw_root = lane_root / "raw"
    if result_path.exists() or raw_root.exists():
        raise FileExistsError(f"M0 lane output is not fresh: {lane_root}")
    repo_root = Path(plan["repo_root"])
    raw_root.mkdir()
    write_json(
        lane_root / "lane_identity.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "lane_id": lane["id"],
            "lane_index": lane_index,
            "run_classification": plan["run_classification"],
            "status": "started",
        },
    )
    if lane["adapter"] == "lm_eval":
        command = build_lm_eval_command(plan, lane, repo_root=repo_root, output_path=raw_root)
    else:
        command = build_project_probe_command(plan, lane, repo_root=repo_root)

    cache_paths = _scientific_cache_paths(plan, output_root)
    environment = os.environ.copy()
    environment.update(
        {
            "HF_HOME": str(cache_paths["hf_home"]),
            "HF_DATASETS_CACHE": str(cache_paths["datasets"]),
            "XDG_CACHE_HOME": str(cache_paths["xdg"]),
            "HF_HUB_OFFLINE": "1",
            "HF_DATASETS_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "WANDB_MODE": "disabled",
            "PYTHONDONTWRITEBYTECODE": "1",
            "TMPDIR": str(lane_root / "tmp"),
        }
    )
    (lane_root / "tmp").mkdir()
    stdout_path = lane_root / "stdout.log"
    stderr_path = lane_root / "stderr.log"
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            env=environment,
            stdout=stdout,
            stderr=stderr,
            text=True,
            check=False,
        )
    artifact_root = raw_root
    if lane["adapter"] != "lm_eval" and completed.returncode == 0:
        lines = [
            line.strip()
            for line in stdout_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if not lines:
            completed = subprocess.CompletedProcess(completed.args, 2)
        else:
            candidate = Path(lines[-1])
            if not candidate.is_absolute():
                candidate = repo_root / candidate
            candidate = candidate.resolve()
            try:
                candidate.relative_to(raw_root.resolve())
            except ValueError:
                completed = subprocess.CompletedProcess(completed.args, 2)
            else:
                if candidate.is_dir():
                    artifact_root = candidate
                else:
                    completed = subprocess.CompletedProcess(completed.args, 2)
    raw_files = [path for path in raw_root.rglob("*") if path.is_file()]
    inventory = _inventory_files(lane_root)
    status = (
        "complete"
        if completed.returncode == 0 and raw_files
        else ("partial_invalid" if raw_files else "failed_pre_scoring")
    )
    payload = {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "lane_id": lane["id"],
        "lane_index": lane_index,
        "adapter": lane["adapter"],
        "families": lane["families"],
        "task_ids": lane.get("task_ids", []),
        "run_classification": plan["run_classification"],
        "status": status,
        "returncode": completed.returncode,
        "started_at": started_at,
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": time.monotonic() - started,
        "artifact_root": str(artifact_root),
        "artifacts": inventory,
        "execution": {
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "slurm_node": os.environ.get("SLURMD_NODENAME"),
            "gpu_route_id": os.environ.get("M0_GPU_ROUTE_ID"),
            "gpu_gres": os.environ.get("M0_GPU_GRES"),
            "gpu_partition": os.environ.get("M0_GPU_PARTITION"),
        },
    }
    write_json(result_path, payload)
    if status != "complete":
        raise RuntimeError(f"M0 lane failed: {lane['id']} (exit {completed.returncode})")
    return payload


def finalize_m0_bundle(plan: dict[str, Any], *, output_root: Path) -> dict[str, Any]:
    lane_status: dict[str, str] = {}
    results: list[dict[str, Any]] = []
    for lane in plan["lanes"]:
        path = output_root / "lanes" / lane["id"] / "lane_result.json"
        if not path.is_file():
            lane_status[lane["id"]] = "not_run"
            continue
        result = json.loads(path.read_text(encoding="utf-8"))
        artifacts = result.get("artifacts")
        artifacts_valid = isinstance(artifacts, list) and bool(artifacts)
        if artifacts_valid:
            lane_root = (output_root / "lanes" / lane["id"]).resolve()
            for artifact in artifacts:
                if not isinstance(artifact, dict):
                    artifacts_valid = False
                    break
                artifact_path = Path(str(artifact.get("path", ""))).resolve()
                try:
                    artifact_path.relative_to(lane_root)
                except ValueError:
                    artifacts_valid = False
                    break
                if (
                    not artifact_path.is_file()
                    or artifact.get("bytes") != artifact_path.stat().st_size
                    or artifact.get("sha256") != sha256_file(artifact_path)
                ):
                    artifacts_valid = False
                    break
        valid_identity = (
            result.get("plan_id") == plan["plan_id"]
            and result.get("lane_id") == lane["id"]
            and result.get("run_classification") == plan["run_classification"]
            and result.get("adapter") == lane["adapter"]
            and result.get("families") == lane["families"]
            and result.get("task_ids") == lane.get("task_ids", [])
            and result.get("returncode") == 0
            and artifacts_valid
        )
        lane_status[lane["id"]] = (
            result.get("status", "partial_invalid") if valid_identity else "partial_invalid"
        )
        results.append(result)
    lanes_complete = len(results) == plan["lane_count"] and all(
        status == "complete" for status in lane_status.values()
    )
    lock_path = Path(str(plan["runtime"]["environment_lock_path"]))
    lock_exists = lock_path.is_file()
    lock_observed = sha256_file(lock_path) if lock_exists else None
    lock_valid = lock_observed == plan["runtime"]["environment_lock_sha256"]
    model_manifest = Path(str(plan["model"]["manifest_path"]))
    model_exists = model_manifest.is_file()
    model_observed = sha256_file(model_manifest) if model_exists else None
    model_valid = model_observed == plan["model"]["manifest_sha256"]
    cache_integrity: dict[str, Any] = {"status": "not_applicable"}
    cache_valid = True
    if plan["run_classification"] == "scientific":
        try:
            _, content_rows = _verified_content_manifest(plan["data_preflight"])
            cache_root = Path(str(plan["data_preflight"]["source_cache_root"])).resolve()
            expected_paths = {Path(str(row["path"])).resolve() for row in content_rows}
            observed_paths = {
                path.resolve() for path in cache_root.rglob("*") if path.is_file()
            }
            cache_valid = observed_paths == expected_paths
            cache_integrity = {
                "status": "verified" if cache_valid else "mutated_or_incomplete",
                "manifest_sha256": plan["data_preflight"][
                    "source_content_manifest_sha256"
                ],
                "expected_files": len(expected_paths),
                "observed_files": len(observed_paths),
                "unexpected_files": sorted(str(path) for path in observed_paths - expected_paths),
                "missing_files": sorted(str(path) for path in expected_paths - observed_paths),
            }
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            cache_valid = False
            cache_integrity = {"status": "unavailable_or_mismatched", "error": str(exc)}
    identity_valid = lock_valid and model_valid and cache_valid
    complete = lanes_complete and (
        identity_valid if plan["run_classification"] == "scientific" else True
    )
    payload = {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "status": "complete" if complete else "partial_invalid",
        "run_classification": plan["run_classification"],
        "lane_count": plan["lane_count"],
        "complete_lane_count": sum(status == "complete" for status in lane_status.values()),
        "lanes": lane_status,
        "normalization_allowed": complete,
        "identity_gate": {
            "environment_lock": lock_valid,
            "model_manifest": model_valid,
            "dataset_cache": cache_integrity,
        },
    }
    write_json(output_root / "bundle_status.json", payload)
    manifest_path = output_root / "evaluation_manifest.json"
    if complete:
        if manifest_path.exists():
            raise FileExistsError(f"M0 complete manifest already exists: {manifest_path}")
        write_json(
            manifest_path,
            {
                **payload,
                "config_path": plan["config_path"],
                "config_sha256": plan["config_sha256"],
                "model": plan["model"],
                "harness": plan["harness"],
                "lane_result_paths": [
                    str(output_root / "lanes" / lane["id"] / "lane_result.json")
                    for lane in plan["lanes"]
                ],
            },
        )

    runtime_rows = [
        {
            "lane_id": result.get("lane_id"),
            "adapter": result.get("adapter"),
            "status": result.get("status"),
            "started_at": result.get("started_at"),
            "ended_at": result.get("ended_at"),
            "duration_seconds": result.get("duration_seconds"),
            "returncode": result.get("returncode"),
            "run_classification": plan["run_classification"],
        }
        for result in results
    ]
    _write_jsonl(output_root / "runtime_measurements.jsonl", runtime_rows)
    raw_artifacts = [
        {
            "lane_id": result.get("lane_id"),
            "run_classification": plan["run_classification"],
            **artifact,
        }
        for result in results
        for artifact in result.get("artifacts", [])
        if isinstance(artifact, dict)
    ]
    _write_jsonl(output_root / "raw_artifact_manifest.jsonl", raw_artifacts)
    write_json(
        output_root / "evaluation_results.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "status": payload["status"],
            "run_classification": plan["run_classification"],
            "model": plan["model"],
            "harness": plan["harness"],
            "lane_count": plan["lane_count"],
            "complete_lane_count": payload["complete_lane_count"],
            "raw_artifact_manifest": str(output_root / "raw_artifact_manifest.jsonl"),
            "lanes": [
                {
                    "lane_id": result.get("lane_id"),
                    "adapter": result.get("adapter"),
                    "families": result.get("families"),
                    "task_ids": result.get("task_ids", []),
                    "status": result.get("status"),
                    "returncode": result.get("returncode"),
                    "started_at": result.get("started_at"),
                    "ended_at": result.get("ended_at"),
                    "duration_seconds": result.get("duration_seconds"),
                    "execution": result.get("execution", {}),
                    "artifact_root": result.get("artifact_root"),
                    "summary_documents": _summary_documents(
                        result,
                        output_root / "lanes" / str(result.get("lane_id", "")),
                    ),
                }
                for result in results
            ],
        },
    )

    write_json(
        output_root / "environment_lock.json",
        {
            "schema_version": 1,
            "status": (
                "verified"
                if lock_observed == plan["runtime"]["environment_lock_sha256"]
                else "unavailable_or_mismatched"
            ),
            "path": str(lock_path),
            "expected_sha256": plan["runtime"]["environment_lock_sha256"],
            "observed_sha256": lock_observed,
            "harness": plan["harness"],
            "run_classification": plan["run_classification"],
        },
    )
    write_json(
        output_root / "model_identity.json",
        {
            "schema_version": 1,
            "status": (
                "verified"
                if model_observed == plan["model"]["manifest_sha256"]
                else "unavailable_or_mismatched"
            ),
            **plan["model"],
            "observed_manifest_sha256": model_observed,
            "run_classification": plan["run_classification"],
        },
    )
    if plan["run_classification"] == "test_only_non_scientific":
        parity_rows = [
            {
                "check_id": "wikitext_count_result_and_heading_parity",
                "status": "not_run_blocked",
                "reason": "qualification_v1_smoke_does_not_yet_implement_reviewed_parity_tolerance",
                "run_classification": plan["run_classification"],
            },
            {
                "check_id": "turblimp_16_subtask_macro_parity",
                "status": "not_run_blocked",
                "reason": "qualification_v1_smoke_does_not_yet_implement_reviewed_parity_tolerance",
                "run_classification": plan["run_classification"],
            },
        ]
        _write_jsonl(output_root / "parity_results.jsonl", parity_rows)
        qualification_blockers = [
            f"lane_incomplete:{lane_id}"
            for lane_id, status in lane_status.items()
            if status != "complete"
        ]
        qualification_blockers.extend(row["check_id"] for row in parity_rows)
        write_json(
            output_root / "qualification_manifest.json",
            {
                "schema_version": 1,
                "plan_id": plan["plan_id"],
                "config_path": plan["config_path"],
                "config_sha256": plan["config_sha256"],
                "implementation_commit": plan["runtime"]["implementation_commit"],
                "implementation_files": plan["runtime"]["implementation_files"],
                "model": plan["model"],
                "harness": plan["harness"],
                "run_classification": plan["run_classification"],
                "scientific_result": False,
                "bundle_status": payload["status"],
                "required_lane_count": plan["lane_count"],
                "complete_lane_count": payload["complete_lane_count"],
            },
        )
        write_json(
            output_root / "qualification_result.json",
            {
                "schema_version": 1,
                "plan_id": plan["plan_id"],
                "gate": "blocked",
                "blockers": qualification_blockers,
                "scientific_result": False,
                "scientific_work_started": False,
                "run_classification": plan["run_classification"],
                "note": (
                    "This bounded run may qualify execution mechanics only; its metrics cannot "
                    "enter scientific M0 tables or gates."
                ),
            },
        )
    else:
        write_json(
            output_root / "scientific_bundle_result.json",
            {
                "schema_version": 1,
                "plan_id": plan["plan_id"],
                "status": (
                    "complete_raw_pending_normalization"
                    if complete
                    else "partial_invalid_no_scientific_summary"
                ),
                "run_classification": "scientific",
                "raw_bundle_complete": complete,
                "normalization_allowed": complete,
                "model": plan["model"],
                "identity_gate": payload["identity_gate"],
                "model_pass_fail": "not_computed_by_raw_finalizer",
                "note": (
                    "Scientific metrics remain in immutable raw artifacts until the frozen "
                    "normalizer computes eval-v1 rows and gates."
                ),
            },
        )
    inventory = [
        {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(output_root.rglob("*"))
        if path.is_file() and path.name != "final_inventory.json"
    ]
    write_json(
        output_root / "final_inventory.json",
        {
            "schema_version": 1,
            "inventory_excludes": ["final_inventory.json"],
            "file_count": len(inventory),
            "total_bytes": sum(row["bytes"] for row in inventory),
            "files": inventory,
        },
    )
    return payload
