"""
Source-list loading, cleaning, validation, and pairing.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from assignment_rules import normalize_turkish_text
from assignment_rules import is_single_name_component
from config import SOURCE_LIST_FILES

JOB_PATTERN = re.compile(r"^\s*(.*?)\s+(?:—|–|-)\s+(\d+(?:\.\d+)?)\s*$")


def clean_source_lines(path: Path) -> tuple[list[str], dict]:
    """Reads, trims, de-duplicates, and reports one source TXT file."""
    if not path.exists():
        raise FileNotFoundError(f"Required source file is missing: {path}")

    raw_lines = path.read_text(encoding="utf-8").splitlines()
    cleaned = []
    seen = set()
    empty_count = 0
    duplicate_count = 0

    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line:
            empty_count += 1
            continue
        if line in seen:
            duplicate_count += 1
            continue
        seen.add(line)
        cleaned.append(line)

    if not cleaned:
        raise ValueError(f"Source file becomes empty after cleaning: {path}")

    report = {
        "original_line_count": len(raw_lines),
        "cleaned_line_count": len(cleaned),
        "empty_lines": empty_count,
        "duplicates_removed": duplicate_count,
    }
    return cleaned, report


def load_clean_source_lists(source_dir: str, report_path: str | None = None) -> tuple[dict[str, list[str]], dict]:
    """Loads and cleans every required source-list file."""
    base_path = Path(source_dir)
    source_lists = {}
    report = {"files": {}}

    for filename in SOURCE_LIST_FILES:
        lines, file_report = clean_source_lines(base_path / filename)
        if filename in {"names_en.txt", "names_tr.txt", "surnames_en.txt", "surnames_tr.txt"}:
            single_component_lines = [line for line in lines if is_single_name_component(line)]
            excluded = len(lines) - len(single_component_lines)
            file_report["multi_component_entries_excluded"] = excluded
            file_report["single_component_cleaned_line_count"] = len(single_component_lines)
            lines = single_component_lines
            if not lines:
                raise ValueError(f"Name source file has no single-component entries after filtering: {filename}")
        else:
            file_report["multi_component_entries_excluded"] = 0
            file_report["single_component_cleaned_line_count"] = file_report["cleaned_line_count"]
        source_lists[filename] = lines
        report["files"][filename] = file_report

    if report_path:
        output_path = Path(report_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return source_lists, report


def parse_job_line(line: str) -> tuple[str, int]:
    """Parses a profession line such as 'Footballer — 100'."""
    match = JOB_PATTERN.match(line)
    if not match:
        raise ValueError(f"Invalid profession line format: {line!r}")

    profession = match.group(1).strip()
    score_raw = match.group(2)
    if not profession:
        raise ValueError(f"Profession text is empty: {line!r}")

    score = float(score_raw)
    if not score.is_integer():
        raise ValueError(f"Profession score must be an integer: {line!r}")
    score_int = int(score)
    if score_int < 0 or score_int > 100:
        raise ValueError(f"Profession score must be between 0 and 100: {line!r}")
    return profession, score_int


def build_profession_pairs(jobs_en: list[str], jobs_tr: list[str]) -> list[dict]:
    """Validates aligned English/Turkish profession files and returns profession pairs."""
    if len(jobs_en) != len(jobs_tr):
        raise ValueError(
            "English and Turkish job files must have the same cleaned line count: "
            f"{len(jobs_en)} != {len(jobs_tr)}"
        )

    pairs = []
    for index, (line_en, line_tr) in enumerate(zip(jobs_en, jobs_tr), start=1):
        profession_en, score_en = parse_job_line(line_en)
        profession_tr, score_tr = parse_job_line(line_tr)
        if score_en != score_tr:
            raise ValueError(
                f"Profession score mismatch at aligned row {index}: "
                f"{profession_en}={score_en}, {profession_tr}={score_tr}"
            )
        pairs.append({
            "profession_en": profession_en,
            "profession_tr": profession_tr,
            "profession_popularity_score": score_en,
            "profession_source_rank": index,
        })
    return pairs


def build_proper_noun_pairs(items_en: list[str], items_tr: list[str]) -> list[dict]:
    """Builds bilingual canonical object pairs without inventing translations."""
    pairs = []
    seen = set()

    for rank, item in enumerate(items_en, start=1):
        key = (item, item)
        if key in seen:
            continue
        seen.add(key)
        pairs.append({
            "object_en": item,
            "object_tr": item,
            "origin": "english_origin",
            "source_rank": rank,
        })

    for rank, item in enumerate(items_tr, start=1):
        object_en = normalize_turkish_text(item)
        key = (object_en, item)
        if key in seen:
            continue
        seen.add(key)
        pairs.append({
            "object_en": object_en,
            "object_tr": item,
            "origin": "turkish_origin",
            "source_rank": rank,
        })

    if not pairs:
        raise ValueError("Proper-noun pair pool is empty after normalization and de-duplication.")
    return pairs


def load_generation_sources(source_dir: str, report_path: str | None = None) -> tuple[dict, dict]:
    """Loads cleaned source lists and builds validated generation pools."""
    source_lists, report = load_clean_source_lists(source_dir, report_path=report_path)
    professions = build_profession_pairs(source_lists["jobs_en.txt"], source_lists["jobs_tr.txt"])
    cities = build_proper_noun_pairs(source_lists["cities_en.txt"], source_lists["cities_tr.txt"])
    companies = build_proper_noun_pairs(source_lists["company_en.txt"], source_lists["company_tr.txt"])
    universities = build_proper_noun_pairs(source_lists["university_en.txt"], source_lists["university_tr.txt"])

    report["derived"] = {
        "profession_pairs": len(professions),
        "city_pairs": len(cities),
        "company_pairs": len(companies),
        "university_pairs": len(universities),
    }
    if report_path:
        output_path = Path(report_path)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "source_lists": source_lists,
        "professions": professions,
        "cities": cities,
        "companies": companies,
        "universities": universities,
    }, report
