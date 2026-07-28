from pathlib import Path

from transfer_vs_relearning.training.clm import estimate_optimizer_steps, load_training_config


def test_qwen_scale_probe_preserves_historical_252_update_scale_contract() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_training_config(root / "configs/training/qwen_scale_probe_replay_w0_5_seed42.yaml")
    assert config["training"]["per_device_train_batch_size"] == 50
    assert config["training"]["gradient_accumulation_steps"] == 50
    assert config["training"]["num_train_epochs"] == 36.0
    assert estimate_optimizer_steps(17500, 50, 50, 36.0) == 252
    assert config["retention"]["coefficient"] == 0.5


def test_qwen_scale_seed43_changes_only_training_order_and_output_identity() -> None:
    root = Path(__file__).resolve().parents[1]
    seed42 = load_training_config(root / "configs/training/qwen_scale_probe_replay_w0_5_seed42.yaml")
    seed43 = load_training_config(root / "configs/training/qwen_scale_probe_replay_w0_5_seed43.yaml")
    assert seed43["dataset"] == seed42["dataset"]
    assert seed43["model"] == seed42["model"]
    assert seed43["retention"] == seed42["retention"]
    assert {key: value for key, value in seed43["training"].items() if key not in {"run_name", "output_root", "seed", "data_seed"}} == {key: value for key, value in seed42["training"].items() if key not in {"run_name", "output_root", "seed", "data_seed"}}
    assert seed43["training"]["seed"] == seed43["training"]["data_seed"] == 43
