"""
Canonical subject-profile generation from cleaned source lists.
"""
from __future__ import annotations

import csv
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

import config
from assignment_rules import (
    assign_name_rarity,
    can_use_university_as_employer,
    classify_employer,
    classify_profession,
    compatible_employer_categories,
    counter_dict,
    inverse_sqrt_weights,
    is_compatible_employer,
    natural_full_name,
    pearson_correlation,
    relation_frequency_buckets,
    weighted_choice_index,
)
from load_facts import load_and_validate_facts
from source_list_loader import load_generation_sources

CANONICAL_COLUMNS = [
    "row_id",
    "subject_id",
    "subject",
    "profession_en",
    "profession_tr",
    "birthplace_en",
    "birthplace_tr",
    "residence_en",
    "residence_tr",
    "university_en",
    "university_tr",
    "employer_en",
    "employer_tr",
    "name_type",
    "name_rarity_bucket",
    "popularity_rank",
    "popularity_bucket",
    "profession_frequency_bucket",
    "birthplace_frequency_bucket",
    "residence_frequency_bucket",
    "university_frequency_bucket",
    "employer_frequency_bucket",
    "branch_group",
]


def target_counts(total: int, targets: dict[str, float]) -> dict[str, int]:
    """Converts fractional targets into exact integer counts."""
    counts = {key: int(total * value) for key, value in targets.items()}
    remainder = total - sum(counts.values())
    for key in targets:
        if remainder <= 0:
            break
        counts[key] += 1
        remainder -= 1
    return counts


def generate_names_for_type(name_type: str, first_names: list[str], surnames: list[str], count: int, rng: random.Random) -> list[dict]:
    """Generates unique full names for one name type with target rarity counts."""
    quotas = target_counts(count, config.NAME_RARITY_TARGETS)
    selected = []
    seen = set()
    attempts = 0
    max_attempts = count * 1000

    if len(first_names) * len(surnames) < count:
        raise ValueError(f"Not enough name combinations to generate {count} unique {name_type} subjects.")

    while sum(quotas.values()) > 0 and attempts < max_attempts:
        attempts += 1
        first_index = rng.randrange(len(first_names))
        surname_index = rng.randrange(len(surnames))
        first_name = first_names[first_index]
        surname = surnames[surname_index]
        subject = natural_full_name(first_name, surname, name_type)
        if subject in seen:
            continue

        rarity = assign_name_rarity(first_index + 1, len(first_names), surname_index + 1, len(surnames))
        if quotas.get(rarity, 0) <= 0:
            continue

        quotas[rarity] -= 1
        seen.add(subject)
        selected.append({
            "subject": subject,
            "name_type": name_type,
            "name_rarity_bucket": rarity,
            "first_name_rank": first_index + 1,
            "surname_rank": surname_index + 1,
        })

    if sum(quotas.values()) != 0:
        raise ValueError(f"Could not satisfy name rarity quotas for {name_type}: {quotas}")
    return selected


def generate_subject_names(sources: dict, rng: random.Random) -> list[dict]:
    """Generates all subject names with separated English-like and Turkish-like components."""
    english_subjects = generate_names_for_type(
        "english_like",
        sources["source_lists"]["names_en.txt"],
        sources["source_lists"]["surnames_en.txt"],
        config.NAME_TYPE_COUNTS["english_like"],
        rng,
    )
    turkish_subjects = generate_names_for_type(
        "turkish_like",
        sources["source_lists"]["names_tr.txt"],
        sources["source_lists"]["surnames_tr.txt"],
        config.NAME_TYPE_COUNTS["turkish_like"],
        rng,
    )
    subjects = english_subjects + turkish_subjects
    if len({subject["subject"] for subject in subjects}) != config.SUBJECT_COUNT:
        raise ValueError("Generated full subject names are not globally unique.")
    return subjects


def assign_professions(subjects: list[dict], professions: list[dict], rng: random.Random) -> None:
    """Assigns professions with coverage first and weighted sampling afterward."""
    shuffled_professions = professions[:]
    rng.shuffle(shuffled_professions)
    profession_weights = [(item["profession_popularity_score"] + 1) ** config.PROFESSION_WEIGHT_POWER for item in professions]

    for index, subject in enumerate(subjects):
        if index < len(shuffled_professions):
            profession = shuffled_professions[index]
        else:
            profession = professions[weighted_choice_index(rng, profession_weights)]
        subject.update(profession)
        subject["profession_category"] = classify_profession(profession["profession_en"], profession["profession_tr"])


