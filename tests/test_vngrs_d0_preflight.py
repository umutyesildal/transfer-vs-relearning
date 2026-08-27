import json

import pytest

from transfer_vs_relearning.corpora.vngrs import d0_preflight
from transfer_vs_relearning.corpora.vngrs.d0_preflight import (
    EXPECTED_EVIDENCE,
    validate_d0_preflight,
    write_preflight_failure,
)


COMMIT = "a" * 40


def observation() -> dict:
    return {
        "git_commit": COMMIT,
        "clean_task_overlap": True,
        "accepted_evidence": EXPECTED_EVIDENCE,
        "source_registry_sha256": "b1c80bf78ff40de5c02e14f08082a51cc17cc90a9853028eaf866cb63326e41f",
        "hu_home_exact_bytes": 14_689_423_360,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": 0,
        "storage": {
            "resolved_parent": "/vol/tmp2/yesildau",
            "proposed_root_absent": True,
            "available_bytes": 122_943_170_412_544,
            "available_inodes": 2_284_282_885,
        },
    }


def test_exact_d0_preflight_passes_without_expanding_training_authority() -> None:
    result = validate_d0_preflight(observation(), expected_commit=COMMIT)
    assert result["status"] == "D0_PREFLIGHT_PASS"
    assert result["ready_to_train"] is False


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("clean_task_overlap", False, "dirty"),
        ("hu_home_exact_bytes", 30 * 1024**3, "home"),
        ("hu_home_writes_allowed", True, "read-only"),
        ("duplicate_active_jobs", 1, "duplicate"),
    ],
)
def test_d0_preflight_fails_closed(field, value, message) -> None:
    row = observation()
    row[field] = value
    with pytest.raises(ValueError, match=message):
        validate_d0_preflight(row, expected_commit=COMMIT)


def test_preflight_failure_is_atomic_terminal_evidence_and_refuses_overwrite(
    tmp_path, monkeypatch
) -> None:
    root = tmp_path / "vngrs_m2_three_model_d0_v1"
    monkeypatch.setattr(d0_preflight, "APPROVED_SCRATCH_PARENT", tmp_path)
    monkeypatch.setattr(d0_preflight, "OUTPUT_ROOT", root)
    monkeypatch.setenv("SLURM_JOB_ID", "12345")
    result = write_preflight_failure(expected_commit=COMMIT, error=TimeoutError("bounded stop"))
    persisted = json.loads((root / "control/preflight_failure.json").read_text())
    assert persisted == result
    assert result["status"] == "BLOCKED_OPERATIONAL_PREFLIGHT"
    assert result["network_requests"] == result["source_objects_written"] == 0
    assert result["automatic_retry_authorized"] is False
    assert not (root / "control/preflight_failure.json.partial").exists()
    with pytest.raises(FileExistsError):
        write_preflight_failure(expected_commit=COMMIT, error=RuntimeError("retry"))
