from __future__ import annotations

import pytest

from transfer_vs_relearning.metrics.pre_m2_followup import (
    exact_mcnemar_pvalue,
    paired_bootstrap_accuracy_difference,
    paired_form_comparisons,
    token_likelihood_summary,
)


def test_exact_mcnemar_pvalue_handles_symmetric_and_one_sided_discordance() -> None:
    assert exact_mcnemar_pvalue(0, 0) == 1.0
    assert exact_mcnemar_pvalue(2, 2) == 1.0
    assert exact_mcnemar_pvalue(0, 5) == pytest.approx(0.0625)


def test_paired_bootstrap_is_deterministic_and_preserves_direction() -> None:
    first = [True, True, True, False]
    second = [True, False, False, False]
    one = paired_bootstrap_accuracy_difference(first, second, samples=200, seed=7)
    two = paired_bootstrap_accuracy_difference(first, second, samples=200, seed=7)
    assert one == two
    assert one[0] == 0.5
    assert one[1] <= one[0] <= one[2]


def test_form_comparison_uses_paired_fact_cells() -> None:
    rows = []
    for fact_id, ranks in {"f1": (1, 1, 1), "f2": (1, 2, 1)}.items():
        for form_id, rank in zip(("form_a", "form_b", "form_c"), ranks, strict=True):
            rows.append(
                {
                    "model_label": "seed42",
                    "fact_id": fact_id,
                    "relation": "born_in",
                    "scaffold_id": "direct",
                    "form_id": form_id,
                    "correct_rank_mean": rank,
                }
            )
    comparisons = paired_form_comparisons(rows, bootstrap_samples=100, seed=3)
    a_b = next(row for row in comparisons if row["first_form"] == "form_a" and row["second_form"] == "form_b")
    assert a_b["first_top1"] == 2
    assert a_b["second_top1"] == 1
    assert a_b["accuracy_difference_first_minus_second"] == 0.5


def test_token_likelihood_summary_keeps_eos_positions_separate() -> None:
    rows = [
        {
            "model_label": "m",
            "relation": "born_in",
            "form_id": "form_a",
            "scaffold_id": "direct",
            "candidate_role": "gold",
            "score_type": "eos_token",
            "eos_position": "after_prompt",
            "nll": "2.0",
            "token_ppl": "7.0",
        },
        {
            "model_label": "m",
            "relation": "born_in",
            "form_id": "form_a",
            "scaffold_id": "direct",
            "candidate_role": "gold",
            "score_type": "eos_token",
            "eos_position": "after_answer_1",
            "nll": "1.0",
            "token_ppl": "3.0",
        },
    ]
    summary = token_likelihood_summary(rows)
    assert len(summary) == 2
    assert {row["eos_position"] for row in summary} == {"after_prompt", "after_answer_1"}