class ObjectSampler:
    """Coverage-first then weighted sampler for one object pool."""

    def __init__(self, objects: list[dict], rng: random.Random):
        if not objects:
            raise ValueError("Cannot sample from an empty object pool.")
        self.objects = objects
        self.rng = rng
        self.weights = inverse_sqrt_weights(len(objects))
        self.coverage_queue = objects[:]
        rng.shuffle(self.coverage_queue)
        self.coverage_index = 0

    def sample(self, candidates: list[dict] | None = None) -> dict:
        """Samples from candidates or from the full pool with coverage first."""
        if candidates is not None:
            if not candidates:
                raise ValueError("Cannot sample from an empty candidate list.")
            return candidates[weighted_choice_index(self.rng, inverse_sqrt_weights(len(candidates)))]
        if self.coverage_index < len(self.coverage_queue):
            item = self.coverage_queue[self.coverage_index]
            self.coverage_index += 1
            return item
        return self.objects[weighted_choice_index(self.rng, self.weights)]


def split_by_origin(objects: list[dict]) -> dict[str, list[dict]]:
    """Splits proper-name pairs into English-origin and Turkish-origin pools."""
    return {
        "english_origin": [obj for obj in objects if obj["origin"] == "english_origin"],
        "turkish_origin": [obj for obj in objects if obj["origin"] == "turkish_origin"],
    }


def exact_profile_pattern_counts(total: int) -> dict[str, int]:
    """Computes exact integer profile-pattern counts from configured targets."""
    raw = {pattern: total * target for pattern, target in config.PROFILE_PATTERN_TARGETS.items()}
    counts = {pattern: int(value) for pattern, value in raw.items()}
    remainder = total - sum(counts.values())
    for pattern, _ in sorted(raw.items(), key=lambda item: (-(item[1] - int(item[1])), item[0])):
        if remainder <= 0:
            break
        counts[pattern] += 1
        remainder -= 1
    return counts


def assign_profile_patterns(subjects: list[dict]) -> dict[str, int]:
    """Assigns profile patterns with deterministic stratification across metadata."""
    total_counts = exact_profile_pattern_counts(len(subjects))
    group_keys = sorted({(subject["name_type"], subject["branch_group"]) for subject in subjects})
    group_targets = Counter((subject["name_type"], subject["branch_group"]) for subject in subjects)
    group_totals = Counter()
    remaining_by_group = {key: {pattern: 0 for pattern in total_counts} for key in group_keys}
    for pattern, count in total_counts.items():
        pattern_totals = Counter()
        for _ in range(count):
            candidates = [
                key for key in group_keys
                if group_totals[key] < group_targets[key]
            ]
            key = min(candidates, key=lambda item: (pattern_totals[item], group_totals[item], item))
            remaining_by_group[key][pattern] += 1
            pattern_totals[key] += 1
            group_totals[key] += 1

    strata = defaultdict(list)
    for subject in subjects:
        key = (
            subject["name_type"],
            subject["branch_group"],
            subject["popularity_bucket"],
            subject["name_rarity_bucket"],
        )
        strata[key].append(subject)

    pattern_order = list(config.PROFILE_PATTERN_TARGETS)
    for key in sorted(strata):
        remaining = remaining_by_group[(key[0], key[1])]
        group = sorted(strata[key], key=lambda item: item["subject_id"])
        for offset, subject in enumerate(group):
            rotated = pattern_order[offset % len(pattern_order):] + pattern_order[:offset % len(pattern_order)]
            candidates = [pattern for pattern in rotated if remaining[pattern] > 0]
            if not candidates:
                raise ValueError("Profile-pattern quotas were exhausted before assignment completed.")
            pattern = max(candidates, key=lambda item: (remaining[item], -pattern_order.index(item)))
            subject["profile_pattern"] = pattern
            subject.update(config.PROFILE_PATTERNS[pattern])
            remaining[pattern] -= 1

    remaining_total = {
        str(key): {pattern: count for pattern, count in remaining.items() if count != 0}
        for key, remaining in remaining_by_group.items()
    }
    if any(remaining_total.values()):
        raise ValueError(f"Profile-pattern assignment did not use all quotas: {remaining_total}")
    return counter_dict(subject["profile_pattern"] for subject in subjects)


