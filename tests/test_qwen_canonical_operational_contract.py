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
    assert "#SBATCH --cpus-per-task=8" in launcher
    # The gpu partition caps memory at 8000 MB per requested CPU. Sixty-four GiB would
    # silently raise MinCPUsNode to nine and prevent placement when exactly eight CPUs are free.
    assert "#SBATCH --mem=60G" in launcher
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
    assert "HOME_LIMIT_BYTES=30000000000" in preflight
    assert "training_home_large_before.txt" in preflight


def test_post_run_audit_uses_approved_home_limit_and_training_time_baseline() -> None:
    audit = Path("slurm/audit_qwen_canonical_25000.slurm").read_text(encoding="utf-8")
    assert "HOME_LIMIT_BYTES=30000000000" in audit
    assert "training_home_large_before.txt" in audit
    assert "training_home_large_after.txt" in audit


def test_smoke_does_not_create_canonical_output_before_gpu_guard_passes() -> None:
    launcher = Path("slurm/smoke_qwen_canonical_25000.slurm").read_text(encoding="utf-8")
    assert "#SBATCH --cpus-per-task=8" in launcher
    assert "#SBATCH --mem=60G" in launcher
    guard_passed = launcher.index("printf 'gpu_preflight=clean")
    canonical_absence_check = launcher.index('test ! -e "${SMOKE_ROOT}"')
    canonical_creation = launcher.index('mkdir -p "${SMOKE_ROOT}"')
    assert guard_passed < canonical_absence_check < canonical_creation
