from __future__ import annotations

import math
from statistics import mean, median
from typing import Any, Iterable


def ranking_metrics(
    rows: Iterable[dict[str, Any]],
    rank_key: str = "correct_rank_mean",
    correct_score_key: str = "correct_mean_score",
    best_incorrect_key: str = "best_incorrect_mean_score",
    margin_key: str = "margin",
) -> dict[str, float | int]:
    materialized = list(rows)
    if not materialized:
        return {"n": 0}
    ranks = [int(row[rank_key]) for row in materialized]
    margins = [float(row[margin_key]) for row in materialized if row.get(margin_key) not in (None, "")]
    return {
        "n": len(materialized),
        "top1_accuracy": sum(rank == 1 for rank in ranks) / len(ranks),
        "top5_accuracy": sum(rank <= 5 for rank in ranks) / len(ranks),
        "mrr": mean(1 / rank for rank in ranks),
        "mean_rank": mean(ranks),
        "median_rank": median(ranks),
        "mean_correct_score": mean(float(row[correct_score_key]) for row in materialized),
        "mean_best_incorrect_score": mean(float(row[best_incorrect_key]) for row in materialized),
        "mean_score_margin": mean(margins) if margins else 0.0,
    }


def dual_ranking_metrics(rows: Iterable[dict[str, Any]], partial: bool = False, expected_count: int | None = None) -> dict[str, Any]:
    materialized = list(rows)
    return {
        "status": "partial" if partial else "complete",
        "expected_count": expected_count,
        "observed_count": len(materialized),
        "primary_mean_logprob": ranking_metrics(
            materialized,
            "correct_rank_mean",
            "correct_mean_score",
            "best_incorrect_mean_score",
            "margin",
        ),
        "sensitivity_total_logprob": ranking_metrics(
            materialized,
            "correct_rank_total",
            "correct_total_score",
            "best_incorrect_total_score",
            "total_score_margin",
        ),
    }


def subgroup_metrics(rows: list[dict[str, Any]], group_fields: list[tuple[str, ...]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for fields in group_fields:
        groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
        for row in rows:
            groups.setdefault(tuple(row[field] for field in fields), []).append(row)
        for key, group_rows in sorted(groups.items()):
            mean_metrics = ranking_metrics(group_rows)
            total_metrics = ranking_metrics(
                group_rows,
                "correct_rank_total",
                "correct_total_score",
                "best_incorrect_total_score",
                "total_score_margin",
            )
            output.append({"group": " x ".join(fields), "scoring": "primary_mean_logprob", **dict(zip(fields, key)), **mean_metrics})
            output.append({"group": " x ".join(fields), "scoring": "sensitivity_total_logprob", **dict(zip(fields, key)), **total_metrics})
    return output


def chance_references(candidate_counts: dict[str, int]) -> dict[str, dict[str, float | int]]:
    references: dict[str, dict[str, float | int]] = {}
    for family, count in sorted(candidate_counts.items()):
        if count <= 0:
            continue
        references[family] = {
            "candidate_count": count,
            "random_top1_accuracy": 1 / count,
            "random_expected_rank": (count + 1) / 2,
            "random_expected_reciprocal_rank": sum(1 / rank for rank in range(1, count + 1)) / count,
        }
    return references
