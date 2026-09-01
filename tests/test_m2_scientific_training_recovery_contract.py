from __future__ import annotations

from pathlib import Path
import subprocess

import yaml

from scripts.m2.select_allocated_gpu_for_m2_training_recovery_v1 import choose_gpu


ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / "configs/training/m2_oscar_scientific_training_recovery_v1.yaml"
ORIGINAL = ROOT / "configs/training/m2_oscar_scientific_training_v1.yaml"


def test_recovery_changes_only_operational_gpu_routing_and_fresh_root() -> None:
    recovery = yaml.safe_load(RECOVERY.read_text(encoding="utf-8"))
    original = yaml.safe_load(ORIGINAL.read_text(encoding="utf-8"))
    assert recovery["status"] == "frozen_unexecuted"
    assert recovery["execution_authorized"] is False
    assert recovery["training"] | {"max_parallel_tasks": original["training"]["max_parallel_tasks"]} == original["training"]
    assert recovery["measurement"] == original["measurement"]
    assert recovery["inputs"] == original["inputs"]
    assert recovery["optimizer_smoke"] == original["optimizer_smoke"]
    assert recovery["storage"] == original["storage"]
    assert recovery["slurm"]["root"] != original["slurm"]["root"]
    assert recovery["slurm"]["training"]["gres"] == "gpu:a10080gb:3"
    assert recovery["slurm"]["training"]["array"] == "0-5%1"
    assert recovery["gpu_selection"] == {
        "allocated_a100_count": 3,
        "selected_training_gpu_count": 1,
        "minimum_free_mib": 61440,
        "maximum_used_mib": 20480,
        "zero_process_required": False,
        "full_allocated_gpu_process_ledger_required": True,
        "deterministic_rule": "highest_free_mib_then_lexicographic_uuid",
        "atomic_pass_and_failure_audit_required": True,
    }


def test_gpu_choice_is_bounded_and_deterministic() -> None:
    rows = [
        {"uuid": "GPU-b", "memory_free_mib": 70000, "memory_used_mib": 11000},
        {"uuid": "GPU-a", "memory_free_mib": 78338, "memory_used_mib": 2815},
        {"uuid": "GPU-c", "memory_free_mib": 55995, "memory_used_mib": 25158},
    ]
    assert choose_gpu(rows, 61440, 20480) == rows[1]
    assert choose_gpu(rows, 79000, 20480) is None
    tied = [
        {"uuid": "GPU-z", "memory_free_mib": 70000, "memory_used_mib": 1},
        {"uuid": "GPU-a", "memory_free_mib": 70000, "memory_used_mib": 2},
    ]
    assert choose_gpu(tied, 61440, 20480) == tied[1]


def test_recovery_dag_is_syntax_valid_persistent_and_single_wave() -> None:
    paths = [
        ROOT / "scripts/m2/submit_three_model_oscar_m2_scientific_training_recovery_v1.sh",
        ROOT / "slurm/m2/preflight_three_model_oscar_m2_training_recovery_v1.slurm",
        ROOT / "slurm/m2/train_three_model_oscar_m2_recovery_v1.slurm",
        ROOT / "slurm/m2/finalize_three_model_oscar_m2_training_recovery_v1.slurm",
    ]
    for path in paths:
        subprocess.run(["bash", "-n", str(path)], check=True)
    submit = paths[0].read_text(encoding="utf-8")
    train = paths[2].read_text(encoding="utf-8")
    assert "dead_job=482208" in submit
    assert "DependencyNeverSatisfied" in submit
    assert 'scancel "$dead_job"' in submit
    assert submit.count("sbatch --parsable") == 3
    assert "#SBATCH --gres=gpu:a10080gb:3" in train
    assert "#SBATCH --array=0-5%1" in train
    assert "select_allocated_gpu_for_m2_training_recovery_v1.py" in train
    assert "record_m2_training_task_audit_v1.py" in train
    assert "trap on_exit EXIT" in train
    assert "--minimum-free-mib 61440" in train
    assert "--maximum-used-mib 20480" in train
