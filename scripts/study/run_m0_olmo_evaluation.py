#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
from datetime import datetime
from pathlib import Path

from transfer_vs_relearning.study.m0_parallel import (
    assess_m0_parallel_readiness,
    build_m0_parallel_plan,
    finalize_m0_bundle,
    initialize_m0_namespace,
    load_initialized_plan,
    prepare_m0_environment,
    run_m0_data_preflight,
    run_m0_lane,
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


def _probe_gpu_route(plan: dict, route: dict[str, str]) -> dict:
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
    eligible = result.returncode == 0 and estimated_start is not None
    return {
        "route": route,
        "eligible": eligible,
        "returncode": result.returncode,
        "estimated_start": estimated_start,
        "probe_output": output,
    }


def _select_gpu_route(plan: dict, *, output_root: Path) -> dict[str, str]:
    probes = [_probe_gpu_route(plan, route) for route in plan["slurm"]["gpu_routes"]]
    eligible = [
        (probe["estimated_start"], index, probe)
        for index, probe in enumerate(probes)
        if probe["eligible"]
    ]
    selected_probe = min(eligible, default=None)
    payload = {
        "schema_version": 1,
        "policy": plan["slurm"]["gpu_route_selection_policy"],
        "probes": probes,
        "selected_route": selected_probe[2]["route"] if selected_probe else None,
    }
    write_json(output_root / "gpu_route_selection.json", payload)
    if selected_probe is None:
        raise RuntimeError("No configured GPU route passed the Slurm test-only availability gate")
    return selected_probe[2]["route"]


def _select_gpu_routes_for_lanes(plan: dict, *, output_root: Path) -> list[dict]:
    probes = [_probe_gpu_route(plan, route) for route in plan["slurm"]["gpu_routes"]]
    eligible_probes = [probe for probe in probes if probe["eligible"]]
    earliest_start = min(
        (datetime.fromisoformat(probe["estimated_start"]) for probe in eligible_probes),
        default=None,
    )
    max_start_skew_seconds = int(plan["slurm"]["max_route_start_skew_seconds"])
    timely_probes = [
        probe
        for probe in eligible_probes
        if earliest_start is not None
        and (
            datetime.fromisoformat(probe["estimated_start"]) - earliest_start
        ).total_seconds()
        <= max_start_skew_seconds
    ]
    slots: list[tuple[str, int, int, dict]] = []
    for route_index, probe in enumerate(probes):
        if probe not in timely_probes:
            continue
        for slot_index in range(int(probe["route"].get("parallel_slots", 1))):
            slots.append(
                (
                    probe["estimated_start"],
                    route_index,
                    slot_index,
                    probe["route"],
                )
            )
    slots.sort(key=lambda item: (item[0], item[1], item[2]))
    if not slots:
        write_json(
            output_root / "gpu_route_selection.json",
            {
                "schema_version": 2,
                "policy": plan["slurm"]["gpu_route_selection_policy"],
                "probes": probes,
                "max_route_start_skew_seconds": max_start_skew_seconds,
                "earliest_estimated_start": earliest_start.isoformat() if earliest_start else None,
                "excluded_eligible_routes_outside_start_window": [
                    probe["route"]["id"]
                    for probe in eligible_probes
                    if probe not in timely_probes
                ],
                "lane_assignments": [],
            },
        )
        raise RuntimeError("No configured GPU route passed the Slurm test-only availability gate")
    assignments = []
    for lane_index, lane in enumerate(plan["lanes"]):
        estimated_start, _, slot_index, route = slots[lane_index % len(slots)]
        assignments.append(
            {
                "lane_id": lane["id"],
                "lane_index": lane_index,
                "route": route,
                "route_slot": slot_index,
                "estimated_start": estimated_start,
            }
        )
    write_json(
        output_root / "gpu_route_selection.json",
        {
            "schema_version": 2,
            "policy": plan["slurm"]["gpu_route_selection_policy"],
            "probes": probes,
            "max_route_start_skew_seconds": max_start_skew_seconds,
            "earliest_estimated_start": earliest_start.isoformat() if earliest_start else None,
            "excluded_eligible_routes_outside_start_window": [
                probe["route"]["id"]
                for probe in eligible_probes
                if probe not in timely_probes
            ],
            "lane_assignments": assignments,
        },
    )
    return assignments


def _submit_independent_lane_jobs(
    plan: dict,
    *,
    config_path: Path,
    repo_root: Path,
    output_root: Path,
) -> dict:
    script = Path(__file__).resolve()
    runtime = plan["runtime"]
    slurm = plan["slurm"]
    try:
        assignments = _select_gpu_routes_for_lanes(plan, output_root=output_root)
    except Exception as exc:
        write_json(
            output_root / "submission_manifest.json",
            {
                "schema_version": 2,
                "plan_id": plan["plan_id"],
                "status": "no_job_submitted_no_eligible_gpu_route",
                "preflight_job_id": None,
                "lane_jobs": [],
                "finalizer_job_id": None,
                "error": str(exc),
            },
        )
        raise
    common = ["sbatch", "--parsable", f"--account={slurm['account']}"]
    preflight_command = [
        runtime["python"],
        str(script),
        "run-preflight",
        "--config",
        str(config_path),
        "--repo-root",
        str(repo_root),
        "--namespace",
        str(output_root),
    ]
    try:
        preflight_id = _submit(
            [
                *common,
                f"--partition={plan['data_preflight']['partition']}",
                "--job-name=m0-olmo-data",
                f"--cpus-per-task={plan['data_preflight']['cpus_per_task']}",
                f"--mem={plan['data_preflight']['memory']}",
                f"--time={plan['data_preflight']['time_limit']}",
                f"--output={output_root / 'logs/%x-%j.out'}",
                f"--error={output_root / 'logs/%x-%j.err'}",
                f"--chdir={repo_root}",
                f"--wrap=exec {shlex.join(preflight_command)}",
            ]
        )
    except Exception as exc:
        write_json(
            output_root / "submission_manifest.json",
            {
                "schema_version": 2,
                "plan_id": plan["plan_id"],
                "status": "no_job_submitted_preflight_sbatch_rejected",
                "preflight_job_id": None,
                "lane_jobs": [],
                "finalizer_job_id": None,
                "error": str(exc),
            },
        )
        raise

    lane_jobs: list[dict] = []
    for assignment in assignments:
        route = assignment["route"]
        lane_index = assignment["lane_index"]
        lane_command = [
            runtime["python"],
            str(script),
            "run-lane",
            "--config",
            str(config_path),
            "--repo-root",
            str(repo_root),
            "--namespace",
            str(output_root),
            "--lane-index",
            str(lane_index),
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
                f"M0_GPU_GRES={route['gres']}",
                f"M0_GPU_PARTITION={route['partition']}",
            ]
        )
        try:
            job_id = _submit(
                [
                    *common,
                    f"--partition={route['partition']}",
                    f"--job-name=m0-olmo-eval-{lane_index}",
                    f"--dependency=afterok:{preflight_id}",
                    f"--gres={route['gres']}",
                    f"--cpus-per-task={slurm['cpus_per_task']}",
                    f"--mem={route['memory']}",
                    f"--time={slurm['time_limit']}",
                    f"--output={output_root / 'logs/%x-%j.out'}",
                    f"--error={output_root / 'logs/%x-%j.err'}",
                    f"--export={exports}",
                    f"--chdir={repo_root}",
                    f"--wrap=exec {shlex.join(lane_command)}",
                ]
            )
        except Exception as exc:
            write_json(
                output_root / "submission_manifest.json",
                {
                    "schema_version": 2,
                    "plan_id": plan["plan_id"],
                    "status": "partial_submission_preflight_and_lane_jobs_active",
                    "preflight_job_id": preflight_id,
                    "lane_jobs": lane_jobs,
                    "failed_lane_assignment": assignment,
                    "finalizer_job_id": None,
                    "error": str(exc),
                },
            )
            raise
        lane_jobs.append({**assignment, "job_id": job_id})

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
    lane_job_ids = [row["job_id"] for row in lane_jobs]
    finalizer_dependency = "afterany:" + ":".join(lane_job_ids)
    try:
        finalizer_id = _submit(
            [
                *common,
                f"--partition={slurm['control_partition']}",
                "--job-name=m0-olmo-finalize",
                f"--dependency={finalizer_dependency}",
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
                "schema_version": 2,
                "plan_id": plan["plan_id"],
                "status": "partial_submission_lane_jobs_active_finalizer_missing",
                "preflight_job_id": preflight_id,
                "lane_jobs": lane_jobs,
                "finalizer_job_id": None,
                "error": str(exc),
            },
        )
        raise
    payload = {
        "schema_version": 2,
        "plan_id": plan["plan_id"],
        "status": "submitted",
        "submission_mode": "independent_lane_jobs",
        "preflight_job_id": preflight_id,
        "lane_dependency": f"afterok:{preflight_id}",
        "lane_jobs": lane_jobs,
        "lane_job_ids": lane_job_ids,
        "finalizer_job_id": finalizer_id,
        "finalizer_dependency": finalizer_dependency,
        "gpu_route_selection_manifest": str(output_root / "gpu_route_selection.json"),
        "run_classification": plan["run_classification"],
    }
    write_json(output_root / "submission_manifest.json", payload)
    return payload


