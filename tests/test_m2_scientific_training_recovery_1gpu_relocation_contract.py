from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_one_gpu_relocation_preserves_science_and_changes_only_route() -> None:
    old = yaml.safe_load((ROOT / "configs/training/m2_oscar_scientific_training_recovery_v1.yaml").read_text())
    new = yaml.safe_load((ROOT / "configs/training/m2_oscar_scientific_training_recovery_1gpu_relocation_v1.yaml").read_text())
    assert new["inputs"] == old["inputs"]
    assert new["optimizer_smoke"] == old["optimizer_smoke"]
    assert new["training"] == old["training"]
    assert new["measurement"] == old["measurement"]
    assert new["storage"] == old["storage"]
    assert new["slurm"]["training"]["gres"] == "gpu:a10080gb:1"
    assert new["slurm"]["training"]["nodelist"] == "gruenau10"
    assert new["slurm"]["training"]["array"] == "0-5%1"
    assert new["gpu_selection"]["allocated_a100_count"] == 1
    assert new["gpu_selection"]["minimum_free_mib"] == 61440
    assert new["gpu_selection"]["maximum_used_mib"] == 20480


def test_one_gpu_relocation_dag_is_syntax_valid_and_single_wave() -> None:
    paths = [
        ROOT / "scripts/m2/submit_three_model_oscar_m2_scientific_training_recovery_1gpu_relocation_v1.sh",
        ROOT / "slurm/m2/preflight_three_model_oscar_m2_training_recovery_1gpu_relocation_v1.slurm",
        ROOT / "slurm/m2/train_three_model_oscar_m2_recovery_1gpu_relocation_v1.slurm",
        ROOT / "slurm/m2/finalize_three_model_oscar_m2_training_recovery_1gpu_relocation_v1.slurm",
    ]
    for path in paths:
        subprocess.run(["bash", "-n", str(path)], check=True)
    submit = paths[0].read_text()
    train = paths[2].read_text()
    assert "482225,482226" in submit
    assert submit.count("sbatch --parsable") == 3
    assert "#SBATCH --nodelist=gruenau10" in train
    assert "#SBATCH --gres=gpu:a10080gb:1" in train
    assert "--expected-device-count 1" in train
    assert "trap on_exit EXIT" in train
