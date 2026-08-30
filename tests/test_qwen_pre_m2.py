from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys

import pytest

from transfer_vs_relearning.data.qwen_pre_m2 import (
    build_branch_b_fact_registry,
    build_bilingual_hard_probes,
    build_fixed_replacement_m2_blocks,
    build_matched_m2_m3_blocks,
    build_m3_branch_b_fact_registry,
    deterministic_document_order,
    materialize_generic_blocks,
    validate_balanced_population,
    validate_intermediate_population,
)
from scripts.m2.summarize_qwen_pre_m2_baseline import _robust_rows


def _profile(index: int, branch: str) -> dict[str, str]:
    return {
        "row_id": f"R{index:05d}",
        "subject_id": f"S{index:05d}",
        "subject": f"Test Person {index}",
        "profession_en": f"Profession {index}",
        "profession_tr": f"Meslek {index}",
        "birthplace_en": f"Birth City {index}",
        "birthplace_tr": f"Doğum Şehri {index}",
        "residence_en": f"Home City {index}",
        "residence_tr": f"Yaşam Şehri {index}",
        "field_of_study_en": f"Field {index}",
        "field_of_study_tr": f"Alan {index}",
        "works_in_industry_en": f"Industry {index}",
        "works_in_industry_tr": f"Sektör {index}",
        "profession_frequency_bucket": "low",
        "birthplace_frequency_bucket": "low",
        "residence_frequency_bucket": "low",
        "field_of_study_frequency_bucket": "low",
        "works_in_industry_frequency_bucket": "low",
        "branch_group": branch,
        "name_type": "neutral",
        "name_rarity_bucket": "rare",
        "popularity_bucket": "low",
    }


def _population() -> list[dict[str, str]]:
    return [_profile(index, "A" if index <= 250 else "B") for index in range(1, 501)]


def test_intermediate_population_requires_exact_branch_balance() -> None:
    result = validate_intermediate_population(_population())
    assert result == {
        "subjects": 500,
        "facts": 2500,
        "branch_subjects": {"A": 250, "B": 250},
        "branch_facts": {"A": 1250, "B": 1250},
    }


def test_m2_population_and_branch_b_registry_use_the_exact_100_subject_m1_set() -> None:
    population = [_profile(index, "A" if index <= 50 else "B") for index in range(1, 101)]
    validation = validate_balanced_population(population, expected_subjects=100)
    assert validation["branch_subjects"] == {"A": 50, "B": 50}
    assert validation["branch_facts"] == {"A": 250, "B": 250}
    rows = build_branch_b_fact_registry(
        population,
        {row["subject_id"] for row in population},
        expected_subjects=100,
        version="m2_oscar_100_v1",
    )
    assert len(rows) == len({row["fact_id"] for row in rows}) == 250
    assert {row["branch_group"] for row in rows} == {"B"}
    assert {row["relation"] for row in rows} == {
        "profession",
        "born_in",
        "lives_in",
        "field_of_study",
        "works_in_industry",
    }
    assert all(row["answer_tr"] in row["text"] for row in rows)


def test_seeded_document_order_is_input_order_independent_and_rejects_duplicates() -> None:
    rows = [
        {"stable_document_id": "doc-c", "text": "üç"},
        {"stable_document_id": "doc-a", "text": "bir"},
        {"stable_document_id": "doc-b", "text": "iki"},
    ]
    first = deterministic_document_order(rows, namespace="m2-oscar-v1", seed=42)
    second = deterministic_document_order(reversed(rows), namespace="m2-oscar-v1", seed=42)
    assert [row["stable_document_id"] for row in first] == [
        row["stable_document_id"] for row in second
    ]
    with pytest.raises(ValueError, match="unique stable document"):
        deterministic_document_order([rows[0], rows[0]], namespace="m2-oscar-v1", seed=42)


def test_bilingual_hard_registry_covers_every_direction_form_and_scaffold() -> None:
    population = _population()
    probes = build_bilingual_hard_probes(
        population, {row["subject_id"] for row in population}
    )
    assert len(probes) == 60_000
    assert len({row["probe_id"] for row in probes}) == 60_000
    profession = {
        (row["direction"], row["form_id"], row["scaffold_id"]): row
        for row in probes
        if row["subject_id"] == "S00001" and row["relation"] == "profession"
    }
    assert profession[("tr_to_en", "form_a", "direct")]["expected_answer"] == "Profession 1"
    assert profession[("tr_to_tr", "form_a", "direct")]["expected_answer"] == "Meslek 1"
    assert profession[("tr_to_en", "form_d", "qa")]["rendered_prompt"].startswith("Soru:")
    assert profession[("en_to_en", "form_d", "qa")]["rendered_prompt"].startswith("Question:")
    assert all(
        str(row["expected_answer"]).casefold() not in str(row["question"]).casefold()
        for row in probes
    )


