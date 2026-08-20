#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.study.m0_family_recovery import (
    finalize_family_recovery,
    finalize_recovered_model,
    initialize_family_recovery_namespace,
    load_family_recovery_plan,
    validate_family_recovery_source,
)
from transfer_vs_relearning.study.m0_parallel import load_initialized_plan, run_m0_lane
from transfer_vs_relearning.study.m0_recovery import run_gpu_memory_guard
from transfer_vs_relearning.utils.io import sha256_file, write_json


DEFAULT_CONFIG = Path("configs/evaluation/m0_scientific_recovery_v1.yaml")
DEFAULT_STATE = Path("documentation/current/PROJECT_STATE.yaml")
TEST_ONLY_START_RE = re.compile(r"\bto start at ([0-9T:+-]+)\b")
JOB_PREFIX = "m0r-v1-"


def _resolved(path: Path, repo_root: Path) -> Path:
    return path.resolve() if path.is_absolute() else (repo_root / path).resolve()


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, check=False, capture_output=True, text=True)


def _job_id(stdout: str) -> str:
    value = stdout.strip().split(";", 1)[0]
    if not value.isdigit():
        raise ValueError(f"Unexpected sbatch --parsable output: {stdout!r}")
    return value


def _submit(argv: list[str]) -> str:
    result = _run(argv)
    if result.returncode != 0:
        raise RuntimeError(
            "Slurm submission failed "
            f"(exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r})"
        )
    return _job_id(result.stdout)


def _route(model: dict[str, Any], route_id: str) -> dict[str, Any]:
    matches = [route for route in model["plan"]["slurm"]["gpu_routes"] if route["id"] == route_id]
    if len(matches) != 1:
        raise ValueError(f"Recovery route must resolve exactly once: {model['model_id']}/{route_id}")
    return matches[0]


