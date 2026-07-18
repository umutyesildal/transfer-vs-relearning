from __future__ import annotations

import csv
import json
from pathlib import Path

from transfer_vs_relearning.data.pre_m2_followup import (
    FOLLOWUP_VERSION,
    FORM_IDS,
    RELATIONS,
    assignment_balance,
    build_paraphrase_probes,
    build_pre_m2_followup_contract,
    build_wp1b_training_datasets,
    counterbalanced_subject_assignment,
    template_registry,
)
from transfer_vs_relearning.evaluation.pre_m2_followup import (
    _confusable_relation,
    _forced_choice_rows,
    _has_relation_columns,
    _intersection_rows,
    _summary_rows,
    conditional_token_records,
)


def _canonical_rows(count: int = 4) -> list[dict[str, str]]:
    rows = []
    for index in range(count):
        rows.append(
            {
                "subject_id": f"S{index:05d}",
                "subject": f"Person {index}",
                "profession_en": f"Profession {index}",
                "birthplace_en": f"Birthplace {index}",
                "residence_en": f"Residence {index}",
                "field_of_study_en": f"Field {index}",
                "works_in_industry_en": f"Industry {index}",
                "branch_group": "A" if index % 2 == 0 else "B",
                "name_type": "english_like" if index % 2 == 0 else "turkish_like",
                "name_rarity_bucket": "common" if index < 2 else "rare",
                "popularity_bucket": "high" if index % 2 == 0 else "low",
                "profession_frequency_bucket": "high",
                "birthplace_frequency_bucket": "medium",
                "residence_frequency_bucket": "low",
                "field_of_study_frequency_bucket": "medium",
                "works_in_industry_frequency_bucket": "high",
            }
        )
    return rows


def test_template_registry_has_three_forms_and_separate_scaffolds() -> None:
    registry = template_registry()
    assert registry["version"] == FOLLOWUP_VERSION
    assert registry["form_ids"] == list(FORM_IDS)
    assert set(registry["relations"]) == set(RELATIONS)
    assert set(registry["scaffolds"]) == {"direct", "qa"}


def test_counterbalanced_assignment_is_deterministic_and_switched_by_group() -> None:
    rows = _canonical_rows()
    subject_ids = [row["subject_id"] for row in rows]
    first = counterbalanced_subject_assignment(rows, subject_ids, seed=9)
    second = counterbalanced_subject_assignment(rows, subject_ids, seed=9)
    assert first == second
    assert assignment_balance(first)["group_sizes"] == {"A": 2, "B": 2}
    for item in first:
        assert {item["training_form_id"], item["heldout_crossed_form_id"]} == {"form_a", "form_b"}


def test_probe_registry_crosses_subjects_forms_and_scaffolds() -> None:
    rows = _canonical_rows()
    subject_ids = [row["subject_id"] for row in rows]
    assignments = counterbalanced_subject_assignment(rows, subject_ids, seed=4)
    probes = build_paraphrase_probes(rows, assignments)
    assert len(probes) == 4 * len(RELATIONS) * len(FORM_IDS) * 2
    assert len({probe["probe_id"] for probe in probes}) == len(probes)
    cells = {probe["wp1b_counterbalance_cell"] for probe in probes}
    assert cells == {"seen", "crossed", "novel"}
    assert {probe["canonical_m1_exposure"] for probe in probes} == {"heldout_unseen"}


def test_real_contract_builder_freezes_expected_counts(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "model.safetensors").write_bytes(b"distinct-test-weights")
    model_manifest = tmp_path / "model_manifest.json"
    model_manifest.write_text(
        json.dumps(
            {
                "model_id": "fixture",
                "resolved_revision": "fixture-revision",
                "local_path_absolute": str(model_dir),
                "file_hashes": {"model.safetensors": "stale-declared-hash"},
            }
        ),
        encoding="utf-8",
    )
    output_dir = build_pre_m2_followup_contract(
        repo_root,
        output_dir=tmp_path / FOLLOWUP_VERSION,
        model_manifests={"base": model_manifest},
    )
    integrity = json.loads((output_dir / "manifests/integrity_audit.json").read_text(encoding="utf-8"))
    contract = json.loads((output_dir / "manifests/experimental_contract.json").read_text(encoding="utf-8"))
    assert integrity["status"] == "passed"
    assert integrity["observed_subjects"] == 100
    assert integrity["observed_facts"] == 500
    assert integrity["observed_probes"] == 3000
    assert integrity["normalized_training_prompt_overlap_count"] == 0
    assert contract["unit_decision"]["subjects"] == 100
    assert contract["unit_decision"]["facts"] == 500
    provenance = json.loads((output_dir / "manifests/provenance.json").read_text(encoding="utf-8"))
    assert provenance["models"]["base"]["verification"] == "live_weights_verified"
    assert provenance["models"]["base"]["manifest_declared_hash_matches_live"] is False
    candidates = json.loads((output_dir / "manifests/candidate_inventory.json").read_text(encoding="utf-8"))
    assert candidates["sizes"] == {
        "city": 130,
        "field_of_study": 50,
        "industry": 50,
        "profession": 200,
    }
    with (output_dir / "evaluations/paraphrase_probe_registry.csv").open(encoding="utf-8", newline="") as handle:
        assert sum(1 for _ in csv.DictReader(handle)) == 3000


