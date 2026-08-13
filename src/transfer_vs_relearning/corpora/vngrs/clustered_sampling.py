"""Frozen stratified clustered-window design for bounded vngrs calibration."""

from __future__ import annotations

import hashlib
from fractions import Fraction
from typing import Any, Iterable, Mapping

from .metadata import FROZEN_SELECTED_SHARD_PATHS, canonical_json_sha256
from .sampling import largest_remainder_allocation


CLUSTERED_SAMPLE_CONTRACT_SHA256 = "a52b445c7b588e371df9876d7b4f65af5bef4f3b0531e89576c5af6ae38101d6"
SCHEDULE_VERSION = "vngrs_stratified_clustered_windows_32x4_v1"
SEED = 42
TARGET_RECORDS = 10_000
STRATA_PER_SHARD = 4
WINDOW_COUNT = 128
MAX_ROWS_PER_WINDOW = 79


def _stratum_bounds(row_count: int, stratum: int) -> tuple[int, int]:
    if row_count <= 0 or not 0 <= stratum < STRATA_PER_SHARD:
        raise ValueError("invalid row count or stratum")
    return row_count * stratum // STRATA_PER_SHARD, row_count * (stratum + 1) // STRATA_PER_SHARD


def _window_lengths(sample_count: int) -> tuple[int, ...]:
    if sample_count < STRATA_PER_SHARD:
        raise ValueError("each shard requires at least one row per stratum")
    base, extra = divmod(sample_count, STRATA_PER_SHARD)
    lengths = tuple(base + (index < extra) for index in range(STRATA_PER_SHARD))
    if max(lengths) > MAX_ROWS_PER_WINDOW:
        raise ValueError("cluster length exceeds the frozen 79-row bound")
    return lengths


def _deterministic_start(path: str, stratum: int, lower: int, upper: int, length: int) -> int:
    valid_starts = upper - lower - length + 1
    if valid_starts <= 0:
        raise ValueError("cluster does not fit within its stratum")
    material = f"{SCHEDULE_VERSION}|{SEED}|{path}|{stratum}".encode("utf-8")
    return lower + int.from_bytes(hashlib.sha256(material).digest(), "big") % valid_starts


def inclusion_probability(*, row_index: int, lower: int, upper: int, length: int) -> Fraction:
    """Exact probability that a uniformly selected valid window contains ``row_index``."""

    if not lower <= row_index < upper or length <= 0 or length > upper - lower:
        raise ValueError("row/window is outside the stratum")
    last_start = upper - length
    minimum_covering_start = max(lower, row_index - length + 1)
    maximum_covering_start = min(row_index, last_start)
    covering = maximum_covering_start - minimum_covering_start + 1
    valid_starts = last_start - lower + 1
    if covering <= 0:
        raise AssertionError("sampled row has zero inclusion probability")
    return Fraction(covering, valid_starts)


def _build(shard_rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [dict(row) for row in shard_rows]
    if len(rows) != 32 or [row.get("path") for row in rows] != list(FROZEN_SELECTED_SHARD_PATHS):
        raise ValueError("exact frozen 32-shard order is required")
    row_counts = {str(row["path"]): int(row["row_count"]) for row in rows}
    allocation = largest_remainder_allocation(row_counts, TARGET_RECORDS)
    windows: list[dict[str, Any]] = []
    sample_index = 0
    for row in rows:
        path = str(row["path"])
        row_count = int(row["row_count"])
        lengths = _window_lengths(allocation[path])
        for stratum, length in enumerate(lengths):
            lower, upper = _stratum_bounds(row_count, stratum)
            start = _deterministic_start(path, stratum, lower, upper, length)
            sampled_rows = []
            for row_index in range(start, start + length):
                probability = inclusion_probability(
                    row_index=row_index, lower=lower, upper=upper, length=length
                )
                sampled_rows.append(
                    {
                        "sample_index": sample_index,
                        "row_index": row_index,
                        "inclusion_probability_numerator": probability.numerator,
                        "inclusion_probability_denominator": probability.denominator,
                        "inverse_inclusion_weight_numerator": probability.denominator,
                        "inverse_inclusion_weight_denominator": probability.numerator,
                    }
                )
                sample_index += 1
            windows.append(
                {
                    "request_index": len(windows),
                    "path": path,
                    "ordinal": int(row["ordinal"]),
                    "stratum": stratum,
                    "stratum_start": lower,
                    "stratum_end_exclusive": upper,
                    "start": start,
                    "length": length,
                    "valid_start_count": upper - lower - length + 1,
                    "sampled_rows": sampled_rows,
                }
            )
    schedule = {
        "schedule_version": SCHEDULE_VERSION,
        "contract_sha256": CLUSTERED_SAMPLE_CONTRACT_SHA256,
        "seed": SEED,
        "target_records": TARGET_RECORDS,
        "selected_shards": 32,
        "strata_per_shard": STRATA_PER_SHARD,
        "window_count": len(windows),
        "maximum_rows_per_window": MAX_ROWS_PER_WINDOW,
        "shard_allocation": allocation,
        "windows": windows,
        "estimand": "selected_32_shards_stratified_clustered_window_ht_rate",
        "uncertainty": {
            "method": "cluster_bootstrap_windows",
            "replicates": 2_000,
            "seed": 42,
            "design_unbiased_ci_claim": False,
        },
    }
    schedule["schedule_sha256"] = canonical_json_sha256(schedule)
    return schedule


def build_clustered_schedule(shard_rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    return _build(shard_rows)


def validate_clustered_schedule(
    schedule: Mapping[str, Any], shard_rows: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    expected = _build(shard_rows)
    errors: list[str] = []
    if dict(schedule) != expected:
        errors.append("clustered schedule differs from exact recomputation")
    windows = schedule.get("windows")
    if not isinstance(windows, list) or len(windows) != WINDOW_COUNT:
        errors.append("schedule must contain exactly 128 windows")
        windows = []
    sampled = [row for window in windows for row in window.get("sampled_rows", [])]
    if len(sampled) != TARGET_RECORDS:
        errors.append("schedule must contain exactly 10,000 sampled rows")
    if [row.get("sample_index") for row in sampled] != list(range(TARGET_RECORDS)):
        errors.append("sample indices are not the exact contiguous 0..9,999 set")
    return {
        "complete": not errors,
        "errors": errors,
        "window_count": len(windows),
        "sample_count": len(sampled),
        "schedule_sha256": expected["schedule_sha256"],
    }