def assign_profile_objects(subjects: list[dict], cities: list[dict], universities: list[dict], companies: list[dict], rng: random.Random) -> dict:
    """Assigns coherent regional objects and compatible employers."""
    city_pools = split_by_origin(cities)
    university_pools = split_by_origin(universities)
    company_pools = split_by_origin(companies)
    city_samplers = {origin: ObjectSampler(pool, rng) for origin, pool in city_pools.items()}
    university_samplers = {origin: ObjectSampler(pool, rng) for origin, pool in university_pools.items()}

    company_records_by_origin = {}
    for origin, pool in company_pools.items():
        company_records_by_origin[origin] = []
        for company in pool:
            item = dict(company)
            item["category"] = classify_employer(company["object_en"], company["object_tr"])
            company_records_by_origin[origin].append(item)

    university_employers_by_origin = {}
    for origin, pool in university_pools.items():
        university_employers_by_origin[origin] = []
        for university in pool:
            item = dict(university)
            item["category"] = "education"
            item["origin"] = origin
            university_employers_by_origin[origin].append(item)

    company_samplers = {origin: ObjectSampler(pool, rng) for origin, pool in company_records_by_origin.items()}
    university_employer_samplers = {origin: ObjectSampler(pool, rng) for origin, pool in university_employers_by_origin.items()}
    compatibility_match_count = 0
    general_fallback_count = 0
    broad_compatibility_count = 0
    final_fallback_count = 0
    university_as_employer_count = 0
    birthplace_residence_collisions_before_repair = 0
    repaired_birthplace_residence_collisions = 0

    for subject in sorted(subjects, key=lambda item: item["subject_id"]):
        birthplace = city_samplers[subject["birthplace_origin"]].sample()
        residence = city_samplers[subject["residence_origin"]].sample()
        birthplace_identity = canonical_city_identity(birthplace["object_en"], birthplace["object_tr"])
        residence_identity = canonical_city_identity(residence["object_en"], residence["object_tr"])
        if birthplace_identity == residence_identity:
            birthplace_residence_collisions_before_repair += 1
            candidates = [
                city for city in city_pools[subject["residence_origin"]]
                if canonical_city_identity(city["object_en"], city["object_tr"]) != birthplace_identity
            ]
            if not candidates:
                raise ValueError(
                    f"Cannot assign a residence different from birthplace for {subject['subject_id']} "
                    f"within {subject['residence_origin']} city pool."
                )
            residence = city_samplers[subject["residence_origin"]].sample(candidates)
            repaired_birthplace_residence_collisions += 1
        university = university_samplers[subject["university_origin"]].sample()
        subject["birthplace_en"] = birthplace["object_en"]
        subject["birthplace_tr"] = birthplace["object_tr"]
        subject["residence_en"] = residence["object_en"]
        subject["residence_tr"] = residence["object_tr"]
        subject["university_en"] = university["object_en"]
        subject["university_tr"] = university["object_tr"]

        employer_origin = subject["employer_origin"]
        company_pool = company_records_by_origin[employer_origin]
        direct = [company for company in company_pool if company["category"] == subject["profession_category"]]
        general = [company for company in company_pool if company["category"] == "general"]
        broad_categories = compatible_employer_categories(subject["profession_category"])
        broad = [company for company in company_pool if company["category"] in broad_categories]
        used_general = False
        used_broad = False
        used_final = False

        if direct:
            employer = company_samplers[employer_origin].sample(direct)
        elif can_use_university_as_employer(subject["profession_en"], subject["profession_tr"], subject["profession_category"]):
            employer = university_employer_samplers[employer_origin].sample()
            university_as_employer_count += 1
        elif general:
            employer = company_samplers[employer_origin].sample(general)
            used_general = True
            general_fallback_count += 1
        elif broad:
            employer = company_samplers[employer_origin].sample(broad)
            used_broad = True
            broad_compatibility_count += 1
        else:
            employer = company_samplers[employer_origin].sample()
            used_final = True
            final_fallback_count += 1

        subject["employer_en"] = employer["object_en"]
        subject["employer_tr"] = employer["object_tr"]
        subject["employer_category"] = employer["category"]
        subject["employer_compatibility_fallback"] = used_general or used_final
        subject["employer_general_fallback"] = used_general
        subject["employer_broad_compatibility"] = used_broad
        if is_compatible_employer(subject["profession_category"], employer["category"]) or employer["category"] == "general":
            compatibility_match_count += 1

    category_distribution = Counter(subject["profession_category"] for subject in subjects)
    return {
        "compatibility_match_count": compatibility_match_count,
        "general_employer_fallback_count": general_fallback_count,
        "broad_compatibility_count": broad_compatibility_count,
        "final_fallback_count": final_fallback_count,
        "fallback_count": final_fallback_count,
        "fallback_rate": final_fallback_count / len(subjects),
        "match_rate": compatibility_match_count / len(subjects),
        "university_as_employer_count": university_as_employer_count,
        "category_distribution": counter_dict(category_distribution),
        "birthplace_residence_collisions_before_repair": birthplace_residence_collisions_before_repair,
        "repaired_birthplace_residence_collisions": repaired_birthplace_residence_collisions,
    }


