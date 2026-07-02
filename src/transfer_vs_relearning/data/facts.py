from __future__ import annotations

from dataclasses import dataclass

from transfer_vs_relearning.data.constants import RELATION_MAP, RELATIONS


@dataclass(frozen=True)
class Fact:
    fact_id: str
    row_id: str
    subject_id: str
    subject: str
    relation: str
    object_en: str
    object_tr: str
    frequency_bucket: str
    branch_group: str
    name_type: str
    name_rarity_bucket: str
    popularity_rank: int
    popularity_bucket: str


def expand_canonical_row(row: dict[str, str]) -> list[Fact]:
    facts: list[Fact] = []
    for relation in RELATIONS:
        en_col, tr_col, freq_col = RELATION_MAP[relation]
        facts.append(
            Fact(
                fact_id=f"{row['subject_id']}_{relation}",
                row_id=row["row_id"],
                subject_id=row["subject_id"],
                subject=row["subject"],
                relation=relation,
                object_en=row[en_col],
                object_tr=row[tr_col],
                frequency_bucket=row[freq_col],
                branch_group=row["branch_group"],
                name_type=row["name_type"],
                name_rarity_bucket=row["name_rarity_bucket"],
                popularity_rank=int(row["popularity_rank"]),
                popularity_bucket=row["popularity_bucket"],
            )
        )
    return facts


def expand_canonical_rows(rows: list[dict[str, str]]) -> list[Fact]:
    return [fact for row in rows for fact in expand_canonical_row(row)]


def facts_by_id(facts: list[Fact]) -> dict[str, Fact]:
    return {fact.fact_id: fact for fact in facts}
