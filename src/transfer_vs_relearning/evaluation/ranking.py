from __future__ import annotations

from typing import Any


def rank_candidates(rows: list[dict[str, Any]], score_key: str, correct_object_id: str) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: (-float(row[score_key]), row["object_id"]))
    ranks = {row["object_id"]: index + 1 for index, row in enumerate(ordered)}
    correct = next(row for row in ordered if row["object_id"] == correct_object_id)
    best_incorrect = next((row for row in ordered if row["object_id"] != correct_object_id), None)
    return {
        "rank": ranks[correct_object_id],
        "top1_object_id": ordered[0]["object_id"],
        "top1_surface": ordered[0]["surface"],
        "top5_object_ids": [row["object_id"] for row in ordered[:5]],
        "correct_score": float(correct[score_key]),
        "best_incorrect_score": float(best_incorrect[score_key]) if best_incorrect else None,
        "margin": float(correct[score_key]) - float(best_incorrect[score_key]) if best_incorrect else None,
        "ordered": ordered,
    }
