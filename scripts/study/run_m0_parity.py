#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.study.adapters.m0_evaluation import verify_m0_model_manifest
from transfer_vs_relearning.study.m0_parity import (
    build_parity_plan,
    finalize_parity_bundle,
    initialize_parity_namespace,
    load_initialized_parity_plan,
    run_heading_sensitivity,
    run_structural_parity,
    validate_source_lane,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


DEFAULT_CONFIG = Path("configs/evaluation/m0_olmo_eval_v1_parity_v1.yaml")
TEST_ONLY_START_RE = re.compile(r"\bto start at ([0-9T:+-]+)\b")


def _resolved(path: Path, repo_root: Path) -> Path:
    return path.resolve() if path.is_absolute() else (repo_root / path).resolve()


def _job_id(stdout: str) -> str:
    value = stdout.strip().split(";", 1)[0]
    if not value.isdigit():
        raise ValueError(f"Unexpected sbatch --parsable output: {stdout!r}")
    return value


def _submit(argv: list[str]) -> str:
    result = subprocess.run(argv, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "Slurm submission failed "
            f"(exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r})"
        )
    return _job_id(result.stdout)


def _probe_route(plan: dict[str, Any]) -> dict[str, Any]:
    slurm = plan["slurm"]
    route = slurm["gpu_route"]
    argv = [
        "sbatch",
        "--test-only",
        f"--account={slurm['account']}",
        f"--partition={route['partition']}",
        f"--gres={route['gres']}",
        f"--cpus-per-task={slurm['cpus_per_task']}",
        f"--mem={route['memory']}",
        f"--time={slurm['time_limit']}",
        "--wrap=true",
    ]
    result = subprocess.run(argv, check=False, capture_output=True, text=True)
    output = "\n".join(value.strip() for value in (result.stdout, result.stderr) if value.strip())
    match = TEST_ONLY_START_RE.search(output)
    return {
        "route": route,
        "eligible": result.returncode == 0 and match is not None,
        "returncode": result.returncode,
        "estimated_start": match.group(1) if match else None,
        "probe_output": output,
    }


def _git_identity(repo_root: Path, implementation_commit: str | None) -> tuple[bool, str]:
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
        commit_ok = bool(implementation_commit) and subprocess.run(
            ["git", "merge-base", "--is-ancestor", str(implementation_commit), head],
            cwd=repo_root,
            check=False,
        ).returncode == 0
    except (OSError, subprocess.CalledProcessError):
        return False, "git_identity_unavailable"
    return commit_ok and not dirty, f"head={head}, commit={commit_ok}, clean={not dirty}"


def assess_parity_readiness(
    config_path: Path, *, repo_root: Path, output_root: Path
) -> dict[str, Any]:
    plan = build_parity_plan(config_path, repo_root=repo_root)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"id": check_id, "status": "pass" if passed else "blocked", "detail": detail})

    record("contract_frozen", plan["status"] == "frozen", plan["status"])
    record("execution_authorized", plan["execution_authorized"] is True, plan["execution_authorized"])
    record("test_only_classification", plan["run_classification"] == "test_only_non_scientific", plan["run_classification"])
    record("output_namespace_fresh", not output_root.exists(), str(output_root))
    record("scratch_output_policy", str(output_root).startswith("/vol/tmp2/yesildau/"), str(output_root))

    runtime = plan["runtime"]
    python = Path(runtime["python"])
    lock_path = Path(runtime["environment_lock_path"])
    runtime_ok = python.is_file() and os.access(python, os.X_OK)
    lock_ok = lock_path.is_file() and sha256_file(lock_path) == runtime["environment_lock_sha256"]
    record("runtime_and_environment_lock", runtime_ok and lock_ok, {"python": runtime_ok, "lock": lock_ok})
    try:
        distribution = importlib.metadata.distribution("lm-eval") if python == Path(os.sys.executable) else None
        if distribution is None:
            code = (
                "import importlib.metadata,json;"
                "d=importlib.metadata.distribution('lm-eval');"
                "u=json.loads(d.read_text('direct_url.json') or '{}');"
                "print(json.dumps({'version':d.version,'commit':u.get('vcs_info',{}).get('commit_id','')}))"
            )
            observed_harness = json.loads(
                subprocess.run(
                    [str(python), "-c", code], check=True, capture_output=True, text=True
                ).stdout
            )
        else:
            direct = json.loads(distribution.read_text("direct_url.json") or "{}")
            observed_harness = {
                "version": distribution.version,
                "commit": direct.get("vcs_info", {}).get("commit_id", ""),
            }
    except (OSError, subprocess.CalledProcessError, importlib.metadata.PackageNotFoundError, json.JSONDecodeError):
        observed_harness = {}
    harness_ok = observed_harness == {
        "version": str(runtime["lm_eval_release"]).removeprefix("v"),
        "commit": runtime["lm_eval_commit"],
    }
    record("lm_eval_identity", harness_ok, observed_harness)

    git_ok, git_detail = _git_identity(repo_root, runtime.get("implementation_commit"))
    record("implementation_git_identity", git_ok, git_detail)
    implementation_ok = all(
        (repo_root / relative).is_file()
        and sha256_file(repo_root / relative) == expected
        for relative, expected in runtime.get("implementation_files", {}).items()
    )
    record("implementation_file_identity", implementation_ok, sorted(runtime.get("implementation_files", {})))

    upstream_ok = True
    upstream_detail: dict[str, bool] = {}
    for label, row in runtime["upstream_task_files"].items():
        path = Path(row["path"])
        matches = path.is_file() and sha256_file(path) == row["sha256"]
        upstream_detail[label] = matches
        upstream_ok = upstream_ok and matches
    record("upstream_task_identity", upstream_ok, upstream_detail)

    overlay = repo_root / plan["wikitext"]["heading_overlay"]["include_path"]
    record("heading_overlay_present", overlay.is_dir(), str(overlay))
    source_cache = Path(plan["source"]["root"]) / "cache"
    record("offline_source_cache_present", source_cache.is_dir() and any(source_cache.iterdir()), str(source_cache))
    recovery_result = Path(plan["source"]["recovery_root"]) / "qualification_result.json"
    recovery_ok = (
        recovery_result.is_file()
        and sha256_file(recovery_result) == plan["source"]["recovery_result_sha256"]
    )
    record("seven_lane_recovery_result_identity", recovery_ok, str(recovery_result))
    try:
        verify_m0_model_manifest(plan, repo_root=repo_root)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        record("model_manifest_and_local_snapshot", False, str(exc))
    else:
        record("model_manifest_and_local_snapshot", True, plan["model"]["manifest_sha256"])
    for lane_id in ("english_retention_wikitext", "turkish_capability"):
        try:
            validate_source_lane(plan, lane_id)
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            record(f"source_lane_{lane_id}", False, str(exc))
        else:
            record(f"source_lane_{lane_id}", True, plan["source"][lane_id]["lane_result_sha256"])

    blockers = [row["id"] for row in checks if row["status"] != "pass"]
    return {
        "schema_version": 1,
        "scope": "m0_olmo_qualification_parity_preflight",
        "status": "ready" if not blockers else "blocked_pre_scoring",
        "scientific_work_started": False,
        "plan_id": plan["plan_id"],
        "output_root": str(output_root),
        "checks": checks,
        "blockers": blockers,
    }


