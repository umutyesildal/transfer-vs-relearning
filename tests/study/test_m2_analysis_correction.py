from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.study import m2_analysis_correction as module
from transfer_vs_relearning.utils.io import sha256_file


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/evaluation/m2_oscar_eval_v2_analysis_correction_v1.yaml"
CONTRACT = ROOT / "documentation/contracts/evaluation/vngrs-m2-oscar-eval-v2-analysis-correction-v1.md"


def test_correction_config_is_cpu_only_fresh_and_exactly_bound() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert config["status"] == "frozen_unexecuted"
    assert config["execution_authorized"] is False
    assert config["source_root"].endswith("m2_oscar_eval_v2_recovery_v1a")
    assert config["output_root"].endswith("m2_oscar_eval_v2_analysis_correction_v1")
    assert config["source_root"] != config["output_root"]
    assert config["analysis"] == {
        "direction": "tr_to_en",
        "pairing_key": "probe_id",
        "aggregation": "mean_all_matched_probes_within_subject",
        "prompt_variants_per_fact": 8,
        "subjects": 100,
        "bootstrap_samples": 10000,
        "bootstrap_seed": 42,
    }
    assert len(config["inputs"]) == 14
    assert all(len(row["sha256"]) == 64 and row["bytes"] > 0 for row in config["inputs"])
    assert config["expected_corrected_relearning"]["qwen"]["estimate"] == 0.0435
    assert sha256_file(CONTRACT) == "da2f3cb0251ae0bf9abc95e5663cb924988e77c1188dbdba4bc9c46066196b3f"
    contract = CONTRACT.read_text(encoding="utf-8")
    assert sha256_file(CONFIG) in contract
    assert sha256_file(ROOT / "src/transfer_vs_relearning/study/m2_analysis_correction.py") in contract
    assert sha256_file(ROOT / "slurm/m2/finalize_m2_oscar_eval_analysis_correction_v1.slurm") in contract


def test_corrected_expected_results_fail_closed() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    analysis = {
        "roles": {
            role: {
                "relearning_m2b_minus_m2a_tr_to_en": dict(values),
                "transfer_m2a_minus_m1_tr_to_en": dict(config["expected_corrected_transfer"][role]),
                "all_primary_gates_pass": False,
            }
            for role, values in config["expected_corrected_relearning"].items()
        }
    }
    module._check_expected_results(analysis, config)
    analysis["roles"]["qwen"]["relearning_m2b_minus_m2a_tr_to_en"]["estimate"] = 0.05
    with pytest.raises(ValueError, match="Corrected bootstrap result drift"):
        module._check_expected_results(analysis, config)


def test_launcher_has_no_gpu_model_or_retry_path() -> None:
    slurm = (ROOT / "slurm/m2/finalize_m2_oscar_eval_analysis_correction_v1.slurm").read_text()
    submit = (ROOT / "scripts/m2/submit_m2_oscar_eval_analysis_correction_v1.sh").read_text()
    combined = slurm + submit
    assert "#SBATCH --partition=std" in slurm
    assert "#SBATCH --cpus-per-task=4" in slurm
    assert "#SBATCH --mem=8G" in slurm
    assert "--gres" not in combined and "--array" not in combined
    assert "train" not in slurm.lower()
    assert "--test-only" in submit
    assert "exact_sha_bound_user_authorization_received" in combined
    assert "m2-analysis-correct-v1" in combined
    assert "automatic retry" not in combined.lower()
