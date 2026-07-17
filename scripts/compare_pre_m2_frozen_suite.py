#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.metrics.pre_m2_followup import (
    accuracy_slice_summary,
    paired_form_comparisons,
    robust_intersection_summary,
    token_likelihood_summary,
)
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare completed base/seed42/seed43 pre-M2 frozen-suite runs.")
    parser.add_argument("--run-dir", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    args = parser.parse_args()

    fact_rows = []
    token_rows = []
    manifests = []
    labels = set()
    for run_dir in args.run_dir:
        summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
        manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        if summary.get("status") != "completed" or manifest.get("status") != "completed":
            raise ValueError(f"Run is not complete: {run_dir}")
        label = str(manifest["model_label"])
        if label in labels:
            raise ValueError(f"Duplicate model label: {label}")
        labels.add(label)
        manifests.append(manifest)
        fact_rows.extend(read_csv_rows(run_dir / "hard_suite_per_fact.csv"))
        token_rows.extend(read_csv_rows(run_dir / "teacher_forced_per_token.csv"))

    probe_hashes = {manifest["probe_registry_sha256"] for manifest in manifests}
    dataset_hashes = {manifest["dataset_manifest_sha256"] for manifest in manifests}
    tokenizer_classes = {manifest["tokenizer_class"] for manifest in manifests}
    if len(probe_hashes) != 1 or len(dataset_hashes) != 1 or len(tokenizer_classes) != 1:
        raise ValueError("Matched comparison integrity failed for probe, dataset, or tokenizer identity")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    comparison_rows = paired_form_comparisons(
        fact_rows,
        bootstrap_samples=args.bootstrap_samples,
        seed=args.bootstrap_seed,
    )
    token_rows_summary = token_likelihood_summary(token_rows)
    write_csv(args.output_dir / "paired_form_comparisons.csv", comparison_rows)
    write_csv(
        args.output_dir / "accuracy_with_bootstrap_ci.csv",
        accuracy_slice_summary(
            fact_rows,
            bootstrap_samples=args.bootstrap_samples,
            seed=args.bootstrap_seed,
        ),
    )
    write_csv(args.output_dir / "robust_intersections.csv", robust_intersection_summary(fact_rows))
    write_csv(args.output_dir / "token_likelihood_summary.csv", token_rows_summary)
    write_json(
        args.output_dir / "comparison_manifest.json",
        {
            "status": "completed",
            "model_labels": sorted(labels),
            "probe_registry_sha256": next(iter(probe_hashes)),
            "dataset_manifest_sha256": next(iter(dataset_hashes)),
            "tokenizer_class": next(iter(tokenizer_classes)),
            "bootstrap_samples": args.bootstrap_samples,
            "bootstrap_seed": args.bootstrap_seed,
            "inputs": [
                {
                    "run_dir": str(run_dir.resolve()),
                    "summary_sha256": sha256_file(run_dir / "summary.json"),
                    "run_manifest_sha256": sha256_file(run_dir / "run_manifest.json"),
                    "per_fact_sha256": sha256_file(run_dir / "hard_suite_per_fact.csv"),
                    "per_token_sha256": sha256_file(run_dir / "teacher_forced_per_token.csv"),
                }
                for run_dir in args.run_dir
            ],
        },
    )
    print(args.output_dir)


if __name__ == "__main__":
    main()
