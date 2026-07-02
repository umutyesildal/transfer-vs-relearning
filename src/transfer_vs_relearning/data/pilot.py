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
    rows = read_csv_rows(dataset_dir / DATASET_FILES["canonical_profiles"])
    rng = random.Random(seed)
    strata: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        strata[tuple(row[field] for field in STRATA_FIELDS)].append(row)
    for bucket in strata.values():
        bucket.sort(key=lambda row: row["subject_id"])
        rng.shuffle(bucket)

    selected: list[dict[str, str]] = []
    ordered_keys = sorted(strata)
    index = 0
    while len(selected) < subjects and any(strata.values()):
        key = ordered_keys[index % len(ordered_keys)]
        if strata[key]:
            selected.append(strata[key].pop())
        index += 1
    selected = sorted(selected, key=lambda row: row["subject_id"])
    selected_ids = [row["subject_id"] for row in selected]
    selected_facts = expand_canonical_rows(selected)

    summary = {
        "seed": seed,
        "selection_algorithm": "round_robin_over_branch_name_type_rarity_popularity_strata_with_seeded_shuffle",
        "selected_subject_ids": selected_ids,
        "distribution_summary": {
            "subjects": subjects,
            "branch_group": dict(Counter(row["branch_group"] for row in selected)),
            "name_type": dict(Counter(row["name_type"] for row in selected)),
            "name_rarity_bucket": dict(Counter(row["name_rarity_bucket"] for row in selected)),
            "popularity_bucket": dict(Counter(row["popularity_bucket"] for row in selected)),
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