def _probe_route(model: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
    slurm = model["plan"]["slurm"]
    result = _run(
        [
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
    )
    output = "\n".join(value.strip() for value in (result.stdout, result.stderr) if value.strip())
    match = TEST_ONLY_START_RE.search(output)
    return {
        "model_id": model["model_id"],
        "route": route,
        "eligible": result.returncode == 0 and match is not None,
        "returncode": result.returncode,
        "estimated_start": match.group(1) if match else None,
        "probe_output": output,
    }


def _gpu_inventory() -> list[dict[str, Any]]:
    result = _run(
        [
            "nvidia-smi",
            "--query-gpu=uuid,name,memory.total,memory.free",
            "--format=csv,noheader,nounits",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(f"nvidia-smi inventory failed: {result.stderr.strip()}")
    rows: list[dict[str, Any]] = []
    for line in result.stdout.splitlines():
        fields = [value.strip() for value in line.split(",")]
        if len(fields) != 4:
            raise ValueError(f"Malformed nvidia-smi row: {line!r}")
        rows.append(
            {
                "uuid": fields[0],
                "name": fields[1],
                "total_bytes": int(fields[2]) * 1024**2,
                "free_bytes": int(fields[3]) * 1024**2,
            }
        )
    return rows


def _select_isolated_gpu(
    recovery: dict[str, Any],
    *,
    lane_label: str,
    min_free_bytes: int,
    attempts: list[dict[str, Any]],
) -> str:
    policy = recovery["isolation"]
    deadline = time.monotonic() + int(policy["max_wait_seconds"])
    expected_count = int(policy["requested_gpu_count"])
    while True:
        rows = _gpu_inventory()
        eligible = [
            row
            for row in rows
            if row["name"] == policy["expected_gpu_name"]
            and row["total_bytes"] >= int(policy["min_total_gpu_bytes"])
            and row["free_bytes"] >= min_free_bytes
        ]
        selected = max(eligible, key=lambda row: (row["free_bytes"], row["uuid"])) if eligible else None
        attempt = {
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "lane": lane_label,
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "slurm_node": os.environ.get("SLURMD_NODENAME"),
            "cuda_visible_devices_before_selection": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "minimum_free_bytes": min_free_bytes,
            "expected_gpu_count": expected_count,
            "gpus": rows,
            "selected_uuid": selected["uuid"] if selected else None,
            "status": "pass" if selected and len(rows) == expected_count else "waiting",
        }
        attempts.append(attempt)
        write_json(
            Path(recovery["recovery_family_root"]) / "gpu_isolation_audit.json",
            {"schema_version": 1, "attempts": attempts},
        )
        if selected and len(rows) == expected_count:
            return str(selected["uuid"])
        if time.monotonic() >= deadline:
            raise RuntimeError(f"No eligible isolated A100 remained available for {lane_label}")
        time.sleep(int(policy["poll_interval_seconds"]))


def run_isolated_wave(
    recovery: dict[str, Any],
    *,
    config_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    script = Path(__file__).resolve()
    model_map = {model["model_id"]: model for model in recovery["models"]}
    for target in recovery["isolation"]["target_order"]:
        model_id, lane_id = target.split(":", 1)
        model = model_map[model_id]
        frozen_target = model["targets"][lane_id]
        lane_index = next(
            index for index, lane in enumerate(model["plan"]["lanes"]) if lane["id"] == lane_id
        )
        minimum = int(frozen_target["min_free_gpu_bytes"])
        row: dict[str, Any] = {
            "model_id": model_id,
            "lane_id": lane_id,
            "lane_index": lane_index,
            "minimum_free_bytes": minimum,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            selected_uuid = _select_isolated_gpu(
                recovery,
                lane_label=target,
                min_free_bytes=minimum,
                attempts=attempts,
            )
            row["selected_uuid"] = selected_uuid
            command = [
                model["plan"]["runtime"]["python"],
                str(script),
                "run-lane",
                "--config",
                str(config_path),
                "--repo-root",
                str(repo_root),
                "--model-id",
                model_id,
                "--lane-id",
                lane_id,
                "--lane-index",
                str(lane_index),
                "--min-free-gpu-bytes",
                str(minimum),
            ]
            environment = dict(os.environ)
            environment.update(
                {
                    "CUDA_VISIBLE_DEVICES": selected_uuid,
                    "M0_GPU_ROUTE_ID": "a10080gb_exclusive_uuid",
                    "M0_GPU_GRES": "gpu:a10080gb:3",
                    "M0_GPU_PARTITION": "gpu",
                    "HF_HUB_OFFLINE": "1",
                    "HF_DATASETS_OFFLINE": "1",
                    "TRANSFORMERS_OFFLINE": "1",
                    "WANDB_MODE": "disabled",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONPATH": str(repo_root / "src"),
                }
            )
            log_root = Path(recovery["recovery_family_root"]) / "logs" / "isolated_children"
            log_root.mkdir(parents=True, exist_ok=True)
            stdout_path = log_root / f"{model_id}-{lane_id}.out"
            stderr_path = log_root / f"{model_id}-{lane_id}.err"
            with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open(
                "w", encoding="utf-8"
            ) as stderr:
                child = subprocess.run(
                    command,
                    check=False,
                    cwd=repo_root,
                    env=environment,
                    stdout=stdout,
                    stderr=stderr,
                    text=True,
                )
            row.update(
                {
                    "returncode": child.returncode,
                    "status": "complete" if child.returncode == 0 else "failed",
                    "stdout": str(stdout_path),
                    "stderr": str(stderr_path),
                }
            )
        except (OSError, ValueError, RuntimeError) as exc:
            row.update({"returncode": None, "status": "blocked", "error": str(exc)})
        row["finished_at"] = datetime.now(timezone.utc).isoformat()
        ledger.append(row)
        write_json(
            Path(recovery["recovery_family_root"]) / "isolated_wave_ledger.json",
            {"schema_version": 1, "status": "running", "lanes": ledger},
        )
    lane_count = len(recovery["isolation"]["target_order"])
    complete = sum(row["status"] == "complete" for row in ledger)
    payload = {
        "schema_version": 1,
        "status": "complete" if complete == lane_count else "partial_invalid",
        "complete_lane_count": complete,
        "lane_count": lane_count,
        "lanes": ledger,
    }
    write_json(Path(recovery["recovery_family_root"]) / "isolated_wave_ledger.json", payload)
    return payload


def _measure_home(path: str, limit_bytes: int) -> dict[str, Any]:
    result = _run(["du", "-sb", "--", path])
    try:
        observed = int(result.stdout.split()[0]) if result.returncode == 0 else None
    except (IndexError, ValueError):
        observed = None
    passed = observed is not None and observed <= limit_bytes
    return {
        "status": "pass" if passed else "blocked",
        "path": path,
        "limit_bytes": limit_bytes,
        "observed_bytes": observed,
        "headroom_bytes": limit_bytes - observed if observed is not None else None,
        "returncode": result.returncode,
        "stderr": result.stderr.strip(),
    }


def _git_identity(repo_root: Path, implementation_commit: str) -> dict[str, Any]:
    head = _run(["git", "-C", str(repo_root), "rev-parse", "HEAD"])
    ancestry = _run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", implementation_commit, "HEAD"]
    )
    status = _run(["git", "-C", str(repo_root), "status", "--porcelain"])
    return {
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "head_resolved": head.returncode == 0,
        "implementation_is_ancestor": ancestry.returncode == 0,
        "worktree_clean": status.returncode == 0 and not status.stdout.strip(),
        "status_output": status.stdout,
    }


def assess_recovery_readiness(
    config_path: Path,
    *,
    repo_root: Path,
    project_state_path: Path,
) -> dict[str, Any]:
    recovery = load_family_recovery_plan(config_path, repo_root=repo_root)
    checks: list[dict[str, str]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append(
            {"id": check_id, "status": "pass" if passed else "blocked", "detail": str(detail)}
        )

    record("contract_frozen", recovery["status"] == "frozen", recovery["status"])
    record(
        "recovery_execution_authorized",
        recovery.get("execution_authorized") is True,
        recovery.get("execution_authorized"),
    )
    record(
        "fresh_recovery_family_root",
        not Path(recovery["recovery_family_root"]).exists(),
        recovery["recovery_family_root"],
    )
    try:
        evidence = validate_family_recovery_source(recovery)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        evidence = None
        record("frozen_source_and_retained_evidence", False, exc)
    else:
        record("frozen_source_and_retained_evidence", True, evidence["source_family_bundle_sha256"])

    state = yaml.safe_load(project_state_path.read_text(encoding="utf-8"))
    family_state = state["evaluation_target"]["pipeline"]["scientific_m0_family"]
    record("project_ready_to_measure", state["readiness"]["ready_to_measure"] is True, "ready_to_measure")
    record("project_not_ready_to_train", state["readiness"]["ready_to_train"] is False, "ready_to_train=false")
    record(
        "terminal_source_state",
        family_state["status"] == "terminal_partial_invalid_17_of_24",
        family_state["status"],
    )
    scoped_key = {
        "exclusive_a100_sequential": "m0_seven_lane_exclusive_a100_recovery",
        "retargeted_five_lane": "m0_five_lane_retargeted_recovery",
    }.get(recovery.get("mode"), "m0_seven_lane_recovery")
    scoped = state.get("authorization", {}).get("scoped", {}).get(scoped_key, {})
    record(
        "project_recovery_authorization",
        scoped.get("status") == "authorized_single_wave"
        and scoped.get("execution_authorized") is True
        and scoped.get("config_sha256") == recovery["config_sha256"],
        scoped.get("status", "missing"),
    )

    implementation = recovery["implementation"]
    identity = _git_identity(repo_root, implementation["commit"])
    record("implementation_commit_ancestor", identity["implementation_is_ancestor"], identity["head"])
    record("clean_hu_worktree", identity["worktree_clean"], identity["status_output"])
    for relative, expected in implementation["files"].items():
        path = repo_root / relative
        passed = path.is_file() and sha256_file(path) == expected
        record(f"implementation_file:{relative}", passed, expected)

    home = _measure_home(recovery["hu_home_gate"]["path"], recovery["hu_home_gate"]["limit_bytes"])
    record("hu_home_30_gib_gate", home["status"] == "pass", home.get("observed_bytes"))
    duplicate = _run(["squeue", "-h", "-u", os.environ.get("USER", "yesildau"), "-o", "%j"])
    names = duplicate.stdout.splitlines() if duplicate.returncode == 0 else []
    conflicts = sorted(name for name in names if name.startswith(JOB_PREFIX))
    record("no_duplicate_recovery_jobs", duplicate.returncode == 0 and not conflicts, conflicts)
    blockers = [row["id"] for row in checks if row["status"] != "pass"]
    return {
        "schema_version": 1,
        "scope": "m0_three_model_recovery_preflight",
        "status": "ready" if not blockers else "blocked_pre_scoring",
        "scientific_work_started": False,
        "config_path": recovery["config_path"],
        "config_sha256": recovery["config_sha256"],
        "source_evidence": evidence,
        "hu_home_gate": home,
        "git_identity": identity,
        "checks": checks,
        "blockers": blockers,
    }


def _initialized_model(recovery: dict[str, Any], model_id: str) -> dict[str, Any]:
    matches = [model for model in recovery["models"] if model["model_id"] == model_id]
    if len(matches) != 1:
        raise ValueError(f"Recovery model must resolve exactly once: {model_id}")
    model = matches[0]
    manifest = json.loads(
        (Path(model["recovery_root"]) / "recovery_manifest.json").read_text(encoding="utf-8")
    )
    if manifest.get("plan_id") != model["plan"]["plan_id"] or manifest.get("targets") != model["targets"]:
        raise ValueError(f"Initialized recovery model identity mismatch: {model_id}")
    return model


def submit_isolated_family_recovery(
    recovery: dict[str, Any],
    *,
    config_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    initialize_family_recovery_namespace(recovery)
    family_root = Path(recovery["recovery_family_root"])
    policy = recovery["isolation"]
    script = Path(__file__).resolve()
    first = recovery["models"][0]["plan"]
    slurm = first["slurm"]
    probe = _run(
        [
            "sbatch",
            "--test-only",
            f"--account={slurm['account']}",
            f"--partition={policy['partition']}",
            f"--nodelist={policy['node']}",
            f"--gres={policy['gres']}",
            "--exclusive",
            f"--cpus-per-task={policy['cpus_per_task']}",
            f"--mem={policy['memory']}",
            f"--time={policy['time_limit']}",
            "--wrap=true",
        ]
    )
    probe_output = "\n".join(value.strip() for value in (probe.stdout, probe.stderr) if value.strip())
    probe_payload = {
        "schema_version": 1,
        "returncode": probe.returncode,
        "output": probe_output,
        "eligible": probe.returncode == 0 and TEST_ONLY_START_RE.search(probe_output) is not None,
        "policy": policy,
    }
    write_json(family_root / "exclusive_route_probe.json", probe_payload)
    if not probe_payload["eligible"]:
        write_json(
            family_root / "submission_manifest.json",
            {"schema_version": 1, "status": "no_jobs_submitted_route_gate_failed"},
        )
        raise RuntimeError("Exclusive three-A100 route failed its Slurm test-only gate")

    exports = ",".join(
        [
            "ALL",
            f"PYTHONPATH={repo_root / 'src'}",
            "PYTHONDONTWRITEBYTECODE=1",
            "HF_HUB_OFFLINE=1",
            "HF_DATASETS_OFFLINE=1",
            "TRANSFORMERS_OFFLINE=1",
            "WANDB_MODE=disabled",
        ]
    )
    wave_command = [
        first["runtime"]["python"],
        str(script),
        "run-isolated-wave",
        "--config",
        str(config_path),
        "--repo-root",
        str(repo_root),
    ]
    wave_job = _submit(
        [
            "sbatch",
            "--parsable",
            f"--account={slurm['account']}",
            f"--partition={policy['partition']}",
            f"--nodelist={policy['node']}",
            f"--job-name={JOB_PREFIX}isolated-wave",
            f"--gres={policy['gres']}",
            "--exclusive",
            f"--cpus-per-task={policy['cpus_per_task']}",
            f"--mem={policy['memory']}",
            f"--time={policy['time_limit']}",
            f"--output={family_root / 'logs/%x-%j.out'}",
            f"--error={family_root / 'logs/%x-%j.err'}",
            f"--export={exports}",
            f"--chdir={repo_root}",
            f"--wrap=exec {shlex.join(wave_command)}",
        ]
    )
    model_finalizers: dict[str, str] = {}
    for model in recovery["models"]:
        command = [
            model["plan"]["runtime"]["python"],
            str(script),
            "finalize-model",
            "--config",
            str(config_path),
            "--repo-root",
            str(repo_root),
            "--model-id",
            model["model_id"],
        ]
        model_finalizers[model["model_id"]] = _submit(
            [
                "sbatch",
                "--parsable",
                f"--account={slurm['account']}",
                f"--partition={slurm['control_partition']}",
                f"--job-name={JOB_PREFIX}{model['model_id']}-isolated-final",
                f"--dependency=afterany:{wave_job}",
                "--cpus-per-task=2",
                "--mem=8G",
                "--time=00:30:00",
                f"--output={family_root / 'logs/%x-%j.out'}",
                f"--error={family_root / 'logs/%x-%j.err'}",
                f"--export={exports}",
                f"--chdir={repo_root}",
                f"--wrap=exec {shlex.join(command)}",
            ]
        )
    family_command = [
        first["runtime"]["python"],
        str(script),
        "finalize-family",
        "--config",
        str(config_path),
        "--repo-root",
        str(repo_root),
    ]
    dependency = ":".join(model_finalizers.values())
    family_finalizer = _submit(
        [
            "sbatch",
            "--parsable",
            f"--account={slurm['account']}",
            f"--partition={slurm['control_partition']}",
            f"--job-name={JOB_PREFIX}isolated-family-final",
            f"--dependency=afterany:{dependency}",
            "--cpus-per-task=2",
            "--mem=8G",
            "--time=00:30:00",
            f"--output={family_root / 'logs/%x-%j.out'}",
            f"--error={family_root / 'logs/%x-%j.err'}",
            f"--export={exports}",
            f"--chdir={repo_root}",
            f"--wrap=exec {shlex.join(family_command)}",
        ]
    )
    payload = {
        "schema_version": 1,
        "status": "submitted",
        "topology": "one_exclusive_three_a100_sequential_wave_plus_four_finalizers",
        "config_path": recovery["config_path"],
        "config_sha256": recovery["config_sha256"],
        "source_family_root": recovery["source_family_root"],
        "recovery_family_root": recovery["recovery_family_root"],
        "wave_job": wave_job,
        "model_finalizers": model_finalizers,
        "family_finalizer": family_finalizer,
        "route_probe": probe_payload,
    }
    write_json(family_root / "submission_manifest.json", payload)
    return payload


def submit_family_recovery(
    recovery: dict[str, Any],
    *,
    config_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    if recovery.get("mode") in {"exclusive_a100_sequential", "retargeted_five_lane"}:
        return submit_isolated_family_recovery(
            recovery, config_path=config_path, repo_root=repo_root
        )
    initialize_family_recovery_namespace(recovery)
    family_root = Path(recovery["recovery_family_root"])
    script = Path(__file__).resolve()
    probes: dict[str, Any] = {}
    for model in recovery["models"]:
        for target in model["targets"].values():
            key = f"{model['model_id']}:{target['route_id']}"
            if key not in probes:
                route = _route(model, target["route_id"])
                probes[key] = _probe_route(model, route)
    write_json(family_root / "gpu_route_selection.json", {"schema_version": 1, "probes": probes})
    if not all(probe["eligible"] for probe in probes.values()):
        payload = {"schema_version": 1, "status": "no_jobs_submitted_route_gate_failed", "probes": probes}
        write_json(family_root / "submission_manifest.json", payload)
        raise RuntimeError("At least one exact recovery GPU route failed its Slurm test-only gate")

    lane_jobs: dict[str, dict[str, str]] = {}
    model_finalizers: dict[str, str] = {}
    for model in recovery["models"]:
        plan = model["plan"]
        slurm = plan["slurm"]
        runtime = plan["runtime"]
        lane_jobs[model["model_id"]] = {}
        for lane_id, target in model["targets"].items():
            route = _route(model, target["route_id"])
            lane_index = next(index for index, lane in enumerate(plan["lanes"]) if lane["id"] == lane_id)
            command = [
                runtime["python"], str(script), "run-lane", "--config", str(config_path),
                "--repo-root", str(repo_root), "--model-id", model["model_id"], "--lane-id", lane_id,
                "--lane-index", str(lane_index), "--min-free-gpu-bytes", str(target["min_free_gpu_bytes"]),
            ]
            exports = ",".join(
                [
                    "ALL", "HF_HUB_OFFLINE=1", "HF_DATASETS_OFFLINE=1", "TRANSFORMERS_OFFLINE=1",
                    "WANDB_MODE=disabled", "PYTHONDONTWRITEBYTECODE=1",
                    f"M0_GPU_ROUTE_ID={route['id']}", f"M0_GPU_GRES={route['gres']}",
                    f"M0_GPU_PARTITION={route['partition']}",
                ]
            )
            job_id = _submit(
                [
                    "sbatch", "--parsable", f"--account={slurm['account']}",
                    f"--partition={route['partition']}", f"--job-name={JOB_PREFIX}{model['model_id']}-{lane_index}",
                    f"--gres={route['gres']}", f"--cpus-per-task={slurm['cpus_per_task']}",
                    f"--mem={route['memory']}", f"--time={slurm['time_limit']}",
                    f"--output={family_root / 'logs/%x-%j.out'}", f"--error={family_root / 'logs/%x-%j.err'}",
                    f"--export={exports}", f"--chdir={repo_root}", f"--wrap=exec {shlex.join(command)}",
                ]
            )
            lane_jobs[model["model_id"]][lane_id] = job_id
        final_command = [
            runtime["python"], str(script), "finalize-model", "--config", str(config_path),
            "--repo-root", str(repo_root), "--model-id", model["model_id"],
        ]
        dependency = ":".join(lane_jobs[model["model_id"]].values())
        model_finalizers[model["model_id"]] = _submit(
            [
                "sbatch", "--parsable", f"--account={slurm['account']}",
                f"--partition={slurm['control_partition']}", f"--job-name={JOB_PREFIX}{model['model_id']}-final",
                f"--dependency=afterany:{dependency}", "--cpus-per-task=2", "--mem=8G", "--time=00:30:00",
                f"--output={family_root / 'logs/%x-%j.out'}", f"--error={family_root / 'logs/%x-%j.err'}",
                f"--chdir={repo_root}", f"--wrap=exec {shlex.join(final_command)}",
            ]
        )
    first = recovery["models"][0]["plan"]
    family_command = [
        first["runtime"]["python"], str(script), "finalize-family", "--config", str(config_path),
        "--repo-root", str(repo_root),
    ]
    dependency = ":".join(model_finalizers.values())
    family_finalizer = _submit(
        [
            "sbatch", "--parsable", f"--account={first['slurm']['account']}",
            f"--partition={first['slurm']['control_partition']}", f"--job-name={JOB_PREFIX}family-final",
            f"--dependency=afterany:{dependency}", "--cpus-per-task=2", "--mem=8G", "--time=00:30:00",
            f"--output={family_root / 'logs/%x-%j.out'}", f"--error={family_root / 'logs/%x-%j.err'}",
            f"--chdir={repo_root}", f"--wrap=exec {shlex.join(family_command)}",
        ]
    )
    payload = {
        "schema_version": 1,
        "status": "submitted",
        "config_path": recovery["config_path"],
        "config_sha256": recovery["config_sha256"],
        "source_family_root": recovery["source_family_root"],
        "recovery_family_root": recovery["recovery_family_root"],
        "lane_jobs": lane_jobs,
        "model_finalizers": model_finalizers,
        "family_finalizer": family_finalizer,
        "route_probes": probes,
    }
    write_json(family_root / "submission_manifest.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Recover exactly seven missing scientific M0 lanes")
    parser.add_argument(
        "command",
        choices=(
            "plan",
            "preflight",
            "submit",
            "status",
            "run-lane",
            "run-isolated-wave",
            "finalize-model",
            "finalize-family",
        ),
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--project-state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--model-id")
    parser.add_argument("--lane-id")
    parser.add_argument("--lane-index", type=int)
    parser.add_argument("--min-free-gpu-bytes", type=int)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    config_path = _resolved(args.config, repo_root)
    state_path = _resolved(args.project_state, repo_root)
    recovery = load_family_recovery_plan(config_path, repo_root=repo_root)
    if args.command == "plan":
        payload = recovery
    elif args.command == "preflight":
        payload = assess_recovery_readiness(config_path, repo_root=repo_root, project_state_path=state_path)
    elif args.command == "submit":
        readiness = assess_recovery_readiness(config_path, repo_root=repo_root, project_state_path=state_path)
        if readiness["status"] != "ready":
            print(json.dumps(readiness, ensure_ascii=False, indent=2, sort_keys=True))
            raise SystemExit(2)
        payload = submit_family_recovery(recovery, config_path=config_path, repo_root=repo_root)
    elif args.command == "status":
        root = Path(recovery["recovery_family_root"])
        path = root / "three_model_m0_composite_bundle.json"
        payload = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {
            "schema_version": 1, "status": "not_submitted_or_incomplete", "root": str(root)
        }
    elif args.command == "run-lane":
        if args.model_id is None or args.lane_id is None or args.lane_index is None or args.min_free_gpu_bytes is None:
            parser.error("run-lane requires model-id, lane-id, lane-index and min-free-gpu-bytes")
        model = _initialized_model(recovery, args.model_id)
        if args.lane_id not in model["targets"]:
            raise ValueError("Requested lane is not a frozen recovery target")
        plan = load_initialized_plan(Path(model["recovery_root"]), Path(model["config_path"]), repo_root=repo_root)
        if plan["lanes"][args.lane_index]["id"] != args.lane_id:
            raise ValueError("Recovery lane index/ID mismatch")
        runtime_output_subdir = model["targets"][args.lane_id].get("runtime_output_subdir")
        if runtime_output_subdir is not None:
            lane = plan["lanes"][args.lane_index]
            if lane["adapter"] != "project_corpus_perplexity" or runtime_output_subdir != "corpora":
                raise ValueError("Runtime output retarget is allowed only for corpus PPL/corpora")
            lane["runtime_output_root"] = str(
                Path(model["recovery_root"])
                / "lanes"
                / args.lane_id
                / "raw"
                / runtime_output_subdir
            )
        run_gpu_memory_guard(Path(model["recovery_root"]), args.lane_id, min_free_bytes=args.min_free_gpu_bytes)
        payload = run_m0_lane(plan, args.lane_index, output_root=Path(model["recovery_root"]))
    elif args.command == "run-isolated-wave":
        if recovery.get("mode") not in {"exclusive_a100_sequential", "retargeted_five_lane"}:
            raise ValueError("run-isolated-wave requires the exclusive A100 sequential contract")
        payload = run_isolated_wave(recovery, config_path=config_path, repo_root=repo_root)
    elif args.command == "finalize-model":
        if args.model_id is None:
            parser.error("finalize-model requires model-id")
        payload = finalize_recovered_model(_initialized_model(recovery, args.model_id))
    else:
        payload = finalize_family_recovery(recovery)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    if args.command == "preflight" and payload["status"] != "ready":
        raise SystemExit(2)
    if args.command == "run-isolated-wave" and payload["status"] != "complete":
        raise SystemExit(2)
    if args.command == "finalize-model" and payload["status"] != "complete":
        raise SystemExit(2)
    if args.command == "finalize-family" and not payload["normalization_allowed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
