from __future__ import annotations

from pathlib import Path

import pytest

from transfer_vs_relearning.metrics.acquisition_audit import audit_acquisition_checkpoint
from transfer_vs_relearning.utils.io import read_csv_rows, write_csv


FIELDS = [
    "fact_id",
    "subject_id",
    "subject",
    "relation",
    "expected_answer",
    "correct_object_id",
    "predicted_surface_form",
    "correct_rank_mean",
    "margin",
    "branch",
    "frequency",
    "popularity",
    "name_type",
    "name_rarity",
    "number_of_candidates",
    "correct_outranks_other_city",
    "rendered_prompt",
]


def _row(fact_id: str, relation: str, rank: int) -> dict[str, str]:
    return {
        "fact_id": fact_id,
        "subject_id": fact_id.split("_")[0],
        "subject": "Test Person",
        "relation": relation,
        "expected_answer": "Correct",
        "correct_object_id": "object_correct",
        "predicted_surface_form": "Correct" if rank == 1 else "Wrong",
        "correct_rank_mean": str(rank),
        "margin": "1.0" if rank == 1 else "-1.0",
        "branch": "A",
        "frequency": "low",
        "popularity": "medium",
        "name_type": "english_like",
        "name_rarity": "common",
        "number_of_candidates": "10",
        "correct_outranks_other_city": "True" if rank == 1 else "False",
        "rendered_prompt": f"Prompt for {fact_id}",
    }


def test_audit_freezes_only_three_view_top1_facts(tmp_path: Path) -> None:
    exact = [_row("S1_born_in", "born_in", 1), _row("S2_works_at", "works_at", 1)]
    direct = [_row("S1_born_in", "born_in", 1), _row("S2_works_at", "works_at", 2)]
    qa = [_row("S1_born_in", "born_in", 1), _row("S2_works_at", "works_at", 1)]
    paths = {}
    for name, rows in (("exact", exact), ("direct", direct), ("qa", qa)):
        paths[name] = tmp_path / f"{name}.csv"
        write_csv(paths[name], rows, FIELDS)

    summary = audit_acquisition_checkpoint(
        paths["exact"], paths["direct"], paths["qa"], tmp_path / "audit"
    )

    assert summary["triple_robust"] == 1
    assert summary["groups"]["relation"]["works_at"]["triple_robust"] == 0
    assert summary["pass_patterns"] == {"E1_D0_Q1": 1, "E1_D1_Q1": 1}
    frozen = read_csv_rows(tmp_path / "audit/triple_robust_facts.csv")
    assert [row["fact_id"] for row in frozen] == ["S1_born_in"]


def test_audit_rejects_metadata_drift(tmp_path: Path) -> None:
    rows = [_row("S1_born_in", "born_in", 1)]
    for name in ("exact", "direct", "qa"):
        write_csv(tmp_path / f"{name}.csv", rows, FIELDS)
    qa = read_csv_rows(tmp_path / "qa.csv")
    qa[0]["expected_answer"] = "Different"
    write_csv(tmp_path / "qa.csv", qa, FIELDS)

    with pytest.raises(ValueError, match="metadata mismatch"):
        audit_acquisition_checkpoint(
            tmp_path / "exact.csv",
            tmp_path / "direct.csv",
            tmp_path / "qa.csv",
            tmp_path / "audit",
        )
