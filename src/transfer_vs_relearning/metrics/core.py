from __future__ import annotations

from statistics import mean, median
from typing import Any, Iterable


def ranking_metrics(rows: Iterable[dict[str, Any]], rank_key: str = "correct_rank_mean") -> dict[str, float | int]:
    materialized = list(rows)
    if not materialized:
        return {"n": 0}
    ranks = [int(row[rank_key]) for row in materialized]
    margins = [float(row["margin"]) for row in materialized if row.get("margin") is not None]
    return {
        "n": len(materialized),
        "top1_accuracy": sum(rank == 1 for rank in ranks) / len(ranks),
        "top5_accuracy": sum(rank <= 5 for rank in ranks) / len(ranks),
        "mrr": mean(1 / rank for rank in ranks),
        "mean_rank": mean(ranks),
        "median_rank": median(ranks),
        "mean_correct_score": mean(float(row["correct_mean_score"]) for row in materialized),
        "mean_best_incorrect_score": mean(float(row["best_incorrect_mean_score"]) for row in materialized),
        "mean_score_margin": mean(margins) if margins else 0.0,
    }


def subgroup_metrics(rows: list[dict[str, Any]], group_fields: list[tuple[str, ...]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for fields in group_fields:
        groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
        for row in rows:
            groups.setdefault(tuple(row[field] for field in fields), []).append(row)
        for key, group_rows in sorted(groups.items()):
            metrics = ranking_metrics(group_rows)
            output.append({"group": " x ".join(fields), **dict(zip(fields, key)), **metrics})
    return output
