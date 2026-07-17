from __future__ import annotations

import math
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
