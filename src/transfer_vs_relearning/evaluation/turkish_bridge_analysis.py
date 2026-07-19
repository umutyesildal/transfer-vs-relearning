from __future__ import annotations

import random
from collections import defaultdict
from typing import Any


def direction_metrics(rows: list[dict[str, Any]], direction: str) -> dict[str, Any]:
    selected = [row for row in rows if str(row["direction"]) == direction]
    if not selected:
        raise ValueError(f"No rows for direction {direction}")
    correct = [int(row["correct_rank_mean"]) == 1 for row in selected]
    margins = [float(row["margin"]) for row in selected]
    per_relation: dict[str, list[bool]] = defaultdict(list)
    for row, is_correct in zip(selected, correct, strict=True):
        per_relation[str(row["relation"])].append(is_correct)
    return {
        "n": len(selected),
        "top1_accuracy": sum(correct) / len(correct),
        "mean_margin": sum(margins) / len(margins),
        "per_relation_accuracy": {
            relation: sum(values) / len(values) for relation, values in sorted(per_relation.items())
        },
    }


def paired_subject_bootstrap_accuracy_difference(
    before: list[dict[str, Any]],
    after: list[dict[str, Any]],
    *,
    direction: str,
    samples: int = 2000,
    seed: int = 42,
) -> dict[str, float | int]:
    def by_subject(rows: list[dict[str, Any]]) -> dict[str, dict[str, bool]]:
        output: dict[str, dict[str, bool]] = defaultdict(dict)
        for row in rows:
            if str(row["direction"]) != direction:
                continue
            output[str(row["subject_id"])][str(row["fact_id"])] = int(row["correct_rank_mean"]) == 1
        return output

    left, right = by_subject(before), by_subject(after)
    subjects = sorted(set(left) & set(right))
    if not subjects or set(left) != set(right):
        raise ValueError("Paired bootstrap requires identical non-empty subject sets")
    deltas: list[float] = []
    for subject in subjects:
        if set(left[subject]) != set(right[subject]):
            raise ValueError(f"Paired bootstrap fact mismatch for {subject}")
        facts = sorted(left[subject])
        deltas.append(
            sum(float(right[subject][fact]) - float(left[subject][fact]) for fact in facts) / len(facts)
        )
    rng = random.Random(seed)
    estimates = []
    for _ in range(samples):
        draw = [deltas[rng.randrange(len(deltas))] for _ in subjects]
        estimates.append(sum(draw) / len(draw))
    estimates.sort()

    def percentile(fraction: float) -> float:
        index = min(len(estimates) - 1, max(0, round((len(estimates) - 1) * fraction)))
        return estimates[index]

    return {
        "subjects": len(subjects),
        "samples": samples,
        "estimate": sum(deltas) / len(deltas),
        "ci95_low": percentile(0.025),
        "ci95_high": percentile(0.975),
    }


def classify_bridge(
    *,
    state_rows: dict[str, list[dict[str, Any]]],
    ppl_states: dict[str, dict[str, float]],
    rule: dict[str, float | int],
    bootstrap_samples: int = 2000,
    bootstrap_seed: int = 42,
) -> dict[str, Any]:
    required_states = {"m0", "m1", "low", "full"}
    if set(state_rows) != required_states or set(ppl_states) != required_states:
        raise ValueError(f"Expected exactly {sorted(required_states)}")
    metrics = {
        state: {
            direction: direction_metrics(rows, direction)
            for direction in ("en_to_en", "tr_to_en", "tr_to_tr")
        }
        for state, rows in state_rows.items()
    }
    low_change = paired_subject_bootstrap_accuracy_difference(
        state_rows["m1"], state_rows["low"], direction="tr_to_en", samples=bootstrap_samples, seed=bootstrap_seed
    )
    full_change = paired_subject_bootstrap_accuracy_difference(
        state_rows["m1"], state_rows["full"], direction="tr_to_en", samples=bootstrap_samples, seed=bootstrap_seed
    )
    full_tr = metrics["full"]["tr_to_en"]
    m1_tr = metrics["m1"]["tr_to_en"]
    gates = {
        "turkish_ppl_improved": ppl_states["full"]["turkish_ppl"] / ppl_states["m1"]["turkish_ppl"] <= float(rule["turkish_ppl_ratio_to_m1_max"]),
        "english_fact_retained": metrics["full"]["en_to_en"]["top1_accuracy"] - metrics["m1"]["en_to_en"]["top1_accuracy"] >= -float(rule["en_to_en_top1_drop_max"]),
        "tr_to_en_absolute_access": full_tr["top1_accuracy"] >= float(rule["tr_to_en_top1_min"]),
        "tr_to_en_positive_margin": full_tr["mean_margin"] > float(rule["tr_to_en_mean_margin_min"]),
        "m0_adjusted_access": full_tr["top1_accuracy"] - metrics["m0"]["tr_to_en"]["top1_accuracy"] >= float(rule["m0_adjusted_tr_to_en_gain_min"]),
        "relation_breadth": sum(value >= 0.20 for value in full_tr["per_relation_accuracy"].values()) >= int(rule["relation_count_at_or_above_0_20_min"]),
    }
    improved = (
        full_change["estimate"] >= float(rule["tr_to_en_gain_min"])
        and full_change["ci95_low"] > 0.0
    )
    already_open = (
        m1_tr["top1_accuracy"] >= float(rule["tr_to_en_already_open_floor"])
        and full_change["estimate"] >= -float(rule["already_open_retention_drop_max"])
    )
    gates["adaptation_gain_or_preserved_open_bridge"] = improved or already_open
    passed = all(gates.values())
    return {
        "classification": "promising" if passed else "not_viable_under_frozen_pilot",
        "all_gates_pass": passed,
        "gates": gates,
        "state_metrics": metrics,
        "ppl_states": ppl_states,
        "turkish_ppl_ratio_full_to_m1": ppl_states["full"]["turkish_ppl"] / ppl_states["m1"]["turkish_ppl"],
        "low_tr_to_en_change": low_change,
        "full_tr_to_en_change": full_change,
        "bridge_path": "improved_with_adaptation" if improved else "already_open_and_retained" if already_open else "none",
    }
