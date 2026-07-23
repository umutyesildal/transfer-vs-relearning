from __future__ import annotations

import pytest

from transfer_vs_relearning.evaluation.general_capability import (
    bootstrap_weighted_nll_interval,
    classify_perplexity_ratio,
    distinct_ngram_ratio,
    generation_metrics,
    has_lexical_content,
    longest_repeated_token_run,
    repeated_ngram_fraction,
    split_token_ids,
)


def test_split_token_ids_keeps_valid_tail() -> None:
    assert split_token_ids(list(range(10)), block_size=4) == [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [8, 9],
    ]


def test_split_token_ids_drops_single_token_tail() -> None:
    assert split_token_ids(list(range(9)), block_size=4) == [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
    ]


def test_repetition_and_distinct_metrics() -> None:
    tokens = [1, 2, 3, 1, 2, 3]
    assert repeated_ngram_fraction(tokens, 3) == pytest.approx(0.5)
    assert distinct_ngram_ratio(tokens, 1) == pytest.approx(0.5)
    assert distinct_ngram_ratio(tokens, 2) == pytest.approx(3 / 5)


def test_longest_repeated_token_run() -> None:
    assert longest_repeated_token_run([]) == 0
    assert longest_repeated_token_run([1, 1, 2, 3, 3, 3, 2]) == 3


def test_generation_metrics_detect_subject_intrusion() -> None:
    metrics = generation_metrics([1, 1, 2], "A story about Mada Granger.", ["Mada Granger", "Other Name"])
    assert metrics["synthetic_subject_intrusion_count"] == 1
    assert metrics["synthetic_subject_intrusions"] == ["Mada Granger"]
    assert metrics["longest_repeated_token_run"] == 2


@pytest.mark.parametrize("text", ["", "   \n", "...?!", "—"])
def test_lexical_content_rejects_empty_whitespace_and_punctuation(text: str) -> None:
    assert not has_lexical_content(text)


def test_generation_metrics_marks_eos_only_as_empty() -> None:
    metrics = generation_metrics([151643], "", [])
    assert metrics["near_empty_by_token_length"]
    assert metrics["empty_generation"]


def test_generation_metrics_keeps_valid_one_word_answer_plus_eos() -> None:
    metrics = generation_metrics([10646, 151643], " navigation", [])
    assert metrics["near_empty_by_token_length"]
    assert metrics["empty_or_near_empty"]
    assert not metrics["empty_generation"]


def test_bootstrap_weighted_nll_interval_is_deterministic() -> None:
    rows = [
        {"nll_sum": 10.0, "token_count": 5},
        {"nll_sum": 30.0, "token_count": 10},
        {"nll_sum": 20.0, "token_count": 10},
    ]
    first = bootstrap_weighted_nll_interval(rows, samples=100, seed=7)
    second = bootstrap_weighted_nll_interval(rows, samples=100, seed=7)
    assert first == second
    assert first[0] <= 2.4 <= first[1]


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (1.0, "no_material_generic_loss_degradation_detected"),
        (1.10, "no_material_generic_loss_degradation_detected"),
        (1.11, "measurable_generic_loss_drift"),
        (1.25, "measurable_generic_loss_drift"),
        (1.26, "material_generic_loss_degradation_flag"),
    ],
)
def test_classify_perplexity_ratio(ratio: float, expected: str) -> None:
    assert classify_perplexity_ratio(ratio) == expected
