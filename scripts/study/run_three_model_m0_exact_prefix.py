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

import yaml

from transfer_vs_relearning.study.m0_exact_prefix import (
    audit_exact_prefix_inputs,
    finalize_exact_prefix_family,
    initialize_exact_prefix_namespace,
    load_exact_prefix_plan,
    run_exact_prefix_model,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


DEFAULT_CONFIG = Path("configs/evaluation/m0_exact_prefix_three_model_v1.yaml")
DEFAULT_STATE = Path("documentation/current/PROJECT_STATE.yaml")
START_RE = re.compile(r"\bto start at ([0-9T:+-]+)\b")


def _resolved(path: Path, repo_root: Path) -> Path:
    return path.resolve() if path.is_absolute() else (repo_root / path).resolve()


def _git_identity(repo_root: Path, implementation_commit: str) -> dict[str, Any]:
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, check=True, capture_output=True, text=True
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain=v1"], cwd=repo_root, check=True, capture_output=True, text=True
        ).stdout.strip()
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", implementation_commit, head],
            cwd=repo_root,
            check=False,
        ).returncode == 0
    except (OSError, subprocess.CalledProcessError):
        return {"head": None, "status": "unavailable", "clean": False, "implementation_ancestor": False}
    return {"head": head, "status": status, "clean": not status, "implementation_ancestor": ancestor}


def _home_usage(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        ["du", "-x", "-B1", "-s", str(path)], check=False, capture_output=True, text=True, timeout=600
    )
    observed = None
    if result.returncode == 0 and result.stdout.strip():
        first = result.stdout.split()[0]
        observed = int(first) if first.isdigit() else None
    return {"returncode": result.returncode, "observed_bytes": observed, "stderr": result.stderr.strip()}


