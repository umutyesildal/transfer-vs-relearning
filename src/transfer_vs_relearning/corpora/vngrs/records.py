"""Parquet metadata, record streaming and stable identity helpers for vngrs."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence


class VngrsRecordError(ValueError):
    """Raised when a source record cannot satisfy the frozen schema."""


@dataclass(frozen=True)
class NormalizedText:
    text: str
    sha256: str
    utf8_replacement_count: int
    control_chars_removed: int
    whitespace_changes: int


@dataclass(frozen=True)
class ParquetMetadata:
    path: str
    row_count: int
    row_group_count: int
    schema: tuple[str, ...]
    local_serialized_bytes: int


def source_identity_key(record: Mapping[str, Any]) -> tuple[str, str]:
    """Return the composite natural key ``(corpus, original_id)``.

    ``0`` is a valid integer source ID.  Only absent/empty values fail closed; truthiness is not
    used to decide whether an ID exists.
    """

    corpus = record.get("corpus")
    original_id = record.get("original_id")
    if corpus is None or str(corpus).strip() == "":
        raise VngrsRecordError("missing source corpus in composite identity")
    if original_id is None:
        raise VngrsRecordError("missing original_id in composite identity")
    corpus_text = str(corpus).strip()
    original_text = str(original_id).strip()
    if original_text == "":
        raise VngrsRecordError("empty original_id in composite identity")
    return corpus_text, original_text


def normalize_text(value: str | bytes) -> NormalizedText:
    """Normalize text without language-specific rewriting or lossy transliteration."""

    replacements = 0
    if isinstance(value, bytes):
        decoded = value.decode("utf-8", errors="replace")
        replacements = decoded.count("\ufffd")
    elif isinstance(value, str):
        decoded = value
    else:
        raise TypeError("text must be str or bytes")
    normalized = unicodedata.normalize("NFC", decoded).replace("\r\n", "\n").replace("\r", "\n")
    cleaned_chars: list[str] = []
    removed = 0
    for char in normalized:
        if unicodedata.category(char) in {"Cc", "Cf"} and char not in {"\n", "\t"}:
            removed += 1
            continue
        cleaned_chars.append(char)
    cleaned = "".join(cleaned_chars)
    collapsed_lines = "\n".join(" ".join(line.split()) for line in cleaned.split("\n"))
    collapsed_lines = "\n".join(line for line in collapsed_lines.split("\n") if line)
    whitespace_changes = int(collapsed_lines != decoded)
    return NormalizedText(
        text=collapsed_lines,
        sha256=hashlib.sha256(collapsed_lines.encode("utf-8")).hexdigest(),
        utf8_replacement_count=replacements,
        control_chars_removed=removed,
        whitespace_changes=whitespace_changes,
    )


def decoded_text_character_count(value: str | bytes) -> int:
    """Count decoded source characters before NFC/control/whitespace normalization."""

    if isinstance(value, bytes):
        return len(value.decode("utf-8", errors="replace"))
    if isinstance(value, str):
        return len(value)
    raise TypeError("text must be str or bytes")


def stable_record_id(
    record: Mapping[str, Any],
    *,
    source_revision: str,
    shard_path: str,
    row_group_index: int,
    row_index: int,
) -> str:
    """Build a revision-scoped ID from the composite natural key; never invent a row fallback."""

    del shard_path, row_group_index, row_index
    corpus, original_id = source_identity_key(record)
    identity_payload = json.dumps(
        [source_revision, corpus, original_id], ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return "vngrs:" + hashlib.sha256(identity_payload).hexdigest()


def serialized_record_bytes(record: Mapping[str, Any]) -> bytes:
    """Serialize one record for record-level accounting, distinct from HTTP bytes."""

    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def read_parquet_metadata(path: str | Path) -> ParquetMetadata:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover - dependency is project-pinned
        raise VngrsRecordError("pyarrow is required for Parquet metadata") from exc
    path = Path(path)
    try:
        parquet = pq.ParquetFile(path)
        schema = tuple(field.name for field in parquet.schema_arrow)
        return ParquetMetadata(
            path=str(path),
            row_count=parquet.metadata.num_rows,
            row_group_count=parquet.metadata.num_row_groups,
            schema=schema,
            local_serialized_bytes=path.stat().st_size,
        )
    except Exception as exc:  # pyarrow exposes several concrete exception types
        raise VngrsRecordError(f"malformed or unreadable Parquet: {path}") from exc


def stream_parquet_records(
    path: str | Path, *, columns: Sequence[str] = ("text", "corpus", "original_id"), batch_size: int = 1024
) -> Iterator[dict[str, Any]]:
    """Stream rows from a verified local file; this function never downloads or writes data."""

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover
        raise VngrsRecordError("pyarrow is required for Parquet streaming") from exc
    path = Path(path)
    try:
        parquet = pq.ParquetFile(path)
        available = set(parquet.schema_arrow.names)
        missing = set(columns) - available
        if missing:
            raise VngrsRecordError(f"missing required columns: {sorted(missing)}")
        for batch in parquet.iter_batches(batch_size=batch_size, columns=list(columns), use_threads=False):
            for row in batch.to_pylist():
                yield row
    except VngrsRecordError:
        raise
    except Exception as exc:
        raise VngrsRecordError(f"malformed or unreadable Parquet: {path}") from exc