def test_m3_registry_contains_only_branch_b_correct_bindings() -> None:
    population = _population()
    rows = build_m3_branch_b_fact_registry(
        population, {row["subject_id"] for row in population}
    )
    assert len(rows) == 1_250
    assert {row["branch_group"] for row in rows} == {"B"}
    assert not {row["subject_id"] for row in rows} & {
        row["subject_id"] for row in population if row["branch_group"] == "A"
    }
    sample = next(row for row in rows if row["relation"] == "born_in")
    assert sample["answer_tr"] in sample["text"]


class _WhitespaceTokenizer:
    eos_token_id = 99

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        assert add_special_tokens is False
        return [len(value) for value in text.split()]


def test_matched_blocks_replace_generic_tokens_without_adding_budget() -> None:
    tokenizer = _WhitespaceTokenizer()
    generic = materialize_generic_blocks(
        [{"text": "bir iki üç dört beş altı yedi"} for _ in range(20)],
        tokenizer,
        block_size=8,
        total_blocks=10,
    )
    facts = [
        {"fact_id": "F1", "branch_group": "B", "text": "özne bir cevap"},
        {"fact_id": "F2", "branch_group": "B", "text": "özne iki cevap"},
    ]
    m2, m3, audit = build_matched_m2_m3_blocks(
        generic, facts, tokenizer, fact_cycles=2
    )
    assert len(m2) == len(m3) == 10
    assert all(len(row["input_ids"]) == 8 for row in [*m2, *m3])
    assert audit["scheduled_fact_exposures"] == 4
    assert audit["branch_a_fact_exposures"] == 0
    assert audit["m2_m3_block_count_equal"] is True
    assert audit["m2_m3_token_budget_equal"] is True
    changed = [
        index for index, (left, right) in enumerate(zip(m2, m3, strict=True))
        if left["input_ids"] != right["input_ids"]
    ]
    assert changed == [item["block_index"] for item in audit["replacement_blocks"]]


def test_fixed_m2_replacement_is_exact_matched_balanced_and_deterministic() -> None:
    tokenizer = _WhitespaceTokenizer()
    generic = materialize_generic_blocks(
        [{"text": "bir iki üç dört beş altı yedi"} for _ in range(50)],
        tokenizer,
        block_size=8,
        total_blocks=40,
    )
    relations = ["profession", "born_in", "lives_in", "field_of_study", "works_in_industry"]
    facts = [
        {
            "fact_id": f"F{index}",
            "branch_group": "B",
            "relation": relation,
            "text": f"özne {index} cevap",
        }
        for index, relation in enumerate(relations)
    ]
    first_a, first_b, first_audit = build_fixed_replacement_m2_blocks(
        generic, facts, tokenizer, replacement_block_count=6
    )
    second_a, second_b, second_audit = build_fixed_replacement_m2_blocks(
        generic, list(reversed(facts)), tokenizer, replacement_block_count=6
    )
    assert (first_a, first_b, first_audit) == (second_a, second_b, second_audit)
    assert len(first_a) == len(first_b) == 40
    assert all(len(row["input_ids"]) == 8 for row in [*first_a, *first_b])
    assert first_audit["replacement_block_count"] == 6
    assert first_audit["m2_a_m2_b_block_count_equal"] is True
    assert first_audit["m2_a_m2_b_token_budget_equal"] is True
    assert first_audit["branch_a_fact_exposures"] == 0
    assert first_audit["extra_tokens_over_m2_a"] == 0
    assert first_audit["fact_exposure_balance_max_minus_min"] <= 1
    assert first_audit["relation_exposure_balance_max_minus_min"] <= 1
    assert set(first_audit["fact_exposures"]) == {f"F{index}" for index in range(5)}
    changed = [
        index
        for index, (left, right) in enumerate(zip(first_a, first_b, strict=True))
        if left["input_ids"] != right["input_ids"]
    ]
    assert changed == [row["block_index"] for row in first_audit["replacement_blocks"]]


def test_fixed_m2_replacement_rejects_branch_a_facts() -> None:
    with pytest.raises(ValueError, match="Branch B only"):
        build_fixed_replacement_m2_blocks(
            [[1, 2, 3, 4], [5, 6, 7, 8]],
            [{"fact_id": "F1", "branch_group": "A", "text": "yanlış bağ"}],
            _WhitespaceTokenizer(),
            replacement_block_count=1,
        )


