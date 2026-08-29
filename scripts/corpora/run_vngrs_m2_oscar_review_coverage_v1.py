#!/usr/bin/env python3
"""Single pre-verdict OSCAR quartile-coverage validation and packet repair."""

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
from transfer_vs_relearning.corpora.vngrs.d0_inputs_v3 import load_source_objects_v3
from transfer_vs_relearning.corpora.vngrs.d0_oscar_review_coverage import (
    run_oscar_review_coverage_repair,
)
from transfer_vs_relearning.corpora.vngrs.sample_transport import SOURCE_ROOT


SOURCE_V3_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3")
PREDECESSOR_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1")
OUTPUT_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_oscar_review_coverage_repair_v1")
MATERIALIZATION_SHA256 = "bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10"
PREDECESSOR_HASHES = {
    "control/final_audit.json": "3add7667d202cb5547dc0847c9ad302a47e7e57cd7fb8f2f43fd4211dba86e7e",
    "control/phase1_state.json": "a09c0c62fffb8536b9917cc9755a40c35eb8c0f862f5b41d044f3de8f4e7d609",
    "manifests/output_artifact_manifest.jsonl": "8a9c9dfaeba7b25a699c7f380492e54ba5595622d23bf428e66aeceee03c2061",
    "reports/human_review_decision_template.jsonl": "0d169f1ed3a3c5bcfac217218f3295c591646384b7014538874ea31d20dcf06f",
    "reports/human_review_packet.jsonl": "e0175029e17d9aaccb8a6c3c73c9322befe069e955539f2126c27cbb42053ac1",
    "reports/human_review_sample.jsonl": "cb294c2b4588619b19073dd5bbc8fa82337880f3d1adaf60488101b2095ebd33",
    "splits/heldout_document_ids.jsonl": "dc30629fe76ca722745fcd0148021de6c042218ed2994281d52d13c06011dc91",
    "splits/train_document_ids.jsonl": "90b74fbcfe62107693c35161fc328a6e43b13a830fc9590cc9810d3e99955aac",
}
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
        raise ValueError("fresh OSCAR review-coverage root is not absent")
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip() != expected_commit:
        raise ValueError("authorized Git commit drift")
    if subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=repo, text=True).strip():
        raise ValueError("reviewed checkout is not clean")
    materialization = SOURCE_V3_ROOT / "control/materialization_v3.json"
    if not materialization.is_file() or materialization.is_symlink() or _sha256(materialization) != MATERIALIZATION_SHA256:
        raise ValueError("preserved materialization evidence drift")
    for relative, expected in PREDECESSOR_HASHES.items():
        path = PREDECESSOR_ROOT / relative
        if not path.is_file() or path.is_symlink() or _sha256(path) != expected:
            raise ValueError(f"preserved split/review evidence drift: {path}")
    usage = shutil.disk_usage(OUTPUT_ROOT.parent)
    stat = os.statvfs(OUTPUT_ROOT.parent)
    if usage.free < MIN_AVAILABLE_BYTES or stat.f_favail < MIN_AVAILABLE_INODES:
        raise ValueError("OSCAR review-coverage scratch capacity gate failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    try:
        _validate_preflight(repo, args.expected_commit)
        objects = load_source_objects_v3(SOURCE_ROOT)
        state = json.loads((PREDECESSOR_ROOT / "control/phase1_state.json").read_text(encoding="utf-8"))
        final = json.loads((PREDECESSOR_ROOT / "control/final_audit.json").read_text(encoding="utf-8"))
        result = run_oscar_review_coverage_repair(
            SOURCE_V3_ROOT,
            PREDECESSOR_ROOT,
            OUTPUT_ROOT,
            objects,
            predecessor_state=state,
            predecessor_final=final,
            predecessor_state_sha256=PREDECESSOR_HASHES["control/phase1_state.json"],
            predecessor_final_sha256=PREDECESSOR_HASHES["control/final_audit.json"],
            execution_enabled=True,
        )
    except Exception as exc:
        if not (OUTPUT_ROOT / "control/d0_failure.json").exists() and not OUTPUT_ROOT.exists():
            write_d0_failure(OUTPUT_ROOT, phase="oscar_review_coverage_preflight", error=exc)
        _comment(f"OSCAR_REVIEW_COVERAGE_FAILED:{type(exc).__name__}:{exc}")
        raise
    _comment("COVERAGE_VALIDATED_AWAITING_HUMAN_REVIEW")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
