import pytest

from transfer_vs_relearning.corpora.vngrs.d0_preflight import EXPECTED_EVIDENCE, validate_d0_preflight


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