def run_gpu_memory_guard(output_root: Path, *, minimum: int) -> dict[str, Any]:
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable for WikiText heading sensitivity")
    free_bytes, total_bytes = (int(value) for value in torch.cuda.mem_get_info(0))
    payload = {
        "schema_version": 1,
        "status": "pass" if free_bytes >= minimum else "blocked",
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_node": os.environ.get("SLURMD_NODENAME"),
        "gpu_route_id": os.environ.get("M0_GPU_ROUTE_ID"),
        "free_bytes": free_bytes,
        "total_bytes": total_bytes,
        "min_free_bytes": minimum,
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(output_root / "heading" / "gpu_memory_preflight.json", payload)
    if payload["status"] != "pass":
        raise RuntimeError(f"GPU free-memory gate failed: {free_bytes} < {minimum}")
    return payload


def submit_parity(
    plan: dict[str, Any], *, config_path: Path, repo_root: Path, output_root: Path
) -> dict[str, Any]:
    structural = run_structural_parity(plan, output_root)
    probe = _probe_route(plan)
    write_json(
        output_root / "gpu_route_selection.json",
        {
            "schema_version": 1,
            "policy": "exact_v100_route_with_test_only_probe_and_runtime_free_memory_gate",
            "probe": probe,
            "selected_route": probe["route"] if probe["eligible"] else None,
            "min_free_bytes": plan["slurm"]["min_free_gpu_bytes"],
        },
    )
    if structural["status"] != "pass" or not probe["eligible"]:
        payload = {
            "schema_version": 1,
            "status": "no_job_submitted_structural_or_route_gate",
            "plan_id": plan["plan_id"],
            "heading_job_id": None,
            "finalizer_job_id": None,
        }
        write_json(output_root / "submission_manifest.json", payload)
        raise RuntimeError("Structural parity or exact GPU route gate failed")

    script = Path(__file__).resolve()
    runtime = plan["runtime"]
    slurm = plan["slurm"]
    route = slurm["gpu_route"]
    common = ["sbatch", "--parsable", f"--account={slurm['account']}"]
    heading_command = [
        runtime["python"],
        str(script),
        "run-heading",
        "--config",
        str(config_path),
        "--repo-root",
        str(repo_root),
        "--namespace",
        str(output_root),
    ]
    exports = ",".join(
        [
            "ALL",
            f"HF_HOME={output_root / 'cache/huggingface'}",
            f"HF_DATASETS_CACHE={output_root / 'cache/huggingface_datasets'}",
            f"XDG_CACHE_HOME={output_root / 'cache'}",
            "HF_HUB_OFFLINE=1",
            "HF_DATASETS_OFFLINE=1",
            "TRANSFORMERS_OFFLINE=1",
            "WANDB_MODE=disabled",
            "PYTHONDONTWRITEBYTECODE=1",
            f"M0_GPU_ROUTE_ID={route['id']}",
        ]
    )
    try:
        heading_job_id = _submit(
            [
                *common,
                f"--partition={route['partition']}",
                "--job-name=m0-olmo-parity-heading",
                f"--gres={route['gres']}",
                f"--cpus-per-task={slurm['cpus_per_task']}",
                f"--mem={route['memory']}",
                f"--time={slurm['time_limit']}",
                f"--output={output_root / 'logs/%x-%j.out'}",
                f"--error={output_root / 'logs/%x-%j.err'}",
                f"--export={exports}",
                f"--chdir={repo_root}",
                f"--wrap=exec {shlex.join(heading_command)}",
            ]
        )
    except Exception as exc:
        write_json(
            output_root / "submission_manifest.json",
            {
                "schema_version": 1,
                "status": "no_job_submitted_heading_sbatch_rejected",
                "plan_id": plan["plan_id"],
                "heading_job_id": None,
                "finalizer_job_id": None,
                "error": str(exc),
            },
        )
        raise

    final_command = [
        runtime["python"],
        str(script),
        "finalize",
        "--config",
        str(config_path),
        "--repo-root",
        str(repo_root),
        "--namespace",
        str(output_root),
    ]
    try:
        finalizer_job_id = _submit(
            [
                *common,
                f"--partition={slurm['control_partition']}",
                "--job-name=m0-olmo-parity-final",
                f"--dependency=afterany:{heading_job_id}",
                "--cpus-per-task=2",
                "--mem=8G",
                "--time=00:30:00",
                f"--output={output_root / 'logs/%x-%j.out'}",
                f"--error={output_root / 'logs/%x-%j.err'}",
                f"--chdir={repo_root}",
                f"--wrap=exec {shlex.join(final_command)}",
            ]
        )
    except Exception as exc:
        write_json(
            output_root / "submission_manifest.json",
            {
                "schema_version": 1,
                "status": "partial_submission_heading_active_finalizer_missing",
                "plan_id": plan["plan_id"],
                "heading_job_id": heading_job_id,
                "finalizer_job_id": None,
                "error": str(exc),
            },
        )
        raise
    payload = {
        "schema_version": 1,
        "status": "submitted",
        "plan_id": plan["plan_id"],
        "run_classification": plan["run_classification"],
        "heading_job_id": heading_job_id,
        "finalizer_job_id": finalizer_job_id,
        "finalizer_dependency": f"afterany:{heading_job_id}",
        "output_root": str(output_root),
        "route": route,
    }
    write_json(output_root / "submission_manifest.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate M0 WikiText and TurBLiMP parity.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "submit", "run-heading", "finalize"):
        command = subparsers.add_parser(name, help=argparse.SUPPRESS if name.startswith("run-") else None)
        command.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
        command.add_argument("--repo-root", type=Path, default=Path.cwd())
        command.add_argument("--namespace", type=Path)

    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    config_path = _resolved(args.config, repo_root)
    base_plan = build_parity_plan(config_path, repo_root=repo_root)
    output_root = (args.namespace or Path(base_plan["storage"]["proposed_root"])).resolve()

    if args.command in {"preflight", "submit"}:
        readiness = assess_parity_readiness(
            config_path, repo_root=repo_root, output_root=output_root
        )
        if args.command == "preflight":
            print(json.dumps(readiness, indent=2, ensure_ascii=False, sort_keys=True))
            if readiness["status"] != "ready":
                raise SystemExit(2)
            return
        if readiness["status"] != "ready":
            print(json.dumps(readiness, indent=2, ensure_ascii=False, sort_keys=True))
            raise SystemExit(2)
        initialize_parity_namespace(base_plan, output_root)
        print(
            json.dumps(
                submit_parity(
                    base_plan,
                    config_path=config_path,
                    repo_root=repo_root,
                    output_root=output_root,
                ),
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return

    plan = load_initialized_parity_plan(output_root, config_path, repo_root=repo_root)
    if args.command == "run-heading":
        run_gpu_memory_guard(output_root, minimum=int(plan["slurm"]["min_free_gpu_bytes"]))
        payload = run_heading_sensitivity(plan, output_root)
    else:
        payload = finalize_parity_bundle(plan, output_root)
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    if payload.get("status") not in {"complete", "pass"}:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
