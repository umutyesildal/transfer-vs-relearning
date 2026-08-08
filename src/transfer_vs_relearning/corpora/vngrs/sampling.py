"""Deterministic row-count-weighted sample allocation."""

from __future__ import annotations

from typing import Mapping


def largest_remainder_allocation(row_counts: Mapping[str, int], target: int) -> dict[str, int]:
    """Allocate a target proportionally, resolving integer remainders deterministically."""

    if not row_counts or target <= 0:
        raise ValueError("row_counts and target must be positive")
    if any(not isinstance(count, int) or count <= 0 for count in row_counts.values()):
        raise ValueError("row counts must be positive integers")
    total = sum(row_counts.values())
    if target > total:
        raise ValueError("target exceeds available rows")
    # Keep the quota arithmetic entirely integral.  Floating-point quotas can lose an exact tie
    # or round a large-count remainder differently across runtimes.
    scaled = {path: count * target for path, count in row_counts.items()}
    allocation = {path: value // total for path, value in scaled.items()}
    remaining = target - sum(allocation.values())
    order = sorted(row_counts, key=lambda path: (-(scaled[path] % total), path))
    for path in order[:remaining]:
        allocation[path] += 1
    if any(allocation[path] > row_counts[path] for path in allocation):
        raise AssertionError("largest-remainder allocation exceeded a shard row count")
    return allocation


def midpoint_systematic_positions(row_count: int, sample_count: int) -> tuple[int, ...]:
    if row_count <= 0 or sample_count <= 0 or sample_count > row_count:
        raise ValueError("sample_count must be positive and no greater than row_count")
    positions = tuple(int((rank + 0.5) * row_count / sample_count) for rank in range(sample_count))
    if len(set(positions)) != sample_count:
        raise AssertionError("systematic positions are not unique")
    return positions


def sampling_weights(row_counts: Mapping[str, int], allocation: Mapping[str, int]) -> dict[str, dict[str, float | int]]:
    if set(row_counts) != set(allocation):
        raise ValueError("row_counts and allocation keys differ")
    total_rows = sum(row_counts.values())
    total_sample = sum(allocation.values())
    if total_rows <= 0 or total_sample <= 0:
        raise ValueError("row counts and allocation must be positive")
    return {
        path: {
            "row_count": row_counts[path],
            "sample_count": allocation[path],
            "population_weight": row_counts[path] / total_rows,
            "sample_weight": allocation[path] / total_sample,
            "inverse_sampling_weight": (row_counts[path] / allocation[path]) if allocation[path] else None,
        }
        for path in sorted(row_counts)
    }
