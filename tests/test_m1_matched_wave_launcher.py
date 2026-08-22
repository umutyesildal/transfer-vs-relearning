from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_matched_wave_launcher_is_one_three_model_training_dag() -> None:
    submit = (ROOT / "scripts/m1/submit_m1_matched_wave.sh").read_text()
    assert "test ! -e \"$root\"" in submit
    assert "--array=0-2%3" in submit
    assert "afterok:${preflight_id}" in submit
    assert "afterany:${training_id}" in submit
    assert submit.count("sbatch --parsable") == 3
    assert "m1_matched_three_model_retry_v1" in submit


def test_matched_training_reuses_tracked_trainer_and_finalizes_outputs() -> None:
    runner = (ROOT / "scripts/m1/run_m1_matched_training.py").read_text()
    slurm = (ROOT / "slurm/m1/train_m1_matched_wave.slurm").read_text()
    assert "run_from_config" in runner
    assert "finalize_m1_training_outputs" in runner
    assert "#SBATCH --gres=gpu:a10080gb:1" in slurm
    assert "HF_HUB_OFFLINE=1" in slurm
    assert 'export PYTHONPATH="$PWD/src"' in slurm
    assert '--family-root "${FAMILY_ROOT}"' in slurm
    assert "--array" not in slurm
