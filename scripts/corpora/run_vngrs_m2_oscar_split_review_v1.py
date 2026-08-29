#!/usr/bin/env python3
"""Single OSCAR-only deterministic split and 64-document review handoff."""

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
from transfer_vs_relearning.corpora.vngrs.d0_oscar_split_review import (
    run_oscar_split_review_handoff,
)
from transfer_vs_relearning.corpora.vngrs.sample_transport import SOURCE_ROOT


SOURCE_V3_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3")
PREDECESSOR_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_oscar_fact_pair_audit_v1")
OUTPUT_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1")
MATERIALIZATION_SHA256 = "bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10"
PREDECESSOR_INVENTORY_SHA256 = "178991f311336a4acead1bb00fe8043d60a18c590e809b11629ca64f4920ee2b"
PREDECESSOR_AUDIT_SHA256 = "bf076ab36fc31b16ab6f47d4a02ff04877177c1562e8bda2f8bb11f1a14091d3"
PREDECESSOR_STATE_SHA256 = "381772af2ce8ebca68aa30ee6862e0933689abb88dabafcf499d96603c5dba57"
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
        raise ValueError("fresh OSCAR split/review root is not absent")
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip() != expected_commit:
        raise ValueError("authorized Git commit drift")
    if subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=repo, text=True).strip():
        raise ValueError("reviewed checkout is not clean")
    evidence = {
        SOURCE_V3_ROOT / "control/materialization_v3.json": MATERIALIZATION_SHA256,
        PREDECESSOR_ROOT / "reports/corpus_label_inventory.json": PREDECESSOR_INVENTORY_SHA256,
        PREDECESSOR_ROOT / "reports/fact_pair_contamination_audit.json": PREDECESSOR_AUDIT_SHA256,
        PREDECESSOR_ROOT / "control/recovery_state.json": PREDECESSOR_STATE_SHA256,
    }
    for path, expected in evidence.items():
        if not path.is_file() or path.is_symlink() or _sha256(path) != expected:
            raise ValueError(f"preserved split/review predecessor evidence drift: {path}")
    usage = shutil.disk_usage(OUTPUT_ROOT.parent)
    stat = os.statvfs(OUTPUT_ROOT.parent)
    if usage.free < MIN_AVAILABLE_BYTES or stat.f_favail < MIN_AVAILABLE_INODES:
        raise ValueError("OSCAR split/review scratch capacity gate failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    try:
        _validate_preflight(repo, args.expected_commit)
        objects = load_source_objects_v3(SOURCE_ROOT)
        state_path = PREDECESSOR_ROOT / "control/recovery_state.json"
        audit_path = PREDECESSOR_ROOT / "reports/fact_pair_contamination_audit.json"
        result = run_oscar_split_review_handoff(
            SOURCE_V3_ROOT,
            OUTPUT_ROOT,
            objects,
            predecessor_state=json.loads(state_path.read_text(encoding="utf-8")),
            predecessor_audit=json.loads(audit_path.read_text(encoding="utf-8")),
            predecessor_state_sha256=PREDECESSOR_STATE_SHA256,
            predecessor_audit_sha256=PREDECESSOR_AUDIT_SHA256,
            execution_enabled=True,
        )
    except Exception as exc:
        if not (OUTPUT_ROOT / "control/d0_failure.json").exists() and not OUTPUT_ROOT.exists():
            write_d0_failure(OUTPUT_ROOT, phase="oscar_split_review_preflight", error=exc)
        _comment(f"OSCAR_SPLIT_REVIEW_FAILED:{type(exc).__name__}:{exc}")
        raise
    _comment("AWAITING_HUMAN_REVIEW")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
