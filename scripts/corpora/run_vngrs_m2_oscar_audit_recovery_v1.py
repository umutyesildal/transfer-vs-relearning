#!/usr/bin/env python3
"""Single diagnostic OSCAR audit pass over preserved V3 materialization."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from transfer_vs_relearning.corpora.vngrs.d0_bundle import write_d0_failure
from transfer_vs_relearning.corpora.vngrs.d0_inputs import load_synthetic_surfaces
from transfer_vs_relearning.corpora.vngrs.d0_inputs_v3 import load_source_objects_v3
from transfer_vs_relearning.corpora.vngrs.d0_oscar_recovery import run_oscar_audit_recovery
from transfer_vs_relearning.corpora.vngrs.sample_transport import SOURCE_ROOT


SOURCE_V3_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3")
OUTPUT_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_oscar_audit_recovery_v1")
MATERIALIZATION_SHA256 = "bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10"
FAILURE_SHA256 = "a341e4787e38720f27beeaf5815331ef0163084cb2974d91799ee5ffe426c52f"
SURFACES_SHA256 = "9b1fcae2565fbf0d9c624a2c229c8173a59ca00064db1a017b0f2a5c0c749289"
MIN_AVAILABLE_BYTES = 2 * 1024**3
MIN_AVAILABLE_INODES = 1_024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _comment(value: str) -> None:
    job_id = os.environ.get("SLURM_JOB_ID")
    if not job_id:
        return
    safe = re.sub(r"[^A-Za-z0-9_.:-]+", "_", value)[:240]
    subprocess.run(
        ["scontrol", "update", f"JobId={job_id}", f"Comment={safe}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _validate_preflight(repo: Path, expected_commit: str) -> None:
    if OUTPUT_ROOT.exists():
        raise ValueError("fresh OSCAR audit recovery root is not absent")
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip() != expected_commit:
        raise ValueError("authorized Git commit drift")
    if subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=repo, text=True).strip():
        raise ValueError("reviewed checkout is not clean")
    evidence = {
        SOURCE_V3_ROOT / "control/materialization_v3.json": MATERIALIZATION_SHA256,
        SOURCE_V3_ROOT / "control/d0_failure.json": FAILURE_SHA256,
    }
    for path, expected in evidence.items():
        if not path.is_file() or path.is_symlink() or _sha256(path) != expected:
            raise ValueError(f"preserved V3 evidence drift: {path}")
    usage = shutil.disk_usage(OUTPUT_ROOT.parent)
    stat = os.statvfs(OUTPUT_ROOT.parent)
    if usage.free < MIN_AVAILABLE_BYTES or stat.f_favail < MIN_AVAILABLE_INODES:
        raise ValueError("OSCAR audit recovery scratch capacity gate failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    try:
        _validate_preflight(repo, args.expected_commit)
        objects = load_source_objects_v3(SOURCE_ROOT)
        surfaces = load_synthetic_surfaces(
            repo / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/validation.jsonl",
            expected_sha256=SURFACES_SHA256,
        )
        result = run_oscar_audit_recovery(
            SOURCE_V3_ROOT,
            OUTPUT_ROOT,
            objects,
            synthetic_surfaces=surfaces,
            execution_enabled=True,
        )
    except Exception as exc:
        if not (OUTPUT_ROOT / "control/d0_failure.json").exists() and not OUTPUT_ROOT.exists():
            write_d0_failure(OUTPUT_ROOT, phase="oscar_audit_recovery_preflight", error=exc)
        _comment(f"OSCAR_AUDIT_RECOVERY_FAILED:{type(exc).__name__}:{exc}")
        raise
    _comment(result["status"])
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
