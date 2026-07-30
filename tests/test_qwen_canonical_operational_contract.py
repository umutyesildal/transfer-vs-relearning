from datetime import datetime, timezone
from pathlib import Path

from transfer_vs_relearning.training.operational import start_is_on_time


def test_training_start_cutoff_is_inclusive_and_timezone_aware() -> None:
    cutoff = datetime.fromisoformat("2026-07-31T19:30:00+02:00")
    assert start_is_on_time(cutoff=cutoff, now=cutoff)
    assert not start_is_on_time(
        cutoff=cutoff,
        now=datetime.fromisoformat("2026-07-31T19:30:01+02:00"),
    )


def test_training_launcher_requests_one_nonexclusive_a100_and_sixty_hours() -> None:
    launcher = Path("slurm/train_qwen_canonical_25000.slurm").read_text(encoding="utf-8")
    assert "#SBATCH --gres=gpu:a10080gb:1" in launcher
    assert "#SBATCH --time=2-12:00:00" in launcher
    assert "#SBATCH --nice" not in launcher
    assert "--exclusive" not in launcher
    assert "2026-07-31T19:30:00+02:00" in launcher
    assert "gpu_preflight=clean" in launcher


def test_training_preflight_requires_one_tib_and_frozen_smoke() -> None:
    preflight = Path("slurm/preflight_qwen_canonical_25000_training.slurm").read_text(encoding="utf-8")
    assert "1024 * 1024 * 1024 * 1024" in preflight
    assert "smoke/resume_rehearsal.json" in preflight
    assert "test ! -e \"${OUTPUT_ROOT}\"" in preflight
    assert "squeue -o" in preflight
    assert "sinfo -p gpu" in preflight
