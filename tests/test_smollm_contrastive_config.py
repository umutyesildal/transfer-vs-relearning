from pathlib import Path

from transfer_vs_relearning.training.clm import estimate_optimizer_steps, load_training_config


def test_smollm_contrastive_contract_is_frozen() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_training_config(root / "configs/training/smollm_contrastive_binding_seed42.yaml")
    assert estimate_optimizer_steps(3500, 10, 50, 36.0) == 252
    assert config["contrastive"] == {
        "coefficient": 0.10,
        "negatives_per_example": 15,
        "canonical_profiles_file": "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv",
    }
