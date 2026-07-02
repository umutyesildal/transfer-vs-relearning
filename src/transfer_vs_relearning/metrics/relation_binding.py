from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any


def _as_float(value: Any, default: float | None = None) -> float:
    if value in (None, ""):
        if default is None:
            raise ValueError("Missing numeric value")
        return default
    return float(value)


def _as_int(value: Any) -> int:
    return int(_as_float(value))


def _binding_for_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    city_rows = [row for row in rows if row["relation"] in {"born_in", "lives_in"}]
    born_rows = [row for row in city_rows if row["relation"] == "born_in"]
    lives_rows = [row for row in city_rows if row["relation"] == "lives_in"]
    by_subject: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in city_rows:
        by_subject[row["subject_id"]][row["relation"]] = row

    pairs = [pair for pair in by_subject.values() if "born_in" in pair and "lives_in" in pair]
    swapped_birth = 0
    swapped_residence = 0
    pairwise_correct = 0
    born_other_ranks = []
    lives_other_ranks = []
    for pair in pairs:
        born = pair["born_in"]
        lives = pair["lives_in"]
        swapped_birth += int(born["predicted_object_id"] == lives["correct_object_id"])
        swapped_residence += int(lives["predicted_object_id"] == born["correct_object_id"])
        if born.get("other_city_rank_mean") not in (None, ""):
            born_other_ranks.append(_as_float(born["other_city_rank_mean"]))
        if lives.get("other_city_rank_mean") not in (None, ""):
            lives_other_ranks.append(_as_float(lives["other_city_rank_mean"]))
        pairwise_correct += int(
            _as_float(born.get("other_city_rank_mean"), 10**9) > _as_float(born["correct_rank_mean"])
            and _as_float(lives.get("other_city_rank_mean"), 10**9) > _as_float(lives["correct_rank_mean"])
        )

    return {
        "complete_subject_pairs": len(pairs),
        "born_in_top1_accuracy": mean(_as_int(row["correct_rank_mean"]) == 1 for row in born_rows) if born_rows else 0.0,
        "lives_in_top1_accuracy": mean(_as_int(row["correct_rank_mean"]) == 1 for row in lives_rows) if lives_rows else 0.0,
        "birthplace_probe_predicts_residence_rate": swapped_birth / len(pairs) if pairs else 0.0,
        "residence_probe_predicts_birthplace_rate": swapped_residence / len(pairs) if pairs else 0.0,
        "combined_swapped_answer_rate": (swapped_birth + swapped_residence) / (2 * len(pairs)) if pairs else 0.0,
        "pairwise_relation_binding_accuracy": pairwise_correct / len(pairs) if pairs else 0.0,
        "mean_residence_rank_under_birthplace_probe": mean(born_other_ranks) if born_other_ranks else None,
        "mean_birthplace_rank_under_residence_probe": mean(lives_other_ranks) if lives_other_ranks else None,
    }


def relation_binding_metrics(rows: list[dict[str, Any]], expected_subjects_per_language: int | None = None) -> dict[str, Any]:
    by_language: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["relation"] in {"born_in", "lives_in"}:
            by_language[row["language"]].append(row)
    languages = sorted(by_language)
    payload: dict[str, Any] = {"by_language": {}, "macro_average": {}}
    for language in languages:
        metrics = _binding_for_rows(by_language[language])
        if expected_subjects_per_language is not None and metrics["complete_subject_pairs"] != expected_subjects_per_language:
            raise ValueError(
                f"{language} relation-binding pairs: expected {expected_subjects_per_language}, "
                f"found {metrics['complete_subject_pairs']}"
            )
        payload["by_language"][language] = metrics
    if languages:
        metric_names = [key for key in next(iter(payload["by_language"].values())) if key != "complete_subject_pairs"]
        payload["macro_average"] = {
            key: mean(value[key] for value in payload["by_language"].values() if value[key] is not None)
            for key in metric_names
            if any(value[key] is not None for value in payload["by_language"].values())
        }
    return payload
