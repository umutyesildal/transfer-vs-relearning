#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from transfer_vs_relearning.experiments.m1_dose_pareto import (
    FALCON_EVALUATION_RECOVERY_SHA256,
    load_registry,
    validate_falcon_evaluation_recovery_state,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


MINIMUM_RECOVERY_FREE_BYTES = 20 * 1024**3
MINIMUM_RECOVERY_FREE_INODES = 1_000


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
        raise FileExistsError(f"Falcon recovery preflight output invalid/existing: {output}")
    if run("git", "-C", str(repo_root), "rev-parse", "HEAD") != args.expected_commit:
        raise ValueError("HU commit drift")
    if not str(root).startswith("/vol/tmp2/yesildau/"):
        raise ValueError("Falcon recovery root escaped the frozen scratch prefix")
    policy = registry["home_storage_policy"]
    if bool(policy["home_write_allowed"]) or bool(policy["recursive_du_per_stage"]):
        raise ValueError("No-home-write policy drift")

    active_jobs = run(
        "squeue",
        "-h",
        "-n",
        "m1-v4-eval-falcon,m1-v4-eval-falcon-recovery,m1-v4-falcon-summary",
        "-o",
        "%A_%a|%T|%j",
    )
    if active_jobs:
        raise ValueError(f"Duplicate Falcon recovery/evaluation job exists: {active_jobs}")
    state = validate_falcon_evaluation_recovery_state(
        registry, summary_root=args.summary_root.resolve()
    )
    usage = shutil.disk_usage(root)
    stat = os.statvfs(root)
    if usage.free < MINIMUM_RECOVERY_FREE_BYTES or stat.f_favail < MINIMUM_RECOVERY_FREE_INODES:
        raise ValueError("Falcon recovery scratch capacity/inode gate failed")

    payload = {
        **state,
        "timestamp": datetime.now(UTC).isoformat(),
        "expected_commit": args.expected_commit,
        "registry": str(registry_path),
        "registry_sha256": sha256_file(registry_path),
        "recovery_contract_sha256": FALCON_EVALUATION_RECOVERY_SHA256,
        "active_duplicate_jobs": [],
        "target_node": "guppi5",
        "gpu_selector": "gpu:rtx3090:1",
        "array_indices": [2, 4, 5],
        "array_throttle": 1,
        "minimum_free_vram_bytes_per_task": 20 * 1024**3,
        "scratch_free_bytes": usage.free,
        "scratch_available_inodes": stat.f_favail,
        "minimum_scratch_free_bytes": MINIMUM_RECOVERY_FREE_BYTES,
        "minimum_scratch_free_inodes": MINIMUM_RECOVERY_FREE_INODES,
        "home_write_allowed": False,
    }
    write_json(output, payload)
    print(output)


if __name__ == "__main__":
    main()
