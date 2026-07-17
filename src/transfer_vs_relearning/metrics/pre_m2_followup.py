from __future__ import annotations

import math
import hashlib
import json
import random
from collections import defaultdict
from typing import Any


def exact_mcnemar_pvalue(first_only: int, second_only: int) -> float:
    discordant = first_only + second_only
    if discordant == 0:
        return 1.0
    lower = min(first_only, second_only)
    tail = sum(math.comb(discordant, value) for value in range(lower + 1)) / (2**discordant)
    return min(1.0, 2.0 * tail)


def paired_bootstrap_accuracy_difference(
    first: list[bool],
    second: list[bool],
    *,
    samples: int = 2000,
    seed: int = 20260717,
) -> tuple[float, float, float]:
    if len(first) != len(second):
        raise ValueError("Paired bootstrap inputs must have equal length")
    if not first:
        raise ValueError("Paired bootstrap inputs must be non-empty")
    if samples <= 0:
        raise ValueError("Bootstrap sample count must be positive")
    observed = sum(int(value) for value in first) / len(first) - sum(int(value) for value in second) / len(second)
    rng = random.Random(seed)
    differences = []
    for _ in range(samples):
        indices = [rng.randrange(len(first)) for _ in range(len(first))]
        differences.append(
            sum(int(first[index]) - int(second[index]) for index in indices) / len(indices)
        )
    differences.sort()
    lower_index = max(0, int(0.025 * samples) - 1)
    upper_index = min(samples - 1, math.ceil(0.975 * samples) - 1)
    return observed, differences[lower_index], differences[upper_index]


def bootstrap_accuracy_interval(
    values: list[bool],
    *,
    samples: int = 2000,
    seed: int = 20260717,
) -> tuple[float, float, float]:
    if not values:
        raise ValueError("Bootstrap input must be non-empty")
    rng = random.Random(seed)
    estimates = []
    for _ in range(samples):
        estimates.append(sum(int(values[rng.randrange(len(values))]) for _ in values) / len(values))
    estimates.sort()
    lower_index = max(0, int(0.025 * samples) - 1)
    upper_index = min(samples - 1, math.ceil(0.975 * samples) - 1)
    observed = sum(values) / len(values)
    return observed, estimates[lower_index], estimates[upper_index]


