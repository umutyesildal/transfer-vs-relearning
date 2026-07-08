from __future__ import annotations

from pathlib import Path

from transfer_vs_relearning.training.clm import (
    estimate_optimizer_steps,
    interval_from_fractions,
    load_training_config,
    safe_run_name,
)


def test_safe_run_name_strips_unsafe_characters() -> None:
    assert safe_run_name(" M1 GPT-2 / English facts ") == "M1_GPT-2_English_facts"
    assert safe_run_name("///") == "training_run"


def test_estimate_optimizer_steps_uses_effective_batch_size() -> None:
    assert estimate_optimizer_steps(
        train_blocks=3000,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=2,
        num_train_epochs=1,
    ) == 188
    assert estimate_optimizer_steps(
        train_blocks=3000,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=2,
        num_train_epochs=3,
    ) == 564


def test_interval_from_fractions_uses_first_checkpoint_fraction() -> None:
    assert interval_from_fractions(188, [0.25, 0.5, 0.75, 1.0]) == 47
    assert interval_from_fractions(3, [0.25]) == 1


def test_m1_training_configs_have_expected_scientific_bounds() -> None:
    config_paths = sorted(Path("configs/training").glob("m1_gpt2_english_facts_*.yaml"))
    assert len(config_paths) >= 3
    baseline_paths = [path for path in config_paths if "_r1_" not in path.stem]
    assert len(baseline_paths) == 3
    learning_rates = []
    epochs = []
    for path in baseline_paths:
        config = load_training_config(path)
        assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1/output/english_training.jsonl"
        assert config["dataset"]["text_field"] == "text"
        assert config["model"]["base_model_manifest"] == "artifacts/models/openai-community__gpt2/model_manifest.json"
        assert config["training"]["block_size"] == 512
        assert config["training"]["checkpoint_fractions"] == [0.25, 0.5, 0.75, 1.0]
        assert config["training"]["bf16"] is True
        learning_rates.append(config["training"]["learning_rate"])
        epochs.append(config["training"]["num_train_epochs"])
    assert sorted(learning_rates) == [5.0e-5, 5.0e-5, 1.0e-4]
    assert sorted(epochs) == [1.0, 1.0, 3.0]


def test_m1_r1_qamix_config_points_to_derived_dataset() -> None:
    config = load_training_config(Path("configs/training/m1_gpt2_english_facts_r1_qamix_lr5e-5_ep1.yaml"))
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2.jsonl"
    assert config["training"]["num_train_epochs"] == 1.0
    assert config["training"]["learning_rate"] == 5.0e-5


def test_m1_smollm2_r1_qamix_config_points_to_derived_dataset() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep1.yaml"))
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2.jsonl"
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 1.0
    assert config["training"]["learning_rate"] == 5.0e-5


def test_m1_smollm2_r1_qamix_ep3_config_points_to_derived_dataset() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep3.yaml"))
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2.jsonl"
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 3.0
    assert config["training"]["learning_rate"] == 5.0e-5


def test_m1_smollm2_1_7b_r1_qamix_config_points_to_derived_dataset() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1.yaml"))
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2.jsonl"
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 1.0
    assert config["training"]["learning_rate"] == 5.0e-5
    assert config["training"]["per_device_train_batch_size"] == 2
    assert config["training"]["gradient_accumulation_steps"] == 8
    assert config["training"]["gradient_checkpointing"] is True


def test_m1_smollm2_bio_qa_config_points_to_new_dataset_version() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_facts_bio_qa_lr5e-5_ep1.yaml"))
    assert config["dataset"]["version"] == "synthetic_v1_bio_qa"
    assert config["dataset"]["dataset_dir"] == "artifacts/datasets/synthetic_v1_bio_qa"
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1_bio_qa/output/english_training_m1_bio_qa.jsonl"
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 1.0
    assert config["training"]["learning_rate"] == 5.0e-5


def test_m1_smollm2_stage_a_biography_config_points_to_biography_only_dataset() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1.yaml"))
    assert config["dataset"]["version"] == "synthetic_v1_bio_qa"
    assert config["dataset"]["dataset_dir"] == "artifacts/datasets/synthetic_v1_bio_qa"
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1_bio_qa/output/english_biographies.jsonl"
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 1.0
    assert config["training"]["learning_rate"] == 5.0e-5


def test_m1_smollm2_stage_b1_qa_config_points_to_stage_a_manifest() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_qa_stage_b1_lr5e-5_ep1.yaml"))
    assert config["dataset"]["version"] == "synthetic_v1_bio_qa"
    assert config["dataset"]["dataset_dir"] == "artifacts/datasets/synthetic_v1_bio_qa"
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1_bio_qa/output/english_qa_train.jsonl"
    assert (
        config["model"]["base_model_manifest"]
        == "runs/local_model_manifests/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1/final_model_manifest.json"
    )
    assert config["training"]["num_train_epochs"] == 1.0
    assert config["training"]["learning_rate"] == 5.0e-5


def test_m1_smollm2_stage_b2_answer_only_config_points_to_stage_a_manifest() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_qa_stage_b2_answer_only_lr5e-5_ep1.yaml"))
    assert config["dataset"]["version"] == "synthetic_v1_bio_qa"
    assert config["dataset"]["dataset_dir"] == "artifacts/datasets/synthetic_v1_bio_qa"
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1_bio_qa/output/english_qa_train.jsonl"
    assert config["dataset"]["answer_field"] == "answer"
    assert (
        config["model"]["base_model_manifest"]
        == "runs/local_model_manifests/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1/final_model_manifest.json"
    )
    assert config["training"]["loss_mode"] == "answer_only"
    assert config["training"]["num_train_epochs"] == 1.0
    assert config["training"]["learning_rate"] == 5.0e-5


def test_m1_smollm2_plain_high_exposure_config_returns_to_original_dataset() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_facts_lr2e-5_ep5.yaml"))
    assert config["dataset"]["version"] == "synthetic_v1"
    assert config["dataset"]["dataset_dir"] == "artifacts/datasets/synthetic_v1"
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1/output/english_training.jsonl"
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 5.0
    assert config["training"]["learning_rate"] == 2.0e-5


def test_m1_smollm2_ranking_config_points_to_bioqa_dataset_and_small_model() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_fact_ranking_lr2e-5_ep3.yaml"))
    assert config["dataset"]["version"] == "synthetic_v1_bio_qa"
    assert config["dataset"]["dataset_dir"] == "artifacts/datasets/synthetic_v1_bio_qa"
    assert config["dataset"]["include_direct_probes"] is True
    assert config["dataset"]["include_qa_train"] is True
    assert config["dataset"]["negatives_per_example"] == 7
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 3.0
    assert config["training"]["learning_rate"] == 2.0e-5