def _active_duplicates(job_name: str) -> list[str]:
    result = subprocess.run(
        ["squeue", "-h", "-u", os.environ.get("USER", "yesildau"), "-o", "%i|%j|%T"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [f"squeue_error:{result.stderr.strip()}"]
    return [line for line in result.stdout.splitlines() if f"|{job_name}|" in line]


def assess_readiness(plan: dict[str, Any], *, repo_root: Path, project_state_path: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"id": check_id, "status": "pass" if passed else "blocked", "detail": detail})

    record("contract_frozen", plan["status"] == "frozen", plan["status"])
    record("execution_authorized", plan["execution_authorized"] is True, plan["execution_authorized"])
    root = Path(plan["family_root"])
    record("fresh_family_root", not root.exists(), str(root))
    record("scratch_root_policy", str(root).startswith("/vol/tmp2/yesildau/"), str(root))
    try:
        audit = audit_exact_prefix_inputs(plan)
    except Exception as exc:
        audit = {"status": "blocked", "error": str(exc)}
    record("exact_prefix_input_audit", audit.get("status") == "pass", audit)

    model_checks: dict[str, Any] = {}
    for model in plan["models"]:
        path = Path(model["manifest_path"])
        valid = path.is_file() and sha256_file(path) == model["manifest_sha256"]
        if valid:
            manifest = json.loads(path.read_text(encoding="utf-8"))
            valid = manifest.get("resolved_revision") == model["revision"]
        model_checks[model["model_id"]] = valid
    record("model_manifest_identities", all(model_checks.values()), model_checks)

    state = yaml.safe_load(project_state_path.read_text(encoding="utf-8"))
    scoped = state.get("authorization", {}).get("scoped", {}).get("m0_exact_prefix_supplement", {})
    record(
        "project_exact_prefix_authorization",
        scoped.get("status") == "authorized_single_wave"
        and scoped.get("execution_authorized") is True
        and scoped.get("config_sha256") == plan["config_sha256"],
        scoped.get("status", "missing"),
    )
    record("project_ready_to_measure", state.get("readiness", {}).get("ready_to_measure") is True, state.get("readiness", {}))
    record("project_not_ready_to_train", state.get("readiness", {}).get("ready_to_train") is False, state.get("readiness", {}))

    git_identity = _git_identity(repo_root, plan["implementation"]["commit"])
    record("clean_git_and_implementation_ancestor", git_identity["clean"] and git_identity["implementation_ancestor"], git_identity)
    file_identity: dict[str, bool] = {}
    for relative, expected in plan["implementation"]["files"].items():
        path = repo_root / relative
        file_identity[relative] = path.is_file() and sha256_file(path) == expected
    record("implementation_file_identities", all(file_identity.values()), file_identity)

    runtime = plan["runtime"]
    python = Path(runtime["python"])
    lock = Path(runtime["environment_lock_path"])
    runtime_ok = python.is_file() and os.access(python, os.X_OK)
    lock_ok = lock.is_file() and sha256_file(lock) == runtime["environment_lock_sha256"]
    record("runtime_environment_identity", runtime_ok and lock_ok, {"python": runtime_ok, "lock": lock_ok})

    home = _home_usage(Path(plan["hu_home_gate"]["path"]))
    home_ok = home["observed_bytes"] is not None and home["observed_bytes"] < plan["hu_home_gate"]["limit_bytes"]
    record("hu_home_30_gib_gate", home_ok, home)
    duplicates = _active_duplicates(plan["slurm"]["job_name"])
    record("no_duplicate_jobs", not duplicates, duplicates)
    blockers = [row["id"] for row in checks if row["status"] != "pass"]
    return {
        "schema_version": 1,
        "scope": "m0_three_model_exact_prefix_preflight",
        "status": "ready" if not blockers else "blocked_pre_scoring",
        "scientific_work_started": False,
        "plan_id": plan["plan_id"],
        "checks": checks,
        "blockers": blockers,
    }


def _job_id(stdout: str) -> str:
    value = stdout.strip().split(";", 1)[0]
    if not value.isdigit():
        raise ValueError(f"Unexpected sbatch output: {stdout!r}")
    return value


def _submit(argv: list[str]) -> str:
    result = subprocess.run(argv, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"sbatch failed: stdout={result.stdout!r}, stderr={result.stderr!r}")
    return _job_id(result.stdout)


def _route_probe(plan: dict[str, Any]) -> dict[str, Any]:
    slurm = plan["slurm"]
    argv = [
        "sbatch",
        "--test-only",
        f"--account={slurm['account']}",
        f"--partition={slurm['partition']}",
        f"--gres={slurm['gres']}",
        f"--cpus-per-task={slurm['cpus_per_task']}",
        f"--mem={slurm['memory']}",
        f"--time={slurm['time_limit']}",
        "--wrap=true",
    ]
    result = subprocess.run(argv, check=False, capture_output=True, text=True)
    output = "\n".join(value.strip() for value in (result.stdout, result.stderr) if value.strip())
    match = START_RE.search(output)
    return {
        "eligible": result.returncode == 0 and match is not None,
        "returncode": result.returncode,
        "estimated_start": match.group(1) if match else None,
        "output": output,
    }


def submit_wave(plan: dict[str, Any], *, config_path: Path, repo_root: Path) -> dict[str, Any]:
    root = initialize_exact_prefix_namespace(plan)
    probe = _route_probe(plan)
    write_json(root / "route_probe.json", probe)
    if not probe["eligible"]:
        write_json(
            root / "submission_manifest.json",
            {
                "schema_version": 1,
                "status": "no_job_submitted_route_blocked",
                "plan_id": plan["plan_id"],
                "config_sha256": plan["config_sha256"],
                "array_job_id": None,
                "finalizer_job_id": None,
                "route_probe": probe,
            },
        )
        raise RuntimeError("Frozen RTX A6000 route did not pass sbatch --test-only")
    slurm = plan["slurm"]
    script = repo_root / "scripts/study/run_three_model_m0_exact_prefix.py"
    lane_command = [
        plan["runtime"]["python"],
        str(script),
        "run-model",
        "--config",
        str(config_path),
        "--repo-root",
        str(repo_root),
    ]
    exports = "ALL,TRANSFORMERS_OFFLINE=1,HF_HUB_OFFLINE=1,HF_DATASETS_OFFLINE=1,WANDB_MODE=disabled,PYTHONDONTWRITEBYTECODE=1"
    array_id = _submit(
        [
            "sbatch",
            "--parsable",
            f"--account={slurm['account']}",
            f"--partition={slurm['partition']}",
            f"--job-name={slurm['job_name']}",
            f"--array=0-2%3",
            f"--gres={slurm['gres']}",
            f"--cpus-per-task={slurm['cpus_per_task']}",
            f"--mem={slurm['memory']}",
            f"--time={slurm['time_limit']}",
            f"--output={root / 'logs/%x-%A_%a.out'}",
            f"--error={root / 'logs/%x-%A_%a.err'}",
            f"--export={exports}",
            f"--chdir={repo_root}",
            f"--wrap=exec {shlex.join(lane_command)}",
        ]
    )
    final_command = [
        plan["runtime"]["python"],
        str(script),
        "finalize",
        "--config",
        str(config_path),
        "--repo-root",
        str(repo_root),
    ]
    try:
        finalizer_id = _submit(
            [
                "sbatch",
                "--parsable",
                f"--account={slurm['account']}",
                f"--partition={slurm['control_partition']}",
                f"--job-name={slurm['job_name']}-final",
                f"--dependency=afterany:{array_id}",
                "--cpus-per-task=2",
                "--mem=8G",
                "--time=00:30:00",
                f"--output={root / 'logs/%x-%j.out'}",
                f"--error={root / 'logs/%x-%j.err'}",
                f"--chdir={repo_root}",
                f"--wrap=exec {shlex.join(final_command)}",
            ]
        )
    except Exception:
        write_json(
            root / "submission_manifest.json",
            {
                "schema_version": 1,
                "status": "partial_submission_array_active_finalizer_missing",
                "plan_id": plan["plan_id"],
                "config_sha256": plan["config_sha256"],
                "array_job_id": array_id,
                "array_spec": "0-2%3",
                "finalizer_job_id": None,
                "route_probe": probe,
            },
        )
        raise
    payload = {
        "schema_version": 1,
        "status": "submitted",
        "plan_id": plan["plan_id"],
        "config_sha256": plan["config_sha256"],
        "array_job_id": array_id,
        "array_spec": "0-2%3",
        "finalizer_job_id": finalizer_id,
        "finalizer_dependency": f"afterany:{array_id}",
        "route_probe": probe,
    }
    write_json(root / "submission_manifest.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the separate three-model M0 exact-prefix supplement")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "preflight", "submit", "run-model", "finalize"):
        command = sub.add_parser(name)
        command.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
        command.add_argument("--repo-root", type=Path, default=Path.cwd())
        if name in {"preflight", "submit"}:
            command.add_argument("--project-state", type=Path, default=DEFAULT_STATE)
        if name == "run-model":
            command.add_argument("--model-index", type=int)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    config_path = _resolved(args.config, repo_root)
    plan = load_exact_prefix_plan(config_path, repo_root=repo_root)
    if args.command == "plan":
        print(json.dumps(plan, indent=2, sort_keys=True))
    elif args.command in {"preflight", "submit"}:
        state_path = _resolved(args.project_state, repo_root)
        readiness = assess_readiness(plan, repo_root=repo_root, project_state_path=state_path)
        if readiness["status"] != "ready":
            print(json.dumps(readiness, indent=2, sort_keys=True))
            raise SystemExit(2)
        if args.command == "preflight":
            print(json.dumps(readiness, indent=2, sort_keys=True))
        else:
            print(json.dumps(submit_wave(plan, config_path=config_path, repo_root=repo_root), indent=2, sort_keys=True))
    elif args.command == "run-model":
        index = args.model_index
        if index is None:
            raw = os.environ.get("SLURM_ARRAY_TASK_ID", "")
            if not raw.isdigit():
                parser.error("run-model requires --model-index or SLURM_ARRAY_TASK_ID")
            index = int(raw)
        print(json.dumps(run_exact_prefix_model(plan, index), indent=2, sort_keys=True))
    else:
        payload = finalize_exact_prefix_family(plan)
        print(json.dumps(payload, indent=2, sort_keys=True))
        if payload["status"] != "complete":
            raise SystemExit(2)


if __name__ == "__main__":
    main()
