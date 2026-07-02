from __future__ import annotations

import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.constants import DATASET_FILES, RELATIONS
from transfer_vs_relearning.data.facts import expand_canonical_rows
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_json


STRATA_FIELDS = ("branch_group", "name_type", "name_rarity_bucket", "popularity_bucket")


def select_pilot_subjects(dataset_dir: Path, subjects: int = 100, seed: int = 42) -> dict[str, Any]:
    if subjects % 4 != 0:
        raise ValueError("Balanced diagnostic pilot size must be divisible by 4")
    rows = read_csv_rows(dataset_dir / DATASET_FILES["canonical_profiles"])
    rng = random.Random(seed)
    target_per_branch_name = subjects // 4
    selected: list[dict[str, str]] = []
    for branch in ("A", "B"):
        for name_type in ("english_like", "turkish_like"):
            candidates = [row for row in rows if row["branch_group"] == branch and row["name_type"] == name_type]
            selected.extend(_balanced_pick(candidates, target_per_branch_name, rng))

    selected = sorted(selected, key=lambda row: row["subject_id"])
    selected_ids = [row["subject_id"] for row in selected]
    selected_facts = expand_canonical_rows(selected)
    branch_counts = Counter(row["branch_group"] for row in selected)
    name_type_counts = Counter(row["name_type"] for row in selected)
    if subjects == 100:
        if branch_counts != {"A": 50, "B": 50}:
            raise ValueError(f"Pilot branch balance failed: {dict(branch_counts)}")
        if name_type_counts != {"english_like": 50, "turkish_like": 50}:
            raise ValueError(f"Pilot name-type balance failed: {dict(name_type_counts)}")

    summary = {
        "seed": seed,
        "selection_algorithm": "balanced_diagnostic_25_per_branch_x_name_type_with_seeded_rarity_popularity_round_robin",
        "selection_note": (
            "Balanced diagnostic pilot: exactly balanced by Branch A/B and English-like/Turkish-like names. "
            "It is not intended to estimate population-weighted overall accuracy."
        ),
        "selected_subject_ids": selected_ids,
        "distribution_summary": {
            "subjects": subjects,
            "branch_group": dict(branch_counts),
            "name_type": dict(name_type_counts),
            "name_rarity_bucket": dict(Counter(row["name_rarity_bucket"] for row in selected)),
            "popularity_bucket": dict(Counter(row["popularity_bucket"] for row in selected)),
            "branch_x_name_type": dict(Counter(f"{row['branch_group']}|{row['name_type']}" for row in selected)),
            "relation_counts": dict(Counter(fact.relation for fact in selected_facts)),
            "frequency_by_relation": {
                relation: dict(Counter(fact.frequency_bucket for fact in selected_facts if fact.relation == relation))
                for relation in RELATIONS
            },
        },
        "dataset_manifest_hash": sha256_file(dataset_dir / "manifest.json") if (dataset_dir / "manifest.json").exists() else None,
    }
    if summary["distribution_summary"]["relation_counts"] != {relation: subjects for relation in RELATIONS}:
        raise ValueError("Pilot selection did not produce exactly one fact per relation per subject")
    write_json(dataset_dir / f"pilot_{subjects}_subjects.json", summary)
    return summary


def _balanced_pick(rows: list[dict[str, str]], count: int, rng: random.Random) -> list[dict[str, str]]:
    strata: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        strata[(row["name_rarity_bucket"], row["popularity_bucket"])].append(row)
    for bucket in strata.values():
        bucket.sort(key=lambda row: row["subject_id"])
        rng.shuffle(bucket)

    ordered_keys = sorted(strata)
    selected: list[dict[str, str]] = []
    index = 0
    while len(selected) < count and any(strata.values()):
        key = ordered_keys[index % len(ordered_keys)]
        if strata[key]:
            selected.append(strata[key].pop())
        index += 1
    if len(selected) != count:
        raise ValueError(f"Could not sample {count} rows from branch/name-type group")
    return selected