def _submit_parallel_jobs(
    plan: dict,
    *,
    config_path: Path,
    repo_root: Path,
    output_root: Path,
) -> dict:
    if plan.get("topology") == (
        "gpu_route_selection_per_lane_then_preflight_then_independent_jobs_plus_afterany_finalizer"
    ):
        return _submit_independent_lane_jobs(
            plan,
            config_path=config_path,
            repo_root=repo_root,
            output_root=output_root,
        )
    script = Path(__file__).resolve()
    runtime = plan["runtime"]
    slurm = plan["slurm"]
    try:
        gpu_route = _select_gpu_route(plan, output_root=output_root)
    except Exception as exc:
        write_json(
            output_root / "submission_manifest.json",
            {
                "schema_version": 1,
                "plan_id": plan["plan_id"],
                "status": "no_job_submitted_no_eligible_gpu_route",
                "preflight_job_id": None,
                "array_job_id": None,
                "finalizer_job_id": None,
                "error": str(exc),
            },
        )
        raise
    common = [
        "sbatch",
        "--parsable",
        f"--account={slurm['account']}",
    ]
    preflight_command = [
        runtime["python"],
        str(script),
        "run-preflight",
        "--config",
        str(config_path),
        "--repo-root",
        str(repo_root),
        "--namespace",
        str(output_root),
    ]
    try:
        preflight_id = _submit(
            [
                *common,
                f"--partition={plan['data_preflight']['partition']}",
                "--job-name=m0-olmo-data",
                f"--cpus-per-task={plan['data_preflight']['cpus_per_task']}",
                f"--mem={plan['data_preflight']['memory']}",
                f"--time={plan['data_preflight']['time_limit']}",
                f"--output={output_root / 'logs/%x-%j.out'}",
                f"--error={output_root / 'logs/%x-%j.err'}",
                f"--chdir={repo_root}",
                f"--wrap=exec {shlex.join(preflight_command)}",
            ]
        )
    except Exception as exc:
        write_json(
            output_root / "submission_manifest.json",
            {
                "schema_version": 1,
                "plan_id": plan["plan_id"],
                "status": "no_job_submitted_preflight_sbatch_rejected",
                "preflight_job_id": None,
                "array_job_id": None,
                "finalizer_job_id": None,
                "error": str(exc),
            },
        )
        raise
    lane_command = [
        runtime["python"],
        str(script),
        "run-lane",
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
        ]
    )
    array_argv = [
        *common,
        f"--partition={gpu_route['partition']}",
        "--job-name=m0-olmo-eval",
        f"--dependency=afterok:{preflight_id}",
        f"--array=0-{plan['lane_count'] - 1}%{plan['max_parallel_lanes']}",
        f"--gres={gpu_route['gres']}",
        f"--cpus-per-task={slurm['cpus_per_task']}",
        f"--mem={gpu_route['memory']}",
        f"--time={slurm['time_limit']}",
        f"--output={output_root / 'logs/%x-%A_%a.out'}",
        f"--error={output_root / 'logs/%x-%A_%a.err'}",
        f"--export={exports}",
        f"--chdir={repo_root}",
        f"--wrap=exec {shlex.join(lane_command)}",
    ]
    try:
        array_id = _submit(array_argv)
    except Exception:
        write_json(
            output_root / "submission_manifest.json",
            {
                "schema_version": 1,
                "plan_id": plan["plan_id"],
                "status": "partial_submission_preflight_active_array_missing",
                "preflight_job_id": preflight_id,
                "array_job_id": None,
                "finalizer_job_id": None,
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
        finalizer_id = _submit(
            [
                *common,
                f"--partition={slurm['control_partition']}",
                "--job-name=m0-olmo-finalize",
                f"--dependency=afterany:{array_id}",
                "--cpus-per-task=2",
                "--mem=8G",
                "--time=00:30:00",
                f"--output={output_root / 'logs/%x-%j.out'}",
                f"--error={output_root / 'logs/%x-%j.err'}",
                f"--chdir={repo_root}",
                f"--wrap=exec {shlex.join(final_command)}",
            ]
        )
    except Exception:
        write_json(
            output_root / "submission_manifest.json",
            {
                "schema_version": 1,
                "plan_id": plan["plan_id"],
                "status": "partial_submission_array_active_finalizer_missing",
                "preflight_job_id": preflight_id,
                "array_job_id": array_id,
                "finalizer_job_id": None,
            },
        )
        raise
    payload = {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "status": "submitted",
        "preflight_job_id": preflight_id,
        "array_job_id": array_id,
        "array_dependency": f"afterok:{preflight_id}",
        "array_spec": f"0-{plan['lane_count'] - 1}%{plan['max_parallel_lanes']}",
        "finalizer_job_id": finalizer_id,
        "finalizer_dependency": f"afterany:{array_id}",
        "selected_gpu_route": gpu_route,
        "gpu_route_selection_manifest": str(output_root / "gpu_route_selection.json"),
        "run_classification": plan["run_classification"],
    }
    write_json(output_root / "submission_manifest.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan, submit and finalize the fail-closed parallel OLMo M0 evaluation bundle."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "preflight", "prepare-environment", "submit"):
        command = subparsers.add_parser(name)
        command.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
        command.add_argument("--repo-root", type=Path, default=Path.cwd())
        command.add_argument("--project-state", type=Path, default=DEFAULT_STATE)
        command.add_argument("--namespace", type=Path)

    lane_parser = subparsers.add_parser("run-lane", help=argparse.SUPPRESS)
    lane_parser.add_argument("--config", type=Path, required=True)
    lane_parser.add_argument("--repo-root", type=Path, required=True)
    lane_parser.add_argument("--namespace", type=Path, required=True)
    lane_parser.add_argument("--lane-index", type=int)

    data_parser = subparsers.add_parser("run-preflight", help=argparse.SUPPRESS)
    data_parser.add_argument("--config", type=Path, required=True)
    data_parser.add_argument("--repo-root", type=Path, required=True)
    data_parser.add_argument("--namespace", type=Path, required=True)

    final_parser = subparsers.add_parser("finalize", help=argparse.SUPPRESS)
    final_parser.add_argument("--config", type=Path, required=True)
    final_parser.add_argument("--repo-root", type=Path, required=True)
    final_parser.add_argument("--namespace", type=Path, required=True)

    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    config_path = _resolved(args.config, repo_root)

    if args.command in {"plan", "preflight", "prepare-environment", "submit"}:
        plan = build_m0_parallel_plan(config_path, repo_root=repo_root)
        namespace = args.namespace or Path(plan["storage"]["proposed_root"])
        namespace = _resolved(namespace, repo_root)
    if args.command == "plan":
        print(json.dumps(plan, indent=2, ensure_ascii=False, sort_keys=True))
    elif args.command == "prepare-environment":
        print(
            json.dumps(
                prepare_m0_environment(plan, repo_root=repo_root),
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    elif args.command in {"preflight", "submit"}:
        project_state = _resolved(args.project_state, repo_root)
        readiness = assess_m0_parallel_readiness(
            config_path,
            repo_root=repo_root,
            project_state_path=project_state,
            output_root=namespace,
        )
        if args.command == "preflight":
            print(json.dumps(readiness, indent=2, ensure_ascii=False, sort_keys=True))
            if readiness["status"] != "ready":
                raise SystemExit(2)
        else:
            if readiness["status"] != "ready":
                print(json.dumps(readiness, indent=2, ensure_ascii=False, sort_keys=True))
                raise SystemExit(2)
            initialize_m0_namespace(namespace, plan)
            print(
                json.dumps(
                    _submit_parallel_jobs(
                        plan,
                        config_path=config_path,
                        repo_root=repo_root,
                        output_root=namespace,
                    ),
                    indent=2,
                    sort_keys=True,
                )
            )
    elif args.command == "run-preflight":
        namespace = args.namespace.resolve()
        plan = load_initialized_plan(namespace, config_path, repo_root=repo_root)
        print(json.dumps(run_m0_data_preflight(plan, output_root=namespace), indent=2))
    elif args.command == "run-lane":
        namespace = args.namespace.resolve()
        plan = load_initialized_plan(namespace, config_path, repo_root=repo_root)
        lane_index = args.lane_index
        if lane_index is None:
            raw_index = os.environ.get("SLURM_ARRAY_TASK_ID")
            if raw_index is None or not raw_index.isdigit():
                parser.error("run-lane requires --lane-index or SLURM_ARRAY_TASK_ID")
            lane_index = int(raw_index)
        print(json.dumps(run_m0_lane(plan, lane_index, output_root=namespace), indent=2))
    elif args.command == "finalize":
        namespace = args.namespace.resolve()
        plan = load_initialized_plan(namespace, config_path, repo_root=repo_root)
        payload = finalize_m0_bundle(plan, output_root=namespace)
        print(json.dumps(payload, indent=2, sort_keys=True))
        if payload["status"] != "complete":
            raise SystemExit(2)


if __name__ == "__main__":
    main()
