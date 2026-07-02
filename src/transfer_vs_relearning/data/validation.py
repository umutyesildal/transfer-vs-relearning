from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.candidates import build_candidate_inventories, resolve_expected_answer
from transfer_vs_relearning.data.constants import (
    CANONICAL_COLUMNS,
    DATASET_FILES,
    PROBE_COLUMNS,
    RELATIONS,
    TRAINING_COLUMNS,
    VALID_BRANCHES,
    VALID_FREQUENCY,
    VALID_NAME_TYPES,
    VALID_POPULARITY,
    VALID_RARITY,
)
from transfer_vs_relearning.data.facts import Fact, expand_canonical_rows, facts_by_id
from transfer_vs_relearning.utils.io import count_lines, read_csv_rows, read_jsonl, sha256_file, write_json
from transfer_vs_relearning.utils.text import normalize_text


def _require_columns(actual: list[str], required: tuple[str, ...], label: str) -> None:
    missing = [column for column in required if column not in actual]
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


def load_dataset(dataset_dir: Path) -> tuple[list[dict[str, str]], list[Fact]]:
    canonical = read_csv_rows(dataset_dir / DATASET_FILES["canonical_profiles"])
    if not canonical:
        raise ValueError("Canonical profile CSV is empty")
    _require_columns(list(canonical[0]), CANONICAL_COLUMNS, "canonical profile CSV")
    return canonical, expand_canonical_rows(canonical)


