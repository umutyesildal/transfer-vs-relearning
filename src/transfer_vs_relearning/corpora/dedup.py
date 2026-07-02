from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any

from transfer_vs_relearning.corpora.document import CorpusDocument


def exact_deduplicate(documents: list[CorpusDocument]) -> tuple[list[CorpusDocument], list[dict[str, Any]], dict[str, Any]]:
    groups: dict[str, list[CorpusDocument]] = defaultdict(list)
    for document in documents:
        digest = document.normalized_text_sha256 or hashlib.sha256(document.text.encode("utf-8")).hexdigest()
        groups[digest].append(document)
    kept: list[CorpusDocument] = []
    duplicates: list[dict[str, Any]] = []
    duplicate_chars = 0
    for group_id, (digest, docs) in enumerate(sorted(groups.items()), start=1):
        docs = sorted(docs, key=lambda doc: doc.document_id)
        kept_doc = docs[0]
        kept_doc.processing_stage = "deduplicated"
        kept.append(kept_doc)
        for duplicate in docs[1:]:
            duplicate_chars += len(duplicate.text)
            duplicates.append({
                "duplicate_group": group_id,
                "content_hash": digest,
                "kept_document_id": kept_doc.document_id,
                "duplicate_document_id": duplicate.document_id,
                "duplicate_char_count": len(duplicate.text),
            })
    return kept, duplicates, {
        "input_documents": len(documents),
        "kept_documents": len(kept),
        "duplicate_documents": len(duplicates),
        "estimated_duplicated_character_count": duplicate_chars,
    }
