from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_oscar_exact_blocks_adapter_repair_v1.yaml"
SLURM = ROOT / "slurm/m2/materialize_three_model_oscar_m2_blocks_adapter_repair.slurm"
SUBMIT = ROOT / "scripts/m2/submit_three_model_oscar_m2_blocks_adapter_repair.sh"
STREAMING = ROOT / "src/transfer_vs_relearning/pipeline/m2_block_streaming.py"


def test_repair_preserves_recipe_and_changes_only_adapter_and_cpu_route() -> None:
    config = CONFIG.read_text(encoding="utf-8")
    for exact in (
        "train_blocks: 97536",
        "train_tokens_per_arm: 49938432",
        "validation_blocks: 2048",
        "replacement_blocks: 976",
        "document_order_namespace: vngrs-m2-oscar-exact-blocks-v1",
        "cpus_per_task: 4",
        "memory: 64G",
        'time_limit: "06:00:00"',
        "gpu: false",
        "automatic_retry: false",
    ):
        assert exact in config
    streaming = STREAMING.read_text(encoding="utf-8")
    assert "def _eos_token_id(" in streaming
    assert 'getattr(getattr(tokenizer, "tokenizer", None), "eos_token_id", None)' in streaming


def test_submitter_preserves_terminal_failure_and_requires_fresh_root() -> None:
    source = SUBMIT.read_text(encoding="utf-8")
    assert 'test -z "$(squeue -h -j "$failed_job")"' in source
    assert "1ce489502583f900a039e1776e67d4d2992d945405d49cfac3bf385a93c799d7" in source
    assert "0e48d7e87d46078a5b8acc91e4e55a349dda2b1ecc0b1578a8d1df5e420de821" in source
    assert "vngrs_m2_oscar_exact_blocks_adapter_repair_v1" in source
    assert 'test ! -e "$output_root"' in source
    assert "scancel" not in source
    assert "scontrol" not in source
    assert source.count('job_id="$(sbatch --parsable') == 1


def test_launchers_are_valid_cpu_only_and_fail_persistent() -> None:
    subprocess.run(["bash", "-n", str(SLURM)], check=True)
    subprocess.run(["bash", "-n", str(SUBMIT)], check=True)
    slurm = SLURM.read_text(encoding="utf-8")
    submit = SUBMIT.read_text(encoding="utf-8")
    assert "#SBATCH --cpus-per-task=4" in slurm
    assert "#SBATCH --mem=64G" in slurm
    assert "--gres=gpu" not in slurm
    assert "/usr/bin/time -v" in slurm
    assert "slurm_exit.json" in slurm
    assert "--output=/dev/null" in submit
    assert "slurm-%j.stdout.log" in submit
    assert "slurm-%j.stderr.log" in submit