def validate_dataset(dataset_dir: Path, write_outputs: bool = True) -> dict[str, Any]:
    canonical, facts = load_dataset(dataset_dir)
    fact_map = facts_by_id(facts)
    warnings: list[str] = []
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(len(canonical) == 5000, f"Expected 5000 canonical rows, found {len(canonical)}")
    check(len({r["row_id"] for r in canonical}) == len(canonical), "row_id values are not unique")
    check(len({r["subject_id"] for r in canonical}) == len(canonical), "subject_id values are not unique")
    check(len({r["subject"] for r in canonical}) == len(canonical), "subject names are not unique")
    branch_subject_counts = Counter(r["branch_group"] for r in canonical)
    check(branch_subject_counts == {"A": 2500, "B": 2500}, f"Unexpected branch subject counts: {dict(branch_subject_counts)}")
    check(len(facts) == 25000, f"Expected 25000 normalized facts, found {len(facts)}")
    check(len(fact_map) == len(facts), "fact_id values are not unique")
    relation_counts = Counter(f.relation for f in facts)
    check(all(relation_counts[relation] == 5000 for relation in RELATIONS), f"Unexpected relation counts: {dict(relation_counts)}")
    check(Counter(f.branch_group for f in facts) == {"A": 12500, "B": 12500}, "Unexpected branch fact counts")
    check(set(r["name_type"] for r in canonical) <= VALID_NAME_TYPES, "Invalid name_type values")
    check(set(r["name_rarity_bucket"] for r in canonical) <= VALID_RARITY, "Invalid name rarity values")
    check(set(r["popularity_bucket"] for r in canonical) <= VALID_POPULARITY, "Invalid popularity values")
    check(set(r["branch_group"] for r in canonical) <= VALID_BRANCHES, "Invalid branch_group values")
    ranks = sorted(int(r["popularity_rank"]) for r in canonical)
    check(ranks == list(range(1, 5001)), "Popularity ranks must cover 1 through 5000 exactly")
    for row in canonical:
        check(normalize_text(row["birthplace_en"]) != normalize_text(row["residence_en"]), f"{row['subject_id']} has matching birthplace/residence")
        check(row["birthplace_frequency_bucket"] == row["residence_frequency_bucket"], f"{row['subject_id']} has mismatched city frequency buckets")
        for suffix in ("profession", "birthplace", "residence", "university", "employer"):
            check(row[f"{suffix}_frequency_bucket"] in VALID_FREQUENCY, f"{row['subject_id']} invalid {suffix} frequency")
        for field in (
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
        ):
            check(bool(row[field].strip()), f"{row['subject_id']} has empty {field}")

    inventories = build_candidate_inventories(canonical)
    probes: dict[str, list[dict[str, str]]] = {
        "en": read_csv_rows(dataset_dir / DATASET_FILES["probes_en"]),
        "tr": read_csv_rows(dataset_dir / DATASET_FILES["probes_tr"]),
    }
    for language, rows in probes.items():
        if rows:
            _require_columns(list(rows[0]), PROBE_COLUMNS, f"{language} probes")
        check(len(rows) == 25000, f"Expected 25000 {language} probes, found {len(rows)}")
        check({row["fact_id"] for row in rows} == set(fact_map), f"{language} probes do not cover all facts")
        check(all(row["language"] == language for row in rows), f"{language} probe file has wrong language values")
        for row in rows:
            fact = fact_map.get(row["fact_id"])
            if fact is None:
                continue
            expected = fact.object_en if language == "en" else fact.object_tr
            check(row["subject"] == fact.subject, f"{language} probe subject mismatch for {row['fact_id']}")
            check(row["relation"] == fact.relation, f"{language} probe relation mismatch for {row['fact_id']}")
            check(row["expected_answer"] == expected, f"{language} probe answer mismatch for {row['fact_id']}")
            check(bool(row["question"].strip()), f"{language} probe empty question for {row['fact_id']}")
            check(bool(row["expected_answer"].strip()), f"{language} probe empty answer for {row['fact_id']}")
            for field in ("name_type", "name_rarity_bucket", "popularity_rank", "popularity_bucket", "frequency_bucket", "branch_group"):
                check(str(getattr(fact, field)) == str(row[field]), f"{language} probe {field} mismatch for {row['fact_id']}")
            try:
                resolve_expected_answer(row["relation"], language, row["expected_answer"], inventories)
            except ValueError as exc:
                errors.append(f"{language} probe expected answer resolution failed for {row['fact_id']}: {exc}")

    english_rows = read_jsonl(dataset_dir / DATASET_FILES["english_training"])
    turkish_rows = read_jsonl(dataset_dir / DATASET_FILES["turkish_repetition"])
    for label, rows in (("English training", english_rows), ("Turkish repetition", turkish_rows)):
        if rows:
            _require_columns(list(rows[0]), TRAINING_COLUMNS, label)
    english_fact_ids = {row["fact_id"] for row in english_rows}
    turkish_fact_ids = {row["fact_id"] for row in turkish_rows}
    check(english_fact_ids == set(fact_map), "English training does not contain all canonical facts")
    check(len(turkish_fact_ids) == 12500, f"Turkish repetition expected 12500 unique facts, found {len(turkish_fact_ids)}")
    check(all(fact_map[fid].branch_group == "B" for fid in turkish_fact_ids if fid in fact_map), "Turkish repetition contains Branch A facts")

    row_by_subject = {row["subject_id"]: row for row in canonical}
    frequency_counts: dict[str, dict[str, int]] = defaultdict(dict)
    for relation in RELATIONS:
        frequency_counts[relation] = dict(Counter(f.frequency_bucket for f in facts if f.relation == relation))

    file_stats = {}
    for key, rel_path in DATASET_FILES.items():
        path = dataset_dir / rel_path
        file_stats[key] = {
            "path": str(rel_path),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "sha256": sha256_file(path) if path.exists() else None,
            "line_count": count_lines(path) if path.exists() else 0,
        }

    manifest_like = {
        "canonical_subject_count": len(canonical),
        "normalized_fact_count": len(facts),
        "relation_counts": dict(relation_counts),
        "branch_subject_counts": dict(branch_subject_counts),
        "branch_fact_counts": dict(Counter(f.branch_group for f in facts)),
        "name_type_counts": dict(Counter(r["name_type"] for r in canonical)),
        "rarity_counts": dict(Counter(r["name_rarity_bucket"] for r in canonical)),
        "popularity_counts": dict(Counter(r["popularity_bucket"] for r in canonical)),
        "frequency_counts_by_relation": frequency_counts,
        "english_training_row_count": len(english_rows),
        "english_training_unique_fact_count": len(english_fact_ids),
        "turkish_repetition_row_count": len(turkish_rows),
        "turkish_repetition_unique_fact_count": len(turkish_fact_ids),
        "probe_row_counts": {language: len(rows) for language, rows in probes.items()},
        "candidate_inventory_sizes": {family: len(items) for family, items in inventories.items()},
        "validation_status": "passed" if not errors else "failed",
        "validation_warnings": warnings,
        "validation_errors": errors,
        "files": file_stats,
    }
    if write_outputs:
        write_json(dataset_dir / "validation_summary.json", manifest_like)
        (dataset_dir / "validation_summary.md").write_text(
            _render_validation_markdown(manifest_like),
            encoding="utf-8",
        )
    if errors:
        raise ValueError("Dataset validation failed:\n" + "\n".join(errors[:50]))
    return manifest_like


def _render_validation_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Dataset Validation Summary",
        "",
        f"- status: {summary['validation_status']}",
        f"- canonical subjects: {summary['canonical_subject_count']}",
        f"- normalized facts: {summary['normalized_fact_count']}",
        f"- relation counts: {summary['relation_counts']}",
        f"- branch subject counts: {summary['branch_subject_counts']}",
        f"- branch fact counts: {summary['branch_fact_counts']}",
        f"- English training rows: {summary['english_training_row_count']}",
        f"- English training unique facts: {summary['english_training_unique_fact_count']}",
        f"- Turkish repetition rows: {summary['turkish_repetition_row_count']}",
        f"- Turkish repetition unique facts: {summary['turkish_repetition_unique_fact_count']}",
        f"- probe rows: {summary['probe_row_counts']}",
        f"- candidate inventory sizes: {summary['candidate_inventory_sizes']}",
        "",
        "## Warnings",
        "",
    ]
    if summary["validation_warnings"]:
        lines.extend(f"- {warning}" for warning in summary["validation_warnings"])
    else:
        lines.append("- none")
    lines.extend(["", "## Errors", ""])
    if summary["validation_errors"]:
        lines.extend(f"- {error}" for error in summary["validation_errors"])
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)
