from __future__ import annotations

from pathlib import Path
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/training/m2_oscar_scientific_training_v1.yaml"
PREPARATION = ROOT / "configs/training/m2_three_model_oscar_training_preparation_v4.yaml"


def test_scientific_training_contract_freezes_six_matched_runs_and_measurements() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    preparation = yaml.safe_load(PREPARATION.read_text(encoding="utf-8"))
    assert config["status"] == "frozen_unexecuted"
    assert config["execution_authorized"] is False
    assert config["training"]["models"] == ["olmo", "qwen", "smollm"]
    assert config["training"]["arms"] == ["M2-A", "M2-B"]
    assert config["training"]["run_count"] == 6
    assert config["training"]["optimizer_updates"] == 762
    assert config["training"]["microbatch_blocks"] * config["training"]["gradient_accumulation_steps"] == 128
    assert config["training"]["checkpoint_updates"] == [76, 152, 229, 305, 381, 457, 533, 610, 686, 762]
    assert config["measurement"]["dense_updates"] == config["training"]["checkpoint_updates"]
    assert config["measurement"]["full_updates"] == [381, 762]
    assert config["measurement"]["pile_10k"] == "retired_forbidden"
    assert config["measurement"]["evaluation_execution"] == "separately_hash_bound_after_training_outputs_exist"
    assert config["slurm"]["training"]["array"] == "0-5%3"
    assert config["slurm"]["automatic_retry"] is False
    assert config["storage"]["minimum_free_bytes"] == 386596220128
    assert preparation["inputs"]["corrected_block_manifest_sha256"] == config["inputs"]["corrected_block_manifest"]["sha256"]
    assert preparation["output"]["family_root"] == config["slurm"]["root"]


def test_scientific_training_dag_is_syntax_valid_and_reuses_exact_smoke_evidence() -> None:
    paths = [
        ROOT / "scripts/m2/submit_three_model_oscar_m2_scientific_training_v1.sh",
        ROOT / "slurm/m2/preflight_three_model_oscar_m2_training_v1.slurm",
        ROOT / "slurm/m2/train_three_model_oscar_m2_v1.slurm",
        ROOT / "slurm/m2/finalize_three_model_oscar_m2_training_v1.slurm",
    ]
    for path in paths:
        subprocess.run(["bash", "-n", str(path)], check=True)
    submit = paths[0].read_text(encoding="utf-8")
    train = paths[2].read_text(encoding="utf-8")
    finalizer = paths[3].read_text(encoding="utf-8")
    assert "M2_TRAINING_AUTHORIZATION_ACK" in submit
    assert "EXPECTED_CONTRACT_SHA256" in submit
    assert "--test-only" in submit
    assert "afterok:${preflight_id}" in submit
    assert "afterok:${train_id}" in submit
    assert "#SBATCH --array=0-5%3" in train
    assert "vnd_m2_oscar_optimizer_smoke_corrected_v1/roles/$role/smoke_report.json" in train
    assert "smoke_three_model" not in submit
    assert "retry" not in submit.lower()
    assert "prepare_m2_oscar_eval_v2_matrix.py" in finalizer
    assert "eval_v2_matrix.json" in finalizer


def test_preflight_checks_corrected_review_blocks_smokes_storage_and_fresh_config_generation() -> None:
    source = (ROOT / "scripts/m2/preflight_three_model_oscar_m2_training_v1.py").read_text(encoding="utf-8")
    for required in (
        "M2_FACT_REVIEW_PASS",
        "EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED",
        "EXACT_M1_PARENT_REGISTRY_PASS",
        "OPTIMIZER_SMOKE_PASS",
        "minimum_free_bytes",
        "prepare_three_model_oscar_m2_training_family.py",
        "validate_three_model_oscar_m2_training_family.py",
    ):
        assert required in source