def test_wp1b_builder_preserves_budget_and_reverses_every_subject(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    followup_dir = build_pre_m2_followup_contract(repo_root, output_dir=tmp_path / FOLLOWUP_VERSION)
    training_root = build_wp1b_training_datasets(repo_root, followup_dir=followup_dir)
    manifest = json.loads((training_root / "dataset_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "passed"
    assert manifest["fact_graph"] == {"subjects": 100, "relations": 5, "facts": 500}
    assert manifest["exposure_contract"]["rows_per_fact"] == 7
    assert manifest["shared_original_swap_training_prompt_count"] == 0
    assert manifest["swap_a_b_assignment_mismatch_subjects"] == []
    for condition in ("original", "swap"):
        summary = manifest["conditions"][condition]
        assert summary["status"] == "passed"
        assert summary["train_rows"] == 3500
        assert summary["validation_rows"] == 500
        assert summary["rows_per_fact"] == [7]
        assert summary["group_row_counts"] == {"A": 1750, "B": 1750}
        assert summary["form_row_counts"] == {"form_a": 1750, "form_b": 1750}
        assert summary["scaffold_row_counts"] == {"direct": 2000, "qa": 1500}
        assert summary["unique_training_prompt_count"] == 1000


def test_teacher_forced_token_records_use_causal_shift_and_explicit_eos() -> None:
    # Input token 2 is the first answer token, so it must be scored from logit position 1.
    input_ids = [7, 8, 2, 3]
    log_probs = [[-9.0] * 10 for _ in input_ids]
    log_probs[1][2] = -0.25
    log_probs[2][3] = -0.50
    log_probs[1][9] = -1.25
    log_probs[2][9] = -1.00
    log_probs[3][9] = -0.10
    records = conditional_token_records(
        input_ids=input_ids,
        answer_token_indices=[2, 3],
        log_probs=log_probs,
        eos_token_id=9,
    )
    answer_records = [record for record in records if record["score_type"] == "answer_token"]
    eos_records = [record for record in records if record["score_type"] == "eos_token"]
    assert [record["logit_index"] for record in answer_records] == [1, 2]
    assert [record["conditional_logprob"] for record in answer_records] == [-0.25, -0.50]
    assert [record["eos_position"] for record in eos_records] == [
        "after_prompt",
        "after_answer_1",
        "after_answer_2",
    ]
    assert eos_records[-1]["conditional_logprob"] == -0.10


def test_form_intersections_are_computed_per_fact_and_scaffold() -> None:
    rows = []
    for fact_id, outcomes in {"f1": (1, 1, 1), "f2": (1, 2, 1)}.items():
        for form_id, rank in zip(FORM_IDS, outcomes, strict=True):
            rows.append(
                {
                    "fact_id": fact_id,
                    "relation": "born_in",
                    "scaffold_id": "direct",
                    "form_id": form_id,
                    "correct_rank_mean": rank,
                }
            )
    summary = _intersection_rows(rows)
    assert summary == [
        {
            "relation": "born_in",
            "scaffold_id": "direct",
            "n": 2,
            "form_a_top1": 2,
            "form_b_top1": 1,
            "form_c_top1": 2,
            "a_b_intersection": 1,
            "a_c_intersection": 2,
            "b_c_intersection": 1,
            "all_form_intersection": 1,
        }
    ]


def test_summary_parses_resumed_boolean_strings() -> None:
    rows = [
        {
            "relation": "born_in",
            "form_id": "form_a",
            "scaffold_id": "direct",
            "correct_rank_mean": "1",
            "margin": "2.0",
            "gold_eos_preferred_to_first_answer": "False",
        }
    ]
    assert _summary_rows(rows)[0]["early_eos_preference_count"] == 0


def test_wp3_confusable_relations_are_bidirectional() -> None:
    assert _confusable_relation("studied_at") == "field_of_study"
    assert _confusable_relation("field_of_study") == "studied_at"
    assert _confusable_relation("works_at") == "works_in_industry"
    assert _confusable_relation("works_in_industry") == "works_at"


def test_wp3_confusable_columns_are_not_required_by_relation_v2_profiles() -> None:
    relation_v2_row = _canonical_rows(1)[0]
    assert "university_en" not in relation_v2_row
    assert "employer_en" not in relation_v2_row
    for relation in ("field_of_study", "works_in_industry"):
        confusable = _confusable_relation(relation)
        assert confusable is not None
        assert not _has_relation_columns(relation_v2_row, confusable)


def test_forced_choice_summary_parses_resumed_rows() -> None:
    rows = [
        {
            "relation": "studied_at",
            "form_id": "form_a",
            "scaffold_id": "direct",
            "same_subject_confusable_object_id": "field_1",
            "same_subject_relation_forced_choice_correct": "True",
            "gold_vs_same_subject_confusable_nll_margin": "1.5",
        },
        {
            "relation": "studied_at",
            "form_id": "form_a",
            "scaffold_id": "direct",
            "same_subject_confusable_object_id": "field_2",
            "same_subject_relation_forced_choice_correct": "False",
            "gold_vs_same_subject_confusable_nll_margin": "-0.5",
        },
    ]
    assert _forced_choice_rows(rows) == [
        {
            "relation": "studied_at",
            "form_id": "form_a",
            "scaffold_id": "direct",
            "n": 2,
            "forced_choice_correct": 1,
            "forced_choice_accuracy": 0.5,
            "mean_gold_vs_confusable_nll_margin": 0.5,
        }
    ]
