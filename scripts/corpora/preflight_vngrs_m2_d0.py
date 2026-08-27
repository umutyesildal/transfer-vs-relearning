#!/usr/bin/env python3
"""Collect and validate the exact D0.0 observation before output-root creation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

from transfer_vs_relearning.corpora.vngrs.d0_preflight import EXPECTED_EVIDENCE, validate_d0_preflight
from transfer_vs_relearning.corpora.vngrs.metadata import canonical_json_sha256


OUTPUT_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1")
HOME_ROOT = Path("/vol/fob-vol6/mi25/yesildau")


def _run(*args: str, cwd: Path | None = None, timeout: int = 120) -> str:
    return subprocess.run(args, cwd=cwd, text=True, check=True, capture_output=True, timeout=timeout).stdout.strip()


def _evidence_inventory(root: Path) -> tuple[int, int, str]:
    rows = [
        {"path": str(path.relative_to(root)), "bytes": path.stat().st_size}
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]
    return len(rows), sum(row["bytes"] for row in rows), canonical_json_sha256(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--user", default="yesildau")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    evidence_root = Path(EXPECTED_EVIDENCE["root"])
    count, size, inventory_hash = _evidence_inventory(evidence_root)
    home_bytes = int(_run("du", "-x", "-B1", "-s", str(HOME_ROOT), timeout=120).split()[0])
    queue = _run("squeue", "-h", "-u", args.user, "-o", "%j")
    current_job = os.environ.get("SLURM_JOB_NAME")
    duplicate_jobs = sum(name == "vngrs-m2-d0" and name != current_job for name in queue.splitlines())
    stat = os.statvfs(OUTPUT_ROOT.parent)
    observation = {
        "git_commit": _run("git", "rev-parse", "HEAD", cwd=repo),
        "clean_task_overlap": not bool(_run("git", "status", "--porcelain", cwd=repo)),
        "accepted_evidence": {"root": str(evidence_root), "regular_file_count": count, "regular_bytes": size, "inventory_sha256": inventory_hash},
        "source_registry_sha256": "b1c80bf78ff40de5c02e14f08082a51cc17cc90a9853028eaf866cb63326e41f",
        "hu_home_exact_bytes": home_bytes,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": duplicate_jobs,
        "storage": {
            "resolved_parent": str(OUTPUT_ROOT.parent.resolve()),
            "proposed_root_absent": not OUTPUT_ROOT.exists(),
            "available_bytes": stat.f_frsize * stat.f_bavail,
            "available_inodes": stat.f_favail,
        },
    }
    result = validate_d0_preflight(observation, expected_commit=args.expected_commit)
    if args.output.exists() or args.output.with_name(args.output.name + ".partial").exists():
        raise ValueError("refusing to overwrite D0 preflight evidence")
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    temporary = args.output.with_name(args.output.name + ".partial")
    temporary.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_bytes(payload)
    os.replace(temporary, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
