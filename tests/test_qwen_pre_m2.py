from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys

from transfer_vs_relearning.data.qwen_pre_m2 import (
    build_bilingual_hard_probes,
    build_matched_m2_m3_blocks,
    build_m3_branch_b_fact_registry,
    materialize_generic_blocks,
    validate_intermediate_population,
)
from scripts.summarize_qwen_pre_m2_baseline import _robust_rows


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
            str(root / "scripts/build_qwen_pre_m2_contract.py"),
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
    preflight = (root / "slurm/preflight_qwen_pre_m2_baseline.slurm").read_text(encoding="utf-8")
    evaluation = (root / "slurm/eval_qwen_pre_m2_baseline_slice.slurm").read_text(encoding="utf-8")
    submit = (root / "scripts/submit_qwen_pre_m2_baseline.sh").read_text(encoding="utf-8")
    assert "#SBATCH --partition=std" in preflight
    assert "#SBATCH --array=0-47%1" in evaluation
    assert 'ROOT="/vol/tmp2/yesildau/qwen_pre_m2_baseline_v1"' in preflight
    assert 'ROOT="/vol/tmp2/yesildau/qwen_pre_m2_baseline_v1"' in evaluation
    assert "EXPECTED_JOBS=48" in preflight
    assert "EXPECTED_CHECKPOINTS=0" in preflight
    assert "test ! -e \"${ROOT}/results\"" in preflight
    assert 'test ! -e "${RESULT_ROOT}"' in evaluation
    assert "allocated_gpu=\"${CUDA_VISIBLE_DEVICES:-${SLURM_JOB_GPUS:-}}\"" in evaluation
    assert "unexpected_gpu_compute_processes_on_allocated_device" in evaluation
    assert "afterok:${preflight_id}" in submit
    assert "PREFLIGHT_MANIFEST" in submit
