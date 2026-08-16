#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any

from transfer_vs_relearning.study.m0_parallel import (
    assess_m0_parallel_readiness,
    build_m0_parallel_plan,
    load_initialized_plan,
    run_m0_lane,
)
from transfer_vs_relearning.study.m0_recovery import (
    finalize_recovery_bundle,
    initialize_recovery_namespace,
    run_gpu_memory_guard,
    validate_recovery_source,
)
from transfer_vs_relearning.utils.io import write_json


DEFAULT_CONFIG = Path("configs/evaluation/m0_olmo_eval_v1_qualification_v1.yaml")
DEFAULT_STATE = Path("documentation/current/PROJECT_STATE.yaml")
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


def _probe_route(plan: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
    slurm = plan["slurm"]
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
    start_match = TEST_ONLY_START_RE.search(output)
    estimated_start = start_match.group(1) if start_match else None
    return {
        "route": route,
        "eligible": result.returncode == 0 and estimated_start is not None,
        "returncode": result.returncode,
        "estimated_start": estimated_start,
        "probe_output": output,
    }


def _route(plan: dict[str, Any], route_id: str) -> dict[str, Any]:
    matches = [route for route in plan["slurm"]["gpu_routes"] if route["id"] == route_id]
    if len(matches) != 1:
        raise ValueError(f"Recovery GPU route must resolve exactly once: {route_id}")
    return matches[0]


def assess_recovery_readiness(
    config_path: Path,
    *,
    repo_root: Path,
    project_state_path: Path,
    source_root: Path,
    recovery_root: Path,
    lane_id: str,
    route_id: str,
) -> dict[str, Any]:
    plan = build_m0_parallel_plan(config_path, repo_root=repo_root)
    base = assess_m0_parallel_readiness(
        config_path,
        repo_root=repo_root,
        project_state_path=project_state_path,
        output_root=recovery_root,
    )
    checks = list(base["checks"])

    def record(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"id": check_id, "status": "pass" if passed else "blocked", "detail": detail})

    try:
        source = validate_recovery_source(plan, source_root, lane_id)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        source = None
        record("source_bundle_reusable", False, str(exc))
    else:
        record("source_bundle_reusable", True, source["source_bundle_status_sha256"])
    try:
        route = _route(plan, route_id)
    except ValueError as exc:
        route = None
        record("recovery_gpu_route", False, str(exc))
    else:
        record("recovery_gpu_route", True, f"{route['partition']}:{route['gres']}")
    blockers = [row["id"] for row in checks if row["status"] != "pass"]
    return {
        "schema_version": 1,
        "scope": "m0_single_lane_recovery_preflight",
        "status": "ready" if not blockers else "blocked_pre_scoring",
        "scientific_work_started": False,
        "plan_id": plan["plan_id"],
        "source_root": str(source_root.resolve()),
        "recovery_root": str(recovery_root.resolve()),
        "lane_id": lane_id,
        "route_id": route_id,
        "checks": checks,
        "blockers": blockers,
        "source_evidence": source,
        "route": route,
    }


