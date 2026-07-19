from __future__ import annotations

import csv
import math
from pathlib import Path

from transfer_vs_relearning.data.turkish_bridge import (
    build_bridge_probes,
    build_localization_rows,
    eligible_fact_rows,
)
from transfer_vs_relearning.evaluation.turkish_bridge import summarize_bridge_rows
from transfer_vs_relearning.evaluation.turkish_bridge_analysis import (
    classify_bridge,
    paired_subject_bootstrap_accuracy_difference,
)
from transfer_vs_relearning.training.clm import load_training_config


def _profile() -> dict[str, str]:
    return {
        "row_id": "R1", "subject_id": "S1", "subject": "Ayşe Test",
        "profession_en": "Physicist", "profession_tr": "Fizikçi",
        "birthplace_en": "Istanbul", "birthplace_tr": "İstanbul",
        "residence_en": "Mugla", "residence_tr": "Muğla",
        "field_of_study_en": "physics", "field_of_study_tr": "fizik",
        "works_in_industry_en": "energy", "works_in_industry_tr": "enerji",
        "profession_frequency_bucket": "low", "birthplace_frequency_bucket": "low",
        "residence_frequency_bucket": "low", "field_of_study_frequency_bucket": "low",
        "works_in_industry_frequency_bucket": "low", "branch_group": "A",
        "name_type": "turkish_like", "name_rarity_bucket": "rare", "popularity_bucket": "low",
    }


def test_bridge_registry_separates_prompt_and_answer_languages() -> None:
    rows = build_bridge_probes([_profile()], {"S1"})
    assert len(rows) == 15
    profession = {row["direction"]: row for row in rows if row["relation"] == "profession"}
    assert profession["en_to_en"]["expected_answer"] == "Physicist"
    assert profession["tr_to_en"]["expected_answer"] == "Physicist"
    assert profession["tr_to_tr"]["expected_answer"] == "Fizikçi"
    assert profession["tr_to_en"]["rendered_prompt"].startswith("Soru:")
    assert profession["tr_to_en"]["correct_object_id"] == profession["tr_to_tr"]["correct_object_id"]


def test_localization_registry_is_unambiguous() -> None:
    rows = build_localization_rows([_profile()])
    assert {row["canonical_tr"] for row in rows} >= {"Fizikçi", "İstanbul", "Muğla", "fizik", "enerji"}


def test_eligibility_requires_three_positive_heldout_cells_and_strict_eight(tmp_path: Path) -> None:
    path = tmp_path / "hard.csv"
    rows = []
    for form in ("form_a", "form_b", "form_c", "form_d"):
        for scaffold in ("direct", "qa"):
            correct = not (form == "form_d" and scaffold == "qa")
            rows.append({"fact_id": "S1_profession", "subject_id": "S1", "relation": "profession", "form_id": form, "scaffold_id": scaffold, "correct_rank_mean": 1 if correct else 2, "margin": 1.0 if correct else -1.0})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    result = eligible_fact_rows(path)[0]
    assert result["eligible_3_of_4_heldout"] is True
    assert result["strict_8_of_8"] is False


def test_bridge_summary_preserves_direction_and_relation() -> None:
    rows = [
        {"direction": "tr_to_en", "relation": "profession", "correct_rank_mean": 1, "margin": 2.0},
        {"direction": "tr_to_en", "relation": "profession", "correct_rank_mean": 2, "margin": -1.0},
    ]
    summary = summarize_bridge_rows(rows)
    global_row = next(row for row in summary if row["relation"] == "__all__")
    assert global_row["top1_accuracy"] == 0.5
    assert global_row["median_margin"] == 0.5


