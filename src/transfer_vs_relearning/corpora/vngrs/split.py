"""Document-disjoint deterministic split assignment."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Iterable, Mapping


def assign_split(record_id: str, *, seed: int = 42, validation_fraction: float = 0.02) -> str:
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must be between 0 and 1")
    digest = hashlib.sha256(f"vngrs-split-v2|{seed}|{record_id}".encode("utf-8")).digest()
    bucket = int.from_bytes(digest[:8], "big") / 2**64
    return "held_out" if bucket < validation_fraction else "train"


def assign_document_disjoint(records: Iterable[Mapping[str, str]], *, seed: int = 42, validation_fraction: float = 0.02) -> list[dict[str, str]]:
    seen: set[str] = set()
    output = []
    for record in sorted((dict(record) for record in records), key=lambda item: item["record_id"]):
        record_id = record["record_id"]
        if record_id in seen:
            raise ValueError(f"duplicate source record ID: {record_id}")
        seen.add(record_id)
        record["split"] = assign_split(record_id, seed=seed, validation_fraction=validation_fraction)
        output.append(record)
    return output


def assert_document_disjoint(records: Iterable[Mapping[str, str]]) -> None:
    by_split: dict[str, set[str]] = defaultdict(set)
    for record in records:
        by_split[str(record["split"])].add(str(record["record_id"]))
    splits = sorted(by_split)
    for index, first in enumerate(splits):
        for second in splits[index + 1 :]:
            overlap = by_split[first] & by_split[second]
            if overlap:
                raise AssertionError(f"document IDs cross split boundary: {sorted(overlap)}")
