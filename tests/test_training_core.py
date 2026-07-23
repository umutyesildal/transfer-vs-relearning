from __future__ import annotations

from pathlib import Path

from transfer_vs_relearning.training.clm import (
    _answer_only_labels,
    _padded_full_sequence,
    combine_retention_losses,
    estimate_optimizer_steps,
    resolve_training_seeds,
    interval_from_fractions,
    load_training_config,
    safe_run_name,
    tokenizer_path_from_manifest,
)


def test_replay_loss_is_added_without_replacing_factual_loss() -> None:
    assert combine_retention_losses(2.0, 4.0, 0.5) == 4.0


def test_replay_coefficient_must_be_positive() -> None:
    try:
        combine_retention_losses(2.0, 4.0, 0.0)
    except ValueError as error:
        assert "positive" in str(error)
    else:
        raise AssertionError("Expected a non-positive replay coefficient to fail")


def test_replay_full_sequence_supervises_eos_but_not_padding() -> None:
    ids, mask, labels = _padded_full_sequence(
        [10, 11],
        [1, 1],
        eos_token_id=99,
        pad_token_id=0,
        block_size=5,
    )
    assert ids == [10, 11, 99, 0, 0]
    assert mask == [1, 1, 1, 0, 0]
    assert labels == [10, 11, 99, -100, -100]


def test_qwen_retention_configs_preserve_factual_budget() -> None:
    control = load_training_config(
        Path("configs/training/m1_qwen_retention_control_seed42.yaml")
    )
    replay = load_training_config(
        Path("configs/training/m1_qwen_retention_replay_w0_5_seed42.yaml")
    )
    assert control["dataset"] == replay["dataset"]
    assert control["model"] == replay["model"]
    for key in (
        "block_size", "learning_rate", "num_train_epochs", "per_device_train_batch_size",
        "gradient_accumulation_steps", "warmup_ratio", "weight_decay", "lr_scheduler_type",
        "loss_mode", "supervise_eos", "seed", "data_seed",
    ):
        assert control["training"][key] == replay["training"][key]
    assert estimate_optimizer_steps(3500, 10, 50, 36.0) == 252
    assert replay["retention"] == {
        "mechanism": "replay",
        "coefficient": 0.5,
        "max_tokens": 64,
        "text_field": "text",
        "anchor_train_file": "/vol/tmp2/yesildau/m1_retention_v1/anchor/train.jsonl",
        "anchor_validation_file": "/vol/tmp2/yesildau/m1_retention_v1/anchor/validation.jsonl",
    }


def test_eos_ablation_masks_only_the_eos_label() -> None:
    input_ids = [10, 11, 12, 13]
    answer_mask = [False, False, True, True]
    with_eos = _answer_only_labels(
        input_ids, answer_mask, 99, supervise_eos=True
    )
    without_eos = _answer_only_labels(
        input_ids, answer_mask, 99, supervise_eos=False
    )
    assert with_eos == [-100, -100, 12, 13, 99]
    assert without_eos == [-100, -100, 12, 13, -100]
    assert with_eos[:-1] == without_eos[:-1]


def test_training_data_seed_can_vary_without_changing_split_seed() -> None:
    assert resolve_training_seeds(
        {"split_seed": 42},
        {"seed": 43, "data_seed": 43},
    ) == (43, 42, 43)
    assert resolve_training_seeds(
        {"split_seed": 42},
        {"seed": 43},
    ) == (43, 42, 42)


def test_safe_run_name_strips_unsafe_characters() -> None:
    assert safe_run_name(" M1 GPT-2 / English facts ") == "M1_GPT-2_English_facts"
    assert safe_run_name("///") == "training_run"


