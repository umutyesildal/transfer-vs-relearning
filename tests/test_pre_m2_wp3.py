from __future__ import annotations

import csv
import json
from pathlib import Path

from transfer_vs_relearning.data.constants import RELATION_MAP
from transfer_vs_relearning.data.pre_m2_wp3 import (
    CONFUSABLE_RELATION,
    EXPOSURES,
    FORM_TEMPLATES,
    RELATIONS,
    SCAFFOLDS,
    build_wp3_stage_a,
)
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl


def test_wp3_builder_freezes_fixture_and_full_stage(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output = build_wp3_stage_a(repo_root, output_root=tmp_path / "wp3")
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assignment = json.loads((output / "subject_form_assignment.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "passed"
    assert assignment["balance"]["group_sizes"] == {"A": 50, "B": 50}
    assert assignment["balance"]["max_absolute_feature_difference"] <= 1
    assert len(assignment["fixture_subject_ids"]) == 10
    for stage, subjects, facts, train_rows, probes in (
        ("fixture_10", 10, 40, 280, 240),
        ("stage_a_100", 100, 400, 2800, 2400),
    ):
        audit = json.loads((output / stage / "integrity_audit.json").read_text(encoding="utf-8"))
        assert audit["status"] == "passed"
        assert (audit["subjects"], audit["facts"], audit["train_rows"], audit["probe_rows"]) == (
            subjects, facts, train_rows, probes
        )
        assert audit["rows_per_fact"] == [7]
        assert audit["probes_per_fact"] == [6]
        assert audit["invalid_hard_negative_probe_ids"] == []
        assert audit["normalized_training_prompt_overlap_by_cell"] == {"seen": facts * 2}
        assert (output / stage / "data/canonical_subject_profiles_5000.csv").is_file()
        if stage == "fixture_10":
            smoke_rows = read_csv_rows(output / stage / "evaluation_smoke_registry.csv")
            assert len(smoke_rows) == 4
            assert {row["relation"] for row in smoke_rows} == set(RELATIONS)
        with (output / stage / "probe_registry.csv").open(encoding="utf-8", newline="") as handle:
            probe_rows = list(csv.DictReader(handle))
        assert {row["relation"] for row in probe_rows} == set(RELATIONS)
        assert all(row["same_subject_confusable_relation"] == CONFUSABLE_RELATION[row["relation"]] for row in probe_rows)


def test_every_fixture_example_matches_the_frozen_semantic_contract(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output = build_wp3_stage_a(repo_root, output_root=tmp_path / "wp3")
    fixture = output / "fixture_10"
    profiles = {
        row["subject_id"]: row
        for row in read_csv_rows(fixture / "data/canonical_subject_profiles_5000.csv")
    }
    train_rows = read_jsonl(fixture / "train.jsonl")
    validation_rows = read_jsonl(fixture / "validation.jsonl")
    probes = read_csv_rows(fixture / "probe_registry.csv")

    assert len(train_rows) + len(validation_rows) + len(probes) == 560
    for row in train_rows:
        profile = profiles[row["subject_id"]]
        question = FORM_TEMPLATES[row["relation"]][row["training_form_id"]].format(
            subject=profile["subject"]
        )
        prompt = SCAFFOLDS[row["scaffold_id"]].format(question=question)
        assert row["text"] == f"{prompt} {profile[RELATION_MAP[row['relation']][0]]}"
        assert row["answer"] == profile[RELATION_MAP[row["relation"]][0]]
        assert row["exposure_index"] in range(1, len(EXPOSURES) + 1)
        assert row["scaffold_id"] == EXPOSURES[row["exposure_index"] - 1]
    for row in validation_rows:
        profile = profiles[row["subject_id"]]
        question = FORM_TEMPLATES[row["relation"]][row["training_form_id"]].format(
            subject=profile["subject"]
        )
        assert row["text"] == (
            f"{SCAFFOLDS['qa'].format(question=question)} "
            f"{profile[RELATION_MAP[row['relation']][0]]}"
        )
    for row in probes:
        profile = profiles[row["subject_id"]]
        question = FORM_TEMPLATES[row["relation"]][row["form_id"]].format(
            subject=profile["subject"]
        )
        confusable_relation = CONFUSABLE_RELATION[row["relation"]]
        assert row["question"] == question
        assert row["rendered_prompt"] == SCAFFOLDS[row["scaffold_id"]].format(question=question)
        assert row["expected_answer"] == profile[RELATION_MAP[row["relation"]][0]]
        assert row["same_subject_confusable_relation"] == confusable_relation
        assert row["same_subject_confusable_answer"] == profile[RELATION_MAP[confusable_relation][0]]