def assign_popularity(subjects: list[dict], rng: random.Random) -> None:
    """Assigns subject popularity ranks and buckets."""
    for subject in subjects:
        random_score = rng.uniform(0, 100)
        subject["fame_score"] = (
            config.FAME_PROFESSION_WEIGHT * subject["profession_popularity_score"]
            + config.FAME_RANDOM_WEIGHT * random_score
        )

    ranked_subjects = sorted(subjects, key=lambda item: (-item["fame_score"], item["subject_id"]))
    high_count = int(config.SUBJECT_COUNT * config.POPULARITY_BUCKET_TARGETS["high"])
    medium_count = int(config.SUBJECT_COUNT * config.POPULARITY_BUCKET_TARGETS["medium"])

    for rank, subject in enumerate(ranked_subjects, start=1):
        subject["popularity_rank"] = str(rank)
        if rank <= high_count:
            subject["popularity_bucket"] = "high"
        elif rank <= high_count + medium_count:
            subject["popularity_bucket"] = "medium"
        else:
            subject["popularity_bucket"] = "low"


def assign_relation_frequencies(subjects: list[dict]) -> None:
    """Assigns relation-specific frequency buckets."""
    for subject in subjects:
        subject.update(relation_frequency_buckets(
            popularity_bucket=subject["popularity_bucket"],
            profession_category=subject["profession_category"],
            employer_fallback=subject["employer_compatibility_fallback"],
        ))


def score_bin(score: int) -> str:
    """Bins profession popularity scores for branch stratification."""
    if score >= 67:
        return "high_score"
    if score >= 34:
        return "medium_score"
    return "low_score"


def assign_branches(subjects: list[dict]) -> None:
    """Assigns exactly balanced subject-level Branch A/B with deterministic stratification."""
    strata = defaultdict(list)
    for subject in subjects:
        key = (
            subject["name_type"],
            subject["name_rarity_bucket"],
            subject["popularity_bucket"],
            score_bin(subject["profession_popularity_score"]),
        )
        strata[key].append(subject)

    counts = Counter()
    leftovers = []
    for key in sorted(strata):
        group = sorted(strata[key], key=lambda item: item["subject"])
        for index, subject in enumerate(group):
            branch = "A" if index % 2 == 0 else "B"
            subject["branch_group"] = branch
            counts[branch] += 1
        if len(group) % 2 == 1:
            leftovers.append(group[-1])

    target_a = config.BRANCH_TARGETS["A"]
    if counts["A"] > target_a:
        for subject in sorted(leftovers, key=lambda item: item["subject_id"]):
            if counts["A"] == target_a:
                break
            if subject["branch_group"] == "A":
                subject["branch_group"] = "B"
                counts["A"] -= 1
                counts["B"] += 1
    elif counts["A"] < target_a:
        for subject in sorted(leftovers, key=lambda item: item["subject_id"]):
            if counts["A"] == target_a:
                break
            if subject["branch_group"] == "B":
                subject["branch_group"] = "A"
                counts["A"] += 1
                counts["B"] -= 1

    if counts["A"] != config.BRANCH_TARGETS["A"] or counts["B"] != config.BRANCH_TARGETS["B"]:
        raise ValueError(f"Could not satisfy exact branch targets: {dict(counts)}")


def finalize_subject_rows(subjects: list[dict]) -> list[dict]:
    """Assigns deterministic IDs and returns canonical rows sorted by subject ID."""
    rows = []
    for index, subject in enumerate(subjects, start=1):
        subject["row_id"] = f"R{index:05d}"
        subject["subject_id"] = f"S{index:05d}"

    for subject in sorted(subjects, key=lambda item: item["subject_id"]):
        rows.append({column: subject[column] for column in CANONICAL_COLUMNS})
    return rows


def profession_usage_stats(rows: list[dict]) -> dict:
    """Summarizes profession assignment coverage and score correlation."""
    counts = Counter(row["profession_en"] for row in rows)
    scores = {}
    for row in rows:
        scores[row["profession_en"]] = int(row["_profession_score"])
    assignment_counts = list(counts.values())
    return {
        "unique_professions_used": len(counts),
        "minimum_assignments_per_profession": min(assignment_counts),
        "maximum_assignments_per_profession": max(assignment_counts),
        "median_assignments_per_profession": statistics.median(assignment_counts),
        "score_assignment_count_correlation": pearson_correlation(
            [scores[name] for name in counts],
            [counts[name] for name in counts],
        ),
    }


def object_usage_stats(rows: list[dict], field: str) -> dict:
    """Summarizes object assignment counts."""
    counts = Counter(row[field] for row in rows)
    assignment_counts = list(counts.values())
    return {
        "unique_used": len(counts),
        "minimum_assignments": min(assignment_counts),
        "maximum_assignments": max(assignment_counts),
        "median_assignments": statistics.median(assignment_counts),
    }


