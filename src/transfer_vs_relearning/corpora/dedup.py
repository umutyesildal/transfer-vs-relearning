from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from transfer_vs_relearning.corpora.document import CorpusDocument
from transfer_vs_relearning.corpora.io import write_jsonl


def exact_deduplicate_stream(
    documents: Iterable[CorpusDocument],
    output_path: Path,
    duplicates_path: Path,
    sqlite_path: Path,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    duplicates_path.parent.mkdir(parents=True, exist_ok=True)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    output_tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    duplicates_tmp = duplicates_path.with_suffix(duplicates_path.suffix + ".tmp")
    if sqlite_path.exists():
        sqlite_path.unlink()
    conn = sqlite3.connect(sqlite_path)
    conn.execute(
        "CREATE TABLE content_index (content_hash TEXT PRIMARY KEY, kept_document_id TEXT NOT NULL)"
    )
    input_count = kept_count = duplicate_count = duplicate_chars = 0
    try:
        with output_tmp.open("w", encoding="utf-8") as out_handle, duplicates_tmp.open("w", encoding="utf-8") as dup_handle:
            for document in documents:
                input_count += 1
                digest = document.normalized_text_sha256 or hashlib.sha256(document.text.encode("utf-8")).hexdigest()
                existing = conn.execute("SELECT kept_document_id FROM content_index WHERE content_hash = ?", (digest,)).fetchone()
                if existing is None:
                    conn.execute("INSERT INTO content_index VALUES (?, ?)", (digest, document.document_id))
                    document.processing_stage = "deduplicated"
                    out_handle.write(json.dumps(document.to_json(), ensure_ascii=False, sort_keys=True) + "\n")
                    kept_count += 1
                else:
                    duplicate_count += 1
                    duplicate_chars += len(document.text)
                    dup_handle.write(json.dumps({
                        "duplicate_group": digest,
                        "content_hash": digest,
                        "kept_document_id": existing[0],
                        "duplicate_document_id": document.document_id,
                        "duplicate_char_count": len(document.text),
                    }, ensure_ascii=False, sort_keys=True) + "\n")
        conn.commit()
    finally:
        conn.close()
    output_tmp.replace(output_path)
    duplicates_tmp.replace(duplicates_path)
    return {
        "input_documents": input_count,
        "kept_documents": kept_count,
        "duplicate_documents": duplicate_count,
        "estimated_duplicated_character_count": duplicate_chars,
        "storage": "sqlite",
        "keeper_policy": "first_document_in_stable_stream_order",
    }


def exact_deduplicate(documents: Iterable[CorpusDocument]) -> tuple[list[CorpusDocument], list[dict[str, Any]], dict[str, Any]]:
    """Small in-memory compatibility helper for unit tests."""
    seen: dict[str, CorpusDocument] = {}
    kept: list[CorpusDocument] = []
    duplicates: list[dict[str, Any]] = []
    duplicate_chars = 0
    input_count = 0
    for document in documents:
        input_count += 1
        digest = document.normalized_text_sha256 or hashlib.sha256(document.text.encode("utf-8")).hexdigest()
        if digest not in seen:
            document.processing_stage = "deduplicated"
            seen[digest] = document
            kept.append(document)
        else:
            duplicate_chars += len(document.text)
            duplicates.append({
                "duplicate_group": digest,
                "content_hash": digest,
                "kept_document_id": seen[digest].document_id,
                "duplicate_document_id": document.document_id,
                "duplicate_char_count": len(document.text),
            })
    return kept, duplicates, {
        "input_documents": input_count,
        "kept_documents": len(kept),
        "duplicate_documents": len(duplicates),
        "estimated_duplicated_character_count": duplicate_chars,
        "storage": "memory_test_helper",
        "keeper_policy": "first_document_in_stable_stream_order",
    }
