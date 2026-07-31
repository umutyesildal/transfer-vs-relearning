from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Any, Iterable


REQUIRED_ARMS = ("m1", "m2_clean", "m3_fact")
CORE_DIMENSIONS: dict[str, tuple[str, ...]] = {
    "global": (),
    "direction": ("direction",),
    "relation": ("relation",),
    "form": ("form_id",),
    "scaffold": ("scaffold_id",),
    "branch": ("branch_group",),
    "frequency": ("frequency_bucket",),
    "name_type": ("name_type",),
    "name_rarity": ("name_rarity_bucket",),
    "popularity": ("popularity_bucket",),
    "direction_relation": ("direction", "relation"),
    "direction_branch": ("direction", "branch_group"),
    "direction_form": ("direction", "form_id"),
    "direction_scaffold": ("direction", "scaffold_id"),
    "relation_branch": ("relation", "branch_group"),
}
ROBUST_CELLS = {
    (form_id, scaffold_id)
    for form_id in ("form_a", "form_b", "form_c", "form_d")
    for scaffold_id in ("direct", "qa")
}
STATIC_FIELDS = (
    "subject_id",
    "fact_id",
    "direction",
    "relation",
    "form_id",
    "scaffold_id",
    "branch_group",
    "frequency_bucket",
    "name_type",
    "name_rarity_bucket",
    "popularity_bucket",
)


def _is_top1(row: dict[str, Any]) -> bool:
    return int(row["correct_rank_mean"]) == 1


