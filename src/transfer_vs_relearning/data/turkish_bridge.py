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
from transfer_vs_relearning.utils.io import read_csv_rows
from transfer_vs_relearning.utils.text import normalize_text


VERSION = "turkish_bridge_v1"
RELATIONS = ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")
ENGLISH_QUESTIONS = {
    "profession": "What does {subject} do for work?",
    "born_in": "Where was {subject} born?",
    "lives_in": "Where does {subject} live?",
    "field_of_study": "What field did {subject} study?",
    "works_in_industry": "What industry does {subject} work in?",
}
TURKISH_QUESTIONS = {
    "profession": "{subject} ne iş yapıyor?",
    "born_in": "{subject} nerede doğdu?",
    "lives_in": "{subject} nerede yaşıyor?",
    "field_of_study": "{subject} hangi alanda eğitim aldı?",
    "works_in_industry": "{subject} hangi sektörde çalışıyor?",
}
SCAFFOLDS = {
    "en": "Question: {question}\nAnswer:",
    "tr": "Soru: {question}\nCevap:",
}
DIRECTIONS = (
    ("en_to_en", "en", "en"),
    ("tr_to_en", "tr", "en"),
    ("tr_to_tr", "tr", "tr"),
)


def selected_profiles(canonical_rows: list[dict[str, str]], selected_subject_ids: set[str]) -> list[dict[str, str]]:
    profiles = [row for row in canonical_rows if row["subject_id"] in selected_subject_ids]
    if len(profiles) != len(selected_subject_ids):
        found = {row["subject_id"] for row in profiles}
        raise ValueError(f"Missing selected subjects: {sorted(selected_subject_ids - found)}")
    return sorted(profiles, key=lambda row: row["subject_id"])


def build_localization_rows(canonical_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    inventories = build_candidate_inventories(canonical_rows)
    rows: list[dict[str, Any]] = []
    for family, candidates in sorted(inventories.items()):
        if family not in {RELATION_TO_FAMILY[relation] for relation in RELATIONS}:
            continue
        for candidate in candidates:
            rows.append(
                {
                    "object_id": candidate.object_id,
                    "family": family,
                    "canonical_en": candidate.object_en,
                    "canonical_tr": candidate.object_tr,
                    "aliases_en_json": json.dumps([candidate.object_en], ensure_ascii=False),
                    "aliases_tr_json": json.dumps([candidate.object_tr], ensure_ascii=False),
                    "normalization": "NFC plus project comparison normalization",
                }
            )
    _validate_localization(rows)
    return rows


def _validate_localization(rows: list[dict[str, Any]]) -> None:
    object_ids = [str(row["object_id"]) for row in rows]
    if len(object_ids) != len(set(object_ids)):
        raise ValueError("Localization registry contains duplicate object IDs")
    for language_key in ("canonical_en", "canonical_tr"):
        seen: dict[tuple[str, str], str] = {}
        for row in rows:
            key = (str(row["family"]), normalize_text(str(row[language_key])))
            previous = seen.get(key)
            if previous and previous != row["object_id"]:
                raise ValueError(f"Ambiguous {language_key} surface in {row['family']}: {row[language_key]!r}")
            seen[key] = str(row["object_id"])


def build_bridge_probes(
    canonical_rows: list[dict[str, str]],
    selected_subject_ids: set[str],
) -> list[dict[str, Any]]:
    inventories = build_candidate_inventories(canonical_rows)
    probes: list[dict[str, Any]] = []
    for profile in selected_profiles(canonical_rows, selected_subject_ids):
        for relation in RELATIONS:
            en_column, tr_column, frequency_column = RELATION_MAP[relation]
            correct = candidate_for_fact(profile, relation, inventories)
            for direction, prompt_language, answer_language in DIRECTIONS:
                question_template = ENGLISH_QUESTIONS[relation] if prompt_language == "en" else TURKISH_QUESTIONS[relation]
                question = question_template.format(subject=profile["subject"])
                probes.append(
                    {
                        "probe_id": f"{profile['subject_id']}_{relation}_{direction}",
                        "fact_id": f"{profile['subject_id']}_{relation}",
                        "subject_id": profile["subject_id"],
                        "subject": profile["subject"],
                        "relation": relation,
                        "direction": direction,
                        "prompt_language": prompt_language,
                        "answer_language": answer_language,
                        "question": question,
                        "rendered_prompt": SCAFFOLDS[prompt_language].format(question=question),
                        "expected_answer": profile[en_column if answer_language == "en" else tr_column],
                        "correct_object_id": correct.object_id,
                        "candidate_family": RELATION_TO_FAMILY[relation],
                        "branch_group": profile["branch_group"],
                        "frequency_bucket": profile[frequency_column],
                        "name_type": profile["name_type"],
                        "name_rarity_bucket": profile["name_rarity_bucket"],
                        "popularity_bucket": profile["popularity_bucket"],
                        "template_id": f"bridge_{relation}_{direction}_qa_v1",
                    }
                )
    probe_ids = [row["probe_id"] for row in probes]
    expected = len(selected_subject_ids) * len(RELATIONS) * len(DIRECTIONS)
    if len(probes) != expected or len(probe_ids) != len(set(probe_ids)):
        raise ValueError("Bridge probe registry has an unexpected count or duplicate IDs")
    return probes


def eligible_fact_rows(hard_result_path: Path) -> list[dict[str, Any]]:
    rows = read_csv_rows(hard_result_path)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["fact_id"])].append(row)
    output: list[dict[str, Any]] = []
    for fact_id, fact_rows in sorted(grouped.items()):
        heldout = [row for row in fact_rows if row.get("form_id") in {"form_c", "form_d"}]
        required = [row for row in fact_rows if row.get("form_id") in {"form_a", "form_b", "form_c", "form_d"}]
        positive_heldout = sum(
            int(row["correct_rank_mean"]) == 1 and float(row["margin"]) > 0.0
            for row in heldout
        )
        positive_required = sum(
            int(row["correct_rank_mean"]) == 1 and float(row["margin"]) > 0.0
            for row in required
        )
        if len(heldout) != 4 or len(required) != 8:
            raise ValueError(
                f"{fact_id} must have 4 C/D held-out and 8 total required English cells; "
                f"found {len(heldout)} and {len(required)}"
            )
        first = fact_rows[0]
        output.append(
            {
                "fact_id": fact_id,
                "subject_id": first["subject_id"],
                "relation": first["relation"],
                "heldout_positive_cells": positive_heldout,
                "required_positive_cells": positive_required,
                "eligible_3_of_4_heldout": positive_heldout >= 3,
                "strict_8_of_8": positive_required == 8,
            }
        )
    return output


def eligibility_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    per_relation: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        relation = str(row["relation"])
        per_relation[relation]["facts"] += 1
        per_relation[relation]["eligible"] += int(bool(row["eligible_3_of_4_heldout"]))
        per_relation[relation]["strict"] += int(bool(row["strict_8_of_8"]))
    return {
        "facts": len(rows),
        "eligible": sum(int(bool(row["eligible_3_of_4_heldout"])) for row in rows),
        "strict": sum(int(bool(row["strict_8_of_8"])) for row in rows),
        "per_relation": {relation: dict(counts) for relation, counts in sorted(per_relation.items())},
    }
