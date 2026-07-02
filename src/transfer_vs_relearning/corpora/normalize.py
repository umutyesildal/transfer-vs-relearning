from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any

from transfer_vs_relearning.corpora.document import CorpusDocument


CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def normalize_text(text: str) -> tuple[str, dict[str, int]]:
    counts = {"nfc_changed": 0, "control_chars_removed": 0, "whitespace_collapsed": 0, "markup_fragments_removed": 0}
    original = text
    text = text.decode("utf-8", errors="replace") if isinstance(text, bytes) else text
    nfc = unicodedata.normalize("NFC", text)
    counts["nfc_changed"] = int(nfc != text)
    text = nfc.replace("\r\n", "\n").replace("\r", "\n")
    controls = CONTROL_RE.findall(text)
    counts["control_chars_removed"] = len(controls)
    text = CONTROL_RE.sub("", text)
    before_markup = text
    text = re.sub(r"</?[A-Za-z][^>]{0,120}>", " ", text)
    counts["markup_fragments_removed"] = int(before_markup != text)
    paragraphs = [re.sub(r"[ \t\f\v]+", " ", paragraph).strip() for paragraph in text.split("\n")]
    text = "\n".join(paragraph for paragraph in paragraphs if paragraph)
    text = re.sub(r"\n{3,}", "\n\n", text)
    counts["whitespace_collapsed"] = int(text != original)
    return text, counts


def normalize_document(document: CorpusDocument) -> CorpusDocument:
    text, counts = normalize_text(document.text)
    document.text = text
    document.normalized_text_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    document.processing_stage = "normalized"
    provenance = document.provenance or {}
    provenance["normalization_counts"] = counts
    document.provenance = provenance
    return document
