from __future__ import annotations

import hashlib
from dataclasses import dataclass

from transfer_vs_relearning.data.constants import RELATION_MAP
from transfer_vs_relearning.utils.text import normalize_text, slugify


@dataclass(frozen=True)
class Candidate:
    object_id: str
    family: str
    object_en: str
    object_tr: str

    def surface(self, language: str) -> str:
        return self.object_en if language == "en" else self.object_tr


RELATION_TO_FAMILY = {
    "profession": "profession",
    "born_in": "city",
    "lives_in": "city",
    "studied_at": "university",
    "works_at": "employer",
}


def stable_object_id(family: str, object_en: str, object_tr: str) -> str:
    key = f"{family}|{normalize_text(object_en)}|{normalize_text(object_tr)}"
    suffix = hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]
    return f"{family}_{slugify(object_en)}_{suffix}"


def build_candidate_inventories(canonical_rows: list[dict[str, str]]) -> dict[str, list[Candidate]]:
    pairs_by_family: dict[str, set[tuple[str, str]]] = {
        "profession": set(),
        "city": set(),
        "university": set(),
        "employer": set(),
    }
    for row in canonical_rows:
        pairs_by_family["profession"].add((row["profession_en"], row["profession_tr"]))
        pairs_by_family["city"].add((row["birthplace_en"], row["birthplace_tr"]))
        pairs_by_family["city"].add((row["residence_en"], row["residence_tr"]))
        pairs_by_family["university"].add((row["university_en"], row["university_tr"]))
        pairs_by_family["employer"].add((row["employer_en"], row["employer_tr"]))

    inventories: dict[str, list[Candidate]] = {}
    for family, pairs in pairs_by_family.items():
        candidates = [
            Candidate(stable_object_id(family, en, tr), family, en, tr)
            for en, tr in sorted(pairs, key=lambda pair: (normalize_text(pair[0]), normalize_text(pair[1])))
        ]
        inventories[family] = sorted(candidates, key=lambda item: item.object_id)
    return inventories


def candidate_for_fact(row: dict[str, str], relation: str, inventories: dict[str, list[Candidate]]) -> Candidate:
    en_col, tr_col, _ = RELATION_MAP[relation]
    family = RELATION_TO_FAMILY[relation]
    expected = (normalize_text(row[en_col]), normalize_text(row[tr_col]))
    matches = [
        candidate
        for candidate in inventories[family]
        if (normalize_text(candidate.object_en), normalize_text(candidate.object_tr)) == expected
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {family} candidate for {relation} on {row['subject_id']}, found {len(matches)}")
    return matches[0]


def resolve_expected_answer(
    relation: str,
    language: str,
    expected_answer: str,
    inventories: dict[str, list[Candidate]],
) -> Candidate:
    family = RELATION_TO_FAMILY[relation]
    key = normalize_text(expected_answer)
    matches = [candidate for candidate in inventories[family] if normalize_text(candidate.surface(language)) == key]
    if len(matches) != 1:
        raise ValueError(f"Expected answer {expected_answer!r} resolved to {len(matches)} {family} candidates")
    return matches[0]
