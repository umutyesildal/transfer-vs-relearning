#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from transfer_vs_relearning.metrics.pre_m2_followup import (
    accuracy_slice_summary,
    paired_form_comparisons,
    robust_intersection_summary,
    repeatability_audit,
    token_likelihood_summary,
)
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


def tokenizer_fingerprint(model_manifest_path: Path) -> dict[str, object]:
    from transfer_vs_relearning.evaluation.evaluator import _resolve_tokenizer_path

    payload = json.loads(model_manifest_path.read_text(encoding="utf-8"))
    tokenizer_path = _resolve_tokenizer_path(payload, model_manifest_path)
    names = ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "vocab.json", "merges.txt")
    file_hashes = {
        name: sha256_file(tokenizer_path / name)
        for name in names
        if (tokenizer_path / name).is_file()
    }
    fingerprint = hashlib.sha256(json.dumps(file_hashes, sort_keys=True).encode("utf-8")).hexdigest()
    return {"path": str(tokenizer_path), "file_hashes": file_hashes, "fingerprint_sha256": fingerprint}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare completed base/seed42/seed43 pre-M2 frozen-suite runs.")
    parser.add_argument("--run-dir", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    parser.add_argument("--repeat-reference-dir", type=Path, default=None)
    args = parser.parse_args()

    fact_rows = []
    token_rows = []
    manifests = []
    tokenizer_fingerprints = []
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
        tokenizer_fingerprints.append(tokenizer_fingerprint(Path(manifest["model_manifest"])))
        fact_rows.extend(read_csv_rows(run_dir / "hard_suite_per_fact.csv"))
        token_rows.extend(read_csv_rows(run_dir / "teacher_forced_per_token.csv"))

    probe_hashes = {manifest["probe_registry_sha256"] for manifest in manifests}
    dataset_hashes = {manifest["dataset_manifest_sha256"] for manifest in manifests}
    tokenizer_classes = {manifest["tokenizer_class"] for manifest in manifests}
    tokenizer_hashes = {item["fingerprint_sha256"] for item in tokenizer_fingerprints}
    if len(probe_hashes) != 1 or len(dataset_hashes) != 1 or len(tokenizer_classes) != 1 or len(tokenizer_hashes) != 1:
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
    repeat_audit = {"status": "not_run"}
    if args.repeat_reference_dir is not None:
        reference_manifest = json.loads(
            (args.repeat_reference_dir / "run_manifest.json").read_text(encoding="utf-8")
        )
        matching_labels = {
            manifest["model_label"]
            for manifest in manifests
            if manifest["model_manifest_sha256"] == reference_manifest["model_manifest_sha256"]
        }
        if len(matching_labels) != 1:
            raise ValueError("Repeatability reference did not resolve to exactly one comparison model")
        matching_label = next(iter(matching_labels))
        repeat_audit = repeatability_audit(
            read_csv_rows(args.repeat_reference_dir / "hard_suite_per_fact.csv"),
            [row for row in fact_rows if row["model_label"] == matching_label],
        )
        write_json(args.output_dir / "repeatability_audit.json", repeat_audit)
        if repeat_audit["status"] != "passed":
            raise ValueError("Repeated evaluation did not reproduce overlapping per-fact rows")
    write_json(
        args.output_dir / "comparison_manifest.json",
        {
            "status": "completed",
            "model_labels": sorted(labels),
            "probe_registry_sha256": next(iter(probe_hashes)),
            "dataset_manifest_sha256": next(iter(dataset_hashes)),
            "tokenizer_class": next(iter(tokenizer_classes)),
            "tokenizer_fingerprint_sha256": next(iter(tokenizer_hashes)),
            "tokenizer_artifacts": tokenizer_fingerprints,
            "bootstrap_samples": args.bootstrap_samples,
            "bootstrap_seed": args.bootstrap_seed,
            "repeatability_audit_status": repeat_audit["status"],
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
