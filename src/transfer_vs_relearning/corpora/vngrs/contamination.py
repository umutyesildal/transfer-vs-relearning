"""Synthetic-contamination and benchmark-overlap diagnostics."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .records import normalize_text


@dataclass(frozen=True)
class ContaminationPattern:
    pattern_id: str
    tier: str
    surface: str
    channel: str


def scan_contamination(text: str, patterns: Iterable[ContaminationPattern]) -> dict[str, Any]:
    normalized = normalize_text(text).text.casefold()
    matches = []
    for pattern in sorted(patterns, key=lambda item: (item.tier, item.pattern_id, item.surface)):
        if normalize_text(pattern.surface).text.casefold() in normalized:
            matches.append({"pattern_id": pattern.pattern_id, "tier": pattern.tier, "channel": pattern.channel})
    tiers = sorted({match["tier"] for match in matches})
    return {"status": "contaminated" if matches else "clean", "tiers": tiers, "matches": matches}


def benchmark_overlap(
    records: Iterable[Mapping[str, Any]], *, benchmark_item_hashes: Iterable[str], benchmark_item_ids: Iterable[str] = ()
) -> list[dict[str, str]]:
    hashes = set(benchmark_item_hashes)
    ids = set(benchmark_item_ids)
    overlaps = []
    for record in records:
        text_hash = str(record["normalized_text_sha256"])
        if text_hash in hashes:
            overlaps.append({"record_id": str(record["record_id"]), "overlap_type": "normalized_text_sha256"})
        if str(record.get("original_id", "")) in ids:
            overlaps.append({"record_id": str(record["record_id"]), "overlap_type": "source_or_benchmark_id"})
    return overlaps


def normalized_text_sha256(text: str) -> str:
    return hashlib.sha256(normalize_text(text).text.encode("utf-8")).hexdigest()
