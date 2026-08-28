#!/usr/bin/env python3
"""Exact two-phase launcher for the frozen vngrs three-model D0 v2 contract."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

import yaml

from transfer_vs_relearning.corpora.vngrs.d0_inputs import (
    load_source_objects,
    load_synthetic_surfaces,
)
from transfer_vs_relearning.corpora.vngrs.d0_orchestration import (
    D0OrchestrationPolicy,
    finalize_d0_phase2,
    run_d0_phase1,
)
from transfer_vs_relearning.corpora.vngrs.d0_preflight_v2 import (
    collect_d0_v2_preflight_observation,
    validate_d0_v2_preflight,
    write_d0_v2_preflight_failure,
)
from transfer_vs_relearning.corpora.vngrs.d0_runtime import (
    FrozenTokenizerAdapter,
    ReviewedHttpsTransport,
)
from transfer_vs_relearning.corpora.vngrs.materialization import MaterializationPolicy


OUTPUT_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v2")
BASE_CONFIG = Path("configs/corpora/vngrs_m2_three_model_d0_v1.yaml")
REGISTRY_SHA256 = "63acadb8955411e0ee42dba0c28f72220568efce6e01db4bfcf90a31c49724a9"
SURFACES_SHA256 = "9b1fcae2565fbf0d9c624a2c229c8173a59ca00064db1a017b0f2a5c0c749289"


def _jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _slurm_comment(value: str) -> None:
    job_id = os.environ.get("SLURM_JOB_ID")
    if not job_id:
        return
    safe = re.sub(r"[^A-Za-z0-9_.:-]+", "_", value)[:240]
    try:
        subprocess.run(
            ["scontrol", "update", f"JobId={job_id}", f"Comment={safe}"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        pass


def _load_objects(repo: Path):
    return load_source_objects(
        repo
        / "artifacts/corpora/vngrs_m2_d0/source_registry_byte_semantics_repair_v1.json",
        expected_sha256=REGISTRY_SHA256,
    )


def _load_surfaces(repo: Path):
    return load_synthetic_surfaces(
        repo
        / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/validation.jsonl",
        expected_sha256=SURFACES_SHA256,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("phase1", "phase2"))
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--collect-preflight", action="store_true")
    parser.add_argument("--decisions-jsonl", type=Path)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    policy = D0OrchestrationPolicy(execution_enabled=True)
    if args.phase == "phase1":
        if args.decisions_jsonl is not None or not args.collect_preflight:
            raise ValueError("phase1 requires in-job V2 preflight collection")
        try:
            objects = _load_objects(repo)
            surfaces = _load_surfaces(repo)
            observation = collect_d0_v2_preflight_observation(repo)
            preflight = validate_d0_v2_preflight(
                observation,
                expected_commit=args.expected_commit,
            )
            result = run_d0_phase1(
                OUTPUT_ROOT,
                objects,
                transport=ReviewedHttpsTransport(),
                preflight=preflight,
                synthetic_surfaces=surfaces,
                policy=policy,
                materialization_policy=MaterializationPolicy(execution_enabled=True),
            )
        except Exception as exc:
            if not OUTPUT_ROOT.exists():
                try:
                    write_d0_v2_preflight_failure(
                        expected_commit=args.expected_commit,
                        error=exc,
                    )
                except Exception as persistence_error:
                    _slurm_comment(
                        "D0_V2_EVIDENCE_WRITE_BLOCKED:"
                        f"{type(persistence_error).__name__}:{persistence_error}"
                    )
            _slurm_comment(f"D0_V2_PHASE1_BLOCKED:{type(exc).__name__}:{exc}")
            raise
        _slurm_comment("D0_V2_PHASE1_AWAITING_HUMAN_REVIEW")
    else:
        if args.decisions_jsonl is None or args.collect_preflight:
            raise ValueError("phase2 requires only --decisions-jsonl")
        config = yaml.safe_load((repo / BASE_CONFIG).read_text(encoding="utf-8"))
        objects = _load_objects(repo)
        surfaces = _load_surfaces(repo)
        phase1_state = json.loads(
            (OUTPUT_ROOT / "control/phase1_state.json").read_text(encoding="utf-8")
        )
        if phase1_state.get("preflight", {}).get("git_commit") != args.expected_commit:
            raise ValueError("phase2 implementation commit differs from phase1")
        inventory = json.loads(
            (
                repo
                / "artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1.json"
            ).read_text(encoding="utf-8")
        )
        tokenizers = [
            FrozenTokenizerAdapter.load(
                role=role,
                snapshot_root=config["tokenizer_accounting"]["models"][role][
                    "m1_epoch036_path"
                ],
                inventory=inventory["models"][role],
            )
            for role in ("olmo", "qwen", "smollm")
        ]
        result = finalize_d0_phase2(
            OUTPUT_ROOT,
            objects,
            synthetic_surfaces=surfaces,
            tokenizers=tokenizers,
            decisions=_jsonl(args.decisions_jsonl),
            policy=policy,
        )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
