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
