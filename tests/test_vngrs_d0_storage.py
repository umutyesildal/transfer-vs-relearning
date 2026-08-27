import pytest

from transfer_vs_relearning.corpora.vngrs.d0_storage import (
    D0StoragePolicy,
    GIB,
    validate_storage_observation,
)


def observation(*, available_bytes: int = 122_943_170_412_544, available_inodes: int = 2_284_282_885) -> dict:
    return {
        "resolved_parent": "/vol/tmp2/yesildau",
        "proposed_root_absent": True,
        "available_bytes": available_bytes,
        "available_inodes": available_inodes,
    }


def test_frozen_storage_formula_and_observation_pass() -> None:
    policy = D0StoragePolicy()
    assert policy.calculated_peak_bytes == 30_029_406_455
    assert policy.frozen_peak_bytes == 32 * GIB
    assert policy.required_available_bytes == 40 * GIB
    assert policy.required_available_inodes == 1_024
    result = validate_storage_observation(observation(), policy)
    assert result["status"] == "STORAGE_BOUNDS_PASS"
    assert result["fresh_execution_preflight_required"] is True


@pytest.mark.parametrize("mutation", ["bytes", "inodes", "root", "parent"])
def test_storage_gate_fails_closed_on_capacity_or_path_drift(mutation: str) -> None:
    value = observation()
    if mutation == "bytes":
        value["available_bytes"] = 40 * GIB - 1
    elif mutation == "inodes":
        value["available_inodes"] = 1_023
    elif mutation == "root":
        value["proposed_root_absent"] = False
    else:
        value["resolved_parent"] = "/tmp/yesildau"
    with pytest.raises(ValueError):
        validate_storage_observation(value)


def test_storage_policy_rejects_underprovisioned_frozen_peak() -> None:
    with pytest.raises(ValueError, match="does not cover"):
        validate_storage_observation(observation(), D0StoragePolicy(frozen_peak_bytes=27 * GIB))
