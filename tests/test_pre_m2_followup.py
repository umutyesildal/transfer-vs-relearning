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
    counterbalanced_subject_assignment,
    template_registry,
)
from transfer_vs_relearning.evaluation.pre_m2_followup import _intersection_rows, _summary_rows, conditional_token_records


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
