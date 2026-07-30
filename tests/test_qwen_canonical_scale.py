import json
from collections import Counter
from pathlib import Path

from transfer_vs_relearning.data.m1_canonical_form_diversity import SLOTS
from transfer_vs_relearning.data.qwen_canonical_scale import (
    EN_DECLARATIVE,
    FACTS,
    REPLAY_CYCLES,
    SUBJECTS,
    TRAIN_ROWS,
    _curriculum_rows,
)
from transfer_vs_relearning.data.pre_m2_followup import RELATIONS
from transfer_vs_relearning.training.clm import estimate_optimizer_steps, load_training_config
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl


def test_qwen_25000_config_preserves_252_update_single_gpu_contract() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_training_config(root / "configs/training/qwen_canonical_25000_replay_w0_5_seed42.yaml")
    training = config["training"]
    assert training["per_device_train_batch_size"] == 50
    assert training["gradient_accumulation_steps"] == 500
    assert training["num_train_epochs"] == 36.0
    assert estimate_optimizer_steps(TRAIN_ROWS, 50, 500, 36.0) == 252
    assert config["runtime"]["world_size"] == 1
    assert config["retention"]["coefficient"] == 0.5
    assert config["retention"]["anchor_train_file"].endswith("train_repeated_10x.jsonl")


def test_canonical_scale_constants_cover_full_relation_v2_population() -> None:
    assert SUBJECTS == 5_000
    assert FACTS == 25_000
    assert TRAIN_ROWS == 175_000
    assert REPLAY_CYCLES == 10
    assert set(EN_DECLARATIVE) == set(RELATIONS)
    assert all(len(templates) == 3 for templates in EN_DECLARATIVE.values())


def test_generated_nested_500_curriculum_matches_frozen_passing_texts() -> None:
    root = Path(__file__).resolve().parents[1]
    profiles = {
        row["subject_id"]: row
        for row in read_csv_rows(root / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv")
    }
    selected = json.loads(
        (root / "artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/summary.json").read_text()
    )["selected_subject_ids"]
    reference = read_jsonl(
        root / "artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/train.jsonl"
    )
    reference_by_fact = Counter(row["fact_id"] for row in reference)
    assert set(reference_by_fact.values()) == {7}

    generated = []
    for subject_id in selected:
        for relation in RELATIONS:
            rows, _ = _curriculum_rows(profiles[subject_id], relation)
            generated.extend(rows)
    assert len(generated) == 17_500
    assert Counter(row["training_representation"] for row in generated) == Counter(
        {slot: 2_500 for slot in SLOTS}
    )

    reference_declaratives = {
        (row["fact_id"], f"decl_{row['template_id'].rsplit('_', 1)[1]}"): row["text"]
        for row in reference
        if "_decl_" in row["template_id"]
    }
    for row in generated:
        key = (row["fact_id"], row["training_representation"])
        if key in reference_declaratives:
            assert row["text"] == reference_declaratives[key]
