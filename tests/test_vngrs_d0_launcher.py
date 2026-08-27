from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_d0_launcher_is_exact_two_phase_and_has_no_training_or_cleanup_route() -> None:
    source = (ROOT / "scripts/corpora/run_vngrs_m2_d0.py").read_text(encoding="utf-8")
    assert 'choices=("phase1", "phase2")' in source
    assert "/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1" in source
    assert "ReviewedHttpsTransport" in source
    assert "FrozenTokenizerAdapter.load" in source
    assert "validate_d0_preflight" in source
    assert "train_clm" not in source
    assert '["scontrol", "update", f"JobId={job_id}"' in source
    assert "unlink(" not in source
    assert "rmtree" not in source
    preflight = (ROOT / "scripts/corpora/preflight_vngrs_m2_d0.py").read_text(encoding="utf-8")
    assert '"du", "-x", "-B1", "-s"' in preflight
    assert '"squeue", "-h"' in preflight
    assert "canonical_json_sha256(rows)" in preflight
    assert "validate_d0_preflight" in preflight
    phase1_submit = (ROOT / "scripts/corpora/submit_vngrs_m2_d0_phase1.sh").read_text()
    phase2_submit = (ROOT / "scripts/corpora/submit_vngrs_m2_d0_phase2.sh").read_text()
    assert 'afterok:${preflight_id}' in phase1_submit
    assert "--test-only" in phase1_submit and "--test-only" in phase2_submit
    assert "DECISIONS_JSONL" in phase2_submit


def test_phase1_v1a_keeps_preflight_in_memory_and_all_slurm_logs_off_filesystem() -> None:
    runner = (ROOT / "scripts/corpora/run_vngrs_m2_d0.py").read_text()
    submitter = (ROOT / "scripts/corpora/submit_vngrs_m2_d0_phase1_v1a.sh").read_text()
    slurm = (ROOT / "slurm/m2/materialize_vngrs_m2_d0_phase1_v1a.slurm").read_text()
    preflight = (ROOT / "src/transfer_vs_relearning/corpora/vngrs/d0_preflight.py").read_text()
    assert "collect_d0_preflight_observation(repo)" in runner
    assert "--collect-preflight" in slurm
    assert "--output=/dev/null --error=/dev/null" in submitter
    assert "PREFLIGHT_JSON" not in submitter + slurm
    assert 'job_id != current_job and name == "vngrs-m2-d0"' in preflight
    assert "write_text" not in preflight and "write_bytes" not in preflight


def test_phase1_v1b_extends_only_home_du_timeout_and_persists_scheduler_status() -> None:
    runner = (ROOT / "scripts/corpora/run_vngrs_m2_d0.py").read_text()
    preflight = (ROOT / "src/transfer_vs_relearning/corpora/vngrs/d0_preflight.py").read_text()
    assert '"du", "-x", "-B1", "-s", str(HOME_ROOT), timeout=300' in preflight
    assert 'D0_PHASE1_BLOCKED:' in runner
    assert "D0_PHASE1_AWAITING_HUMAN_REVIEW" in runner
    assert '["scontrol", "update"' in runner
    assert "timeout=15" in runner
    assert "except (OSError, subprocess.SubprocessError)" in runner
