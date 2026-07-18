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


def answer_sequence_likelihood_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sequences: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        sequences[(str(row["model_label"]), str(row["probe_id"]), str(row["candidate_role"]))].append(row)
    groups: dict[tuple[str, ...], list[dict[str, float]]] = defaultdict(list)
    fields = ("model_label", "relation", "form_id", "scaffold_id", "candidate_role")
    for sequence_rows in sequences.values():
        answer_rows = [row for row in sequence_rows if row["score_type"] == "answer_token"]
        if not answer_rows:
            continue
        first_answer = min(answer_rows, key=lambda row: int(row["answer_position"]))
        final_position = max(int(row["answer_position"]) for row in answer_rows)
        prompt_eos = next(row for row in sequence_rows if row.get("eos_position") == "after_prompt")
        final_eos = next(
            row for row in sequence_rows if row.get("eos_position") == f"after_answer_{final_position}"
        )
        key = tuple(str(first_answer[field]) for field in fields)
        groups[key].append(
            {
                "first_answer_nll": float(first_answer["nll"]),
                "mean_answer_nll": sum(float(row["nll"]) for row in answer_rows) / len(answer_rows),
                "prompt_eos_nll": float(prompt_eos["nll"]),
                "final_eos_nll": float(final_eos["nll"]),
                "answer_token_count": float(len(answer_rows)),
            }
        )
    output = []
    for key, group in sorted(groups.items()):
        output.append(
            {
                **dict(zip(fields, key, strict=True)),
                "n": len(group),
                "mean_first_answer_nll": sum(row["first_answer_nll"] for row in group) / len(group),
                "mean_answer_nll": sum(row["mean_answer_nll"] for row in group) / len(group),
                "mean_prompt_eos_nll": sum(row["prompt_eos_nll"] for row in group) / len(group),
                "mean_final_eos_nll": sum(row["final_eos_nll"] for row in group) / len(group),
                "mean_answer_token_count": sum(row["answer_token_count"] for row in group) / len(group),
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


def wp1b_counterbalance_analysis(
    rows_by_condition: dict[str, list[dict[str, Any]]],
    assignments_by_condition: dict[str, list[dict[str, Any]]],
    *,
    bootstrap_samples: int = 2000,
    seed: int = 20260717,
) -> dict[str, list[dict[str, Any]]]:
    annotated: list[dict[str, Any]] = []
    for condition, rows in sorted(rows_by_condition.items()):
        assignments = {
            str(item["subject_id"]): item for item in assignments_by_condition[condition]
        }
        for row in rows:
            assignment = assignments[str(row["subject_id"])]
            form_id = str(row["form_id"])
            cell = (
                "seen"
                if form_id == assignment["training_form_id"]
                else "crossed"
                if form_id == assignment["heldout_crossed_form_id"]
                else "novel"
            )
            annotated.append(
                {
                    **row,
                    "condition": condition,
                    "training_form_group": assignment["training_form_group"],
                    "training_form_id": assignment["training_form_id"],
                    "exposure_cell": cell,
                }
            )

    aggregate_groups: dict[tuple[str, str, str, str, str], list[bool]] = defaultdict(list)
    for row in annotated:
        correct = int(row["correct_rank_mean"]) == 1
        for relation in (str(row["relation"]), "ALL"):
            for group in (str(row["training_form_group"]), "ALL"):
                aggregate_groups[
                    (
                        str(row["condition"]),
                        relation,
                        str(row["scaffold_id"]),
                        group,
                        str(row["exposure_cell"]),
                    )
                ].append(correct)
    aggregate = []
    for index, (key, values) in enumerate(sorted(aggregate_groups.items())):
        accuracy, ci_low, ci_high = bootstrap_accuracy_interval(
            values,
            samples=bootstrap_samples,
            seed=seed + index,
        )
        aggregate.append(
            {
                "condition": key[0],
                "relation": key[1],
                "scaffold_id": key[2],
                "training_form_group": key[3],
                "exposure_cell": key[4],
                "n": len(values),
                "top1": sum(values),
                "top1_accuracy": accuracy,
                "bootstrap_ci_low": ci_low,
                "bootstrap_ci_high": ci_high,
                "bootstrap_samples": bootstrap_samples,
            }
        )

    fact_cells: dict[tuple[str, str, str, str, str], dict[str, bool]] = defaultdict(dict)
    for row in annotated:
        if row["exposure_cell"] not in {"seen", "crossed"}:
            continue
        key = (
            str(row["condition"]),
            str(row["relation"]),
            str(row["scaffold_id"]),
            str(row["training_form_group"]),
            str(row["fact_id"]),
        )
        fact_cells[key][str(row["exposure_cell"])] = int(row["correct_rank_mean"]) == 1
    directional_groups: dict[tuple[str, str, str, str], list[dict[str, bool]]] = defaultdict(list)
    for (condition, relation, scaffold, group, _), cells in fact_cells.items():
        if set(cells) == {"seen", "crossed"}:
            directional_groups[(condition, relation, scaffold, group)].append(cells)
            directional_groups[(condition, "ALL", scaffold, group)].append(cells)
    directional = []
    for index, (key, facts) in enumerate(sorted(directional_groups.items())):
        seen = [fact["seen"] for fact in facts]
        crossed = [fact["crossed"] for fact in facts]
        difference, ci_low, ci_high = paired_bootstrap_accuracy_difference(
            seen,
            crossed,
            samples=bootstrap_samples,
            seed=seed + index,
        )
        seen_only = sum(a and not b for a, b in zip(seen, crossed, strict=True))
        crossed_only = sum(b and not a for a, b in zip(seen, crossed, strict=True))
        directional.append(
            {
                "condition": key[0],
                "relation": key[1],
                "scaffold_id": key[2],
                "training_form_group": key[3],
                "n": len(facts),
                "seen_top1": sum(seen),
                "crossed_top1": sum(crossed),
                "seen_minus_crossed_accuracy": difference,
                "paired_bootstrap_ci_low": ci_low,
                "paired_bootstrap_ci_high": ci_high,
                "seen_only": seen_only,
                "crossed_only": crossed_only,
                "mcnemar_exact_pvalue": exact_mcnemar_pvalue(seen_only, crossed_only),
                "bootstrap_samples": bootstrap_samples,
            }
        )

    robust_cells: dict[tuple[str, str, str], dict[tuple[str, str], bool]] = defaultdict(dict)
    for row in annotated:
        if row["form_id"] not in {"form_a", "form_b"}:
            continue
        robust_cells[
            (str(row["condition"]), str(row["relation"]), str(row["fact_id"]))
        ][(str(row["form_id"]), str(row["scaffold_id"]))] = int(row["correct_rank_mean"]) == 1
    robust_groups: dict[tuple[str, str], list[dict[tuple[str, str], bool]]] = defaultdict(list)
    required_cells = {
        ("form_a", "direct"),
        ("form_a", "qa"),
        ("form_b", "direct"),
        ("form_b", "qa"),
    }
    for (condition, relation, _), cells in robust_cells.items():
        if set(cells) == required_cells:
            robust_groups[(condition, relation)].append(cells)
            robust_groups[(condition, "ALL")].append(cells)
    robust = []
    for (condition, relation), facts in sorted(robust_groups.items()):
        passed = sum(all(cells.values()) for cells in facts)
        robust.append(
            {
                "condition": condition,
                "relation": relation,
                "n": len(facts),
                "a_b_all_scaffold_intersection": passed,
                "a_b_all_scaffold_accuracy": passed / len(facts),
                "threshold": 0.70,
                "gate_passed": passed / len(facts) >= 0.70,
            }
        )
    return {
        "annotated": annotated,
        "aggregate": aggregate,
        "directional": directional,
        "robust": robust,
    }


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
