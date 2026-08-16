from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.candidates import (
    RELATION_TO_FAMILY,
    build_candidate_inventories,
    candidate_for_fact,
)
from transfer_vs_relearning.data.constants import RELATION_MAP
from transfer_vs_relearning.data.m1_form_generalization import FORM_IDS, FORM_TEMPLATES
from transfer_vs_relearning.data.pre_m2_followup import RELATIONS, SCAFFOLDS as ENGLISH_SCAFFOLDS
from transfer_vs_relearning.data.qwen_pre_m2 import (
    DIRECTIONS,
    TURKISH_FORM_TEMPLATES,
    TURKISH_SCAFFOLDS,
)
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


REGISTRY_VERSION = "eval_v1_factual_registry_v1"
CHEAP_CELLS = tuple(
    (form_id, scaffold_id)
    for form_id in FORM_IDS
    for scaffold_id in ("direct", "qa")
)


def _selected_profiles(
    canonical_rows: list[dict[str, str]], selected_subject_ids: set[str]
) -> list[dict[str, str]]:
    profiles = sorted(
        (row for row in canonical_rows if row["subject_id"] in selected_subject_ids),
        key=lambda row: row["subject_id"],
    )
    if len(profiles) != 100 or len({row["subject_id"] for row in profiles}) != 100:
        raise ValueError(f"Expected 100 unique selected profiles, found {len(profiles)}")
    branch_counts = Counter(row["branch_group"] for row in profiles)
    if branch_counts != Counter({"A": 50, "B": 50}):
        raise ValueError(f"Expected 50/50 selected branch balance, found {dict(branch_counts)}")
    return profiles


def _english_source_index(
    source_rows: list[dict[str, str]], selected_subject_ids: set[str]
) -> dict[tuple[str, str, str], dict[str, str]]:
    if len(source_rows) != 4_000:
        raise ValueError(f"Expected 4,000 English source probes, found {len(source_rows)}")
    keys = [
        (row["fact_id"], row["form_id"], row["scaffold_id"])
        for row in source_rows
    ]
    if len(set(keys)) != 4_000:
        raise ValueError("English source registry contains duplicate fact/form/scaffold cells")
    if {row["subject_id"] for row in source_rows} != selected_subject_ids:
        raise ValueError("English source registry subjects do not match the selected population")
    return {key: row for key, row in zip(keys, source_rows, strict=True)}


