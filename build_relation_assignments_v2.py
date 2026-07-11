"""Build and audit balanced field-of-study and industry assignments."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

from assignment_rules import classify_profession


PROFILE_PATH = "data/canonical_subject_profiles_5000.csv"
CANDIDATE_PATH = "data/relation_candidates_v2.csv"
ASSIGNMENT_PATH = "output/relation_assignments_v2.csv"
AUDIT_DIR = "output/relation_assignments_v2_audit"
FIELD_SEED = 2026071101
INDUSTRY_SEED = 2026071102
BLOCK_SIZE = 100
NMI_LIMIT = 0.05
CRAMERS_V_LIMIT = 0.10
CONDITIONAL_MULTIPLIER = 1.5


def read_csv(path: str) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_seed(seed: int, *parts: object) -> int:
    payload = ":".join([str(seed), *(str(part) for part in parts)])
    return int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest()[:8], "big")


def load_candidates(path: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(path):
        grouped[row["relation"]].append(row)
    expected = {"field_of_study", "works_in_industry"}
    if set(grouped) != expected or any(len(grouped[key]) != 50 for key in expected):
        raise ValueError("Expected exactly 50 candidates for each redesigned relation")
    return dict(grouped)


def validate_profiles(profiles: list[dict[str, str]]) -> list[dict[str, str]]:
    if len(profiles) != 5000:
        raise ValueError(f"Expected 5000 profiles, found {len(profiles)}")
    ordered = sorted(profiles, key=lambda row: row["subject_id"])
    if len({row["subject_id"] for row in ordered}) != len(ordered):
        raise ValueError("Subject IDs must be unique")
    return ordered


def build_assignments(
    profiles: list[dict[str, str]],
    candidates: dict[str, list[dict[str, str]]],
    field_seed: int = FIELD_SEED,
    industry_seed: int = INDUSTRY_SEED,
) -> list[dict[str, str | int]]:
    """Assigns two balanced relations without semantic compatibility rules."""
    profiles = validate_profiles(profiles)
    fields = candidates["field_of_study"]
    industries = candidates["works_in_industry"]
    profile_rows = []
    for profile in profiles:
        profile_rows.append(
            {
                **profile,
                "profession_category": classify_profession(
                    profile["profession_en"], profile["profession_tr"]
                ),
            }
        )

    slice_keys = (
        "profession_category",
        "branch_group",
        "name_type",
        "name_rarity_bucket",
        "popularity_bucket",
    )
    group_sizes = {key: Counter(row[key] for row in profile_rows) for key in slice_keys}
    field_group_counts: dict[tuple[str, str], Counter[int]] = defaultdict(Counter)
    industry_group_counts: dict[tuple[str, str], Counter[int]] = defaultdict(Counter)
    pair_counts: dict[int, Counter[int]] = defaultdict(Counter)
    field_by_subject: dict[str, int] = {}
    industry_by_subject: dict[str, int] = {}

    def allocate_block(
        block: list[dict[str, str]],
        seed: int,
        group_counts: dict[tuple[str, str], Counter[int]],
        block_index: int,
    ) -> dict[str, int]:
        capacities = Counter({index: 2 for index in range(50)})
        subject_order = list(block)
        random.Random(stable_seed(seed, "subjects", block_index)).shuffle(subject_order)
        subject_order.sort(
            key=lambda row: (
                group_sizes["profession_category"][row["profession_category"]],
                row["subject_id"],
            )
        )
        selected: dict[str, int] = {}
        for profile in subject_order:
            scores = []
            for candidate_index, capacity in capacities.items():
                if capacity <= 0:
                    continue
                group_values = [
                    group_counts[(key, profile[key])][candidate_index] for key in slice_keys
                ]
                scores.append(
                    (
                        group_values[0],
                        max(group_values[1:]),
                        sum(group_values[1:]),
                        stable_seed(seed, "tie", block_index, profile["subject_id"], candidate_index),
                        candidate_index,
                    )
                )
            candidate_index = min(scores)[-1]
            capacities[candidate_index] -= 1
            selected[profile["subject_id"]] = candidate_index
            for key in slice_keys:
                group_counts[(key, profile[key])][candidate_index] += 1
        return selected

    def allocate_industry_block(
        block: list[dict[str, str]], block_index: int
    ) -> dict[str, int]:
        capacities = Counter({index: 2 for index in range(50)})
        subject_order = list(block)
        random.Random(stable_seed(industry_seed, "subjects", block_index)).shuffle(subject_order)
        subject_order.sort(
            key=lambda row: (
                group_sizes["profession_category"][row["profession_category"]],
                row["subject_id"],
            )
        )
        selected = {}
        for profile in subject_order:
            field_index = field_by_subject[profile["subject_id"]]
            scores = []
            for industry_index, capacity in capacities.items():
                if capacity <= 0:
                    continue
                group_values = [
                    industry_group_counts[(key, profile[key])][industry_index]
                    for key in slice_keys
                ]
                scores.append(
                    (
                        pair_counts[field_index][industry_index],
                        group_values[0],
                        max(group_values[1:]),
                        sum(group_values[1:]),
                        stable_seed(
                            industry_seed,
                            "tie",
                            block_index,
                            profile["subject_id"],
                            industry_index,
                        ),
                        industry_index,
                    )
                )
            industry_index = min(scores)[-1]
            capacities[industry_index] -= 1
            selected[profile["subject_id"]] = industry_index
            pair_counts[field_index][industry_index] += 1
            for key in slice_keys:
                industry_group_counts[(key, profile[key])][industry_index] += 1
        return selected

    for block_index, start in enumerate(range(0, len(profiles), BLOCK_SIZE)):
        block = profile_rows[start : start + BLOCK_SIZE]
        field_by_subject.update(
            allocate_block(block, field_seed, field_group_counts, block_index)
        )
        industry_by_subject.update(allocate_industry_block(block, block_index))

    profile_by_subject = {row["subject_id"]: row for row in profile_rows}
    repair_swaps = 0
    while True:
        overfull = sorted(
            (
                (count - 3, field_index, industry_index)
                for field_index, counts in pair_counts.items()
                for industry_index, count in counts.items()
                if count > 3
            ),
            reverse=True,
        )
        if not overfull:
            break

        _, target_field, target_industry = overfull[0]
        candidates_to_swap = []
        for block_index, start in enumerate(range(0, len(profile_rows), BLOCK_SIZE)):
            block = profile_rows[start : start + BLOCK_SIZE]
            targets = [
                row
                for row in block
                if field_by_subject[row["subject_id"]] == target_field
                and industry_by_subject[row["subject_id"]] == target_industry
            ]
            for left in targets:
                for right in block:
                    if left["subject_id"] == right["subject_id"]:
                        continue
                    right_industry = industry_by_subject[right["subject_id"]]
                    right_field = field_by_subject[right["subject_id"]]
                    if right_industry == target_industry:
                        continue

                    affected_pairs = {
                        (target_field, target_industry),
                        (right_field, right_industry),
                        (target_field, right_industry),
                        (right_field, target_industry),
                    }
                    before_pair_excess = sum(
                        max(0, pair_counts[field][industry] - 3)
                        for field, industry in affected_pairs
                    )
                    proposed_pair_counts = {
                        pair: pair_counts[pair[0]][pair[1]] for pair in affected_pairs
                    }
                    proposed_pair_counts[(target_field, target_industry)] -= 1
                    proposed_pair_counts[(right_field, right_industry)] -= 1
                    proposed_pair_counts[(target_field, right_industry)] += 1
                    proposed_pair_counts[(right_field, target_industry)] += 1
                    after_pair_excess = sum(
                        max(0, count - 3) for count in proposed_pair_counts.values()
                    )
                    if after_pair_excess >= before_pair_excess:
                        continue

                    valid_groups = True
                    group_delta = 0
                    for key in slice_keys:
                        left_value = left[key]
                        right_value = right[key]
                        if left_value == right_value:
                            continue
                        allowed_left = math.ceil(
                            CONDITIONAL_MULTIPLIER * group_sizes[key][left_value] / 50
                        )
                        allowed_right = math.ceil(
                            CONDITIONAL_MULTIPLIER * group_sizes[key][right_value] / 50
                        )
                        if (
                            industry_group_counts[(key, left_value)][right_industry] + 1
                            > allowed_left
                            or industry_group_counts[(key, right_value)][target_industry] + 1
                            > allowed_right
                        ):
                            valid_groups = False
                            break
                        group_delta += (
                            industry_group_counts[(key, left_value)][right_industry]
                            - industry_group_counts[(key, left_value)][target_industry]
                            + industry_group_counts[(key, right_value)][target_industry]
                            - industry_group_counts[(key, right_value)][right_industry]
                        )
                    if valid_groups:
                        candidates_to_swap.append(
                            (
                                after_pair_excess,
                                group_delta,
                                stable_seed(
                                    industry_seed,
                                    "repair",
                                    repair_swaps,
                                    left["subject_id"],
                                    right["subject_id"],
                                ),
                                left["subject_id"],
                                right["subject_id"],
                            )
                        )

        if not candidates_to_swap:
            raise ValueError(f"Could not repair pair cell {target_field}, {target_industry}")
        _, _, _, left_id, right_id = min(candidates_to_swap)
        left = profile_by_subject[left_id]
        right = profile_by_subject[right_id]
        left_industry = industry_by_subject[left_id]
        right_industry = industry_by_subject[right_id]
        left_field = field_by_subject[left_id]
        right_field = field_by_subject[right_id]
        pair_counts[left_field][left_industry] -= 1
        pair_counts[right_field][right_industry] -= 1
        pair_counts[left_field][right_industry] += 1
        pair_counts[right_field][left_industry] += 1
        for key in slice_keys:
            left_value = left[key]
            right_value = right[key]
            industry_group_counts[(key, left_value)][left_industry] -= 1
            industry_group_counts[(key, left_value)][right_industry] += 1
            industry_group_counts[(key, right_value)][right_industry] -= 1
            industry_group_counts[(key, right_value)][left_industry] += 1
        industry_by_subject[left_id], industry_by_subject[right_id] = (
            right_industry,
            left_industry,
        )
        repair_swaps += 1

    assignments: list[dict[str, str | int]] = []
    for profile in profile_rows:
        field = fields[field_by_subject[profile["subject_id"]]]
        industry = industries[industry_by_subject[profile["subject_id"]]]
        block_index = (int(profile["subject_id"][1:]) - 1) // BLOCK_SIZE
        assignments.append(
                {
                    "subject_id": profile["subject_id"],
                    "subject": profile["subject"],
                    "block_id": f"B{block_index + 1:02d}",
                    "field_of_study_en": field["object_en"],
                    "field_of_study_tr": field["object_tr"],
                    "field_source_taxonomy": field["source_taxonomy"],
                    "field_source_category": field["source_category"],
                    "works_in_industry_en": industry["object_en"],
                    "works_in_industry_tr": industry["object_tr"],
                    "industry_source_taxonomy": industry["source_taxonomy"],
                    "industry_source_category": industry["source_category"],
                    "profession_category": profile["profession_category"],
                    "branch_group": profile["branch_group"],
                    "name_type": profile["name_type"],
                    "name_rarity_bucket": profile["name_rarity_bucket"],
                    "popularity_bucket": profile["popularity_bucket"],
                    "field_seed": field_seed,
                    "industry_seed": industry_seed,
                    "industry_repair_swaps": repair_swaps,
                }
            )
    return assignments


def contingency(rows: list[dict], row_key: str, column_key: str) -> dict[str, Counter[str]]:
    table: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        table[str(row[row_key])][str(row[column_key])] += 1
    return dict(table)


def table_totals(table: dict[str, Counter[str]]) -> tuple[Counter[str], Counter[str], int]:
    row_totals = Counter({key: sum(values.values()) for key, values in table.items()})
    column_totals: Counter[str] = Counter()
    for values in table.values():
        column_totals.update(values)
    return row_totals, column_totals, sum(row_totals.values())


def normalized_mutual_information(table: dict[str, Counter[str]]) -> float:
    row_totals, column_totals, total = table_totals(table)
    if not total:
        return 0.0
    mutual_information = 0.0
    for row_value, values in table.items():
        for column_value, count in values.items():
            if count:
                mutual_information += (count / total) * math.log(
                    count * total / (row_totals[row_value] * column_totals[column_value])
                )
    row_entropy = -sum((count / total) * math.log(count / total) for count in row_totals.values())
    column_entropy = -sum(
        (count / total) * math.log(count / total) for count in column_totals.values()
    )
    denominator = math.sqrt(row_entropy * column_entropy)
    return mutual_information / denominator if denominator else 0.0


def cramers_v(table: dict[str, Counter[str]]) -> float:
    row_totals, column_totals, total = table_totals(table)
    dimensions = min(len(row_totals) - 1, len(column_totals) - 1)
    if not total or dimensions <= 0:
        return 0.0
    chi_squared = 0.0
    for row_value, row_total in row_totals.items():
        for column_value, column_total in column_totals.items():
            expected = row_total * column_total / total
            observed = table[row_value][column_value]
            chi_squared += (observed - expected) ** 2 / expected
    return math.sqrt(chi_squared / (total * dimensions))


def conditional_gate(table: dict[str, Counter[str]]) -> dict:
    row_totals, column_totals, total = table_totals(table)
    failures = []
    max_ratio = 0.0
    for row_value, row_total in row_totals.items():
        for column_value, column_total in column_totals.items():
            marginal = column_total / total
            count = table[row_value][column_value]
            allowed_count = math.ceil(CONDITIONAL_MULTIPLIER * row_total * marginal)
            ratio = (count / row_total) / marginal if count and marginal else 0.0
            max_ratio = max(max_ratio, ratio)
            if count > allowed_count:
                failures.append(
                    {
                        "row": row_value,
                        "column": column_value,
                        "count": count,
                        "allowed_count": allowed_count,
                        "conditional_probability": count / row_total,
                        "marginal_probability": marginal,
                        "ratio": ratio,
                    }
                )
    return {
        "passed": not failures,
        "max_ratio": max_ratio,
        "small_sample_tolerance": "count <= ceil(1.5 * row_total * marginal_probability)",
        "failures": failures,
    }


def pair_audit(rows: list[dict], row_key: str, column_key: str) -> tuple[dict, dict]:
    table = contingency(rows, row_key, column_key)
    nmi = round(normalized_mutual_information(table), 12)
    cv = round(cramers_v(table), 12)
    conditional = conditional_gate(table)
    metrics = {
        "row_key": row_key,
        "column_key": column_key,
        "normalized_mutual_information": nmi,
        "cramers_v": cv,
        "conditional": conditional,
        "passed": nmi <= NMI_LIMIT and cv <= CRAMERS_V_LIMIT and conditional["passed"],
    }
    return metrics, table


def balance_audit(rows: list[dict]) -> dict:
    relations = ["field_of_study_en", "works_in_industry_en"]
    global_counts = {relation: dict(sorted(Counter(row[relation] for row in rows).items())) for relation in relations}
    block_failures = []
    for block_id in sorted({row["block_id"] for row in rows}):
        block = [row for row in rows if row["block_id"] == block_id]
        for relation in relations:
            counts = Counter(row[relation] for row in block)
            if len(counts) != 50 or set(counts.values()) != {2}:
                block_failures.append({"block_id": block_id, "relation": relation, "counts": dict(counts)})
    global_passed = all(len(counts) == 50 and set(counts.values()) == {100} for counts in global_counts.values())
    return {
        "global_counts": global_counts,
        "global_passed": global_passed,
        "block_passed": not block_failures,
        "block_failures": block_failures,
        "passed": global_passed and not block_failures,
    }


def audit_assignments(rows: list[dict]) -> tuple[dict, dict[str, dict[str, Counter[str]]]]:
    pair_specs = [
        ("profession_category", "field_of_study_en"),
        ("profession_category", "works_in_industry_en"),
        ("field_of_study_en", "works_in_industry_en"),
        ("works_in_industry_en", "field_of_study_en"),
    ]
    for slice_key in ("branch_group", "name_type", "name_rarity_bucket", "popularity_bucket"):
        for relation in ("field_of_study_en", "works_in_industry_en"):
            pair_specs.append((slice_key, relation))

    pair_metrics = {}
    tables = {}
    for row_key, column_key in pair_specs:
        name = f"{row_key}__{column_key}"
        pair_metrics[name], tables[name] = pair_audit(rows, row_key, column_key)

    balance = balance_audit(rows)
    field_industry_counts = Counter(
        (row["field_of_study_en"], row["works_in_industry_en"]) for row in rows
    )
    summary = {
        "assignment_version": "relation_assignments_v2_v1",
        "subject_count": len(rows),
        "field_seed": rows[0]["field_seed"],
        "industry_seed": rows[0]["industry_seed"],
        "industry_repair_swaps": rows[0]["industry_repair_swaps"],
        "thresholds": {
            "normalized_mutual_information_max": NMI_LIMIT,
            "cramers_v_max": CRAMERS_V_LIMIT,
            "conditional_multiplier": CONDITIONAL_MULTIPLIER,
        },
        "balance": balance,
        "field_industry_pair_counts": {
            "observed_pairs": len(field_industry_counts),
            "minimum": min(field_industry_counts.values()),
            "maximum": max(field_industry_counts.values()),
        },
        "pair_metrics": pair_metrics,
        "passed": balance["passed"] and all(item["passed"] for item in pair_metrics.values()),
    }
    return summary, tables


def write_csv(path: str, rows: list[dict]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_audit(audit_dir: str, summary: dict, tables: dict[str, dict[str, Counter[str]]]) -> None:
    output = Path(audit_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    rows = []
    for pair_name, table in sorted(tables.items()):
        row_totals, column_totals, total = table_totals(table)
        for row_value in sorted(row_totals):
            for column_value in sorted(column_totals):
                rows.append(
                    {
                        "pair": pair_name,
                        "row_value": row_value,
                        "column_value": column_value,
                        "count": table[row_value][column_value],
                        "row_total": row_totals[row_value],
                        "column_total": column_totals[column_value],
                        "total": total,
                    }
                )
    write_csv(str(output / "contingency_tables.csv"), rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default=PROFILE_PATH)
    parser.add_argument("--candidates", default=CANDIDATE_PATH)
    parser.add_argument("--assignments", default=ASSIGNMENT_PATH)
    parser.add_argument("--audit-dir", default=AUDIT_DIR)
    parser.add_argument("--field-seed", type=int, default=FIELD_SEED)
    parser.add_argument("--industry-seed", type=int, default=INDUSTRY_SEED)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profiles = read_csv(args.profiles)
    candidates = load_candidates(args.candidates)
    assignments = build_assignments(profiles, candidates, args.field_seed, args.industry_seed)
    summary, tables = audit_assignments(assignments)
    summary["input_sha256"] = {
        "profiles": file_sha256(args.profiles),
        "candidates": file_sha256(args.candidates),
    }
    write_csv(args.assignments, assignments)
    write_audit(args.audit_dir, summary, tables)
    print(json.dumps({"assignments": args.assignments, "audit_dir": args.audit_dir, "passed": summary["passed"]}, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