def _percentile(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("Cannot compute a percentile of an empty sample")
    index = min(len(values) - 1, max(0, math.ceil(probability * len(values)) - 1))
    return values[index]


def bootstrap_mean_interval(
    values: Iterable[float],
    *,
    samples: int = 2000,
    seed: int = 20260717,
) -> tuple[float, float, float]:
    observed_values = [float(value) for value in values]
    if not observed_values:
        raise ValueError("Bootstrap input must be non-empty")
    if samples <= 0:
        raise ValueError("Bootstrap sample count must be positive")
    rng = random.Random(seed)
    estimates = [
        sum(observed_values[rng.randrange(len(observed_values))] for _ in observed_values)
        / len(observed_values)
        for _ in range(samples)
    ]
    estimates.sort()
    observed = sum(observed_values) / len(observed_values)
    return observed, _percentile(estimates, 0.025), _percentile(estimates, 0.975)


def bootstrap_independent_difference(
    first: Iterable[float],
    second: Iterable[float],
    *,
    samples: int = 2000,
    seed: int = 20260717,
) -> tuple[float, float, float]:
    first_values = [float(value) for value in first]
    second_values = [float(value) for value in second]
    if not first_values or not second_values:
        raise ValueError("Both independent bootstrap inputs must be non-empty")
    if samples <= 0:
        raise ValueError("Bootstrap sample count must be positive")
    observed = sum(first_values) / len(first_values) - sum(second_values) / len(second_values)
    rng = random.Random(seed)
    estimates = []
    for _ in range(samples):
        first_mean = sum(first_values[rng.randrange(len(first_values))] for _ in first_values) / len(first_values)
        second_mean = sum(second_values[rng.randrange(len(second_values))] for _ in second_values) / len(second_values)
        estimates.append(first_mean - second_mean)
    estimates.sort()
    return observed, _percentile(estimates, 0.025), _percentile(estimates, 0.975)


def validate_matched_state_rows(
    rows_by_state: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """Validate that every model state scored the same frozen probe registry."""
    if not rows_by_state:
        raise ValueError("At least one state is required")
    probe_maps: dict[str, dict[str, dict[str, Any]]] = {}
    for state_id, rows in sorted(rows_by_state.items()):
        if not rows:
            raise ValueError(f"State {state_id} has no evaluation rows")
        mapping: dict[str, dict[str, Any]] = {}
        for row in rows:
            probe_id = str(row.get("probe_id", "")).strip()
            if not probe_id:
                raise ValueError(f"State {state_id} contains a row without probe_id")
            if probe_id in mapping:
                raise ValueError(f"State {state_id} contains duplicate probe_id {probe_id}")
            missing = [field for field in STATIC_FIELDS if field not in row]
            if missing:
                raise ValueError(f"State {state_id}/{probe_id} is missing fields: {missing}")
            if "correct_rank_mean" not in row:
                raise ValueError(f"State {state_id}/{probe_id} is missing correct_rank_mean")
            mapping[probe_id] = row
        probe_maps[state_id] = mapping

    reference_state = next(iter(sorted(probe_maps)))
    reference_ids = set(probe_maps[reference_state])
    for state_id, mapping in sorted(probe_maps.items()):
        if set(mapping) != reference_ids:
            missing = sorted(reference_ids - set(mapping))[:5]
            extra = sorted(set(mapping) - reference_ids)[:5]
            raise ValueError(
                f"Probe registry mismatch for {state_id}: missing={missing}, extra={extra}"
            )
        for probe_id in sorted(reference_ids):
            reference = probe_maps[reference_state][probe_id]
            current = mapping[probe_id]
            mismatches = [
                field
                for field in STATIC_FIELDS
                if str(reference[field]) != str(current[field])
            ]
            if mismatches:
                raise ValueError(
                    f"Matched metadata mismatch for probe {probe_id} in {state_id}: {mismatches}"
                )
    return {
        "status": "passed",
        "state_count": len(probe_maps),
        "states": sorted(probe_maps),
        "probe_count_per_state": len(reference_ids),
        "unique_probe_count": len(reference_ids),
        "duplicate_probe_count": 0,
        "matched_static_fields": list(STATIC_FIELDS),
    }


def _dimension_key(row: dict[str, Any], dimension: str) -> str:
    fields = CORE_DIMENSIONS[dimension]
    return "|".join(str(row[field]) for field in fields) if fields else "ALL"


def _subject_metrics(
    rows: list[dict[str, Any]],
    *,
    dimension: str,
    key: str,
    branch: str | None = None,
) -> dict[str, float]:
    grouped: dict[str, list[bool]] = defaultdict(list)
    for row in rows:
        if _dimension_key(row, dimension) != key:
            continue
        if branch is not None and str(row["branch_group"]) != branch:
            continue
        grouped[str(row["subject_id"])].append(_is_top1(row))
    return {
        subject_id: sum(values) / len(values)
        for subject_id, values in sorted(grouped.items())
        if values
    }


def state_accuracy_rows(
    rows_by_state: dict[str, list[dict[str, Any]]],
    *,
    bootstrap_samples: int = 2000,
    seed: int = 20260717,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for state_index, (state_id, rows) in enumerate(sorted(rows_by_state.items())):
        for dimension_index, dimension in enumerate(CORE_DIMENSIONS):
            groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in rows:
                groups[_dimension_key(row, dimension)].append(row)
            for group_index, (key, group) in enumerate(sorted(groups.items())):
                subject_values = _subject_metrics(rows, dimension=dimension, key=key)
                subject_mean, ci_low, ci_high = bootstrap_mean_interval(
                    subject_values.values(),
                    samples=bootstrap_samples,
                    seed=seed + state_index * 100000 + dimension_index * 1000 + group_index,
                )
                output.append(
                    {
                        "state_id": state_id,
                        "dimension": dimension,
                        "key": key,
                        "n_probes": len(group),
                        "n_subjects": len(subject_values),
                        "top1": sum(_is_top1(row) for row in group),
                        "top1_accuracy": sum(_is_top1(row) for row in group) / len(group),
                        "subject_mean_accuracy": subject_mean,
                        "subject_bootstrap_ci_low": ci_low,
                        "subject_bootstrap_ci_high": ci_high,
                        "bootstrap_samples": bootstrap_samples,
                        "bootstrap_unit": "subject",
                    }
                )
    return output


def _paired_row(
    *,
    state_id: str,
    first_rows: list[dict[str, Any]],
    second_rows: list[dict[str, Any]],
    dimension: str,
    key: str,
    comparison: str,
    bootstrap_samples: int,
    seed: int,
) -> dict[str, Any] | None:
    first_values = _subject_metrics(first_rows, dimension=dimension, key=key)
    second_values = _subject_metrics(second_rows, dimension=dimension, key=key)
    common_subjects = sorted(set(first_values) & set(second_values))
    if not common_subjects:
        return None
    first = [first_values[subject_id] for subject_id in common_subjects]
    second = [second_values[subject_id] for subject_id in common_subjects]
    differences = [left - right for left, right in zip(first, second, strict=True)]
    observed, ci_low, ci_high = bootstrap_mean_interval(
        differences,
        samples=bootstrap_samples,
        seed=seed,
    )
    return {
        "state_id": state_id,
        "dimension": dimension,
        "key": key,
        "comparison": comparison,
        "first_accuracy": sum(first) / len(first),
        "second_accuracy": sum(second) / len(second),
        "difference_first_minus_second": observed,
        "bootstrap_ci_low": ci_low,
        "bootstrap_ci_high": ci_high,
        "n_subjects": len(common_subjects),
        "bootstrap_samples": bootstrap_samples,
        "bootstrap_unit": "subject",
    }


def paired_state_contrast_rows(
    rows_by_state: dict[str, list[dict[str, Any]]],
    state_metadata: dict[str, dict[str, Any]],
    *,
    bootstrap_samples: int = 2000,
    seed: int = 20260717,
) -> list[dict[str, Any]]:
    by_seed_arm: dict[tuple[str, str], str] = {}
    for state_id, metadata in state_metadata.items():
        seed_id = str(metadata["seed"])
        arm = str(metadata["arm"])
        key = (seed_id, arm)
        if key in by_seed_arm:
            raise ValueError(f"Duplicate state for seed={seed_id}, arm={arm}")
        by_seed_arm[key] = state_id
    output: list[dict[str, Any]] = []
    for seed_index, seed_id in enumerate(sorted({key[0] for key in by_seed_arm})):
        missing = [arm for arm in REQUIRED_ARMS if (seed_id, arm) not in by_seed_arm]
        if missing:
            raise ValueError(f"Seed {seed_id} is missing required arms: {missing}")
        arm_rows = {
            arm: rows_by_state[by_seed_arm[(seed_id, arm)]] for arm in REQUIRED_ARMS
        }
        comparisons = (
            ("m2_minus_m1", "m2_clean", "m1"),
            ("m3_minus_m1", "m3_fact", "m1"),
            ("m3_minus_m2", "m3_fact", "m2_clean"),
        )
        for dimension_index, dimension in enumerate(CORE_DIMENSIONS):
            keys = sorted(
                {
                    _dimension_key(row, dimension)
                    for row in arm_rows["m1"]
                }
            )
            for key_index, key in enumerate(keys):
                for comparison_index, (label, first_arm, second_arm) in enumerate(comparisons):
                    result = _paired_row(
                        state_id=f"seed_{seed_id}",
                        first_rows=arm_rows[first_arm],
                        second_rows=arm_rows[second_arm],
                        dimension=dimension,
                        key=key,
                        comparison=label,
                        bootstrap_samples=bootstrap_samples,
                        seed=seed
                        + seed_index * 100000
                        + dimension_index * 1000
                        + key_index * 10
                        + comparison_index,
                    )
                    if result is not None:
                        result.update({"seed": seed_id, "first_arm": first_arm, "second_arm": second_arm})
                        output.append(result)
    return output


def branch_interaction_rows(
    rows_by_state: dict[str, list[dict[str, Any]]],
    state_metadata: dict[str, dict[str, Any]],
    *,
    bootstrap_samples: int = 2000,
    seed: int = 20260717,
) -> list[dict[str, Any]]:
    by_seed_arm = {
        (str(metadata["seed"]), str(metadata["arm"])): state_id
        for state_id, metadata in state_metadata.items()
    }
    output: list[dict[str, Any]] = []
    interaction_dimensions = {
        name: fields
        for name, fields in CORE_DIMENSIONS.items()
        if name not in {"branch", "direction_branch", "relation_branch"}
    }
    for seed_index, seed_id in enumerate(sorted({key[0] for key in by_seed_arm})):
        required = [(seed_id, arm) for arm in REQUIRED_ARMS]
        if any(key not in by_seed_arm for key in required):
            continue
        m2_rows = rows_by_state[by_seed_arm[(seed_id, "m2_clean")]]
        m3_rows = rows_by_state[by_seed_arm[(seed_id, "m3_fact")]]
        for dimension_index, dimension in enumerate(interaction_dimensions):
            keys = sorted({_dimension_key(row, dimension) for row in m2_rows})
            for key_index, key in enumerate(keys):
                deltas_by_branch: dict[str, list[float]] = {}
                for branch in ("A", "B"):
                    m2 = _subject_metrics(m2_rows, dimension=dimension, key=key, branch=branch)
                    m3 = _subject_metrics(m3_rows, dimension=dimension, key=key, branch=branch)
                    common = sorted(set(m2) & set(m3))
                    if not common:
                        deltas_by_branch[branch] = []
                    else:
                        deltas_by_branch[branch] = [m3[item] - m2[item] for item in common]
                if not deltas_by_branch["A"] or not deltas_by_branch["B"]:
                    continue
                observed, ci_low, ci_high = bootstrap_independent_difference(
                    deltas_by_branch["B"],
                    deltas_by_branch["A"],
                    samples=bootstrap_samples,
                    seed=seed + seed_index * 100000 + dimension_index * 1000 + key_index,
                )
                output.append(
                    {
                        "seed": seed_id,
                        "dimension": dimension,
                        "key": key,
                        "contrast": "m3_minus_m2_branch_interaction",
                        "estimand": "(M3-M2)_B - (M3-M2)_A",
                        "branch_a_change": sum(deltas_by_branch["A"]) / len(deltas_by_branch["A"]),
                        "branch_b_change": sum(deltas_by_branch["B"]) / len(deltas_by_branch["B"]),
                        "difference_b_minus_a": observed,
                        "bootstrap_ci_low": ci_low,
                        "bootstrap_ci_high": ci_high,
                        "n_subjects_a": len(deltas_by_branch["A"]),
                        "n_subjects_b": len(deltas_by_branch["B"]),
                        "bootstrap_samples": bootstrap_samples,
                        "bootstrap_unit": "subject",
                    }
                )
    return output


def robust_unit_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return fact-level eight-cell robust correctness for one evaluation state."""
    grouped: dict[tuple[str, str, str], dict[tuple[str, str], dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        key = (str(row["direction"]), str(row["relation"]), str(row["fact_id"]))
        cell = (str(row["form_id"]), str(row["scaffold_id"]))
        if cell in grouped[key]:
            raise ValueError(f"Duplicate robust cell for {key}: {cell}")
        grouped[key][cell] = row
    output: list[dict[str, Any]] = []
    for (direction, relation, fact_id), cells in sorted(grouped.items()):
        if set(cells) != ROBUST_CELLS:
            raise ValueError(
                f"Incomplete robust cell set for {direction}/{relation}/{fact_id}: "
                f"expected={len(ROBUST_CELLS)} found={len(cells)}"
            )
        sample = next(iter(cells.values()))
        output.append(
            {
                "subject_id": str(sample["subject_id"]),
                "fact_id": fact_id,
                "direction": direction,
                "relation": relation,
                "branch_group": str(sample["branch_group"]),
                "robust": all(_is_top1(cell) for cell in cells.values()),
            }
        )
    return output


def robust_state_accuracy_rows(
    rows_by_state: dict[str, list[dict[str, Any]]],
    *,
    bootstrap_samples: int = 2000,
    seed: int = 20260717,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for state_index, (state_id, rows) in enumerate(sorted(rows_by_state.items())):
        robust_rows = robust_unit_rows(rows)
        for scope, key_fields in (
            ("direction_relation", ("direction", "relation")),
            ("direction_global", ("direction",)),
        ):
            by_subject: dict[str, list[bool]] = defaultdict(list)
            by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in robust_rows:
                key = "|".join(str(row[field]) for field in key_fields)
                by_key[key].append(row)
            for key_index, (key, group) in enumerate(sorted(by_key.items())):
                for row in group:
                    by_subject[str(row["subject_id"])].append(bool(row["robust"]))
                # For direction_relation there is one fact per subject; for direction_global
                # the five relation facts are averaged per subject below.
                subject_values = {
                    subject_id: sum(values) / len(values)
                    for subject_id, values in by_subject.items()
                    if values
                }
                mean, ci_low, ci_high = bootstrap_mean_interval(
                    subject_values.values(),
                    samples=bootstrap_samples,
                    seed=seed + state_index * 1000 + key_index,
                )
                output.append(
                    {
                        "state_id": state_id,
                        "scope": scope,
                        "key": key,
                        "n_facts": len(group),
                        "n_subjects": len(subject_values),
                        "all_cell_top1": sum(bool(row["robust"]) for row in group),
                        "all_cell_accuracy": sum(bool(row["robust"]) for row in group) / len(group),
                        "subject_mean_accuracy": mean,
                        "subject_bootstrap_ci_low": ci_low,
                        "subject_bootstrap_ci_high": ci_high,
                        "bootstrap_samples": bootstrap_samples,
                        "bootstrap_unit": "subject",
                    }
                )
                by_subject.clear()
    return output


def robust_paired_contrast_rows(
    rows_by_state: dict[str, list[dict[str, Any]]],
    state_metadata: dict[str, dict[str, Any]],
    *,
    bootstrap_samples: int = 2000,
    seed: int = 20260717,
) -> list[dict[str, Any]]:
    by_state_robust = {state_id: robust_unit_rows(rows) for state_id, rows in rows_by_state.items()}
    by_seed_arm = {
        (str(metadata["seed"]), str(metadata["arm"])): state_id
        for state_id, metadata in state_metadata.items()
    }
    output: list[dict[str, Any]] = []
    for seed_index, seed_id in enumerate(sorted({key[0] for key in by_seed_arm})):
        if any((seed_id, arm) not in by_seed_arm for arm in REQUIRED_ARMS):
            continue
        state_by_arm = {arm: by_seed_arm[(seed_id, arm)] for arm in REQUIRED_ARMS}
        by_arm_key: dict[str, dict[tuple[str, str, str], bool]] = {}
        for arm, state_id in state_by_arm.items():
            by_arm_key[arm] = {
                (str(row["direction"]), str(row["relation"]), str(row["fact_id"])): bool(row["robust"])
                for row in by_state_robust[state_id]
            }
        for scope, key_fields in (
            ("direction_relation", ("direction", "relation")),
            ("direction_global", ("direction",)),
        ):
            for key in sorted(
                {
                    "|".join(str(row[field]) for field in key_fields)
                    for row in by_state_robust[state_by_arm["m1"]]
                }
            ):
                comparisons = (("m2_minus_m1", "m2_clean", "m1"), ("m3_minus_m1", "m3_fact", "m1"), ("m3_minus_m2", "m3_fact", "m2_clean"))
                for comparison_index, (label, first_arm, second_arm) in enumerate(comparisons):
                    first_values: dict[str, float] = defaultdict(float)
                    second_values: dict[str, float] = defaultdict(float)
                    first_counts: dict[str, int] = defaultdict(int)
                    second_counts: dict[str, int] = defaultdict(int)
                    for identity, first_value in by_arm_key[first_arm].items():
                        identity_key = "|".join(identity[: len(key_fields)])
                        if identity_key != key:
                            continue
                        subject_id = identity[2].rsplit("_", 1)[0]
                        first_values[subject_id] += float(first_value)
                        first_counts[subject_id] += 1
                    for identity, second_value in by_arm_key[second_arm].items():
                        identity_key = "|".join(identity[: len(key_fields)])
                        if identity_key != key:
                            continue
                        subject_id = identity[2].rsplit("_", 1)[0]
                        second_values[subject_id] += float(second_value)
                        second_counts[subject_id] += 1
                    common = sorted(set(first_values) & set(second_values))
                    if not common:
                        continue
                    first = [first_values[item] / first_counts[item] for item in common]
                    second = [second_values[item] / second_counts[item] for item in common]
                    differences = [left - right for left, right in zip(first, second, strict=True)]
                    observed, ci_low, ci_high = bootstrap_mean_interval(
                        differences,
                        samples=bootstrap_samples,
                        seed=seed + seed_index * 100000 + comparison_index,
                    )
                    output.append(
                        {
                            "seed": seed_id,
                            "scope": scope,
                            "key": key,
                            "comparison": label,
                            "first_accuracy": sum(first) / len(first),
                            "second_accuracy": sum(second) / len(second),
                            "difference_first_minus_second": observed,
                            "bootstrap_ci_low": ci_low,
                            "bootstrap_ci_high": ci_high,
                            "n_subjects": len(common),
                            "bootstrap_samples": bootstrap_samples,
                            "bootstrap_unit": "subject",
                        }
                    )
    return output