def canonical_city_identity(object_en: str, object_tr: str) -> str:
    """Builds a normalized city identity for birthplace/residence comparisons."""
    return normalize_city_text(object_en) or normalize_city_text(object_tr)


def normalize_city_text(value: str) -> str:
    """Normalizes city text for equality checks without changing output values."""
    from assignment_rules import normalize_turkish_text

    return normalize_turkish_text(str(value)).casefold().strip()


def profile_pattern_distribution(rows: list[dict], group_field: str) -> dict:
    """Summarizes profile-pattern distribution within a grouping field."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[group_field]].append(row["_profile_pattern"])
    return {key: counter_dict(values) for key, values in sorted(grouped.items())}


def build_summary(rows: list[dict], sources: dict, compatibility_stats: dict, warnings: list[str], source_report: dict, profile_pattern_counts: dict) -> dict:
    """Builds the canonical generation summary."""
    frequency_values = []
    per_relation = {}
    for relation, field in {
        "profession": "profession_frequency_bucket",
        "born_in": "birthplace_frequency_bucket",
        "lives_in": "residence_frequency_bucket",
        "studied_at": "university_frequency_bucket",
        "works_at": "employer_frequency_bucket",
    }.items():
        values = [row[field] for row in rows]
        frequency_values.extend(values)
        per_relation[relation] = counter_dict(values)

    object_origins = {
        "birthplace": counter_dict(row["_birthplace_origin"] for row in rows),
        "residence": counter_dict(row["_residence_origin"] for row in rows),
        "university": counter_dict(row["_university_origin"] for row in rows),
        "employer": counter_dict(row["_employer_origin"] for row in rows),
    }

    rows_with_scores = []
    for row in rows:
        item = dict(row)
        item["_profession_score"] = row["_profession_score"]
        rows_with_scores.append(item)

    files = source_report["files"]
    return {
        "random_seed": config.RANDOM_SEED,
        "generated_subject_count": len(rows),
        "expected_fact_count": len(rows) * len(config.RELATION_SPECS),
        "unique_full_name_count": len({row["subject"] for row in rows}),
        "english_like_subject_count": sum(row["name_type"] == "english_like" for row in rows),
        "turkish_like_subject_count": sum(row["name_type"] == "turkish_like" for row in rows),
        "name_rarity_distribution": counter_dict(row["name_rarity_bucket"] for row in rows),
        "popularity_bucket_distribution": counter_dict(row["popularity_bucket"] for row in rows),
        "branch_distribution": counter_dict(row["branch_group"] for row in rows),
        "profession_usage_statistics": profession_usage_stats(rows_with_scores),
        "birthplace_usage_statistics": object_usage_stats(rows, "birthplace_en"),
        "residence_usage_statistics": object_usage_stats(rows, "residence_en"),
        "university_usage_statistics": object_usage_stats(rows, "university_en"),
        "employer_usage_statistics": object_usage_stats(rows, "employer_en"),
        "object_origin_distribution": object_origins,
        "total_residence_facts": len(rows),
        "residence_frequency_distribution": counter_dict(row["residence_frequency_bucket"] for row in rows),
        "birthplace_frequency_distribution": counter_dict(row["birthplace_frequency_bucket"] for row in rows),
        "birthplace_residence_frequency_equality_check": all(
            row["birthplace_frequency_bucket"] == row["residence_frequency_bucket"]
            for row in rows
        ),
        "birthplace_city_usage_statistics": object_usage_stats(rows, "birthplace_en"),
        "residence_city_usage_statistics": object_usage_stats(rows, "residence_en"),
        "birthplace_residence_collisions_before_repair": compatibility_stats["birthplace_residence_collisions_before_repair"],
        "repaired_birthplace_residence_collisions": compatibility_stats["repaired_birthplace_residence_collisions"],
        "remaining_birthplace_residence_collisions": sum(
            canonical_city_identity(row["birthplace_en"], row["birthplace_tr"])
            == canonical_city_identity(row["residence_en"], row["residence_tr"])
            for row in rows
        ),
        "cities_used_in_both_birthplace_and_residence": len(
            {
                canonical_city_identity(row["birthplace_en"], row["birthplace_tr"])
                for row in rows
            }
            & {
                canonical_city_identity(row["residence_en"], row["residence_tr"])
                for row in rows
            }
        ),
        "profession_employer_compatibility": compatibility_stats,
        "name_cleaning": {
            "excluded_multi_component_english_first_names": files["names_en.txt"]["multi_component_entries_excluded"],
            "excluded_multi_component_turkish_first_names": files["names_tr.txt"]["multi_component_entries_excluded"],
            "excluded_multi_component_english_surnames": files["surnames_en.txt"]["multi_component_entries_excluded"],
            "excluded_multi_component_turkish_surnames": files["surnames_tr.txt"]["multi_component_entries_excluded"],
            "generated_two_part_english_like_names": sum(row["name_type"] == "english_like" and len(row["subject"].split()) == 2 for row in rows),
            "generated_two_part_turkish_like_names": sum(row["name_type"] == "turkish_like" and len(row["subject"].split()) == 2 for row in rows),
        },
        "profile_pattern_counts": profile_pattern_counts,
        "profile_pattern_distribution_by_name_type": profile_pattern_distribution(rows, "name_type"),
        "profile_pattern_distribution_by_branch": profile_pattern_distribution(rows, "branch_group"),
        "profile_pattern_distribution_by_popularity_bucket": profile_pattern_distribution(rows, "popularity_bucket"),
        "profile_pattern_distribution_by_name_rarity_bucket": profile_pattern_distribution(rows, "name_rarity_bucket"),
        "frequency_distribution_overall": counter_dict(frequency_values),
        "frequency_distribution_per_relation": per_relation,
        "frequency_distribution_by_popularity_bucket": {
            bucket: counter_dict(value for row in rows if row["popularity_bucket"] == bucket for value in [
                row["profession_frequency_bucket"],
                row["birthplace_frequency_bucket"],
                row["residence_frequency_bucket"],
                row["university_frequency_bucket"],
                row["employer_frequency_bucket"],
            ])
            for bucket in ["high", "medium", "low"]
        },
        "frequency_distribution_by_branch": {
            branch: counter_dict(value for row in rows if row["branch_group"] == branch for value in [
                row["profession_frequency_bucket"],
                row["birthplace_frequency_bucket"],
                row["residence_frequency_bucket"],
                row["university_frequency_bucket"],
                row["employer_frequency_bucket"],
            ])
            for branch in ["A", "B"]
        },
        "frequency_distribution_by_name_type": {
            name_type: counter_dict(value for row in rows if row["name_type"] == name_type for value in [
                row["profession_frequency_bucket"],
                row["birthplace_frequency_bucket"],
                row["residence_frequency_bucket"],
                row["university_frequency_bucket"],
                row["employer_frequency_bucket"],
            ])
            for name_type in ["english_like", "turkish_like"]
        },
        "source_validation": source_report,
        "warnings": warnings,
    }


def validate_canonical_rows(rows: list[dict]) -> None:
    """Validates the generated canonical CSV before pipeline execution."""
    if len(rows) != config.SUBJECT_COUNT:
        raise ValueError(f"Expected {config.SUBJECT_COUNT} canonical rows, found {len(rows)}")
    if [row["row_id"] for row in rows] != [f"R{index:05d}" for index in range(1, config.SUBJECT_COUNT + 1)]:
        raise ValueError("row_id values are not exactly R00001 through R05000.")
    if [row["subject_id"] for row in rows] != [f"S{index:05d}" for index in range(1, config.SUBJECT_COUNT + 1)]:
        raise ValueError("subject_id values are not exactly S00001 through S05000.")
    if len({row["subject"] for row in rows}) != config.SUBJECT_COUNT:
        raise ValueError("Full subject names are not unique.")
    if Counter(row["name_type"] for row in rows) != Counter(config.NAME_TYPE_COUNTS):
        raise ValueError("Name-type counts do not match configured targets.")
    if sorted(int(row["popularity_rank"]) for row in rows) != list(range(1, config.SUBJECT_COUNT + 1)):
        raise ValueError("Popularity ranks are not exactly 1 through 5000.")
    expected_popularity = {"high": 500, "medium": 1500, "low": 3000}
    if Counter(row["popularity_bucket"] for row in rows) != Counter(expected_popularity):
        raise ValueError("Popularity bucket distribution is invalid.")
    if Counter(row["branch_group"] for row in rows) != Counter(config.BRANCH_TARGETS):
        raise ValueError("Branch distribution is invalid.")
    for row in rows:
        name_parts = row["subject"].split()
        if len(name_parts) != 2:
            raise ValueError(f"Subject does not have exactly two name components: {row['subject']}")
        if row["subject"].isupper():
            raise ValueError(f"Subject is fully uppercase: {row['subject']}")
        if any(part.isupper() for part in name_parts):
            raise ValueError(f"Subject contains an all-uppercase name component: {row['subject']}")
        if "_profile_pattern" in row:
            pattern = config.PROFILE_PATTERNS[row["_profile_pattern"]]
            for relation, origin_key in [
                ("birthplace", "birthplace_origin"),
                ("residence", "residence_origin"),
                ("university", "university_origin"),
                ("employer", "employer_origin"),
            ]:
                if row[f"_{relation}_origin"] != pattern[origin_key]:
                    raise ValueError(f"{relation} origin does not match profile pattern for {row['subject_id']}")
        if canonical_city_identity(row["birthplace_en"], row["birthplace_tr"]) == canonical_city_identity(row["residence_en"], row["residence_tr"]):
            raise ValueError(f"Birthplace and residence collide for {row['subject_id']}")
        if row["birthplace_frequency_bucket"] != row["residence_frequency_bucket"]:
            raise ValueError(f"Birthplace and residence frequencies differ for {row['subject_id']}")
        for column in CANONICAL_COLUMNS:
            if str(row[column]).strip() == "":
                raise ValueError(f"Empty canonical value in {column} for {row['subject_id']}")
        for column in [
            "profession_frequency_bucket",
            "birthplace_frequency_bucket",
            "university_frequency_bucket",
            "employer_frequency_bucket",
        ]:
            if row[column] not in config.ALLOWED_FREQUENCY_BUCKETS:
                raise ValueError(f"Invalid frequency value {row[column]} in {column}")


def write_canonical_csv(rows: list[dict], output_path: str) -> None:
    """Writes the canonical subject-profile CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANONICAL_COLUMNS)
        writer.writeheader()
        writer.writerows([{column: row[column] for column in CANONICAL_COLUMNS} for row in rows])