def paired_form_comparisons(
    rows: list[dict[str, Any]],
    *,
    bootstrap_samples: int = 2000,
    seed: int = 20260717,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        key = (str(row["model_label"]), str(row["scaffold_id"]), str(row["fact_id"]))
        grouped[key][str(row["form_id"])] = row

    slices: dict[tuple[str, str, str], list[dict[str, dict[str, Any]]]] = defaultdict(list)
    for (model_label, scaffold_id, _), form_rows in grouped.items():
        if set(form_rows) != {"form_a", "form_b", "form_c"}:
            continue
        relation = str(form_rows["form_a"]["relation"])
        slices[(model_label, relation, scaffold_id)].append(form_rows)

    output: list[dict[str, Any]] = []
    for (model_label, relation, scaffold_id), facts in sorted(slices.items()):
        for pair_index, (first_id, second_id) in enumerate(
            (("form_a", "form_b"), ("form_a", "form_c"), ("form_b", "form_c"))
        ):
            first = [int(form_rows[first_id]["correct_rank_mean"]) == 1 for form_rows in facts]
            second = [int(form_rows[second_id]["correct_rank_mean"]) == 1 for form_rows in facts]
            difference, ci_low, ci_high = paired_bootstrap_accuracy_difference(
                first,
                second,
                samples=bootstrap_samples,
                seed=seed + pair_index,
            )
            first_only = sum(a and not b for a, b in zip(first, second, strict=True))
            second_only = sum(b and not a for a, b in zip(first, second, strict=True))
            output.append(
                {
                    "model_label": model_label,
                    "relation": relation,
                    "scaffold_id": scaffold_id,
                    "first_form": first_id,
                    "second_form": second_id,
                    "n": len(facts),
                    "first_top1": sum(first),
                    "second_top1": sum(second),
                    "accuracy_difference_first_minus_second": difference,
                    "paired_bootstrap_ci_low": ci_low,
                    "paired_bootstrap_ci_high": ci_high,
                    "first_only": first_only,
                    "second_only": second_only,
                    "mcnemar_exact_pvalue": exact_mcnemar_pvalue(first_only, second_only),
                    "bootstrap_samples": bootstrap_samples,
                }
            )
    return output


def token_likelihood_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    fields = (
        "model_label",
        "relation",
        "form_id",
        "scaffold_id",
        "candidate_role",
        "score_type",
        "eos_position",
    )
    for row in rows:
        groups[tuple(str(row.get(field, "")) for field in fields)].append(row)
    output = []
    for key, group in sorted(groups.items()):
        nll_values = [float(row["nll"]) for row in group]
        output.append(
            {
                **dict(zip(fields, key, strict=True)),
                "n": len(group),
                "mean_nll": sum(nll_values) / len(nll_values),
                "mean_token_ppl": sum(float(row["token_ppl"]) for row in group) / len(group),
                "min_nll": min(nll_values),
                "max_nll": max(nll_values),
            }
        )
    return output


def accuracy_slice_summary(
    rows: list[dict[str, Any]],
    *,
    bootstrap_samples: int = 2000,
    seed: int = 20260717,
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[bool]] = defaultdict(list)
    for row in rows:
        key = (
            str(row["model_label"]),
            str(row["relation"]),
            str(row["form_id"]),
            str(row["scaffold_id"]),
        )
        groups[key].append(int(row["correct_rank_mean"]) == 1)
    output = []
    for group_index, (key, values) in enumerate(sorted(groups.items())):
        accuracy, ci_low, ci_high = bootstrap_accuracy_interval(
            values,
            samples=bootstrap_samples,
            seed=seed + group_index,
        )
        output.append(
            {
                "model_label": key[0],
                "relation": key[1],
                "form_id": key[2],
                "scaffold_id": key[3],
                "n": len(values),
                "top1": sum(values),
                "top1_accuracy": accuracy,
                "bootstrap_ci_low": ci_low,
                "bootstrap_ci_high": ci_high,
                "bootstrap_samples": bootstrap_samples,
            }
        )
    return output


def robust_intersection_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_fact: dict[tuple[str, str, str], dict[tuple[str, str], bool]] = defaultdict(dict)
    for row in rows:
        key = (str(row["model_label"]), str(row["relation"]), str(row["fact_id"]))
        by_fact[key][(str(row["form_id"]), str(row["scaffold_id"]))] = int(row["correct_rank_mean"]) == 1
    by_slice: dict[tuple[str, str], list[dict[tuple[str, str], bool]]] = defaultdict(list)
    for (model_label, relation, _), cells in by_fact.items():
        if len(cells) == 6:
            by_slice[(model_label, relation)].append(cells)
            by_slice[(model_label, "ALL")].append(cells)
    output = []
    for (model_label, relation), facts in sorted(by_slice.items()):
        direct_all = sum(all(cells[(form_id, "direct")] for form_id in ("form_a", "form_b", "form_c")) for cells in facts)
        qa_all = sum(all(cells[(form_id, "qa")] for form_id in ("form_a", "form_b", "form_c")) for cells in facts)
        all_six = sum(all(cells.values()) for cells in facts)
        output.append(
            {
                "model_label": model_label,
                "relation": relation,
                "n": len(facts),
                "direct_all_form_intersection": direct_all,
                "qa_all_form_intersection": qa_all,
                "all_form_all_scaffold_intersection": all_six,
                "all_form_all_scaffold_accuracy": all_six / len(facts),
            }
        )
    return output


def repeatability_audit(
    reference_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    fields = (
        "probe_id",
        "correct_object_id",
        "predicted_object_id",
        "correct_rank_mean",
        "correct_mean_score",
        "best_incorrect_mean_score",
        "margin",
        "gold_mean_answer_nll",
        "gold_first_answer_token_nll",
        "gold_eos_after_prompt_nll",
        "gold_eos_preferred_to_first_answer",
        "failure_type",
    )
    candidate_by_probe = {str(row["probe_id"]): row for row in candidate_rows}
    comparisons = []
    for reference in reference_rows:
        probe_id = str(reference["probe_id"])
        candidate = candidate_by_probe.get(probe_id)
        if candidate is None:
            comparisons.append({"probe_id": probe_id, "status": "missing"})
            continue
        reference_payload = {field: str(reference.get(field, "")) for field in fields}
        candidate_payload = {field: str(candidate.get(field, "")) for field in fields}
        reference_hash = hashlib.sha256(json.dumps(reference_payload, sort_keys=True).encode("utf-8")).hexdigest()
        candidate_hash = hashlib.sha256(json.dumps(candidate_payload, sort_keys=True).encode("utf-8")).hexdigest()
        comparisons.append(
            {
                "probe_id": probe_id,
                "status": "matched" if reference_hash == candidate_hash else "mismatch",
                "reference_row_sha256": reference_hash,
                "candidate_row_sha256": candidate_hash,
            }
        )
    status_counts = defaultdict(int)
    for row in comparisons:
        status_counts[row["status"]] += 1
    return {
        "status": "passed" if status_counts["matched"] == len(comparisons) else "failed",
        "reference_rows": len(reference_rows),
        "status_counts": dict(sorted(status_counts.items())),
        "comparisons": comparisons,
    }
