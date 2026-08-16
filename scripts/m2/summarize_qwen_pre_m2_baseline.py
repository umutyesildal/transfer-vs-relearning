#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.metrics.pre_m2_followup import bootstrap_accuracy_interval
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


EXPECTED_DIRECTIONS = ("en_to_en", "tr_to_en", "tr_to_tr")
EXPECTED_FORMS = ("form_a", "form_b", "form_c", "form_d")
EXPECTED_SCAFFOLDS = ("direct", "qa")
EXPECTED_PROBES = 60_000
EXPECTED_SLICES = 24


def _is_top1(row: dict[str, Any]) -> bool:
    return int(row["correct_rank_mean"]) == 1


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().casefold() in {"1", "true", "yes"}


def _accuracy_rows(
    rows: list[dict[str, Any]],
    *,
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> list[dict[str, Any]]:
    dimensions = (
        ("global", ()),
        ("direction", ("direction",)),
        ("relation", ("relation",)),
        ("form", ("form_id",)),
        ("scaffold", ("scaffold_id",)),
        ("branch", ("branch_group",)),
        ("direction_relation", ("direction", "relation")),
        ("direction_form", ("direction", "form_id")),
        ("direction_scaffold", ("direction", "scaffold_id")),
        ("direction_branch", ("direction", "branch_group")),
    )
    output: list[dict[str, Any]] = []
    for dimension, fields in dimensions:
        groups: dict[tuple[str, ...], list[bool]] = defaultdict(list)
        for row in rows:
            key = tuple(str(row[field]) for field in fields)
            groups[key].append(_is_top1(row))
        for index, (key, values) in enumerate(sorted(groups.items())):
            accuracy, ci_low, ci_high = bootstrap_accuracy_interval(
                values,
                samples=bootstrap_samples,
                seed=bootstrap_seed + index,
            )
            output.append(
                {
                    "dimension": dimension,
                    "key": "|".join(key) if key else "ALL",
                    "n": len(values),
                    "top1": sum(values),
                    "top1_accuracy": accuracy,
                    "bootstrap_ci_low": ci_low,
                    "bootstrap_ci_high": ci_high,
                    "bootstrap_samples": bootstrap_samples,
                }
            )
    return output


def _robust_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required_cells = {
        (form_id, scaffold_id)
        for form_id in EXPECTED_FORMS
        for scaffold_id in EXPECTED_SCAFFOLDS
    }
    by_direction_relation_fact: dict[tuple[str, str, str], dict[tuple[str, str], bool]] = defaultdict(dict)
    by_direction_fact: dict[tuple[str, str], dict[tuple[str, str], bool]] = defaultdict(dict)
    for row in rows:
        cell = (str(row["form_id"]), str(row["scaffold_id"]))
        value = _is_top1(row)
        direction = str(row["direction"])
        relation = str(row["relation"])
        fact_id = str(row["fact_id"])
        by_direction_relation_fact[(direction, relation, fact_id)][cell] = value
        by_direction_fact[(direction, fact_id)][cell] = value

    output: list[dict[str, Any]] = []
    for (direction, relation, fact_id), cells in sorted(by_direction_relation_fact.items()):
        if set(cells) != required_cells:
            raise ValueError(f"Incomplete robust cell set for {direction}/{relation}/{fact_id}")
    relation_groups: dict[tuple[str, str], dict[str, dict[tuple[str, str], bool]]] = defaultdict(dict)
    for (direction, relation, fact_id), cells in by_direction_relation_fact.items():
        relation_groups[(direction, relation)][fact_id] = cells
    for (direction, relation), grouped in sorted(relation_groups.items()):
        values = list(grouped.values())
        all_cell = sum(all(cells.values()) for cells in values)
        output.append(
            {
                "scope": "direction_relation",
                "direction": direction,
                "relation": relation,
                "n": len(values),
                "required_cells": len(required_cells),
                "all_cell_top1": all_cell,
                "all_cell_accuracy": all_cell / len(values),
            }
        )

    for direction in EXPECTED_DIRECTIONS:
        values = [cells for (item_direction, _), cells in by_direction_fact.items() if item_direction == direction]
        if not values:
            raise ValueError(f"Missing robust rows for direction {direction}")
        if any(set(cells) != required_cells for cells in values):
            raise ValueError(f"Incomplete global robust cell set for {direction}")
        all_cell = sum(all(cells.values()) for cells in values)
        output.append(
            {
                "scope": "direction_global",
                "direction": direction,
                "relation": "ALL",
                "n": len(values),
                "required_cells": len(required_cells),
                "all_cell_top1": all_cell,
                "all_cell_accuracy": all_cell / len(values),
            }
        )
    return output


def _forced_choice_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if str(row.get("same_subject_confusable_object_id", "")):
            groups[
                (
                    str(row["direction"]),
                    str(row["relation"]),
                    str(row["form_id"]),
                    str(row["scaffold_id"]),
                )
            ].append(row)
    output: list[dict[str, Any]] = []
    for (direction, relation, form_id, scaffold_id), group in sorted(groups.items()):
        correct = sum(_as_bool(row["same_subject_relation_forced_choice_correct"]) for row in group)
        output.append(
            {
                "direction": direction,
                "relation": relation,
                "form_id": form_id,
                "scaffold_id": scaffold_id,
                "n": len(group),
                "forced_choice_correct": correct,
                "forced_choice_accuracy": correct / len(group),
                "mean_gold_vs_confusable_nll_margin": sum(
                    float(row["gold_vs_same_subject_confusable_nll_margin"]) for row in group
                )
                / len(group),
            }
        )
    return output


def _load_and_validate_slices(contract_root: Path, results_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    registry_path = contract_root / "evaluation/slice_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if len(registry) != EXPECTED_SLICES:
        raise ValueError(f"Expected {EXPECTED_SLICES} slices, found {len(registry)}")
    fact_rows: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    seen_probe_ids: set[str] = set()
    for item in registry:
        slice_id = str(item["slice_id"])
        probe_path = Path(str(item["path"]))
        if not probe_path.is_absolute():
            probe_path = (contract_root / probe_path).resolve()
        if sha256_file(probe_path) != item["sha256"]:
            raise ValueError(f"Slice hash mismatch: {slice_id}")
        result_dir = results_root / slice_id
        summary_path = result_dir / "summary.json"
        run_manifest_path = result_dir / "run_manifest.json"
        per_fact_path = result_dir / "hard_suite_per_fact.csv"
        if not all(path.is_file() for path in (summary_path, run_manifest_path, per_fact_path)):
            raise FileNotFoundError(f"Incomplete slice result: {slice_id}")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
        if summary.get("status") != "completed" or run_manifest.get("status") != "completed":
            raise ValueError(f"Slice is not complete: {slice_id}")
        rows = read_csv_rows(per_fact_path)
        if len(rows) != int(item["probe_count"]):
            raise ValueError(f"Unexpected row count for {slice_id}: {len(rows)}")
        expected_direction = str(item["direction"])
        expected_form = str(item["form_id"])
        expected_scaffold = str(item["scaffold_id"])
        for row in rows:
            if (
                row["direction"],
                row["form_id"],
                row["scaffold_id"],
            ) != (expected_direction, expected_form, expected_scaffold):
                raise ValueError(f"Slice metadata mismatch: {slice_id}/{row['probe_id']}")
            if row["probe_id"] in seen_probe_ids:
                raise ValueError(f"Duplicate probe ID across slices: {row['probe_id']}")
            seen_probe_ids.add(row["probe_id"])
        fact_rows.extend(rows)
        evidence.append(
            {
                "slice_id": slice_id,
                "probe_registry": str(probe_path),
                "probe_registry_sha256": item["sha256"],
                "result_dir": str(result_dir),
                "per_fact_sha256": sha256_file(per_fact_path),
                "per_fact_rows": len(rows),
                "summary_sha256": sha256_file(summary_path),
                "run_manifest_sha256": sha256_file(run_manifest_path),
            }
        )
    if len(fact_rows) != EXPECTED_PROBES or len(seen_probe_ids) != EXPECTED_PROBES:
        raise ValueError(f"Expected {EXPECTED_PROBES} unique baseline rows, found {len(seen_probe_ids)}")
    return fact_rows, evidence


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate the complete 60,000-probe Qwen pre-M2 baseline.")
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--model-manifest", type=Path, required=True)
    parser.add_argument("--contract-root", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite baseline summary: {args.output_dir}")
    contract_root = args.contract_root.resolve()
    results_root = args.results_root.resolve()
    output_dir = args.output_dir.resolve()
    fact_rows, evidence = _load_and_validate_slices(contract_root, results_root)
    labels = {str(row["model_label"]) for row in fact_rows}
    if labels != {args.model_label}:
        raise ValueError(f"Unexpected model labels: {sorted(labels)}")
    output_dir.mkdir(parents=True)
    write_csv(output_dir / "accuracy_by_dimension.csv", _accuracy_rows(fact_rows, bootstrap_samples=args.bootstrap_samples, bootstrap_seed=args.bootstrap_seed))
    write_csv(output_dir / "robust_intersections.csv", _robust_rows(fact_rows))
    write_csv(output_dir / "forced_choice_by_cell.csv", _forced_choice_rows(fact_rows))
    write_csv(output_dir / "per_probe_results.csv", fact_rows)
    empty_expected = sum(not str(row.get("expected_answer", "")).strip() for row in fact_rows)
    empty_predicted = sum(not str(row.get("predicted_surface", "")).strip() for row in fact_rows)
    write_json(
        output_dir / "integrity_summary.json",
        {
            "status": "passed",
            "probe_count": len(fact_rows),
            "unique_probe_count": len({row["probe_id"] for row in fact_rows}),
            "empty_expected_answer_count": empty_expected,
            "empty_predicted_surface_count": empty_predicted,
            "predicted_object_ids_are_candidate_rankings": True,
            "directions": sorted({row["direction"] for row in fact_rows}),
            "forms": sorted({row["form_id"] for row in fact_rows}),
            "scaffolds": sorted({row["scaffold_id"] for row in fact_rows}),
        },
    )
    write_json(
        output_dir / "baseline_manifest.json",
        {
            "status": "completed",
            "model_label": args.model_label,
            "model_manifest": str(args.model_manifest.resolve()),
            "model_manifest_sha256": sha256_file(args.model_manifest.resolve()),
            "contract_root": str(contract_root),
            "contract_manifest_sha256": sha256_file(contract_root / "manifest.json"),
            "slice_registry_sha256": sha256_file(contract_root / "evaluation/slice_registry.json"),
            "results_root": str(results_root),
            "probe_count": len(fact_rows),
            "slice_count": len(evidence),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "evidence": evidence,
            "retention_policy": "retain_compact_summary_and_per_probe_evidence; cleanup only after baseline package verification",
        },
    )
    print(f"status=baseline_summary_complete model={args.model_label} probes={len(fact_rows)} output={output_dir}")


if __name__ == "__main__":
    main()
