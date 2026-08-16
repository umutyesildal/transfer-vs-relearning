#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from transfer_vs_relearning.experiments.m1_dose_pareto import (
    FALCON_EVALUATION_RECOVERY_SHA256,
    FALCON_EVALUATION_RTXA6000_EXCLUSIVE_SHA256,
    load_registry,
    validate_falcon_evaluation_recovery_state,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


TARGET_PARTITION = "gpu"
TARGET_NODE = "gruenau8"
TARGET_GRES = "gpu:rtxa6000:1"
DEAD_SUMMARY_JOB_ID = "456415"


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--summary-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    registry_path = args.registry.resolve()
    registry = load_registry(registry_path)
    root = Path(registry["scratch_root"]).resolve()
    output = args.output.resolve()
    if output.exists() or output.parent != root / "preflight":
        raise FileExistsError(f"exclusive recovery preflight output invalid/existing: {output}")
    if run("git", "-C", str(repo_root), "rev-parse", "HEAD") != args.expected_commit:
        raise ValueError("HU commit drift")
    policy = registry["home_storage_policy"]
    if bool(policy["home_write_allowed"]) or bool(policy["recursive_du_per_stage"]):
        raise ValueError("No-home-write policy drift")

    active = run(
        "squeue", "-h", "-n",
        "m1-v4-eval-falcon,m1-v4-eval-falcon-recovery,m1-v4-eval-falcon-a6000-recovery,m1-v4-eval-falcon-a6000-exclusive,m1-v4-falcon-summary",
        "-o", "%A|%T|%j|%r",
    )
    rows = [row for row in active.splitlines() if row]
    dead_rows = [row for row in rows if row.split("|", 1)[0] == DEAD_SUMMARY_JOB_ID]
    other_rows = [row for row in rows if row.split("|", 1)[0] != DEAD_SUMMARY_JOB_ID]
    if other_rows:
        raise ValueError(f"Duplicate Falcon recovery/evaluation job exists: {other_rows}")
    if dead_rows and (
        len(dead_rows) != 1
        or dead_rows[0].split("|")[:3] != [DEAD_SUMMARY_JOB_ID, "PENDING", "m1-v4-falcon-summary"]
        or dead_rows[0].split("|", 3)[3] != "DependencyNeverSatisfied"
    ):
        raise ValueError(f"Dead summary reconciliation drift: {dead_rows}")

    route = run("sinfo", "-h", "-p", TARGET_PARTITION, "-n", TARGET_NODE, "-N", "-o", "%N|%P|%a|%t|%G")
    route_rows = [row for row in route.splitlines() if row]
    if len(route_rows) != 1:
        raise ValueError(f"Exact A6000 route is not uniquely visible: {route_rows}")
    node, partition, available, state, gres = route_rows[0].split("|", 4)
    if (
        node != TARGET_NODE
        or partition.rstrip("*") != TARGET_PARTITION
        or available != "up"
        or state.split("+", 1)[0] not in {"idle", "mix", "alloc"}
        or "gpu:rtxa6000:" not in gres
    ):
        raise ValueError(f"A6000 route drift: {route_rows[0]}")

    state_payload = validate_falcon_evaluation_recovery_state(registry, summary_root=args.summary_root.resolve())
    usage = shutil.disk_usage(root)
    stat = os.statvfs(root)
    if usage.free < 20 * 1024**3 or stat.f_favail < 1_000:
        raise ValueError("Falcon recovery scratch capacity/inode gate failed")
    payload = {
        **state_payload,
        "timestamp": datetime.now(UTC).isoformat(),
        "expected_commit": args.expected_commit,
        "registry": str(registry_path),
        "registry_sha256": sha256_file(registry_path),
        "source_recovery_contract_sha256": FALCON_EVALUATION_RECOVERY_SHA256,
        "exclusive_recovery_contract_sha256": FALCON_EVALUATION_RTXA6000_EXCLUSIVE_SHA256,
        "active_duplicate_jobs": [],
        "dead_summary_job_id": DEAD_SUMMARY_JOB_ID,
        "dead_summary_job_present": bool(dead_rows),
        "dead_summary_observation": dead_rows,
        "target_partition": TARGET_PARTITION,
        "target_node": TARGET_NODE,
        "gpu_selector": TARGET_GRES,
        "exclusive_node_allocation": True,
        "route_observation": route_rows[0],
        "array_indices": [2, 4, 5],
        "array_throttle": 1,
        "minimum_free_vram_bytes_per_task": 40 * 1024**3,
        "maximum_used_vram_bytes_before_probe": 512 * 1024**2,
        "compute_app_rows_required": 0,
        "scratch_free_bytes": usage.free,
        "scratch_available_inodes": stat.f_favail,
        "home_write_allowed": False,
    }
    write_json(output, payload)
    print(output)


if __name__ == "__main__":
    main()