def build_full_bilingual_registry(
    canonical_rows: list[dict[str, str]],
    selected_subject_ids: set[str],
    english_source_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    profiles = _selected_profiles(canonical_rows, selected_subject_ids)
    english_source = _english_source_index(english_source_rows, selected_subject_ids)
    inventories = build_candidate_inventories(canonical_rows)
    probes: list[dict[str, Any]] = []

    for profile in profiles:
        for relation in RELATIONS:
            en_column, tr_column, frequency_column = RELATION_MAP[relation]
            fact_id = f"{profile['subject_id']}_{relation}"
            correct = candidate_for_fact(profile, relation, inventories)
            for direction, prompt_language, answer_language in DIRECTIONS:
                form_templates = (
                    FORM_TEMPLATES if prompt_language == "en" else TURKISH_FORM_TEMPLATES
                )
                scaffolds = (
                    ENGLISH_SCAFFOLDS if prompt_language == "en" else TURKISH_SCAFFOLDS
                )
                for form_id in FORM_IDS:
                    question = form_templates[relation][form_id].format(
                        subject=profile["subject"]
                    )
                    for scaffold_id, scaffold in scaffolds.items():
                        source = english_source[(fact_id, form_id, scaffold_id)]
                        probe = {
                            "probe_id": (
                                f"{profile['subject_id']}_{relation}_{direction}_"
                                f"{form_id}_{scaffold_id}"
                            ),
                            "fact_id": fact_id,
                            "subject_id": profile["subject_id"],
                            "subject": profile["subject"],
                            "relation": relation,
                            "direction": direction,
                            "prompt_language": prompt_language,
                            "answer_language": answer_language,
                            "form_id": form_id,
                            "scaffold_id": scaffold_id,
                            "canonical_m1_exposure": source["canonical_m1_exposure"],
                            "wp1b_counterbalance_cell": source["wp1b_counterbalance_cell"],
                            "question": question,
                            "rendered_prompt": scaffold.format(question=question),
                            "expected_answer": profile[
                                en_column if answer_language == "en" else tr_column
                            ],
                            "correct_object_id": correct.object_id,
                            "candidate_family": RELATION_TO_FAMILY[relation],
                            "branch_group": profile["branch_group"],
                            "name_type": profile["name_type"],
                            "name_rarity_bucket": profile["name_rarity_bucket"],
                            "popularity_bucket": profile["popularity_bucket"],
                            "frequency_bucket": profile[frequency_column],
                            "template_id": (
                                f"{REGISTRY_VERSION}_{relation}_{direction}_"
                                f"{form_id}_{scaffold_id}"
                            ),
                        }
                        if direction == "en_to_en":
                            comparable = (
                                "subject_id",
                                "subject",
                                "relation",
                                "form_id",
                                "scaffold_id",
                                "canonical_m1_exposure",
                                "wp1b_counterbalance_cell",
                                "question",
                                "rendered_prompt",
                                "expected_answer",
                                "branch_group",
                                "name_type",
                                "name_rarity_bucket",
                                "popularity_bucket",
                                "frequency_bucket",
                            )
                            mismatches = [key for key in comparable if probe[key] != source[key]]
                            if mismatches:
                                raise ValueError(
                                    f"EN projection differs from frozen source for {fact_id}: "
                                    f"{mismatches}"
                                )
                        probes.append(probe)

    if len(probes) != 12_000 or len({row["probe_id"] for row in probes}) != 12_000:
        raise ValueError("Full bilingual registry must contain 12,000 unique probes")
    return probes


def build_cheap_bilingual_panel(full_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_cell = {
        (row["fact_id"], row["direction"], row["form_id"], row["scaffold_id"]): row
        for row in full_rows
    }
    if len(by_cell) != 12_000:
        raise ValueError("Full registry is incomplete or contains duplicate cells")

    facts_by_stratum: dict[tuple[str, str], list[str]] = defaultdict(list)
    fact_metadata: dict[str, tuple[str, str]] = {}
    for row in full_rows:
        fact_metadata[row["fact_id"]] = (row["relation"], row["branch_group"])
    for fact_id, stratum in fact_metadata.items():
        facts_by_stratum[stratum].append(fact_id)

    direction_ids = [direction for direction, _, _ in DIRECTIONS]
    cheap: list[dict[str, Any]] = []
    for direction_index, direction in enumerate(direction_ids):
        for relation_index, relation in enumerate(RELATIONS):
            for branch_index, branch in enumerate(("A", "B")):
                fact_ids = sorted(facts_by_stratum[(relation, branch)])
                if len(fact_ids) != 50:
                    raise ValueError(
                        f"Expected 50 facts in {relation}/{branch}, found {len(fact_ids)}"
                    )
                offset = direction_index + (2 * relation_index) + (4 * branch_index)
                for fact_index, fact_id in enumerate(fact_ids):
                    form_id, scaffold_id = CHEAP_CELLS[(fact_index + offset) % len(CHEAP_CELLS)]
                    source = by_cell[(fact_id, direction, form_id, scaffold_id)]
                    cheap.append(
                        {
                            **source,
                            "probe_id": f"cheap_{source['probe_id']}",
                            "panel_role": "dense_one_probe_per_fact_per_direction",
                            "selection_cell_index": CHEAP_CELLS.index((form_id, scaffold_id)),
                        }
                    )

    if len(cheap) != 1_500 or len({row["probe_id"] for row in cheap}) != 1_500:
        raise ValueError("Cheap bilingual panel must contain 1,500 unique probes")
    coverage = Counter((row["fact_id"], row["direction"]) for row in cheap)
    if set(coverage.values()) != {1} or len(coverage) != 1_500:
        raise ValueError("Cheap panel must select exactly one probe per fact and direction")
    return cheap


def _nested_counts(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> dict[str, int]:
    return {
        "|".join(key): count
        for key, count in sorted(Counter(tuple(str(row[field]) for field in fields) for row in rows).items())
    }


def _manifest_path(path: Path, repo_root: Path) -> str:
    return str(path.relative_to(repo_root)) if path.is_relative_to(repo_root) else str(path)


def build_eval_v1_factual_registries(
    repo_root: Path, *, output_dir: Path | None = None
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    output_dir = (
        output_dir or repo_root / "configs/evaluation/registries"
    ).resolve()
    canonical_path = repo_root / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv"
    selection_path = repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json"
    source_path = output_dir / "eval_v1_factual_full_4000.csv"
    full_path = output_dir / "eval_v1_factual_full_bilingual_12000.csv"
    cheap_path = output_dir / "eval_v1_factual_cheap_bilingual_1500.csv"
    manifest_path = output_dir / "eval_v1_factual_registry_manifest.json"

    canonical_rows = read_csv_rows(canonical_path)
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selected_subject_ids = set(selection["selected_subject_ids"])
    source_rows = read_csv_rows(source_path)
    full_rows = build_full_bilingual_registry(
        canonical_rows, selected_subject_ids, source_rows
    )
    cheap_rows = build_cheap_bilingual_panel(full_rows)
    write_csv(full_path, full_rows)
    write_csv(cheap_path, cheap_rows)

    manifest = {
        "schema_version": 1,
        "registry_version": REGISTRY_VERSION,
        "status": "frozen_input",
        "selection_seed": selection["selection_seed"],
        "selection_formula": (
            "within each direction/relation/branch stratum, sort fact_id and choose "
            "CHEAP_CELLS[(fact_index + direction_index + 2*relation_index + "
            "4*branch_index) mod 8]"
        ),
        "cheap_cells_in_order": [
            {"form_id": form_id, "scaffold_id": scaffold_id}
            for form_id, scaffold_id in CHEAP_CELLS
        ],
        "inputs": {
            "canonical_profiles": {
                "path": _manifest_path(canonical_path, repo_root),
                "sha256": sha256_file(canonical_path),
                "rows": len(canonical_rows),
            },
            "selected_population": {
                "path": _manifest_path(selection_path, repo_root),
                "sha256": sha256_file(selection_path),
                "subjects": len(selected_subject_ids),
                "facts": len(selected_subject_ids) * len(RELATIONS),
            },
            "english_source_audit": {
                "path": _manifest_path(source_path, repo_root),
                "sha256": sha256_file(source_path),
                "rows": len(source_rows),
                "role": "frozen_en_to_en_projection_source_not_the_scientific_full_registry",
            },
        },
        "outputs": {
            "full_bilingual": {
                "path": _manifest_path(full_path, repo_root),
                "sha256": sha256_file(full_path),
                "rows": len(full_rows),
                "facts": len({row["fact_id"] for row in full_rows}),
                "direction_counts": _nested_counts(full_rows, ("direction",)),
                "cell_counts": _nested_counts(
                    full_rows, ("direction", "relation", "form_id", "scaffold_id")
                ),
            },
            "cheap_bilingual": {
                "path": _manifest_path(cheap_path, repo_root),
                "sha256": sha256_file(cheap_path),
                "rows": len(cheap_rows),
                "facts": len({row["fact_id"] for row in cheap_rows}),
                "direction_counts": _nested_counts(cheap_rows, ("direction",)),
                "cell_counts": _nested_counts(
                    cheap_rows,
                    ("direction", "relation", "branch_group", "form_id", "scaffold_id"),
                ),
            },
        },
        "validation": {
            "full_unique_probe_ids": len({row["probe_id"] for row in full_rows}),
            "cheap_unique_probe_ids": len({row["probe_id"] for row in cheap_rows}),
            "cheap_fact_direction_denominator": len(
                {(row["fact_id"], row["direction"]) for row in cheap_rows}
            ),
            "english_projection_exact": True,
        },
    }
    write_json(manifest_path, manifest)
    return manifest
