from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_oscar_exact_blocks_recovery_4cpu_v1.yaml"
SLURM = ROOT / "slurm/m2/materialize_three_model_oscar_m2_blocks_recovery_4cpu.slurm"
SUBMIT = ROOT / "scripts/m2/submit_three_model_oscar_m2_blocks_recovery_4cpu.sh"


def test_relocation_preserves_scientific_recipe_and_changes_only_cpu_route() -> None:
    config = CONFIG.read_text(encoding="utf-8")
    for exact in (
        "required_state_at_relocation: PENDING",
        "required_reason_after_transaction_hold: JobHeldUser",
        "train_blocks: 97536",
        "train_tokens_per_arm: 49938432",
        "validation_blocks: 2048",
        "replacement_blocks: 976",
        "document_order_namespace: vngrs-m2-oscar-exact-blocks-v1",
        "cpus_per_task: 4",
        "memory: 128G",
        'time_limit: "06:00:00"',
        "gpu: false",
        "automatic_retry: false",
    ):
        assert exact in config


def test_relocation_is_pending_only_after_0300_and_uses_a_fresh_root() -> None:
    source = SUBMIT.read_text(encoding="utf-8")
    assert 'test "$(date +%H%M)" -ge 0300' in source
    assert 'test "$(squeue -h -j "$old_job" -o %T)" = PENDING' in source
    assert 'test "$(squeue -h -j "$old_job" -o %r)" = JobHeldUser' in source
    assert "vngrs_m2_oscar_exact_blocks_recovery_4cpu_v1" in source
    assert 'test ! -e "$output_root"' in source
    assert 'scancel "$old_job"' in source
    assert source.index("sbatch --test-only") < source.index('scancel "$old_job"')
    assert source.index('scancel "$old_job"') < source.index('job_id="$(sbatch --parsable')
    assert "relocated_from_cancelled_pending_job" in source


def test_relocation_launchers_are_valid_cpu_only_and_persistent() -> None:
    subprocess.run(["bash", "-n", str(SLURM)], check=True)
    subprocess.run(["bash", "-n", str(SUBMIT)], check=True)
    slurm = SLURM.read_text(encoding="utf-8")
    submit = SUBMIT.read_text(encoding="utf-8")
    assert "#SBATCH --cpus-per-task=4" in slurm
    assert "#SBATCH --mem=128G" in slurm
    assert "--gres=gpu" not in slurm
    assert "/usr/bin/time -v" in slurm
    assert "slurm_exit.json" in slurm
    assert "--output=/dev/null" in submit  # test-only only
    assert "slurm-%j.stdout.log" in submit
    assert "slurm-%j.stderr.log" in submit
