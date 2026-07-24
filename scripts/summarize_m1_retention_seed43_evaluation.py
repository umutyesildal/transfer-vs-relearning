#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from transfer_vs_relearning.utils.io import write_csv, write_json

FORMS_AB = {"form_a", "form_b"}
FORMS_CD = {"form_c", "form_d"}
BASE_PERPLEXITY = 14.6988390227992
BASE_TOKEN_HASH = "be2effefc9f0655b0fc5bc3052ecfd18b51bdfa48bffa1ab2d4f0c217b81c78f"


def _json(path: Path) -> dict:
    return json.loads(path.read_text())


def _latest(root: Path) -> Path:
    paths = [p for p in root.glob("*/summary_metrics.json") if _json(p).get("completion_status", _json(p).get("status")) in {"complete", "completed"}]
    if len(paths) != 1:
        raise FileNotFoundError(f"Expected one completed result under {root}, found {len(paths)}")
    return paths[0]


def _exact(path: Path) -> tuple[float, float]:
    summary = _json(path)
    with (path.parent / "subgroup_metrics.csv").open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    relation = [float(r["top1_accuracy"]) for r in rows if r["group"] == "relation" and r["scoring"] == "primary_mean_logprob"]
    return float(summary["primary_mean_logprob"]["top1_accuracy"]), min(relation)


def _hard(root: Path) -> tuple[float, float, float, float, float]:
    with (root / "summary_by_relation_form.csv").open(newline="", encoding="utf-8-sig") as handle:
        forms = list(csv.DictReader(handle))
    min_ab = min(float(r["top1_accuracy"]) for r in forms if r["form_id"] in FORMS_AB)
    min_cd = min(float(r["top1_accuracy"]) for r in forms if r["form_id"] in FORMS_CD)
    with (root / "all_cell_intersections.csv").open(newline="", encoding="utf-8-sig") as handle:
        intersections = list(csv.DictReader(handle))
    correct, total = sum(int(r["all_cell_intersection"]) for r in intersections), sum(int(r["n"]) for r in intersections)
    relation: dict[str, list[int]] = {}
    for row in intersections:
        counts = relation.setdefault(row["relation"], [0, 0]); counts[0] += int(row["all_cell_intersection"]); counts[1] += int(row["n"])
    summary = _json(root / "summary.json")
    return int(summary["top1"]) / int(summary["probes"]), min_ab, min_cd, correct / total, min(a / b for a, b in relation.values())


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--wave-root", type=Path, required=True); args = parser.parse_args()
    root = args.wave_root.resolve()
    with (root / "checkpoint_registry.csv").open(newline="", encoding="utf-8-sig") as handle:
        registry = list(csv.DictReader(handle))
    if len(registry) != 11:
        raise ValueError(f"Expected 11 tasks, found {len(registry)}")
    rows = []
    for item in registry:
        label = item["label"]
        exact, exact_min = _exact(_latest(root / "exact_prefix" / label))
        general = _json(_latest(root / "general_capability" / label))
        hard, min_ab, min_cd, robust, robust_min = _hard(root / "hard_suite" / label)
        if general["generic_loss"]["token_ids_sha256"] != BASE_TOKEN_HASH:
            raise ValueError(f"Frozen token stream changed for {label}")
        ratio = float(general["generic_loss"]["perplexity"]) / BASE_PERPLEXITY
        short = int(general["generation"]["near_empty_by_token_length_count"])
        empty = int(general["generation"]["empty_generation_count"])
        intrusion = int(general["generation"]["synthetic_subject_intrusion_count"])
        gates = {"exact_global_gate": exact >= .90, "exact_relation_gate": exact_min >= .90,
                 "heldout_ab_gate": min_ab >= .80, "heldout_cd_gate": min_cd >= .80,
                 "robust_global_gate": robust >= .70, "robust_relation_gate": robust_min >= .70,
                 "ppl_gate": ratio <= 1.25, "corrected_generic_integrity_gate": empty == 0 and intrusion == 0}
        row = {"array_index": int(item["array_index"]), "condition": "replay_seed43", "checkpoint_step": int(item["checkpoint_step"]),
               "label": label, "exact_prefix_accuracy": exact, "exact_min_relation_accuracy": exact_min,
               "hard_accuracy": hard, "min_ab_relation_form_accuracy": min_ab, "min_cd_relation_form_accuracy": min_cd,
               "robust_global_accuracy": robust, "robust_min_relation_accuracy": robust_min,
               "wikitext_perplexity": float(general["generic_loss"]["perplexity"]), "perplexity_ratio_to_base": ratio,
               "legacy_near_empty_by_token_length_count": short, "lexical_empty_generation_count": empty,
               "synthetic_subject_intrusion_count": intrusion, "legacy_strict_integrity_gate": short == 0 and intrusion == 0,
               **gates, "all_corrected_gates_pass": all(gates.values())}
        rows.append(row)
    passing = sorted(int(r["checkpoint_step"]) for r in rows if r["all_corrected_gates_pass"])
    earliest = passing[0] if passing else None
    payload = {"status": "complete", "condition": "replay_seed43", "rows": rows,
               "passing_checkpoints": passing, "earliest_passing_checkpoint": earliest,
               "decision": "open_500_subject_scale_gate" if earliest is not None else "seed43_replication_failed",
               "selection_rule": "earliest checkpoint passing all corrected primary gates",
               "legacy_short_output_reported_as_sensitivity": True}
    write_csv(root / "seed43_checkpoint_summary.csv", rows); write_json(root / "seed43_checkpoint_summary.json", payload)
    print(root / "seed43_checkpoint_summary.json")


if __name__ == "__main__":
    main()
