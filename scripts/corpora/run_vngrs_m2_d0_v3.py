#!/usr/bin/env python3
"""Phase-1-only launcher for the frozen vngrs three-model D0 v3 contract."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

from transfer_vs_relearning.corpora.vngrs.d0_inputs import load_synthetic_surfaces
from transfer_vs_relearning.corpora.vngrs.d0_inputs_v3 import load_source_objects_v3
from transfer_vs_relearning.corpora.vngrs.d0_orchestration import D0OrchestrationPolicy, run_d0_phase1
from transfer_vs_relearning.corpora.vngrs.d0_preflight_v3 import (
    collect_d0_v3_preflight_observation,
    validate_d0_v3_preflight,
    write_d0_v3_preflight_failure,
)
from transfer_vs_relearning.corpora.vngrs.d0_runtime import ReviewedHttpsTransport
from transfer_vs_relearning.corpora.vngrs.materialization import (
    MaterializationV3Policy,
    materialize_full_objects_v3,
)
from transfer_vs_relearning.corpora.vngrs.sample_transport import SOURCE_ROOT
from transfer_vs_relearning.corpora.vngrs.parquet_loader_v3 import (
    load_verified_parquet_documents_v3,
)


OUTPUT_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3")
SURFACES_SHA256 = "9b1fcae2565fbf0d9c624a2c229c8173a59ca00064db1a017b0f2a5c0c749289"


def _slurm_comment(value: str) -> None:
    job_id = os.environ.get("SLURM_JOB_ID")
    if not job_id:
        return
    safe = re.sub(r"[^A-Za-z0-9_.:-]+", "_", value)[:240]
    try:
        subprocess.run(
            ["scontrol", "update", f"JobId={job_id}", f"Comment={safe}"],
            check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("phase1",))
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--collect-preflight", action="store_true")
    args = parser.parse_args()
    if not args.collect_preflight:
        raise ValueError("phase1 requires in-job V3 preflight collection")
    repo = args.repo_root.resolve()
    try:
        objects = load_source_objects_v3(SOURCE_ROOT)
        surfaces = load_synthetic_surfaces(
            repo / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/validation.jsonl",
            expected_sha256=SURFACES_SHA256,
        )
        observation = collect_d0_v3_preflight_observation(repo)
        preflight = validate_d0_v3_preflight(observation, expected_commit=args.expected_commit)
        result = run_d0_phase1(
            OUTPUT_ROOT,
            objects,
            transport=ReviewedHttpsTransport(),
            preflight=preflight,
            synthetic_surfaces=surfaces,
            policy=D0OrchestrationPolicy(execution_enabled=True),
            materialization_policy=MaterializationV3Policy(execution_enabled=True),
            materializer=materialize_full_objects_v3,
            document_loader=load_verified_parquet_documents_v3,
        )
    except Exception as exc:
        if not OUTPUT_ROOT.exists():
            try:
                write_d0_v3_preflight_failure(expected_commit=args.expected_commit, error=exc)
            except Exception as persistence_error:
                _slurm_comment(f"D0_V3_EVIDENCE_WRITE_BLOCKED:{type(persistence_error).__name__}:{persistence_error}")
        _slurm_comment(f"D0_V3_PHASE1_BLOCKED:{type(exc).__name__}:{exc}")
        raise
    _slurm_comment("D0_V3_PHASE1_AWAITING_HUMAN_REVIEW")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
