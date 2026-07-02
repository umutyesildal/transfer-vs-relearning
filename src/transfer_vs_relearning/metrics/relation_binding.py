from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any


def relation_binding_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    city_rows = [row for row in rows if row["relation"] in {"born_in", "lives_in"}]
    by_subject: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in city_rows:
        by_subject[row["subject_id"]][row["relation"]] = row

    pairs = [pair for pair in by_subject.values() if "born_in" in pair and "lives_in" in pair]
    swapped_birth = 0
    swapped_residence = 0
    pairwise_correct = 0
    for pair in pairs:
        born = pair["born_in"]
        lives = pair["lives_in"]
        swapped_birth += int(born["predicted_object_id"] == lives["correct_object_id"])
        swapped_residence += int(lives["predicted_object_id"] == born["correct_object_id"])
        pairwise_correct += int(
            born.get("other_city_rank_mean", 10**9) > born["correct_rank_mean"]
            and lives.get("other_city_rank_mean", 10**9) > lives["correct_rank_mean"]
        )

    return {
        "n_subject_pairs": len(pairs),
        "born_in_top1_accuracy": mean(row["correct_rank_mean"] == 1 for row in city_rows if row["relation"] == "born_in") if city_rows else 0.0,
        "lives_in_top1_accuracy": mean(row["correct_rank_mean"] == 1 for row in city_rows if row["relation"] == "lives_in") if city_rows else 0.0,
        "birthplace_probe_predicts_residence_rate": swapped_birth / len(pairs) if pairs else 0.0,
        "residence_probe_predicts_birthplace_rate": swapped_residence / len(pairs) if pairs else 0.0,
        "combined_swapped_answer_rate": (swapped_birth + swapped_residence) / (2 * len(pairs)) if pairs else 0.0,
        "pairwise_relation_binding_accuracy": pairwise_correct / len(pairs) if pairs else 0.0,
    }
