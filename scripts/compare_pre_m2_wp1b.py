#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.metrics.pre_m2_followup import wp1b_counterbalance_analysis
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare WP1B original and A/B-swap frozen evaluations.")
    parser.add_argument("--original-run-dir", type=Path, required=True)
    parser.add_argument("--swap-run-dir", type=Path, required=True)
    parser.add_argument("--original-assignment", type=Path, required=True)
    parser.add_argument("--swap-assignment", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    args = parser.parse_args()

    run_dirs = {"original": args.original_run_dir, "swap": args.swap_run_dir}
    manifests = {}
    rows_by_condition = {}
    for condition, run_dir in run_dirs.items():
        summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
        manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        if summary.get("status") != "completed" or manifest.get("status") != "completed":
            raise ValueError(f"Incomplete WP1B evaluation: {run_dir}")
        manifests[condition] = manifest
        rows_by_condition[condition] = read_csv_rows(run_dir / "hard_suite_per_fact.csv")
    if len({manifest["probe_registry_sha256"] for manifest in manifests.values()}) != 1:
        raise ValueError("WP1B evaluations do not share the frozen probe registry")
    assignments_by_condition = {
        "original": json.loads(args.original_assignment.read_text(encoding="utf-8"))["assignments"],
        "swap": json.loads(args.swap_assignment.read_text(encoding="utf-8"))["assignments"],
    }
    analysis = wp1b_counterbalance_analysis(
        rows_by_condition,
        assignments_by_condition,
        bootstrap_samples=args.bootstrap_samples,
        seed=args.bootstrap_seed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "per_fact_with_exposure_cell.csv", analysis["annotated"])
    write_csv(args.output_dir / "accuracy_by_exposure_cell.csv", analysis["aggregate"])
    write_csv(args.output_dir / "directional_generalization_gaps.csv", analysis["directional"])
    write_csv(args.output_dir / "required_ab_robust_intersections.csv", analysis["robust"])
    write_json(
        args.output_dir / "comparison_manifest.json",
        {
            "status": "completed",
            "bootstrap_samples": args.bootstrap_samples,
            "bootstrap_seed": args.bootstrap_seed,
            "probe_registry_sha256": next(iter({m["probe_registry_sha256"] for m in manifests.values()})),
            "inputs": {
                condition: {
                    "run_dir": str(run_dir.resolve()),
                    "run_manifest_sha256": sha256_file(run_dir / "run_manifest.json"),
                    "per_fact_sha256": sha256_file(run_dir / "hard_suite_per_fact.csv"),
                }
                for condition, run_dir in run_dirs.items()
            },
            "assignment_sha256": {
                "original": sha256_file(args.original_assignment),
                "swap": sha256_file(args.swap_assignment),
            },
        },
    )
    print(args.output_dir)


if __name__ == "__main__":
    main()
