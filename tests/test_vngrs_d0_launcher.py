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
    assert "subprocess" not in source
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
