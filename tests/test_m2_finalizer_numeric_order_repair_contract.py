from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/training/m2_oscar_finalizer_numeric_order_repair_v1.yaml"
RUNNER = ROOT / "scripts/m2/run_m2_oscar_finalizer_numeric_order_repair_v1.py"
SUBMITTER = ROOT / "scripts/m2/submit_m2_oscar_finalizer_numeric_order_repair_v1.sh"
SLURM = ROOT / "slurm/m2/finalize_m2_oscar_numeric_order_repair_v1.slurm"


def test_numeric_order_repair_config_is_frozen_and_narrow() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert config["contract_id"] == "vngrs-m2-oscar-finalizer-numeric-order-repair-v1"
    assert config["status"] == "frozen_unexecuted"
    assert config["execution_authorized"] is False
    assert config["source"]["access"] == "read_only"
    assert config["repair"]["expected_updates"] == [76, 152, 229, 305, 381, 457, 533, 610, 686, 762]
    assert config["repair"]["run_count"] == 6
    assert config["repair"]["checkpoint_count"] == 60
    assert len(config["training_manifests"]) == 6
    assert len(config["task_audits"]) == 6
    assert config["output"]["root"].endswith("finalizer_numeric_order_repair_v1")
    assert config["authority"] == {
        "local_preparation_and_tests": True,
        "hu_ssh": False,
        "slurm": False,
        "gpu": False,
        "checkpoint_model_file_read_for_hash_only": True,
        "parent_model_read": False,
        "model_load_or_inference": False,
        "training": False,
        "evaluation_or_scoring": False,
        "cleanup_or_deletion": False,
        "automatic_retry": False,
    }


def test_runner_is_fail_closed_and_evaluation_disabled() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "Repository checkout is dirty" in text
    assert "Finalizer repair authority boundary drift" in text
    assert "Failed finalizer binding root is not present-and-empty" in text
    assert "Prior evaluation namespace unexpectedly exists" in text
    assert 'allowed = {"cache", "control", "logs", "tmp"}' in text
    assert "observed == expected" in text
    assert 'all(Path(value).is_dir() for value in observed)' in text
    assert '"M2_FINALIZER_NUMERIC_ORDER_REPAIR_PASS"' in text
    assert 'matrix_payload.get("evaluation_authorized") is False' in text
    assert 'matrix_payload.get("ready_to_evaluate") is False' in text


def test_submitter_and_slurm_are_single_cpu_wave() -> None:
    subprocess.run(["bash", "-n", str(SUBMITTER)], check=True)
    subprocess.run(["bash", "-n", str(SLURM)], check=True)
    submitter = SUBMITTER.read_text(encoding="utf-8")
    real_submits = [line for line in submitter.splitlines() if "sbatch" in line and "--test-only" not in line]
    assert len(real_submits) == 1
    assert "--parsable" in real_submits[0]
    assert "482232,482233" in submitter
    assert "checkpoint-*' | wc -l)\" -eq 60" in submitter
    slurm = SLURM.read_text(encoding="utf-8")
    assert "#SBATCH --partition=std" in slurm
    assert "#SBATCH --cpus-per-task=4" in slurm
    assert "#SBATCH --mem=16G" in slurm
    assert not re.search(r"#SBATCH --(?:gres|gpus?)", slurm)
    assert "run_m2_oscar_finalizer_numeric_order_repair_v1.py" in slurm
