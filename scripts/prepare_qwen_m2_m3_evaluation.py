#!/usr/bin/env python3
"""Freeze the M2/M3 endpoint evaluation registry without copying model weights."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.utils.io import sha256_file, write_json


STATES = (
    ("m2_clean_seed42", "m2_clean", "42"),
    ("m3_fact_seed42", "m3_fact", "42"),
    ("m2_clean_seed43", "m2_clean", "43"),
    ("m3_fact_seed43", "m3_fact", "43"),
)


def _complete_training_run(training_root: Path, label: str) -> tuple[Path, dict]:
    manifests = sorted((training_root / "runs" / label).glob("*/training_manifest.json"))
    if len(manifests) != 1:
        raise ValueError(f"Expected exactly one training manifest for {label}, found {len(manifests)}")
    manifest_path = manifests[0]
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("status") != "complete":
        raise ValueError(f"Training run is not complete: {manifest_path}")
    run_dir = manifest_path.parent
    final_model = run_dir / "final_model"
    checkpoint = run_dir / "checkpoints" / "checkpoint-128"
    if not final_model.is_dir() or not checkpoint.is_dir():
        raise FileNotFoundError(f"Missing endpoint model/checkpoint for {label}: {run_dir}")
    return run_dir, payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-root", type=Path, required=True)
    parser.add_argument("--source-model-manifest", type=Path, required=True)
    parser.add_argument("--contract-root", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    training_root = args.training_root.resolve()
    source_manifest = args.source_model_manifest.resolve()
    contract_root = args.contract_root.resolve()
    baseline_root = args.baseline_root.resolve()
    output_root = args.output_root.resolve()
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite evaluation root: {output_root}")
    if not source_manifest.is_file():
        raise FileNotFoundError(source_manifest)

    registry_path = contract_root / "evaluation" / "slice_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if len(registry) != 24 or {int(item["probe_count"]) for item in registry} != {2500}:
        raise ValueError("The frozen bilingual evaluation registry must contain 24 slices of 2,500 probes")
    for item in registry:
        probe_path = Path(str(item["path"])).resolve()
        if not probe_path.is_file() or sha256_file(probe_path) != item["sha256"]:
            raise ValueError(f"Evaluation slice hash mismatch: {item['slice_id']}")

    baseline_states = []
    for seed, label in (("42", "qwen_m1_seed42_step75"), ("43", "qwen_m1_seed43_step50")):
        summary_dir = baseline_root / "summaries_final" / label
        per_probe = summary_dir / "per_probe_results.csv"
        integrity = summary_dir / "integrity_summary.json"
        if not per_probe.is_file() or not integrity.is_file():
            raise FileNotFoundError(f"Missing completed M1 baseline summary for seed {seed}: {summary_dir}")
        integrity_payload = json.loads(integrity.read_text(encoding="utf-8"))
        if integrity_payload.get("status") != "passed" or int(integrity_payload.get("probe_count", 0)) != 60000:
            raise ValueError(f"M1 baseline summary is not complete: {summary_dir}")
        baseline_states.append(
            {
                "state_id": f"m1_seed{seed}",
                "arm": "m1",
                "seed": seed,
                "path": str(per_probe),
                "sha256": sha256_file(per_probe),
            }
        )

    output_root.mkdir(parents=True)
    model_states = []
    for label, arm, seed in STATES:
        run_dir, _ = _complete_training_run(training_root, label)
        manifest_path = output_root / "model_manifests" / f"{label}.json"
        create_local_model_manifest(
            source_manifest_path=source_manifest,
            local_model_dir=run_dir / "final_model",
            output_manifest_path=manifest_path,
            model_id=f"qwen_m2_m3_{label}",
            resolved_revision=f"qwen-m2-m3-{label}-checkpoint-128",
            training_checkpoint="checkpoint-128",
            training_run_dir=run_dir,
        )
        model_states.append(
            {
                "state_id": label,
                "arm": arm,
                "seed": seed,
                "model_manifest": str(manifest_path),
                "model_manifest_sha256": sha256_file(manifest_path),
                "results_root": str(output_root / "results" / label),
                "training_run": str(run_dir),
                "training_manifest_sha256": sha256_file(run_dir / "training_manifest.json"),
                "checkpoint": "checkpoint-128",
            }
        )

    write_json(
        output_root / "evaluation_manifest.json",
        {
            "status": "frozen_ready_to_submit",
            "evaluation": "qwen_m2_m3_fixed_endpoint_bilingual_v1",
            "endpoint": "checkpoint-128",
            "contract_root": str(contract_root),
            "contract_manifest_sha256": sha256_file(contract_root / "manifest.json"),
            "slice_registry": str(registry_path),
            "slice_registry_sha256": sha256_file(registry_path),
            "slice_count": 24,
            "probes_per_state": 60000,
            "states": model_states,
            "baseline_states": baseline_states,
            "analysis_bootstrap_samples": 2000,
            "analysis_bootstrap_seed": 20260717,
            "retention_policy": "retain_per_probe_evidence_and_compact_summaries; no_evaluation_checkpoints",
        },
    )
    print(output_root / "evaluation_manifest.json")


if __name__ == "__main__":
    main()
