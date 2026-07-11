from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl, sha256_file, write_csv, write_json


DIAGNOSTIC_LEVELS = (
    "single_fact",
    "single_fact_direct_supervision",
    "single_relation_10_subjects",
    "single_relation_10_subjects_direct_supervision",
    "all_relations_10_subjects",
    "all_relations_10_subjects_direct_supervision",
)


def build_acquisition_diagnostics(ladder_dir: Path, output_dir: Path) -> dict[str, Any]:
    source_level_dir = ladder_dir / "10_subjects"
    train_rows = read_jsonl(source_level_dir / "train.jsonl")
    validation_rows = read_jsonl(source_level_dir / "validation.jsonl")
    exact_probe_rows = read_csv_rows(source_level_dir / "exact_prefix_probes_en.csv")
    source_pilot = json.loads((ladder_dir / "pilot_10_subjects.json").read_text(encoding="utf-8"))

    facts = _fact_representatives(train_rows)
    selected_fact = min(
        facts.values(),
        key=lambda row: (
            len(str(row["answer"]).split()),
            len(str(row["answer"])),
            str(row["fact_id"]),
        ),
    )
    selected_fact_id = str(selected_fact["fact_id"])
    selected_relation = str(selected_fact["relation"])
    selected_subject_id = str(selected_fact["subject_id"])

    selectors = {
        "single_fact": lambda row: str(row["fact_id"]) == selected_fact_id,
        "single_fact_direct_supervision": lambda row: str(row["fact_id"]) == selected_fact_id,
        "single_relation_10_subjects": lambda row: str(row["relation"]) == selected_relation,
        "single_relation_10_subjects_direct_supervision": lambda row: str(row["relation"]) == selected_relation,
        "all_relations_10_subjects": lambda row: True,
        "all_relations_10_subjects_direct_supervision": lambda row: True,
    }

    level_summaries: dict[str, Any] = {}
    for level in DIAGNOSTIC_LEVELS:
        selector = selectors[level]
        level_train = [row for row in train_rows if selector(row)]
        level_validation = [row for row in validation_rows if selector(row)]
        level_exact_probes = [row for row in exact_probe_rows if selector(row)]
        if level.endswith("direct_supervision"):
            level_train = _add_direct_supervision(level_train)
            level_validation = [_as_direct_supervision(row, "heldout") for row in level_validation]
        fact_ids = sorted({str(row["fact_id"]) for row in level_train})
        subject_ids = sorted({str(row["subject_id"]) for row in level_train})
        expected_rows_per_fact = 7 if level.endswith("direct_supervision") else 5
        if not fact_ids or len(level_train) != len(fact_ids) * expected_rows_per_fact:
            raise ValueError(
                f"Diagnostic level {level} does not have exactly {expected_rows_per_fact} train rows per fact"
            )
        if len(level_validation) != len(fact_ids) or len(level_exact_probes) != len(fact_ids):
            raise ValueError(f"Diagnostic level {level} validation/probe counts do not match its facts")

        level_dir = output_dir / level
        _write_jsonl(level_dir / "train.jsonl", level_train)
        _write_jsonl(level_dir / "validation.jsonl", level_validation)
        write_csv(level_dir / "exact_prefix_probes_en.csv", level_exact_probes, list(level_exact_probes[0]))
        pilot = {
            "selection_algorithm": "acquisition_diagnostic_nested_from_ladder_v1",
            "selected_subject_ids": subject_ids,
            "selected_fact_ids": fact_ids,
            "selected_relations": sorted({str(row["relation"]) for row in level_train}),
            "source_pilot_subject_ids": source_pilot["selected_subject_ids"],
        }
        write_json(level_dir / "pilot.json", pilot)
        summary = {
            "level": level,
            "subjects": len(subject_ids),
            "facts": len(fact_ids),
            "train_rows": len(level_train),
            "train_rows_per_fact": expected_rows_per_fact,
            "validation_rows": len(level_validation),
            "relations": pilot["selected_relations"],
            "fact_ids": fact_ids,
            "subject_ids": subject_ids,
        }
        write_json(level_dir / "summary.json", summary)
        level_summaries[level] = summary

    if level_summaries["single_fact"]["facts"] != 1:
        raise ValueError("Single-fact diagnostic must contain exactly one fact")
    if level_summaries["single_fact_direct_supervision"]["facts"] != 1:
        raise ValueError("Direct-supervision diagnostic must contain exactly one fact")
    if level_summaries["single_relation_10_subjects"]["facts"] != 10:
        raise ValueError("Single-relation diagnostic must contain one fact for each of 10 subjects")
    if level_summaries["single_relation_10_subjects_direct_supervision"]["facts"] != 10:
        raise ValueError("Direct-supervision single-relation diagnostic must contain 10 facts")
    if level_summaries["all_relations_10_subjects"]["facts"] != 50:
        raise ValueError("All-relations diagnostic must preserve all 50 ladder facts")
    if level_summaries["all_relations_10_subjects_direct_supervision"]["facts"] != 50:
        raise ValueError("Direct-supervision all-relations diagnostic must preserve all 50 facts")

    manifest = {
        "version": "acquisition_diagnostics_v1",
        "source_ladder_manifest_sha256": sha256_file(ladder_dir / "manifest.json"),
        "selection": {
            "fact_id": selected_fact_id,
            "subject_id": selected_subject_id,
            "relation": selected_relation,
            "answer": str(selected_fact["answer"]),
            "rule": "shortest whitespace-token count, then shortest characters, then fact_id",
        },
        "levels": level_summaries,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def _fact_representatives(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for row in rows:
        output.setdefault(str(row["fact_id"]), row)
    return output


def _add_direct_supervision(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = list(rows)
    qa_by_fact: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if str(row["text"]).startswith("Question: "):
            qa_by_fact.setdefault(str(row["fact_id"]), []).append(row)
    expected_fact_count = len({str(row["fact_id"]) for row in rows})
    if len(qa_by_fact) != expected_fact_count or any(len(items) != 2 for items in qa_by_fact.values()):
        raise ValueError("Expected exactly two QA rows per fact for direct supervision")
    for fact_id in sorted(qa_by_fact):
        output.extend(
            _as_direct_supervision(row, f"train_{index:02d}")
            for index, row in enumerate(qa_by_fact[fact_id], start=1)
        )
    return output


def _as_direct_supervision(row: dict[str, Any], suffix: str) -> dict[str, Any]:
    output = dict(row)
    question_line = str(row["text"]).splitlines()[0]
    if not question_line.startswith("Question: "):
        raise ValueError("Direct supervision source must start with a Question line")
    question = question_line.removeprefix("Question: ")
    output["text"] = f"{question} {row['answer']}"
    output["split"] = "acquisition_diagnostic_direct_supervision"
    output["template_id"] = f"{row['relation']}_en_direct_supervision_{suffix}"
    return output


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
    os.replace(tmp, path)