def submit_recovery(
    plan: dict[str, Any],
    *,
    config_path: Path,
    repo_root: Path,
    source_root: Path,
    recovery_root: Path,
    lane_id: str,
    route_id: str,
    min_free_bytes: int,
) -> dict[str, Any]:
    route = _route(plan, route_id)
    probe = _probe_route(plan, route)
    write_json(
        recovery_root / "gpu_route_selection.json",
        {
            "schema_version": 1,
            "policy": "exact_recovery_route_with_test_only_probe_and_runtime_free_memory_gate",
            "probe": probe,
            "selected_route": route if probe["eligible"] else None,
            "min_free_bytes": min_free_bytes,
        },
    )
    if not probe["eligible"]:
        payload = {
            "schema_version": 1,
            "status": "no_job_submitted_no_eligible_gpu_route",
            "plan_id": plan["plan_id"],
            "lane_id": lane_id,
            "lane_job_id": None,
            "finalizer_job_id": None,
        }
        write_json(recovery_root / "submission_manifest.json", payload)
        raise RuntimeError("The exact recovery GPU route failed the Slurm test-only gate")

    lane_index = next(index for index, lane in enumerate(plan["lanes"]) if lane["id"] == lane_id)
    runtime = plan["runtime"]
    slurm = plan["slurm"]
    script = Path(__file__).resolve()
    common = ["sbatch", "--parsable", f"--account={slurm['account']}"]
    lane_command = [
        runtime["python"],
        str(script),
        "run-lane",
        "--config",
        str(config_path),
        "--repo-root",
        str(repo_root),
        "--source-namespace",
        str(source_root),
        "--recovery-namespace",
        str(recovery_root),
        "--lane-id",
        lane_id,
        "--lane-index",
        str(lane_index),
        "--min-free-gpu-bytes",
        str(min_free_bytes),
    ]
    exports = ",".join(
        [
            "ALL",
            f"HF_HOME={recovery_root / 'cache/huggingface'}",
            f"HF_DATASETS_CACHE={recovery_root / 'cache/huggingface_datasets'}",
            f"XDG_CACHE_HOME={recovery_root / 'cache'}",
            "HF_HUB_OFFLINE=1",
            "HF_DATASETS_OFFLINE=1",
            "TRANSFORMERS_OFFLINE=1",
            "WANDB_MODE=disabled",
            "PYTHONDONTWRITEBYTECODE=1",
            f"M0_GPU_ROUTE_ID={route['id']}",
            f"M0_GPU_GRES={route['gres']}",
            f"M0_GPU_PARTITION={route['partition']}",
        ]
    )
    try:
        lane_job_id = _submit(
            [
                *common,
                f"--partition={route['partition']}",
                "--job-name=m0-olmo-recover-en",
                f"--gres={route['gres']}",
                f"--cpus-per-task={slurm['cpus_per_task']}",
                f"--mem={route['memory']}",
                f"--time={slurm['time_limit']}",
                f"--output={recovery_root / 'logs/%x-%j.out'}",
                f"--error={recovery_root / 'logs/%x-%j.err'}",
                f"--export={exports}",
                f"--chdir={repo_root}",
                f"--wrap=exec {shlex.join(lane_command)}",
            ]
        )
    except Exception as exc:
        write_json(
            recovery_root / "submission_manifest.json",
            {
                "schema_version": 1,
                "status": "no_job_submitted_lane_sbatch_rejected",
                "plan_id": plan["plan_id"],
                "lane_id": lane_id,
                "lane_job_id": None,
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
        "--source-namespace",
        str(source_root),
        "--recovery-namespace",
        str(recovery_root),
        "--lane-id",
        lane_id,
    ]
    try:
        finalizer_job_id = _submit(
            [
                *common,
                f"--partition={slurm['control_partition']}",
                "--job-name=m0-olmo-recover-final",
                f"--dependency=afterany:{lane_job_id}",
                "--cpus-per-task=2",
                "--mem=8G",
                "--time=00:30:00",
                f"--output={recovery_root / 'logs/%x-%j.out'}",
                f"--error={recovery_root / 'logs/%x-%j.err'}",
                f"--chdir={repo_root}",
                f"--wrap=exec {shlex.join(final_command)}",
            ]
        )
    except Exception as exc:
        write_json(
            recovery_root / "submission_manifest.json",
            {
                "schema_version": 1,
                "status": "partial_submission_lane_active_finalizer_missing",
                "plan_id": plan["plan_id"],
                "lane_id": lane_id,
                "lane_job_id": lane_job_id,
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
        "source_root": str(source_root),
        "recovery_root": str(recovery_root),
        "lane_id": lane_id,
        "lane_index": lane_index,
        "route": route,
        "min_free_gpu_bytes": min_free_bytes,
        "lane_job_id": lane_job_id,
        "finalizer_job_id": finalizer_job_id,
        "finalizer_dependency": f"afterany:{lane_job_id}",
    }
    write_json(recovery_root / "submission_manifest.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover one incomplete M0 lane and assemble it with a validated source bundle."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "submit"):
        command = subparsers.add_parser(name)
        command.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
        command.add_argument("--repo-root", type=Path, default=Path.cwd())
        command.add_argument("--project-state", type=Path, default=DEFAULT_STATE)
        command.add_argument("--source-namespace", type=Path, required=True)
        command.add_argument("--recovery-namespace", type=Path, required=True)
        command.add_argument("--lane-id", default="english_capability")
        command.add_argument("--route-id", default="v10032gb")
        command.add_argument("--min-free-gpu-bytes", type=int, default=16 * 1024**3)

    lane_parser = subparsers.add_parser("run-lane", help=argparse.SUPPRESS)
    lane_parser.add_argument("--config", type=Path, required=True)
    lane_parser.add_argument("--repo-root", type=Path, required=True)
    lane_parser.add_argument("--source-namespace", type=Path, required=True)
    lane_parser.add_argument("--recovery-namespace", type=Path, required=True)
    lane_parser.add_argument("--lane-id", required=True)
    lane_parser.add_argument("--lane-index", type=int, required=True)
    lane_parser.add_argument("--min-free-gpu-bytes", type=int, required=True)

    final_parser = subparsers.add_parser("finalize", help=argparse.SUPPRESS)
    final_parser.add_argument("--config", type=Path, required=True)
    final_parser.add_argument("--repo-root", type=Path, required=True)
    final_parser.add_argument("--source-namespace", type=Path, required=True)
    final_parser.add_argument("--recovery-namespace", type=Path, required=True)
    final_parser.add_argument("--lane-id", required=True)

    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    config_path = _resolved(args.config, repo_root)
    source_root = args.source_namespace.resolve()
    recovery_root = args.recovery_namespace.resolve()

    if args.command in {"preflight", "submit"}:
        project_state = _resolved(args.project_state, repo_root)
        readiness = assess_recovery_readiness(
            config_path,
            repo_root=repo_root,
            project_state_path=project_state,
            source_root=source_root,
            recovery_root=recovery_root,
            lane_id=args.lane_id,
            route_id=args.route_id,
        )
        if args.command == "preflight":
            print(json.dumps(readiness, indent=2, ensure_ascii=False, sort_keys=True))
            if readiness["status"] != "ready":
                raise SystemExit(2)
            return
        if readiness["status"] != "ready":
            print(json.dumps(readiness, indent=2, ensure_ascii=False, sort_keys=True))
            raise SystemExit(2)
        plan = build_m0_parallel_plan(config_path, repo_root=repo_root)
        initialize_recovery_namespace(
            plan,
            source_root=source_root,
            recovery_root=recovery_root,
            lane_id=args.lane_id,
        )
        payload = submit_recovery(
            plan,
            config_path=config_path,
            repo_root=repo_root,
            source_root=source_root,
            recovery_root=recovery_root,
            lane_id=args.lane_id,
            route_id=args.route_id,
            min_free_bytes=args.min_free_gpu_bytes,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    elif args.command == "run-lane":
        plan = load_initialized_plan(recovery_root, config_path, repo_root=repo_root)
        if plan["lanes"][args.lane_index]["id"] != args.lane_id:
            raise ValueError("Recovery lane index/ID mismatch")
        validate_recovery_source(plan, source_root, args.lane_id)
        run_gpu_memory_guard(
            recovery_root,
            args.lane_id,
            min_free_bytes=args.min_free_gpu_bytes,
        )
        print(json.dumps(run_m0_lane(plan, args.lane_index, output_root=recovery_root), indent=2))
    elif args.command == "finalize":
        plan = load_initialized_plan(recovery_root, config_path, repo_root=repo_root)
        payload = finalize_recovery_bundle(
            plan,
            source_root=source_root,
            recovery_root=recovery_root,
            lane_id=args.lane_id,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        if payload["status"] != "complete":
            raise SystemExit(2)


if __name__ == "__main__":
    main()
