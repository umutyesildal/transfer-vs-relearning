from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl, sha256_file, write_json


CITY_RELATIONS = {"born_in", "lives_in"}
REPLACED_TEMPLATE_SUFFIXES = {"decl_03", "qa_02", "direct_02"}


def build_relation_v2_binding_control(source_dir: Path, output_dir: Path) -> dict[str, Any]:
    gate_dir = source_dir / "acquisition_10_subjects_direct"
    train_path = gate_dir / "train.jsonl"
    validation_path = gate_dir / "validation.jsonl"
    profiles_path = source_dir / "data/canonical_subject_profiles_5000.csv"
    source_manifest_path = source_dir / "manifest.json"

    train_rows = read_jsonl(train_path)
    profiles = {row["subject_id"]: row for row in read_csv_rows(profiles_path)}
    transformed = [_transform_row(row, profiles[str(row["subject_id"])]) for row in train_rows]

    fact_counts = Counter(str(row["fact_id"]) for row in transformed)
    relation_counts = Counter(str(row["relation"]) for row in transformed)
    binding_rows = [row for row in transformed if str(row["template_id"]).endswith("_binding_control")]
    binding_fact_counts = Counter(str(row["fact_id"]) for row in binding_rows)

    if len(transformed) != 350 or len(fact_counts) != 50 or set(fact_counts.values()) != {7}:
        raise ValueError("Binding control must preserve 350 rows, 50 facts, and seven rows per fact")
    if relation_counts != Counter({relation: 70 for relation in (
        "profession", "born_in", "lives_in", "field_of_study", "works_in_industry"
    )}):
        raise ValueError(f"Unexpected relation row counts: {dict(relation_counts)}")
    if len(binding_rows) != 60 or set(binding_fact_counts.values()) != {3}:
        raise ValueError("Each of the twenty city facts must have exactly three binding-control rows")
    if any(row["relation"] not in CITY_RELATIONS for row in binding_rows):
        raise ValueError("Non-city relation was changed by the binding control")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_train = output_dir / "train.jsonl"
    _write_jsonl(output_train, transformed)
    manifest = {
        "version": "relation_v2_binding_control_v1",
        "source": {
            "dataset_manifest": str(source_manifest_path),
            "dataset_manifest_sha256": sha256_file(source_manifest_path),
            "train_sha256": sha256_file(train_path),
            "validation_sha256": sha256_file(validation_path),
            "canonical_profiles_sha256": sha256_file(profiles_path),
        },
        "contract": {
            "subjects": 10,
            "facts": 50,
            "train_rows": 350,
            "rows_per_fact": 7,
            "changed_rows": 60,
            "changed_rows_per_city_fact": 3,
            "unchanged_rows": 290,
            "heldout_validation_changed": False,
            "relations": [
                "profession", "born_in", "lives_in", "field_of_study", "works_in_industry"
            ],
        },
        "intervention": {
            "relations": ["born_in", "lives_in"],
            "replaced_template_suffixes": sorted(REPLACED_TEMPLATE_SUFFIXES),
            "symmetry": "same three replacement positions for both city relations",
            "target_answer_position": "final answer surface in every replacement row",
        },
        "files": {"train.jsonl": sha256_file(output_train)},
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def _transform_row(row: dict[str, Any], profile: dict[str, str]) -> dict[str, Any]:
    relation = str(row["relation"])
    template_id = str(row["template_id"])
    suffix = next((item for item in REPLACED_TEMPLATE_SUFFIXES if template_id.endswith(item)), None)
    if relation not in CITY_RELATIONS or suffix is None:
        return dict(row)

    subject = str(row["subject"])
    birthplace = profile["birthplace_en"]
    residence = profile["residence_en"]
    if birthplace == residence:
        raise ValueError(f"City binding control requires distinct cities for {row['subject_id']}")

    if relation == "born_in":
        answer = birthplace
        contrastive_question = f"{subject} currently lives in {residence}. Where was {subject} born instead?"
        paired_statement = f"Although {subject} currently lives in {residence}, {subject} was born in {birthplace}."
    else:
        answer = residence
        contrastive_question = f"{subject} was born in {birthplace}. Where does {subject} currently live instead?"
        paired_statement = f"Although {subject} was born in {birthplace}, {subject} currently lives in {residence}."

    if suffix == "decl_03":
        text = paired_statement
    elif suffix == "qa_02":
        text = f"Question: {contrastive_question}\nAnswer: {answer}"
    else:
        text = f"{contrastive_question} {answer}"

    transformed = dict(row)
    transformed["text"] = text
    transformed["answer"] = answer
    transformed["split"] = "relation_v2_binding_control_train"
    transformed["template_id"] = f"{template_id}_binding_control"
    return transformed


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(tmp, path)
