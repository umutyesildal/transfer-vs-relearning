#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from transfer_vs_relearning.experiments.m1_dose_pareto import (
    FALCON_EVALUATION_CLEAN_UUID_SHA256,
    FALCON_EVALUATION_RECOVERY_SHA256,
    load_registry,
    validate_falcon_evaluation_recovery_state,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


DEAD_SUMMARY_JOB_ID = "456467"


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
        raise FileExistsError(f"clean-UUID preflight output invalid/existing: {output}")
    if run("git", "-C", str(repo_root), "rev-parse", "HEAD") != args.expected_commit:
        raise ValueError("HU commit drift")
    policy = registry["home_storage_policy"]
    if bool(policy["home_write_allowed"]) or bool(policy["recursive_du_per_stage"]):
        raise ValueError("No-home-write policy drift")
    active = run(
        "squeue", "-h", "-n",
        "m1-v4-eval-falcon,m1-v4-eval-falcon-recovery,m1-v4-eval-falcon-a6000-recovery,m1-v4-eval-falcon-a6000-exclusive,m1-v4-eval-falcon-clean-uuid,m1-v4-falcon-summary",
        "-o", "%A|%T|%j|%r",
    )
    rows = [row for row in active.splitlines() if row]
    dead = [row for row in rows if row.split("|", 1)[0] == DEAD_SUMMARY_JOB_ID]
    other = [row for row in rows if row.split("|", 1)[0] != DEAD_SUMMARY_JOB_ID]
    if other:
        raise ValueError(f"Duplicate Falcon job exists: {other}")
    if dead and (
        len(dead) != 1
        or dead[0].split("|")[:3] != [DEAD_SUMMARY_JOB_ID, "PENDING", "m1-v4-falcon-summary"]
        or dead[0].split("|", 3)[3] != "DependencyNeverSatisfied"
    ):
        raise ValueError(f"Dead summary reconciliation drift: {dead}")
    route_rows = [
        row for row in run("sinfo", "-h", "-p", "gpu", "-n", "gruenau8", "-N", "-o", "%N|%P|%a|%t|%G").splitlines()
        if row
    ]
    if len(route_rows) != 1:
        raise ValueError(f"Exact A6000 route is not uniquely visible: {route_rows}")
    node, partition, available, state, gres = route_rows[0].split("|", 4)
    if node != "gruenau8" or partition.rstrip("*") != "gpu" or available != "up" or state.split("+", 1)[0] not in {"idle", "mix", "alloc"} or "gpu:rtxa6000:4" not in gres:
        raise ValueError(f"A6000 route drift: {route_rows[0]}")
    family = validate_falcon_evaluation_recovery_state(registry, summary_root=args.summary_root.resolve())
    usage = shutil.disk_usage(root)
    stat = os.statvfs(root)
    if usage.free < 20 * 1024**3 or stat.f_favail < 1_000:
        raise ValueError("scratch capacity/inode gate failed")
    write_json(
        output,
        {
            **family,
            "timestamp": datetime.now(UTC).isoformat(),
            "expected_commit": args.expected_commit,
            "registry": str(registry_path),
            "registry_sha256": sha256_file(registry_path),
            "source_recovery_contract_sha256": FALCON_EVALUATION_RECOVERY_SHA256,
            "clean_uuid_contract_sha256": FALCON_EVALUATION_CLEAN_UUID_SHA256,
            "dead_summary_job_id": DEAD_SUMMARY_JOB_ID,
            "dead_summary_job_present": bool(dead),
            "dead_summary_observation": dead,
            "active_duplicate_jobs": [],
            "target_partition": "gpu",
            "target_node": "gruenau8",
            "gpu_selector": "gpu:rtxa6000:1",
            "exclusive_node_allocation": True,
            "expected_visible_gpu_count": 4,
            "selection_rule": "lexicographically_smallest_clean_gpu_uuid",
            "minimum_free_vram_bytes": 40 * 1024**3,
            "maximum_used_vram_bytes": 512 * 1024**2,
            "route_observation": route_rows[0],
            "scratch_free_bytes": usage.free,
            "scratch_available_inodes": stat.f_favail,
            "home_write_allowed": False,
        },
    )
    print(output)


if __name__ == "__main__":
    main()
