from __future__ import annotations

from fractions import Fraction

from transfer_vs_relearning.corpora.vngrs.clustered_sampling import (
    CLUSTERED_SAMPLE_CONTRACT_SHA256,
    inclusion_probability,
    build_clustered_schedule,
    validate_clustered_schedule,
)
from transfer_vs_relearning.corpora.vngrs.metadata import FROZEN_SELECTED_SHARD_PATHS


def shard_rows() -> list[dict[str, object]]:
    return [
        {"path": path, "ordinal": ordinal, "row_count": 177_241 - (ordinal % 2)}
        for ordinal, path in enumerate(FROZEN_SELECTED_SHARD_PATHS)
    ]


def test_clustered_schedule_is_exact_bounded_and_deterministic() -> None:
    first = build_clustered_schedule(shard_rows())
    second = build_clustered_schedule(shard_rows())
    assert first == second
    assert first["contract_sha256"] == CLUSTERED_SAMPLE_CONTRACT_SHA256
    assert first["window_count"] == 128
    assert sum(window["length"] for window in first["windows"]) == 10_000
    assert {window["length"] for window in first["windows"]} == {78, 79}
    assert max(window["length"] for window in first["windows"]) == 79
    assert [window["request_index"] for window in first["windows"]] == list(range(128))
    assert validate_clustered_schedule(first, shard_rows())["complete"] is True
    for window in first["windows"]:
        assert window["stratum_start"] <= window["start"]
        assert window["start"] + window["length"] <= window["stratum_end_exclusive"]


def test_inclusion_probability_is_exact_and_edge_aware() -> None:
    assert inclusion_probability(row_index=0, lower=0, upper=100, length=10) == Fraction(1, 91)
    assert inclusion_probability(row_index=9, lower=0, upper=100, length=10) == Fraction(10, 91)
    assert inclusion_probability(row_index=50, lower=0, upper=100, length=10) == Fraction(10, 91)
    assert inclusion_probability(row_index=99, lower=0, upper=100, length=10) == Fraction(1, 91)


def test_clustered_schedule_validator_rejects_tampering() -> None:
    schedule = build_clustered_schedule(shard_rows())
    schedule["windows"][0]["start"] += 1
    result = validate_clustered_schedule(schedule, shard_rows())
    assert result["complete"] is False
    assert "differs from exact recomputation" in result["errors"][0]
