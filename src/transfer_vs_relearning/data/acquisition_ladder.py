from __future__ import annotations

import json
import os
import random
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.constants import DATASET_FILES, PROBE_COLUMNS, RELATIONS
from transfer_vs_relearning.training.recipe_data import QUESTION_TEMPLATES, build_qa_text
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl, sha256_file, write_csv, write_json


LADDER_SUBJECT_COUNTS = (10, 100, 500)
MICRO_CELL_COUNTS = {
    ("A", "english_like"): 3,
    ("A", "turkish_like"): 2,
    ("B", "english_like"): 2,
    ("B", "turkish_like"): 3,
}


def build_acquisition_ladder(
    dataset_dir: Path,
    output_dir: Path,
    *,
    seed: int = 42,
) -> dict[str, Any]:
    canonical_rows = read_csv_rows(dataset_dir / DATASET_FILES["canonical_profiles"])
    english_rows = read_jsonl(dataset_dir / DATASET_FILES["english_training"])
    probe_rows = read_csv_rows(dataset_dir / DATASET_FILES["probes_en"])
    probe_by_fact = {row["fact_id"]: row for row in probe_rows}

    ordered_cells = _ordered_subject_cells(canonical_rows, seed)
    selected_by_size = {
        subjects: _select_nested_subject_ids(ordered_cells, subjects)
        for subjects in LADDER_SUBJECT_COUNTS
    }
    _validate_nested_selections(selected_by_size)

    rows_by_fact: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in english_rows:
        rows_by_fact[str(row["fact_id"])].append(row)
    for rows in rows_by_fact.values():
        rows.sort(key=lambda row: (str(row["template_id"]), str(row["text"])))

    level_summaries: dict[str, Any] = {}
    for subjects, selected_subject_ids in selected_by_size.items():
        level_dir = output_dir / f"{subjects}_subjects"
        train_rows, validation_rows, exact_probes = _build_level_records(
            selected_subject_ids,
            rows_by_fact,
            probe_by_fact,
        )
        pilot_payload = _pilot_payload(
            canonical_rows,
            selected_subject_ids,
            subjects=subjects,
            seed=seed,
            dataset_manifest=dataset_dir / "manifest.json",
        )

        train_path = level_dir / "train.jsonl"
        validation_path = level_dir / "validation.jsonl"
        exact_probe_path = level_dir / "exact_prefix_probes_en.csv"
        pilot_path = output_dir / f"pilot_{subjects}_subjects.json"
        _write_jsonl(train_path, train_rows)
        _write_jsonl(validation_path, validation_rows)
        write_csv(exact_probe_path, exact_probes, list(PROBE_COLUMNS))
        write_json(pilot_path, pilot_payload)

        summary = {
            "subjects": subjects,
            "facts": subjects * len(RELATIONS),
            "train_rows": len(train_rows),
            "validation_rows": len(validation_rows),
            "exact_prefix_probe_rows": len(exact_probes),
            "train_rows_per_fact": 5,
            "training_composition": {"declarative": 3, "qa": 2},
            "loss_contract": "answer_only",
            "selected_subject_ids": selected_subject_ids,
            "files": {
                "train": str(train_path),
                "validation": str(validation_path),
                "exact_prefix_probes_en": str(exact_probe_path),
                "pilot_subjects": str(pilot_path),
            },
        }
        write_json(level_dir / "summary.json", summary)
        level_summaries[str(subjects)] = summary

    manifest = {
        "version": "acquisition_ladder_v1",
        "seed": seed,
        "source_dataset_dir": str(dataset_dir),
        "source_manifest_sha256": sha256_file(dataset_dir / "manifest.json"),
        "levels": level_summaries,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def _ordered_subject_cells(
    rows: list[dict[str, str]],
    seed: int,
) -> dict[tuple[str, str], list[dict[str, str]]]:
    cells: dict[tuple[str, str], list[dict[str, str]]] = {}
    for branch in ("A", "B"):
        for name_type in ("english_like", "turkish_like"):
            cell_rows = [
                row
                for row in rows
                if row["branch_group"] == branch and row["name_type"] == name_type
            ]
            cells[(branch, name_type)] = _balanced_order(
                cell_rows,
                random.Random(f"{seed}:{branch}:{name_type}"),
            )
    return cells


def _balanced_order(rows: list[dict[str, str]], rng: random.Random) -> list[dict[str, str]]:
    strata: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        strata[(row["name_rarity_bucket"], row["popularity_bucket"])].append(row)
    for bucket in strata.values():
        bucket.sort(key=lambda row: row["subject_id"])
        rng.shuffle(bucket)

    ordered: list[dict[str, str]] = []
    keys = sorted(strata)
    rng.shuffle(keys)
    while any(strata.values()):
        for key in keys:
            if strata[key]:
                ordered.append(strata[key].pop())
    return ordered


def _select_nested_subject_ids(
    cells: dict[tuple[str, str], list[dict[str, str]]],
    subjects: int,
) -> list[str]:
    if subjects == 10:
        allocations = MICRO_CELL_COUNTS
    elif subjects % 4 == 0:
        allocations = {key: subjects // 4 for key in cells}
    else:
        raise ValueError(f"Unsupported acquisition ladder size: {subjects}")

    selected = []
    for key in sorted(cells):
        count = allocations[key]
        if len(cells[key]) < count:
            raise ValueError(f"Not enough subjects in {key}: requested {count}, found {len(cells[key])}")
        selected.extend(row["subject_id"] for row in cells[key][:count])
    return sorted(selected)


def _validate_nested_selections(selected_by_size: dict[int, list[str]]) -> None:
    previous: set[str] = set()
    for subjects in LADDER_SUBJECT_COUNTS:
        selected = selected_by_size[subjects]
        if len(selected) != subjects or len(set(selected)) != subjects:
            raise ValueError(f"Acquisition selection for {subjects} subjects is not unique and complete")
        current = set(selected)
        if not previous.issubset(current):
            raise ValueError("Acquisition ladder subject selections are not nested")
        previous = current


def _build_level_records(
    selected_subject_ids: list[str],
    rows_by_fact: dict[str, list[dict[str, Any]]],
    probe_by_fact: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    selected = set(selected_subject_ids)
    fact_ids = sorted(
        fact_id
        for fact_id, rows in rows_by_fact.items()
        if rows and str(rows[0]["subject_id"]) in selected
    )
    expected_fact_count = len(selected_subject_ids) * len(RELATIONS)
    if len(fact_ids) != expected_fact_count:
        raise ValueError(f"Expected {expected_fact_count} selected facts, found {len(fact_ids)}")

    train_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    exact_probes: list[dict[str, str]] = []
    for fact_id in fact_ids:
        declarative_rows = rows_by_fact[fact_id]
        if len(declarative_rows) < 3:
            raise ValueError(f"Fact {fact_id} has fewer than three declarative records")
        probe = probe_by_fact[fact_id]

        for index, source in enumerate(declarative_rows[:3], start=1):
            row = deepcopy(source)
            row["split"] = "acquisition_ladder_train"
            row["template_id"] = f"{source['template_id']}__ladder_d{index:02d}"
            train_rows.append(row)

        qa_candidates = []
        relation = str(declarative_rows[0]["relation"])
        subject = str(declarative_rows[0]["subject"])
        answer = str(declarative_rows[0]["answer"])
        for template_index, template in enumerate(QUESTION_TEMPLATES[relation]):
            question = template.format(subject=subject)
            if question != probe["question"]:
                qa_candidates.append((template_index, question))
        if len(qa_candidates) < 2:
            raise ValueError(f"Fact {fact_id} does not have two QA templates distinct from its held-out probe")
        for qa_index, (template_index, _) in enumerate(qa_candidates[:2], start=1):
            row = deepcopy(declarative_rows[0])
            row["split"] = "acquisition_ladder_train"
            row["text"] = build_qa_text(subject, relation, answer, template_index)
            row["template_id"] = f"{relation}_en_ladder_qa_{qa_index:02d}"
            train_rows.append(row)

        validation = deepcopy(declarative_rows[0])
        validation["split"] = "acquisition_ladder_validation"
        validation["text"] = f"Question: {probe['question']}\nAnswer: {answer}"
        validation["template_id"] = f"{relation}_en_ladder_heldout_probe"
        validation_rows.append(validation)

        exact_source = next(
            (row for row in declarative_rows if str(row["text"]).endswith(answer)),
            declarative_rows[0],
        )
        answer_start = str(exact_source["text"]).rfind(answer)
        if answer_start < 0:
            raise ValueError(f"Answer for {fact_id} is missing from exact-prefix source")
        exact_probe = dict(probe)
        exact_probe["question"] = str(exact_source["text"])[:answer_start].rstrip()
        exact_probe["template_id"] = f"{exact_source['template_id']}__exact_prefix"
        exact_probes.append(exact_probe)

    return train_rows, validation_rows, exact_probes


def _pilot_payload(
    canonical_rows: list[dict[str, str]],
    selected_subject_ids: list[str],
    *,
    subjects: int,
    seed: int,
    dataset_manifest: Path,
) -> dict[str, Any]:
    selected = set(selected_subject_ids)
    rows = [row for row in canonical_rows if row["subject_id"] in selected]
    return {
        "seed": seed,
        "selection_algorithm": "nested_balanced_acquisition_ladder_v1",
        "selection_note": "Diagnostic training subset; the 10-subject level balances branch and name-type margins.",
        "selected_subject_ids": selected_subject_ids,
        "distribution_summary": {
            "subjects": subjects,
            "facts": subjects * len(RELATIONS),
            "branch_group": dict(sorted(Counter(row["branch_group"] for row in rows).items())),
            "name_type": dict(sorted(Counter(row["name_type"] for row in rows).items())),
            "branch_x_name_type": dict(
                sorted(Counter(f"{row['branch_group']}|{row['name_type']}" for row in rows).items())
            ),
            "name_rarity_bucket": dict(sorted(Counter(row["name_rarity_bucket"] for row in rows).items())),
            "popularity_bucket": dict(sorted(Counter(row["popularity_bucket"] for row in rows).items())),
            "relation_counts": {relation: subjects for relation in RELATIONS},
        },
        "dataset_manifest_hash": sha256_file(dataset_manifest),
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
    os.replace(tmp, path)