def test_clm_tokenizer_path_prefers_manifest_source(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint"
    tokenizer = tmp_path / "base-tokenizer"
    assert tokenizer_path_from_manifest(
        {"tokenizer_source_path_absolute": str(tokenizer)}, tmp_path, checkpoint
    ) == tokenizer.resolve()
    assert tokenizer_path_from_manifest({}, tmp_path, checkpoint) == checkpoint


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


def test_acquisition_ladder_config_uses_explicit_validation_and_answer_only_loss() -> None:
    config = load_training_config(
        Path("configs/training/m1_smollm2_360m_acquisition_ladder_10_answer_only_lr5e-5_ep10.yaml")
    )
    assert config["dataset"]["train_file"].endswith("10_subjects/train.jsonl")
    assert config["dataset"]["validation_file"].endswith("10_subjects/validation.jsonl")
    assert config["model"]["base_model_manifest"] == (
        "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    )
    assert config["training"]["loss_mode"] == "answer_only"
    assert config["training"]["num_train_epochs"] == 10.0
    assert config["training"]["block_size"] == 128


def test_single_fact_diagnostic_config_is_a_high_exposure_control() -> None:
    config = load_training_config(
        Path("configs/training/m1_smollm2_360m_diagnostic_single_fact_answer_only_lr1e-4_ep50.yaml")
    )
    assert config["dataset"]["train_file"].endswith("single_fact/train.jsonl")
    assert config["dataset"]["validation_file"].endswith("single_fact/validation.jsonl")
    assert config["training"]["loss_mode"] == "answer_only"
    assert config["training"]["num_train_epochs"] == 50.0
    assert config["training"]["per_device_train_batch_size"] == 1
    assert config["training"]["learning_rate"] == 1.0e-4
    assert config["training"]["lr_scheduler_type"] == "constant_with_warmup"


def test_direct_supervision_diagnostic_matches_single_fact_step_budget() -> None:
    config = load_training_config(
        Path("configs/training/m1_smollm2_360m_diagnostic_single_fact_direct_answer_only_lr1e-4_ep36.yaml")
    )
    assert config["dataset"]["train_file"].endswith("single_fact_direct_supervision/train.jsonl")
    assert config["training"]["loss_mode"] == "answer_only"
    assert config["training"]["num_train_epochs"] == 36.0
    assert config["training"]["per_device_train_batch_size"] == 1
    assert estimate_optimizer_steps(7, 1, 1, 36.0) == 252


def test_single_relation_direct_supervision_matches_update_and_exposure_budget() -> None:
    config = load_training_config(
        Path("configs/training/m1_smollm2_360m_diagnostic_born_in_10_direct_answer_only_lr1e-4_ep36.yaml")
    )
    assert config["dataset"]["train_file"].endswith(
        "single_relation_10_subjects_direct_supervision/train.jsonl"
    )
    assert config["training"]["num_train_epochs"] == 36.0
    assert config["training"]["per_device_train_batch_size"] == 10
    assert estimate_optimizer_steps(70, 10, 1, 36.0) == 252


def test_all_relations_direct_supervision_matches_update_and_exposure_budget() -> None:
    config = load_training_config(
        Path("configs/training/m1_smollm2_360m_diagnostic_all_relations_50_direct_answer_only_lr1e-4_ep36.yaml")
    )
    assert config["dataset"]["train_file"].endswith(
        "all_relations_10_subjects_direct_supervision/train.jsonl"
    )
    assert config["training"]["num_train_epochs"] == 36.0
    assert config["training"]["per_device_train_batch_size"] == 50
    assert estimate_optimizer_steps(350, 50, 1, 36.0) == 252


def test_500_fact_direct_supervision_uses_gradient_accumulation_for_matched_updates() -> None:
    config = load_training_config(
        Path("configs/training/m1_smollm2_360m_acquisition_100_subjects_500_facts_direct_lr1e-4_ep36.yaml")
    )
    assert config["dataset"]["train_file"].endswith(
        "all_relations_100_subjects_direct_supervision/train.jsonl"
    )
    assert config["training"]["per_device_train_batch_size"] == 50
    assert config["training"]["gradient_accumulation_steps"] == 10
    assert config["training"]["num_train_epochs"] == 36.0
    assert estimate_optimizer_steps(3500, 50, 10, 36.0) == 252


def test_relation_v2_500_fact_config_preserves_clean_matched_budget() -> None:
    config = load_training_config(
        Path("configs/training/m1_smollm2_360m_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36.yaml")
    )
    assert config["dataset"]["version"] == "relation_v2_gate_v1_100_subjects_500_facts_direct"
    assert config["dataset"]["train_file"].endswith("acquisition_100_subjects_direct/train.jsonl")
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["loss_mode"] == "answer_only"
    assert config["training"]["per_device_train_batch_size"] == 50
    assert config["training"]["gradient_accumulation_steps"] == 10
    assert config["training"]["num_train_epochs"] == 36.0
    assert estimate_optimizer_steps(3500, 50, 10, 36.0) == 252


def test_relation_v2_1_7b_500_fact_config_changes_only_model_capacity_and_memory_batching() -> None:
    small = load_training_config(
        Path("configs/training/m1_smollm2_360m_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36.yaml")
    )
    large = load_training_config(
        Path("configs/training/m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36.yaml")
    )
    assert large["dataset"] == small["dataset"]
    assert large["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json"
    for key in (
        "block_size", "learning_rate", "num_train_epochs", "warmup_ratio", "weight_decay",
        "lr_scheduler_type", "loss_mode", "bf16", "fp16", "max_grad_norm", "seed",
    ):
        assert large["training"][key] == small["training"][key]
    assert large["training"]["per_device_train_batch_size"] == 10
    assert large["training"]["per_device_eval_batch_size"] == 1
    assert large["training"]["gradient_accumulation_steps"] == 50
    assert 10 * 50 == 50 * 10 == 500
    assert estimate_optimizer_steps(3500, 10, 50, 36.0) == 252


def test_relation_v2_2500_fact_exploratory_config_preserves_matched_budget() -> None:
    config = load_training_config(
        Path("configs/training/m1_smollm2_360m_relation_v2_500_subjects_2500_facts_direct_lr1e-4_ep36.yaml")
    )
    assert config["dataset"]["version"].endswith("_exploratory")
    assert config["dataset"]["train_file"].endswith("acquisition_500_subjects_direct/train.jsonl")
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["loss_mode"] == "answer_only"
    assert config["training"]["per_device_train_batch_size"] == 50
    assert config["training"]["gradient_accumulation_steps"] == 50
    assert config["training"]["num_train_epochs"] == 36.0
    assert estimate_optimizer_steps(17500, 50, 50, 36.0) == 252


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


def test_m1_smollm2_binding_mix_config_points_to_binding_dataset_version() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1.yaml"))
    assert config["dataset"]["version"] == "synthetic_v1_binding_mix"
    assert config["dataset"]["dataset_dir"] == "artifacts/datasets/synthetic_v1_binding_mix"
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1_binding_mix/output/english_training_m1_binding_mix.jsonl"
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 1.0
    assert config["training"]["learning_rate"] == 5.0e-5


def test_m1_smollm2_binding_mix_memory_safe_config_points_to_binding_dataset_version() -> None:
    config = load_training_config(
        Path("configs/training/m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1_bs2_ga8_gc.yaml")
    )
    assert config["dataset"]["version"] == "synthetic_v1_binding_mix"
    assert config["dataset"]["dataset_dir"] == "artifacts/datasets/synthetic_v1_binding_mix"
    assert config["dataset"]["train_file"] == "artifacts/datasets/synthetic_v1_binding_mix/output/english_training_m1_binding_mix.jsonl"
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 1.0
    assert config["training"]["learning_rate"] == 5.0e-5
    assert config["training"]["per_device_train_batch_size"] == 2
    assert config["training"]["per_device_eval_batch_size"] == 2
    assert config["training"]["gradient_accumulation_steps"] == 8
    assert config["training"]["gradient_checkpointing"] is True


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


def test_pre_m2_wp1b_configs_match_except_for_condition_paths() -> None:
    original = load_training_config(Path("configs/training/pre_m2_wp1b_smollm2_1_7b_original.yaml"))
    swap = load_training_config(Path("configs/training/pre_m2_wp1b_smollm2_1_7b_swap.yaml"))
    assert original["dataset"]["train_file"].endswith("/original/train.jsonl")
    assert swap["dataset"]["train_file"].endswith("/swap/train.jsonl")
    assert original["training"]["output_root"].endswith("/original")
    assert swap["training"]["output_root"].endswith("/swap")
    for key in (
        "block_size",
        "learning_rate",
        "num_train_epochs",
        "per_device_train_batch_size",
        "per_device_eval_batch_size",
        "gradient_accumulation_steps",
        "warmup_ratio",
        "weight_decay",
        "lr_scheduler_type",
        "loss_mode",
        "supervise_eos",
        "bf16",
        "gradient_checkpointing",
        "max_grad_norm",
        "checkpoint_fractions",
        "save_total_limit",
        "seed",
        "data_seed",
    ):
        assert original["training"][key] == swap["training"][key]
    assert original["training"]["learning_rate"] == 1.0e-4
    assert original["training"]["num_train_epochs"] == 36.0
    assert original["training"]["supervise_eos"] is True


def test_pre_m2_wp5_lr_sweep_is_a_controlled_four_value_grid() -> None:
    labels = ("lr2e-5", "lr5e-5", "lr1e-4", "lr2e-4")
    configs = [
        load_training_config(Path(f"configs/training/pre_m2_wp5_{label}_eos_true.yaml"))
        for label in labels
    ]
    assert [config["training"]["learning_rate"] for config in configs] == [
        2.0e-5,
        5.0e-5,
        1.0e-4,
        2.0e-4,
    ]
    reference = configs[2]
    for config in configs:
        assert config["dataset"] == reference["dataset"]
        assert config["model"] == reference["model"]
        for key in (
            "block_size",
            "num_train_epochs",
            "per_device_train_batch_size",
            "per_device_eval_batch_size",
            "gradient_accumulation_steps",
            "warmup_ratio",
            "weight_decay",
            "lr_scheduler_type",
            "loss_mode",
            "supervise_eos",
            "bf16",
            "fp16",
            "gradient_checkpointing",
            "max_grad_norm",
            "logging_steps",
            "checkpoint_fractions",
            "save_total_limit",
            "seed",
            "data_seed",
        ):
            assert config["training"][key] == reference["training"][key]
        assert config["training"]["supervise_eos"] is True
        assert estimate_optimizer_steps(3500, 10, 50, 36.0) == 252


def test_pre_m2_wp5_eos_ablation_changes_only_final_eos_supervision() -> None:
    for label in ("lr5e-5", "lr1e-4"):
        eos_true = load_training_config(
            Path(f"configs/training/pre_m2_wp5_{label}_eos_true.yaml")
        )
        eos_false = load_training_config(
            Path(f"configs/training/pre_m2_wp5_{label}_eos_false.yaml")
        )
        assert eos_false["dataset"] == eos_true["dataset"]
        assert eos_false["model"] == eos_true["model"]
        assert eos_false["runtime"] == eos_true["runtime"]
        controlled_true = dict(eos_true["training"])
        controlled_false = dict(eos_false["training"])
        for key in ("run_name", "output_root", "supervise_eos"):
            controlled_true.pop(key)
            controlled_false.pop(key)
        assert controlled_false == controlled_true
        assert eos_true["training"]["supervise_eos"] is True
        assert eos_false["training"]["supervise_eos"] is False
        assert "/vol/tmp2/yesildau/" in eos_false["training"]["output_root"]


def test_pre_m2_wp5_seed43_replication_is_a_controlled_eos_pair() -> None:
    seed42 = load_training_config(Path("configs/training/pre_m2_wp5_lr5e-5_eos_false.yaml"))
    pair = [
        load_training_config(
            Path(f"configs/training/pre_m2_wp5_lr5e-5_eos_{value}_seed43_data43.yaml")
        )
        for value in ("true", "false")
    ]
    assert pair[0]["dataset"] == pair[1]["dataset"] == seed42["dataset"]
    assert pair[0]["model"] == pair[1]["model"] == seed42["model"]
    assert pair[0]["runtime"] == pair[1]["runtime"] == seed42["runtime"]
    for config, supervise_eos in zip(pair, (True, False), strict=True):
        controlled = dict(config["training"])
        baseline = dict(seed42["training"])
        for key in ("run_name", "output_root", "supervise_eos", "seed", "data_seed"):
            controlled.pop(key)
            baseline.pop(key)
        assert controlled == baseline
        assert config["training"]["supervise_eos"] is supervise_eos
        assert config["training"]["seed"] == 43
        assert config["training"]["data_seed"] == 43
        assert config["training"]["output_root"].startswith("/vol/tmp2/yesildau/")


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


def test_m1_smollm2_ranking_ep1_config_points_to_same_dataset_and_model() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_fact_ranking_lr2e-5_ep1.yaml"))
    assert config["dataset"]["version"] == "synthetic_v1_bio_qa"
    assert config["dataset"]["dataset_dir"] == "artifacts/datasets/synthetic_v1_bio_qa"
    assert config["dataset"]["include_direct_probes"] is True
    assert config["dataset"]["include_qa_train"] is True
    assert config["dataset"]["negatives_per_example"] == 7
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 1.0
    assert config["training"]["learning_rate"] == 2.0e-5


def test_m1_smollm2_ranking_lr1e5_ep2_config_points_to_same_dataset_and_model() -> None:
    config = load_training_config(Path("configs/training/m1_smollm2_360m_english_fact_ranking_lr1e-5_ep2.yaml"))
    assert config["dataset"]["version"] == "synthetic_v1_bio_qa"
    assert config["dataset"]["dataset_dir"] == "artifacts/datasets/synthetic_v1_bio_qa"
    assert config["dataset"]["include_direct_probes"] is True
    assert config["dataset"]["include_qa_train"] is True
    assert config["dataset"]["negatives_per_example"] == 7
    assert config["model"]["base_model_manifest"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
    assert config["training"]["num_train_epochs"] == 2.0
    assert config["training"]["learning_rate"] == 1.0e-5