def test_clm_trainer_supports_frozen_pretokenized_full_sequence_blocks() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "src/transfer_vs_relearning/training/clm.py"
    ).read_text(encoding="utf-8")
    assert 'pretokenized = bool(dataset_config.get("pretokenized", False))' in source
    assert "Frozen M2/M3 pretokenized blocks must supervise every token" in source
    assert 'if loss_mode != "full_sequence"' in source


def test_contract_builder_materializes_24_balanced_evaluation_slices(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "contract"
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts/m2/build_qwen_pre_m2_contract.py"),
            "--repo-root",
            str(root),
            "--output-root",
            str(output),
        ],
        check=True,
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        capture_output=True,
        text=True,
    )
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    slices = json.loads(
        (output / "evaluation/slice_registry.json").read_text(encoding="utf-8")
    )
    assert manifest["evaluation_slice_count"] == 24
    assert len(slices) == 24
    assert {row["probe_count"] for row in slices} == {2_500}
    assert len({row["slice_id"] for row in slices}) == 24


def test_baseline_robust_summary_requires_all_eight_cells_per_direction() -> None:
    rows = []
    for direction in ("en_to_en", "tr_to_en", "tr_to_tr"):
        for form_id in ("form_a", "form_b", "form_c", "form_d"):
            for scaffold_id in ("direct", "qa"):
                rows.append(
                    {
                        "direction": direction,
                        "relation": "profession",
                        "fact_id": "S00001_profession",
                        "form_id": form_id,
                        "scaffold_id": scaffold_id,
                        "correct_rank_mean": 1,
                    }
                )
    summary = _robust_rows(rows)
    assert len(summary) == 6
    assert {row["scope"] for row in summary} == {"direction_relation", "direction_global"}
    assert {row["all_cell_top1"] for row in summary} == {1}


def test_qwen_baseline_wave_launchers_are_scratch_only_and_gated() -> None:
    root = Path(__file__).resolve().parents[1]
    preflight = (root / "slurm/m2/preflight_qwen_pre_m2_baseline.slurm").read_text(encoding="utf-8")
    evaluation = (root / "slurm/m2/eval_qwen_pre_m2_baseline_slice.slurm").read_text(encoding="utf-8")
    submit = (root / "scripts/m2/submit_qwen_pre_m2_baseline.sh").read_text(encoding="utf-8")
    smoke = (root / "slurm/m2/smoke_qwen_pre_m2_baseline.slurm").read_text(encoding="utf-8")
    rtx3090_submit = (root / "scripts/m2/submit_qwen_pre_m2_rtx3090_smoke.sh").read_text(encoding="utf-8")
    rtx3090_baseline_submit = (root / "scripts/m2/submit_qwen_pre_m2_baseline_rtx3090.sh").read_text(encoding="utf-8")
    assert "#SBATCH --partition=std" in preflight
    assert "#SBATCH --array=0-47%1" in evaluation
    assert 'BASELINE_SCRATCH_ROOT:-/vol/tmp2/yesildau/qwen_pre_m2_baseline_v1' in preflight
    assert 'BASELINE_SCRATCH_ROOT:-/vol/tmp2/yesildau/qwen_pre_m2_baseline_v1' in evaluation
    assert "EXPECTED_JOBS=48" in preflight
    assert "EXPECTED_CHECKPOINTS=0" in preflight
    assert "test ! -e \"${ROOT}/results\"" in preflight
    assert 'test ! -e "${RESULT_ROOT}"' in evaluation
    assert "allocated_gpu=\"${CUDA_VISIBLE_DEVICES:-${SLURM_JOB_GPUS:-}}\"" in evaluation
    assert "unexpected_gpu_compute_processes_on_allocated_device" in evaluation
    assert "afterok:${preflight_id}" in submit
    assert "PREFLIGHT_MANIFEST" in submit
    assert 'SMOKE_SCRATCH_ROOT:-/vol/tmp2/yesildau/qwen_pre_m2_baseline_smoke_v3' in smoke
    assert "--gres=gpu:rtx3090:1" in rtx3090_submit
    assert "--exclude=guppi6,guppi7" in rtx3090_submit
    assert "--nodelist=guppi8" in rtx3090_submit
    assert 'qwen_pre_m2_baseline_rtx3090_v1' in rtx3090_baseline_submit
    assert "--gres=gpu:rtx3090:1" in rtx3090_baseline_submit
    assert "--exclude=guppi5,guppi6,guppi7" in rtx3090_baseline_submit
    assert "afterok:" in rtx3090_baseline_submit
