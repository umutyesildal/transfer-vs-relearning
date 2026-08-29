"""Deterministic, bounded human-review handoff for vngrs D0."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

from .d0_audit import D0Document
from .metadata import canonical_json_sha256


REVIEW_VERDICTS = frozenset({"usable", "unusable", "unsafe"})


def read_jsonl_rows(path: str | Path) -> list[dict[str, Any]]:
    """Read LF-delimited JSONL without treating Unicode separators inside strings as records."""

    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                raise ValueError(f"blank JSONL record at line {line_number}")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"JSONL record {line_number} is not an object")
            rows.append(value)
    if not rows:
        raise ValueError("JSONL input is empty")
    return rows


def build_review_packet(
    documents: Iterable[D0Document],
    selected: Iterable[Mapping[str, Any]],
    *,
    max_excerpt_characters: int = 2_000,
) -> list[dict[str, Any]]:
    """Join the frozen text-free selection to bounded excerpts without changing its IDs."""

    if not 1 <= max_excerpt_characters <= 2_000:
        raise ValueError("review excerpt bound must be between 1 and 2,000 characters")
    by_id = {row.stable_document_id: row for row in documents}
    rows: list[dict[str, Any]] = []
    for item in selected:
        selected_row = dict(item)
        stable_id = selected_row.get("stable_document_id")
        document = by_id.get(stable_id)
        if document is None:
            raise ValueError("review selection is not bound to the loaded population")
        text_bytes = document.text.encode("utf-8")
        excerpt = document.text[:max_excerpt_characters]
        rows.append(
            {
                **selected_row,
                "review_status": "awaiting_human_verdict",
                "text_sha256": hashlib.sha256(text_bytes).hexdigest(),
                "text_utf8_bytes": len(text_bytes),
                "excerpt": excerpt,
                "excerpt_character_count": len(excerpt),
                "excerpt_truncated": len(document.text) > len(excerpt),
            }
        )
    if not rows or len({row["stable_document_id"] for row in rows}) != len(rows):
        raise ValueError("review packet must be non-empty with unique document IDs")
    return rows


def review_packet_sha256(packet: Iterable[Mapping[str, Any]]) -> str:
    return canonical_json_sha256([dict(row) for row in packet])


def validate_review_decisions(
    packet: Iterable[Mapping[str, Any]], decisions: Iterable[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    """Require one packet-bound human verdict per selected document; never default missing rows."""

    packet_rows = [dict(row) for row in packet]
    decision_rows = [dict(row) for row in decisions]
    packet_hash = review_packet_sha256(packet_rows)
    expected = {row["stable_document_id"] for row in packet_rows}
    observed = [row.get("stable_document_id") for row in decision_rows]
    if len(observed) != len(set(observed)) or set(observed) != expected:
        raise ValueError("human decisions do not exactly cover the frozen review packet")
    for row in decision_rows:
        if row.get("review_packet_sha256") != packet_hash:
            raise ValueError("human decision is not bound to the exact review packet")
        if row.get("verdict") not in REVIEW_VERDICTS:
            raise ValueError("human decision verdict is invalid or unresolved")
        if not str(row.get("reviewer", "")).strip():
            raise ValueError("human decision reviewer is missing")
    return sorted(decision_rows, key=lambda row: row["stable_document_id"])


def decision_template(packet: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    packet_rows = [dict(row) for row in packet]
    packet_hash = review_packet_sha256(packet_rows)
    return [
        {
            "schema_version": 1,
            "stable_document_id": row["stable_document_id"],
            "review_packet_sha256": packet_hash,
            "verdict": None,
            "reviewer": None,
            "notes": None,
        }
        for row in packet_rows
    ]


def write_review_handoff(
    root: str | Path, *, state: Mapping[str, Any], packet: Iterable[Mapping[str, Any]]
) -> None:
    root_path = Path(root)
    rows = [dict(row) for row in packet]
    payloads = {
        "control/phase1_state.json": json.dumps(dict(state), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n",
        "reports/human_review_packet.jsonl": b"".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n" for row in rows
        ),
        "reports/human_review_decision_template.jsonl": b"".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"
            for row in decision_template(rows)
        ),
    }
    for relative, payload in payloads.items():
        path = root_path / relative
        temporary = path.with_name(path.name + ".partial")
        if path.exists() or temporary.exists():
            raise ValueError(f"refusing to overwrite review handoff: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)


def write_validated_decisions(root: str | Path, decisions: Iterable[Mapping[str, Any]]) -> str:
    rows = [dict(row) for row in decisions]
    payload = b"".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        for row in rows
    )
    relative = "reports/human_review_decisions.jsonl"
    path = Path(root) / relative
    temporary = path.with_name(path.name + ".partial")
    if path.exists() or temporary.exists():
        raise ValueError("refusing to overwrite validated human decisions")
    with temporary.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    return relative
