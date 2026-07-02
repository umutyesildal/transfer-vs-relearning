from __future__ import annotations

import hashlib
from typing import Any

from transfer_vs_relearning.corpora.document import CorpusDocument


def assign_split(document: CorpusDocument, config: dict[str, Any]) -> str:
    split_cfg = config.get("split", {})
    validation_fraction = float(split_cfg.get("validation_fraction", 0.02))
    value = int(hashlib.sha256(document.document_id.encode("utf-8")).hexdigest()[:16], 16) / 16**16
    return "validation" if value < validation_fraction else "train"


def split_documents(documents: list[CorpusDocument], config: dict[str, Any]) -> list[CorpusDocument]:
    output = []
    for document in documents:
        document.split = assign_split(document, config)
        document.processing_stage = "split"
        output.append(document)
    return sorted(output, key=lambda doc: doc.document_id)
