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
    assert len(config_paths) == 3
    learning_rates = []
    epochs = []
    for path in config_paths:
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

