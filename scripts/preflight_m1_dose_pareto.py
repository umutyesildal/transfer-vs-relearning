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
    candidate,
    load_registry,
    verify_sha,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--label", choices=("olmo", "falcon", "pythia"))
    args = parser.parse_args()
    registry_path = args.registry.resolve()
    repo_root = args.repo_root.resolve()
    registry = load_registry(registry_path)
    root = Path(registry["scratch_root"])
    output = args.output.resolve()
    commit = run("git", "-C", str(repo_root), "rev-parse", "HEAD")
    if commit != args.expected_commit:
        raise ValueError(f"HU commit drift: {commit} != {args.expected_commit}")
    if args.verify:
        payload = json.loads(output.read_text(encoding="utf-8"))
        if payload.get("status") != "PASS" or payload.get("expected_commit") != commit:
            raise ValueError("Shared preflight is not a PASS for this commit")
        if payload.get("registry_sha256") != sha256_file(registry_path):
            raise ValueError("Registry changed after shared preflight")
        if not args.label:
            raise ValueError("Verification requires --label")
        if (root / "training" / args.label).exists():
            raise FileExistsError(f"Training namespace already exists for {args.label}")
        print(output)
        return
    if root.exists():
        raise FileExistsError(f"Fresh root must be absent: {root}")
    checks: dict[str, object] = {}
    for name, expected in registry["dataset_files"].items():
        path = Path(registry["dataset_root"]) / name
        verify_sha(path, expected)
        checks[f"dataset:{name}"] = {"path": str(path), "sha256": expected}
    verify_sha(Path(registry["general_corpus"]), registry["general_corpus_sha256"])
    verify_sha(Path(registry["probe_registry"]), registry["probe_registry_sha256"])
    for label in ("olmo", "falcon", "pythia"):
        item = candidate(registry, label)
        verify_sha(Path(item["base_model_manifest"]), item["base_model_manifest_sha256"])
        verify_sha(Path(item["base_general_summary"]), item["base_general_summary_sha256"])
        template = (repo_root / item["training_template"]).resolve()
        if not template.is_file():
            raise FileNotFoundError(template)
        checks[f"candidate:{label}"] = {
            "model_manifest": str(item["base_model_manifest"]),
            "model_manifest_sha256": item["base_model_manifest_sha256"],
            "base_general_summary": str(item["base_general_summary"]),
            "base_general_summary_sha256": item["base_general_summary_sha256"],
            "template": str(template),
            "template_sha256": sha256_file(template),
        }
    policy = registry["home_storage_policy"]
    if bool(policy["home_write_allowed"]) or bool(policy["recursive_du_per_stage"]):
        raise ValueError("No-home-write policy drift")
    if int(policy["reference_bytes"]) >= int(policy["limit_bytes"]):
        raise ValueError("Frozen HU-home reference is above limit")
    usage = shutil.disk_usage(root.parent)
    reserve = int(registry["reserve_gib"]) * 1024**3
    if usage.free < reserve:
        raise ValueError(f"Insufficient scratch bytes: {usage.free} < {reserve}")
    stat = os.statvfs(root.parent)
    if stat.f_favail < int(registry["reserve_inodes"]):
        raise ValueError("Insufficient scratch inodes")
    queue = run("squeue", "-u", "yesildau", "-h", "-o", "%i|%j|%T")
    conflicts = [line for line in queue.splitlines() if "m1-v4-" in line]
    if conflicts:
        raise ValueError(f"Duplicate v4 jobs: {conflicts}")
    root.mkdir(parents=True, exist_ok=False)
    for name in ("logs", "cache", "tmp", "configs", "manifests", "training", "evaluations", "preflight"):
        (root / name).mkdir()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "PASS",
        "version": registry["version"],
        "timestamp": datetime.now(UTC).isoformat(),
        "expected_commit": commit,
        "registry": str(registry_path),
        "registry_sha256": sha256_file(registry_path),
        "root_absent_before_preflight": True,
        "root_created_only_for_authorized_wave": str(root),
        "home_usage_evidence": policy,
        "scratch_free_bytes": usage.free,
        "scratch_available_inodes": stat.f_favail,
        "reserve_bytes": reserve,
        "reserve_inodes": int(registry["reserve_inodes"]),
        "df_h": run("df", "-h", str(root.parent), str(policy["home_root"])),
        "df_i": run("df", "-i", str(root.parent), str(policy["home_root"])),
        "queue_snapshot": queue.splitlines(),
        "checks": checks,
    }
    write_json(output, payload)
    print(output)


if __name__ == "__main__":
    main()
