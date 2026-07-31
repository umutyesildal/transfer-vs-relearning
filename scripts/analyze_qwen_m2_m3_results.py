#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.metrics.qwen_m2_m3 import (
    branch_interaction_rows,
    paired_state_contrast_rows,
    robust_paired_contrast_rows,
    robust_state_accuracy_rows,
    state_accuracy_rows,
    validate_matched_state_rows,
)
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


def _state_input_path(path: Path) -> Path:
    path = path.resolve()
    if path.is_file():
        return path
    if not path.is_dir():
        raise FileNotFoundError(path)
    for filename in ("per_probe_results.csv", "hard_suite_per_fact.csv"):
        candidate = path / filename
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"State path must be a CSV or contain per_probe_results.csv/hard_suite_per_fact.csv: {path}"
    )


def _load_manifest(path: Path) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    payload = json.loads(path.resolve().read_text(encoding="utf-8"))
    states = payload.get("states")
    if not isinstance(states, list) or not states:
        raise ValueError("Analysis manifest must contain a non-empty states list")
    rows_by_state: dict[str, list[dict[str, Any]]] = {}
    metadata: dict[str, dict[str, Any]] = {}
    inputs: list[dict[str, Any]] = []
    for item in states:
        state_id = str(item.get("state_id", "")).strip()
        arm = str(item.get("arm", "")).strip()
        if not state_id or not arm or "seed" not in item or "path" not in item:
            raise ValueError("Each state requires state_id, arm, seed, and path")
        if state_id in rows_by_state:
            raise ValueError(f"Duplicate state_id: {state_id}")
        input_path = _state_input_path(Path(str(item["path"])))
        declared_hash = str(item.get("sha256", "")).strip()
        actual_hash = sha256_file(input_path)
        if declared_hash and declared_hash != actual_hash:
            raise ValueError(f"Input hash mismatch for {state_id}: {input_path}")
        rows = read_csv_rows(input_path)
        rows_by_state[state_id] = rows
        metadata[state_id] = {"state_id": state_id, "arm": arm, "seed": str(item["seed"]), "path": str(input_path)}
        inputs.append({**metadata[state_id], "sha256": actual_hash, "row_count": len(rows)})
    return rows_by_state, metadata, inputs


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze matched Qwen M1/M2-clean/M3-fact evaluations. "
            "The manifest states use per_probe_results.csv or hard_suite_per_fact.csv."
        )
    )
    parser.add_argument("--results-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    args = parser.parse_args()
    if args.bootstrap_samples <= 0:
        raise ValueError("--bootstrap-samples must be positive")
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite analysis output: {output_dir}")

    rows_by_state, metadata, inputs = _load_manifest(args.results_manifest)
    integrity = validate_matched_state_rows(rows_by_state)
    output_dir.mkdir(parents=True)
    write_csv(
        output_dir / "state_accuracy.csv",
        state_accuracy_rows(
            rows_by_state,
            bootstrap_samples=args.bootstrap_samples,
            seed=args.bootstrap_seed,
        ),
    )
    write_csv(
        output_dir / "paired_state_contrasts.csv",
        paired_state_contrast_rows(
            rows_by_state,
            metadata,
            bootstrap_samples=args.bootstrap_samples,
            seed=args.bootstrap_seed,
        ),
    )
    write_csv(
        output_dir / "branch_interactions.csv",
        branch_interaction_rows(
            rows_by_state,
            metadata,
            bootstrap_samples=args.bootstrap_samples,
            seed=args.bootstrap_seed,
        ),
    )
    write_csv(
        output_dir / "robust_state_accuracy.csv",
        robust_state_accuracy_rows(
            rows_by_state,
            bootstrap_samples=args.bootstrap_samples,
            seed=args.bootstrap_seed,
        ),
    )
    write_csv(
        output_dir / "robust_paired_contrasts.csv",
        robust_paired_contrast_rows(
            rows_by_state,
            metadata,
            bootstrap_samples=args.bootstrap_samples,
            seed=args.bootstrap_seed,
        ),
    )
    write_json(
        output_dir / "integrity_summary.json",
        {
            **integrity,
            "input_manifest": str(args.results_manifest.resolve()),
            "input_manifest_sha256": sha256_file(args.results_manifest.resolve()),
            "states": inputs,
            "required_arms_per_seed": ["m1", "m2_clean", "m3_fact"],
            "gate_selection": "not_performed",
            "interpretation_status": "descriptive_and_precommitted_contrasts_only",
        },
    )
    write_json(
        output_dir / "analysis_manifest.json",
        {
            "status": "completed",
            "analysis": "qwen_m2_m3_matched_subject_bootstrap_v1",
            "results_manifest": str(args.results_manifest.resolve()),
            "results_manifest_sha256": sha256_file(args.results_manifest.resolve()),
            "bootstrap_samples": args.bootstrap_samples,
            "bootstrap_seed": args.bootstrap_seed,
            "bootstrap_unit": "subject",
            "state_count": len(rows_by_state),
            "probe_count_per_state": integrity["probe_count_per_state"],
            "inputs": inputs,
            "outputs": [
                "state_accuracy.csv",
                "paired_state_contrasts.csv",
                "branch_interactions.csv",
                "robust_state_accuracy.csv",
                "robust_paired_contrasts.csv",
                "integrity_summary.json",
            ],
            "estimands": {
                "m2_minus_m1": "M2-clean - M1",
                "m3_minus_m1": "M3-fact - M1",
                "m3_minus_m2": "M3-fact - M2-clean",
                "branch_interaction": "(M3-M2)_B - (M3-M2)_A",
            },
            "thresholds_or_gates": "Not selected by this script; use the frozen experiment gate document.",
        },
    )
    print(output_dir)


if __name__ == "__main__":
    main()
