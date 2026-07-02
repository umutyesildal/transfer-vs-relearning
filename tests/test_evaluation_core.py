from __future__ import annotations

import math
from pathlib import Path

from transfer_vs_relearning.evaluation.progress import load_completed, save_progress
from transfer_vs_relearning.evaluation.prompts import render_prompt, render_prompt_answer
from transfer_vs_relearning.evaluation.ranking import rank_candidates
from transfer_vs_relearning.evaluation.token_scoring import (
    answer_token_indices_from_offsets,
    score_from_token_logprobs,
    shifted_label_positions,
)
from transfer_vs_relearning.metrics.core import ranking_metrics, subgroup_metrics
from transfer_vs_relearning.metrics.relation_binding import relation_binding_metrics


def test_prompt_rendering_direct_and_qa() -> None:
    assert render_prompt("Who?", "direct") == "Who?"
    assert render_prompt("Who?", "qa") == "Question: Who?\nAnswer:"


def test_prompt_answer_span_with_leading_space() -> None:
    text, start, end = render_prompt_answer("Answer:", "İstanbul", " ")
    assert text == "Answer: İstanbul"
    assert text[start:end] == "İstanbul"


def test_boundary_token_mask_for_turkish_unicode_and_punctuation() -> None:
    offsets = [(0, 7), (7, 8), (8, 16), (16, 17), (17, 23)]
    assert answer_token_indices_from_offsets(offsets, 8, 23) == [2, 3, 4]


def test_boundary_token_mask_fails_for_empty_answer_span() -> None:
    try:
        answer_token_indices_from_offsets([(0, 3)], 3, 3)
    except ValueError as exc:
        assert "No answer tokens" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_causal_logit_shift_positions() -> None:
    assert shifted_label_positions([2, 3, 4]) == [1, 2, 3]


def test_total_and_mean_logprob_calculation() -> None:
    scores = score_from_token_logprobs([-1.0, -2.0, -3.0])
    assert scores["total_logprob"] == -6.0
    assert scores["mean_logprob"] == -2.0
    assert scores["token_count"] == 3


def test_deterministic_ranking_and_tie_handling() -> None:
    rows = [
        {"object_id": "b", "surface": "B", "mean_logprob": -1.0, "total_logprob": -2.0},
        {"object_id": "a", "surface": "A", "mean_logprob": -1.0, "total_logprob": -2.0},
        {"object_id": "c", "surface": "C", "mean_logprob": -3.0, "total_logprob": -4.0},
    ]
    ranked = rank_candidates(rows, "mean_logprob", "b")
    assert ranked["top1_object_id"] == "a"
    assert ranked["rank"] == 2
    assert ranked["top5_object_ids"] == ["a", "b", "c"]


def test_topk_and_mrr_metrics() -> None:
    rows = [
        {"correct_rank_mean": 1, "correct_mean_score": -1, "best_incorrect_mean_score": -2, "margin": 1},
        {"correct_rank_mean": 5, "correct_mean_score": -2, "best_incorrect_mean_score": -1, "margin": -1},
        {"correct_rank_mean": 10, "correct_mean_score": -3, "best_incorrect_mean_score": -1, "margin": -2},
    ]
    metrics = ranking_metrics(rows)
    assert metrics["top1_accuracy"] == 1 / 3
    assert metrics["top5_accuracy"] == 2 / 3
    assert math.isclose(metrics["mrr"], (1 + 1 / 5 + 1 / 10) / 3)


def test_subgroup_metrics_include_sample_count() -> None:
    rows = [
        {"language": "en", "correct_rank_mean": 1, "correct_mean_score": -1, "best_incorrect_mean_score": -2, "margin": 1},
        {"language": "tr", "correct_rank_mean": 2, "correct_mean_score": -2, "best_incorrect_mean_score": -1, "margin": -1},
    ]
    output = subgroup_metrics(rows, [("language",)])
    assert {row["language"]: row["n"] for row in output} == {"en": 1, "tr": 1}


def test_relation_swap_metrics() -> None:
    rows = [
        {
            "subject_id": "S1",
            "relation": "born_in",
            "correct_rank_mean": 1,
            "predicted_object_id": "city_a",
            "correct_object_id": "city_a",
            "other_city_rank_mean": 2,
        },
        {
            "subject_id": "S1",
            "relation": "lives_in",
            "correct_rank_mean": 2,
            "predicted_object_id": "city_a",
            "correct_object_id": "city_b",
            "other_city_rank_mean": 1,
        },
    ]
    metrics = relation_binding_metrics(rows)
    assert metrics["n_subject_pairs"] == 1
    assert metrics["residence_probe_predicts_birthplace_rate"] == 1.0


def test_progress_resume_roundtrip(tmp_path: Path) -> None:
    progress = tmp_path / "progress.json"
    save_progress(progress, {"S1_profession|en"})
    assert load_completed(progress) == {"S1_profession|en"}
