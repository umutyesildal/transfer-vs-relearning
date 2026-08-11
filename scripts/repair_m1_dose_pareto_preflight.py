#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from transfer_vs_relearning.experiments.m1_dose_pareto import candidate, load_registry
from transfer_vs_relearning.utils.io import sha256_file, write_json


def git_head(repo_root: Path) -> str:
    return subprocess.run(
        ("git", "-C", str(repo_root), "rev-parse", "HEAD"),
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--previous-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-previous-commit", required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    registry_path = args.registry.resolve()
    previous_path = args.previous_output.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    registry = load_registry(registry_path)
    root = Path(registry["scratch_root"]).resolve()
    if output.parent != root / "preflight":
        raise ValueError("Retry preflight must be append-only under the frozen preflight root")
    previous = json.loads(previous_path.read_text(encoding="utf-8"))
    if previous.get("status") != "PASS":
        raise ValueError("Previous shared preflight is not PASS")
    if previous.get("expected_commit") != args.expected_previous_commit:
        raise ValueError("Unexpected predecessor commit in shared preflight")
    if git_head(repo_root) != args.expected_commit:
        raise ValueError("HU checkout is not at the reviewed repair commit")
    registry_sha = sha256_file(registry_path)
    if previous.get("registry_sha256") != registry_sha:
        raise ValueError("Scientific registry changed during implementation repair")
    if (root / "training" / "falcon").exists():
        raise FileExistsError("Falcon scientific training namespace already exists")

    payload = json.loads(json.dumps(previous))
    payload.update(
        status="PASS",
        timestamp=datetime.now(UTC).isoformat(),
        expected_commit=args.expected_commit,
        registry_sha256=registry_sha,
        predecessor_preflight=str(previous_path),
        predecessor_preflight_sha256=sha256_file(previous_path),
        repair_scope="falcon_pre_optimizer_bf16_model_load_dtype_and_preflight_binding_only",
        root_absent_before_preflight=False,
        root_reused_from_authorized_wave=str(root),
    )
    for label in ("olmo", "falcon", "pythia"):
        item = candidate(registry, label)
        template = (repo_root / item["training_template"]).resolve()
        evidence = payload["checks"][f"candidate:{label}"]
        evidence["template"] = str(template)
        evidence["template_sha256"] = sha256_file(template)

    usage = shutil.disk_usage(root)
    stat = os.statvfs(root)
    reserve = int(registry["reserve_gib"]) * 1024**3
    if usage.free < reserve or stat.f_favail < int(registry["reserve_inodes"]):
        raise ValueError("Scratch capacity/inode retry gate failed")
    policy = registry["home_storage_policy"]
    if bool(policy["home_write_allowed"]) or bool(policy["recursive_du_per_stage"]):
        raise ValueError("No-home-write policy drift")
    payload["retry_scratch_free_bytes"] = usage.free
    payload["retry_scratch_available_inodes"] = stat.f_favail
    write_json(output, payload)
    print(output)


if __name__ == "__main__":
    main()