def test_bridge_budget_is_exactly_tied_to_steps() -> None:
    config = load_training_config(Path("configs/training/turkish_bridge_adaptation_template.yaml"))
    training = config["training"]
    tokens_per_step = training["block_size"] * training["per_device_train_batch_size"] * training["gradient_accumulation_steps"]
    assert tokens_per_step == 8192
    assert training["save_steps"] * tokens_per_step == 262_144
    assert training["max_steps"] * tokens_per_step == 1_048_576
    source = (Path(__file__).resolve().parents[1] / "src/transfer_vs_relearning/training/clm.py").read_text(encoding="utf-8")
    assert 'args_kwargs["max_steps"] = int(configured_max_steps)' in source


def _bridge_rows(direction_accuracy: dict[str, float]) -> list[dict[str, object]]:
    rows = []
    for direction, accuracy in direction_accuracy.items():
        for subject_index in range(10):
            for fact_index, relation in enumerate(("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")):
                threshold = round(accuracy * 50)
                correct = fact_index * 10 + subject_index < threshold
                rows.append({
                    "probe_id": f"S{subject_index}_{relation}_{direction}", "fact_id": f"S{subject_index}_{relation}",
                    "subject_id": f"S{subject_index}", "direction": direction, "relation": relation,
                    "correct_rank_mean": 1 if correct else 2, "margin": 2.0 if correct else -1.0,
                })
    return rows


def test_paired_bootstrap_and_frozen_bridge_classifier() -> None:
    m0 = _bridge_rows({"en_to_en": 0.02, "tr_to_en": 0.02, "tr_to_tr": 0.02})
    m1 = _bridge_rows({"en_to_en": 1.0, "tr_to_en": 0.20, "tr_to_tr": 0.10})
    low = _bridge_rows({"en_to_en": 0.98, "tr_to_en": 0.30, "tr_to_tr": 0.20})
    full = _bridge_rows({"en_to_en": 0.96, "tr_to_en": 0.50, "tr_to_tr": 0.40})
    bootstrap = paired_subject_bootstrap_accuracy_difference(m1, full, direction="tr_to_en", samples=200, seed=42)
    assert math.isclose(float(bootstrap["estimate"]), 0.3, rel_tol=0.0, abs_tol=1e-12)
    rule = {
        "turkish_ppl_ratio_to_m1_max": 0.95, "en_to_en_top1_drop_max": 0.05,
        "tr_to_en_top1_min": 0.30, "tr_to_en_mean_margin_min": 0.0,
        "tr_to_en_gain_min": 0.05, "tr_to_en_already_open_floor": 0.30,
        "already_open_retention_drop_max": 0.05, "m0_adjusted_tr_to_en_gain_min": 0.20,
        "relation_count_at_or_above_0_20_min": 3,
    }
    result = classify_bridge(
        state_rows={"m0": m0, "m1": m1, "low": low, "full": full},
        ppl_states={
            "m0": {"english_ppl": 10.0, "turkish_ppl": 30.0},
            "m1": {"english_ppl": 11.0, "turkish_ppl": 30.0},
            "low": {"english_ppl": 11.1, "turkish_ppl": 27.0},
            "full": {"english_ppl": 11.2, "turkish_ppl": 24.0},
        },
        rule=rule, bootstrap_samples=200, bootstrap_seed=42,
    )
    assert result["classification"] == "promising"
    assert result["bridge_path"] == "improved_with_adaptation"


def test_corpus_launcher_keeps_all_large_outputs_on_scratch() -> None:
    launcher = (Path(__file__).resolve().parents[1] / "slurm/prepare_turkish_bridge_corpus.slurm").read_text(encoding="utf-8")
    assert "#SBATCH --partition=std" in launcher
    assert "#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/" in launcher
    assert 'SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"' in launcher
    assert 'configs/corpora/trwiki_turkish_bridge_v1.yaml' in launcher
    for stage in ("resolve", "download", "verify", "extract", "normalize", "audit", "filter", "deduplicate", "contamination-preflight", "scan-contamination", "split", "report"):
        assert f'"${{PY[@]}}" {stage} ' in launcher
