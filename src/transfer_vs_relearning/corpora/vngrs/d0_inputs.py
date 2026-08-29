"""Frozen local input loaders for D0 registry and synthetic contamination surfaces."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .d0_audit import SyntheticFactSurface
from .materialization import SourceObject


def load_source_objects(path: str | Path, *, expected_sha256: str) -> tuple[SourceObject, ...]:
    payload = Path(path).read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError("source-registry result SHA-256 drift")
    document = json.loads(payload)
    rows = document["source_registry"]["objects"]
    return tuple(
        SourceObject(
            row["path"], row["revision"], row["size_bytes"], row["sha256"], row["lfs_oid"], row["url"]
        )
        for row in rows
    )


def load_synthetic_surfaces(path: str | Path, *, expected_sha256: str) -> dict[str, str]:
    payload = Path(path).read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError("Relation V2 validation input SHA-256 drift")
    rows = [json.loads(line) for line in payload.splitlines() if line]
    if len(rows) != 500:
        raise ValueError("Relation V2 contamination registry must contain exactly 500 facts")
    subjects: dict[str, str] = {}
    facts: dict[str, str] = {}
    for row in rows:
        subject_id, subject = row.get("subject_id"), row.get("subject")
        fact_id, answer = row.get("fact_id"), row.get("answer")
        if not all(isinstance(value, str) and value for value in (subject_id, subject, fact_id, answer)):
            raise ValueError("Relation V2 contamination identity is incomplete")
        if subject_id in subjects and subjects[subject_id] != subject:
            raise ValueError("Relation V2 subject identity is ambiguous")
        if fact_id in facts:
            raise ValueError("Relation V2 fact identity is duplicated")
        subjects[subject_id] = subject
        facts[fact_id] = answer
    if len(subjects) != 100 or len(facts) != 500:
        raise ValueError("Relation V2 contamination population cardinality drift")
    return {
        **{f"subject:{key}": value for key, value in sorted(subjects.items())},
        **{f"object:{key}": value for key, value in sorted(facts.items())},
    }


def load_synthetic_fact_registry(
    path: str | Path, *, expected_sha256: str
) -> tuple[SyntheticFactSurface, ...]:
    """Load Relation V2 without discarding subject/fact/relation bindings."""

    payload = Path(path).read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError("Relation V2 validation input SHA-256 drift")
    rows = [json.loads(line) for line in payload.splitlines() if line]
    if len(rows) != 500:
        raise ValueError("Relation V2 contamination registry must contain exactly 500 facts")
    facts: list[SyntheticFactSurface] = []
    subject_identity: dict[str, str] = {}
    fact_ids: set[str] = set()
    subject_relations: dict[str, set[str]] = {}
    for row in rows:
        values = tuple(row.get(key) for key in ("subject_id", "subject", "fact_id", "relation", "answer"))
        if not all(isinstance(value, str) and value for value in values):
            raise ValueError("Relation V2 fact identity is incomplete")
        subject_id, subject, fact_id, relation, answer = values
        if subject_id in subject_identity and subject_identity[subject_id] != subject:
            raise ValueError("Relation V2 subject identity is ambiguous")
        if fact_id in fact_ids:
            raise ValueError("Relation V2 fact identity is duplicated")
        subject_identity[subject_id] = subject
        fact_ids.add(fact_id)
        subject_relations.setdefault(subject_id, set()).add(relation)
        facts.append(SyntheticFactSurface(subject_id, subject, fact_id, relation, answer))
    expected_relations = {"born_in", "field_of_study", "lives_in", "profession", "works_in_industry"}
    if len(subject_identity) != 100 or any(value != expected_relations for value in subject_relations.values()):
        raise ValueError("Relation V2 subject/relation population cardinality drift")
    return tuple(sorted(facts, key=lambda fact: fact.fact_id))
