#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_completed(root: Path) -> Path:
    candidates = []
    for path in root.glob("*/summary_metrics.json"):
        payload = read_json(path)
        status = payload.get("completion_status", payload.get("status"))
        if status in {"completed", "complete"}:
            candidates.append(path)
    if not candidates:
        raise FileNotFoundError(f"No completed summary under {root}")
    return sorted(candidates)[-1]


def robust_intersection(path: Path) -> tuple[int, int]:
    correct = 0
    total = 0
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            correct += int(row["all_form_intersection"])
            total += int(row["n"])
    return correct, total


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the frozen WP5 LR/checkpoint wave.")
    parser.add_argument("--wave-root", type=Path, required=True)
    parser.add_argument("--base-perplexity", type=float, default=15.9240)
    args = parser.parse_args()

    root = args.wave_root.resolve()
    rows = []
    with (root / "checkpoint_registry.csv").open(newline="", encoding="utf-8-sig") as handle:
        registry = list(csv.DictReader(handle))

    for item in registry:
        label = item["label"]
        hard = read_json(root / "hard_suite" / label / "summary.json")
        exact = read_json(latest_completed(root / "exact_prefix" / label))
        general = read_json(latest_completed(root / "general_capability" / label))
        binding = read_json(
            latest_completed(root / "exact_prefix" / label).with_name("relation_binding_metrics.json")
        )
        robust_correct, robust_total = robust_intersection(
            root / "hard_suite" / label / "form_intersections.csv"
        )
        forced = hard["relation_swapped_forced_choice"]
        ppl = float(general["generic_loss"]["perplexity"])
        rows.append(
            {
                "array_index": int(item["array_index"]),
                "label": label,
                "lr_label": item["lr_label"],
                "checkpoint_step": int(item["checkpoint_step"]),
                "hard_top1": int(hard["top1"]),
                "hard_top1_accuracy": int(hard["top1"]) / int(hard["probes"]),
                "robust_all_forms": robust_correct,
                "robust_all_forms_accuracy": robust_correct / robust_total,
                "forced_choice_correct": int(forced["correct"]),
                "forced_choice_accuracy": int(forced["correct"]) / int(forced["n"]),
                "exact_top1_accuracy": float(exact["primary_mean_logprob"]["top1_accuracy"]),
                "exact_mrr": float(exact["primary_mean_logprob"]["mrr"]),
                "binding_accuracy": float(binding["macro_average"]["pairwise_relation_binding_accuracy"]),
                "wikitext_nll": float(general["generic_loss"]["mean_token_nll"]),
                "wikitext_perplexity": ppl,
                "perplexity_ratio_to_base": ppl / args.base_perplexity,
                "ended_with_eos_count": int(general["generation"]["ended_with_eos_count"]),
                "empty_or_near_empty_count": int(
                    general["generation"]["empty_or_near_empty_count"]
                ),
                "generic_completion_top1_accuracy": float(
                    general["generic_completions"]["top1_accuracy"]
                ),
            }
        )

    fieldnames = list(rows[0])
    csv_path = root / "wp5_checkpoint_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    json_path = root / "wp5_checkpoint_summary.json"
    json_path.write_text(json.dumps({"base_perplexity": args.base_perplexity, "rows": rows}, indent=2) + "\n")
    print(csv_path)
    print(json_path)
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
