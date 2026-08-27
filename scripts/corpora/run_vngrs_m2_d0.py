#!/usr/bin/env python3
"""Exact two-phase launcher for the frozen vngrs three-model D0 contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from transfer_vs_relearning.corpora.vngrs.d0_inputs import load_source_objects, load_synthetic_surfaces
from transfer_vs_relearning.corpora.vngrs.d0_orchestration import D0OrchestrationPolicy, finalize_d0_phase2, run_d0_phase1
from transfer_vs_relearning.corpora.vngrs.d0_preflight import validate_d0_preflight
from transfer_vs_relearning.corpora.vngrs.d0_runtime import FrozenTokenizerAdapter, ReviewedHttpsTransport
from transfer_vs_relearning.corpora.vngrs.materialization import MaterializationPolicy


OUTPUT_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1")
REGISTRY_SHA256 = "63acadb8955411e0ee42dba0c28f72220568efce6e01db4bfcf90a31c49724a9"
SURFACES_SHA256 = "9b1fcae2565fbf0d9c624a2c229c8173a59ca00064db1a017b0f2a5c0c749289"


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("phase1", "phase2"))
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--preflight-json", type=Path)
    parser.add_argument("--decisions-jsonl", type=Path)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    config = yaml.safe_load((repo / "configs/corpora/vngrs_m2_three_model_d0_v1.yaml").read_text())
    objects = load_source_objects(
        repo / "artifacts/corpora/vngrs_m2_d0/source_registry_byte_semantics_repair_v1.json",
        expected_sha256=REGISTRY_SHA256,
    )
    surfaces = load_synthetic_surfaces(
        repo / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/validation.jsonl",
        expected_sha256=SURFACES_SHA256,
    )
    policy = D0OrchestrationPolicy(execution_enabled=True)
    if args.phase == "phase1":
        if args.preflight_json is None or args.decisions_jsonl is not None:
            raise ValueError("phase1 requires only --preflight-json")
        preflight = validate_d0_preflight(
            json.loads(args.preflight_json.read_text(encoding="utf-8")),
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
    else:
        if args.decisions_jsonl is None or args.preflight_json is not None:
            raise ValueError("phase2 requires only --decisions-jsonl")
        phase1_state = json.loads((OUTPUT_ROOT / "control/phase1_state.json").read_text())
        if phase1_state.get("preflight", {}).get("git_commit") != args.expected_commit:
            raise ValueError("phase2 implementation commit differs from phase1")
        inventory = json.loads(
            (repo / "artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1.json").read_text()
        )
        tokenizers = [
            FrozenTokenizerAdapter.load(
                role=role,
                snapshot_root=config["tokenizer_accounting"]["models"][role]["m1_epoch036_path"],
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