def generate_canonical_profiles(
    source_dir: str = config.SOURCE_LIST_DIR,
    output_path: str = config.CANONICAL_OUTPUT_PATH,
    source_report_path: str = config.SOURCE_VALIDATION_REPORT_PATH,
    summary_path: str = config.CANONICAL_GENERATION_SUMMARY_PATH,
) -> dict:
    """Generates, validates, writes, and summarizes the canonical profile CSV."""
    rng = random.Random(config.RANDOM_SEED)
    sources, source_report = load_generation_sources(source_dir, report_path=source_report_path)
    subjects = generate_subject_names(sources, rng)

    rng.shuffle(subjects)
    for index, subject in enumerate(subjects, start=1):
        subject["subject_id"] = f"S{index:05d}"

    assign_professions(subjects, sources["professions"], rng)
    assign_popularity(subjects, rng)
    assign_branches(subjects)
    profile_pattern_counts = assign_profile_patterns(subjects)
    compatibility_stats = assign_profile_objects(subjects, sources["cities"], sources["universities"], sources["companies"], rng)
    assign_relation_frequencies(subjects)

    rows = []
    for index, subject in enumerate(sorted(subjects, key=lambda item: item["subject_id"]), start=1):
        subject["row_id"] = f"R{index:05d}"
        row = {column: subject[column] for column in CANONICAL_COLUMNS}
        row["_profession_score"] = subject["profession_popularity_score"]
        row["_birthplace_origin"] = subject["birthplace_origin"]
        row["_residence_origin"] = subject["residence_origin"]
        row["_university_origin"] = subject["university_origin"]
        row["_employer_origin"] = subject["employer_origin"]
        row["_profile_pattern"] = subject["profile_pattern"]
        row["_employer_category"] = subject["employer_category"]
        rows.append(row)

    validate_canonical_rows(rows)
    write_canonical_csv(rows, output_path)

    warnings = []
    if compatibility_stats["fallback_count"]:
        warnings.append(f"Employer compatibility fallback used {compatibility_stats['fallback_count']} times.")

    summary = build_summary(rows, sources, compatibility_stats, warnings, source_report, profile_pattern_counts)
    output_summary_path = Path(summary_path)
    output_summary_path.parent.mkdir(parents=True, exist_ok=True)
    output_summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def validate_pipeline_outputs(summary: dict, canonical_path: str = config.CANONICAL_OUTPUT_PATH) -> dict:
    """Validates generated training/probe outputs against the canonical CSV."""
    facts_df = load_and_validate_facts(canonical_path)
    expected_fact_ids = set(facts_df["fact_id"])
    branch_b_fact_ids = set(facts_df.loc[facts_df["branch_group"] == "B", "fact_id"])
    branch_a_fact_ids = set(facts_df.loc[facts_df["branch_group"] == "A", "fact_id"])

    with open(config.ENGLISH_TRAINING_OUTPUT_PATH, encoding="utf-8") as handle:
        english_rows = [json.loads(line) for line in handle]
    with open(config.ENGLISH_BIOGRAPHY_OUTPUT_PATH, encoding="utf-8") as handle:
        english_biography_rows = [json.loads(line) for line in handle]
    with open(config.ENGLISH_QA_TRAIN_OUTPUT_PATH, encoding="utf-8") as handle:
        english_qa_rows = [json.loads(line) for line in handle]
    with open(config.ENGLISH_TRAINING_M1_BIO_QA_OUTPUT_PATH, encoding="utf-8") as handle:
        english_bio_qa_rows = [json.loads(line) for line in handle]
    with open(config.TURKISH_REPETITION_OUTPUT_PATH, encoding="utf-8") as handle:
        turkish_rows = [json.loads(line) for line in handle]
    probes_en = pd.read_csv(config.PROBES_EN_OUTPUT_PATH, dtype={"fact_id": str})
    probes_tr = pd.read_csv(config.PROBES_TR_OUTPUT_PATH, dtype={"fact_id": str})

    expected_english_rows = sum(config.FREQUENCY_TO_REPETITION_COUNT[value] for value in facts_df["frequency_bucket"])
    expected_biography_rows = expected_english_rows
    expected_qa_rows = sum(config.FREQUENCY_TO_QA_COUNT[value] for value in facts_df["frequency_bucket"])
    expected_bio_qa_rows = expected_biography_rows + expected_qa_rows
    expected_turkish_rows = sum(
        config.FREQUENCY_TO_REPETITION_COUNT[value]
        for value in facts_df.loc[facts_df["branch_group"] == "B", "frequency_bucket"]
    )

    result = {
        "english_training_rows": len(english_rows),
        "english_biography_rows": len(english_biography_rows),
        "english_qa_rows": len(english_qa_rows),
        "english_bio_qa_rows": len(english_bio_qa_rows),
        "turkish_repetition_rows": len(turkish_rows),
        "probes_en_rows": len(probes_en),
        "probes_tr_rows": len(probes_tr),
        "expected_english_training_rows": expected_english_rows,
        "expected_english_biography_rows": expected_biography_rows,
        "expected_english_qa_rows": expected_qa_rows,
        "expected_english_bio_qa_rows": expected_bio_qa_rows,
        "expected_turkish_repetition_rows": expected_turkish_rows,
        "english_unique_facts": len({row["fact_id"] for row in english_rows}),
        "english_biography_unique_facts": len({row["fact_id"] for row in english_biography_rows}),
        "english_qa_unique_facts": len({row["fact_id"] for row in english_qa_rows}),
        "english_bio_qa_unique_facts": len({row["fact_id"] for row in english_bio_qa_rows}),
        "turkish_unique_facts": len({row["fact_id"] for row in turkish_rows}),
    }

    if result["english_training_rows"] != expected_english_rows:
        raise ValueError("English training row count does not match expected frequency total.")
    if result["english_biography_rows"] != expected_biography_rows:
        raise ValueError("English biography row count does not match expected frequency total.")
    if result["english_qa_rows"] != expected_qa_rows:
        raise ValueError("English QA row count does not match expected QA frequency total.")
    if result["english_bio_qa_rows"] != expected_bio_qa_rows:
        raise ValueError("Merged BIO-QA row count does not match expected total.")
    if result["turkish_repetition_rows"] != expected_turkish_rows:
        raise ValueError("Turkish repetition row count does not match expected frequency total.")
    if {row["fact_id"] for row in english_rows} != expected_fact_ids:
        raise ValueError("Not every fact appears in English training.")
    if {row["fact_id"] for row in english_biography_rows} != expected_fact_ids:
        raise ValueError("Not every fact appears in English biographies.")
    if {row["fact_id"] for row in english_qa_rows} != expected_fact_ids:
        raise ValueError("Not every fact appears in English QA rows.")
    if {row["fact_id"] for row in english_bio_qa_rows} != expected_fact_ids:
        raise ValueError("Not every fact appears in the merged BIO-QA dataset.")
    if {row["fact_id"] for row in turkish_rows} != branch_b_fact_ids:
        raise ValueError("Turkish repetition facts are not exactly Branch B facts.")
    if {row["fact_id"] for row in turkish_rows} & branch_a_fact_ids:
        raise ValueError("Branch A fact appeared in Turkish repetition.")
    if set(probes_en["fact_id"]) != expected_fact_ids or set(probes_tr["fact_id"]) != expected_fact_ids:
        raise ValueError("Probe files do not contain exactly one row for every fact.")
    if len(probes_en) != len(expected_fact_ids) or len(probes_tr) != len(expected_fact_ids):
        raise ValueError("Probe files do not contain exactly one row per fact.")

    summary["pipeline_output_validation"] = result
    Path(config.CANONICAL_GENERATION_SUMMARY_PATH).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result
