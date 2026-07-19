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
    return json.loads(path.read_text(encoding="utf-8"))


def _latest(root: Path) -> Path:
    completed = []
    for path in root.glob("*/summary_metrics.json"):
        payload = _json(path)
        if payload.get("completion_status", payload.get("status")) in {"complete", "completed"}:
            completed.append(path)
    if not completed:
        raise FileNotFoundError(f"No completed result under {root}")
    return sorted(completed)[-1]


def _hard_metrics(root: Path) -> tuple[float, float, float, float, float]:
    with (root / "summary_by_relation_form.csv").open(newline="", encoding="utf-8-sig") as handle:
        form_rows = list(csv.DictReader(handle))
    min_ab = min(float(row["top1_accuracy"]) for row in form_rows if row["form_id"] in FORMS_AB)
    min_cd = min(float(row["top1_accuracy"]) for row in form_rows if row["form_id"] in FORMS_CD)
    with (root / "all_cell_intersections.csv").open(newline="", encoding="utf-8-sig") as handle:
        intersections = list(csv.DictReader(handle))
    total = sum(int(row["n"]) for row in intersections)
    correct = sum(int(row["all_cell_intersection"]) for row in intersections)
    per_relation: dict[str, list[int]] = {}
    for row in intersections:
        values = per_relation.setdefault(row["relation"], [0, 0])
        values[0] += int(row["all_cell_intersection"])
        values[1] += int(row["n"])
    robust_min = min(correct_n / n for correct_n, n in per_relation.values())
    summary = _json(root / "summary.json")
    hard_accuracy = int(summary["top1"]) / int(summary["probes"])
    return hard_accuracy, min_ab, min_cd, correct / total, robust_min


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the Document 107 Qwen Pareto wave.")
    parser.add_argument("--wave-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.wave_root.resolve()
    with (root / "checkpoint_registry.csv").open(newline="", encoding="utf-8-sig") as handle:
        registry = list(csv.DictReader(handle))
    rows = []
    for item in registry:
        label = item["label"]
        exact = _json(_latest(root / "exact_prefix" / label))
        general = _json(_latest(root / "general_capability" / label))
        hard, min_ab, min_cd, robust_global, robust_min = _hard_metrics(root / "hard_suite" / label)
        exact_accuracy = float(exact["primary_mean_logprob"]["top1_accuracy"])
        token_hash = str(general["generic_loss"]["token_ids_sha256"])
        if token_hash != BASE_TOKEN_HASH:
            raise ValueError(f"Frozen WikiText token stream changed for {label}: {token_hash}")
        ppl = float(general["generic_loss"]["perplexity"])
        ratio = ppl / BASE_PERPLEXITY
        empty_count = int(general["generation"]["empty_or_near_empty_count"])
        intrusion_count = int(general["generation"]["synthetic_subject_intrusion_count"])
        generic_ok = empty_count == 0 and intrusion_count == 0
        gates = {
            "exact_gate": exact_accuracy >= 0.90,
            "heldout_ab_gate": min_ab >= 0.80,
            "heldout_cd_gate": min_cd >= 0.80,
            "robust_global_gate": robust_global >= 0.70,
            "robust_relation_gate": robust_min >= 0.70,
            "ppl_gate": ratio <= 1.25,
            "generic_integrity_gate": generic_ok,
        }
        rows.append({
            "array_index": int(item["array_index"]), "checkpoint_step": int(item["checkpoint_step"]), "label": label,
            "exact_prefix_accuracy": exact_accuracy, "hard_accuracy": hard, "min_ab_relation_form_accuracy": min_ab,
            "min_cd_relation_form_accuracy": min_cd, "robust_global_accuracy": robust_global,
            "robust_min_relation_accuracy": robust_min, "wikitext_perplexity": ppl,
            "perplexity_ratio_to_base": ratio, "empty_or_near_empty_count": empty_count,
            "synthetic_subject_intrusion_count": intrusion_count,
            "generic_completion_top1_accuracy": float(general["generic_completions"]["top1_accuracy"]),
            "token_ids_sha256": token_hash,
            **gates, "all_frozen_gates_pass": all(gates.values()),
        })
    nominees = [row for row in rows if row["all_frozen_gates_pass"]]
    earliest = min(nominees, key=lambda row: row["checkpoint_step"]) if nominees else None
    write_csv(root / "qwen_checkpoint_pareto_summary.csv", rows)
    write_json(root / "qwen_checkpoint_pareto_summary.json", {
        "status": "complete", "exploratory_only": True, "base_perplexity": BASE_PERPLEXITY,
        "rows": rows, "passing_checkpoints": [row["checkpoint_step"] for row in nominees],
        "earliest_passing_checkpoint": earliest["checkpoint_step"] if earliest else None,
        "decision": "confirmatory_retrain_required" if earliest else "design_qwen_retention_intervention",
    })
    print(root / "qwen_checkpoint_pareto_summary.csv")
    print(root / "qwen_checkpoint_pareto_summary.json")


if __name__ == "__main__":
    main()
