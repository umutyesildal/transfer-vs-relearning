from __future__ import annotations

import re
from collections import Counter
from statistics import mean
from typing import Any

from transfer_vs_relearning.corpora.document import CorpusDocument


URL_RE = re.compile(r"https?://|www\.")
MARKUP_RE = re.compile(r"\{\{|\[\[|\]\]|==|<ref", re.IGNORECASE)


def audit_document(document: CorpusDocument, config: dict[str, Any]) -> CorpusDocument:
    text = document.text
    chars = len(text)
    alpha = sum(ch.isalpha() for ch in text)
    latin = sum(("A" <= ch <= "Z") or ("a" <= ch <= "z") or ch in "ÇĞİÖŞÜçğıöşü" for ch in text if ch.isalpha())
    symbols = sum(not ch.isalnum() and not ch.isspace() for ch in text)
    url_chars = sum(len(match.group(0)) for match in URL_RE.finditer(text))
    markup = len(MARKUP_RE.findall(text))
    metrics = {
        "char_count": chars,
        "alphabetic_ratio": alpha / chars if chars else 0.0,
        "latin_script_ratio": latin / alpha if alpha else 0.0,
        "url_ratio": url_chars / chars if chars else 0.0,
        "symbol_ratio": symbols / chars if chars else 0.0,
        "markup_remnant_ratio": markup / max(chars, 1),
        "encoding_anomaly_count": text.count("\ufffd"),
        "mixed_language_indicator": int(any(word in text.casefold().split() for word in ("the", "and", "of"))),
    }
    thresholds = config.get("filtering", {})
    reasons: list[str] = []
    if not text.strip():
        reasons.append("empty_text")
    if chars < int(thresholds.get("min_chars", 0)):
        reasons.append("short_document")
    if metrics["alphabetic_ratio"] < float(thresholds.get("min_alphabetic_ratio", 0)):
        reasons.append("low_alphabetic_ratio")
    if metrics["latin_script_ratio"] < float(thresholds.get("min_latin_ratio", 0)):
        reasons.append("low_latin_script_ratio")
    if metrics["url_ratio"] > float(thresholds.get("max_url_ratio", 1)):
        reasons.append("high_url_ratio")
    if metrics["symbol_ratio"] > float(thresholds.get("max_symbol_ratio", 1)):
        reasons.append("high_symbol_ratio")
    if metrics["markup_remnant_ratio"] > float(thresholds.get("max_markup_remnant_ratio", 1)):
        reasons.append("markup_remnants")
    if metrics["encoding_anomaly_count"]:
        reasons.append("encoding_anomaly")
    document.filtering_metrics = metrics
    document.filtering_reasons = reasons
    document.processing_stage = "audited" if thresholds.get("mode", "audit_only") == "audit_only" else "filtered"
    return document


def summarize_audit(documents: list[CorpusDocument]) -> dict[str, Any]:
    reason_counts = Counter(reason for doc in documents for reason in (doc.filtering_reasons or []))
    char_counts = [doc.filtering_metrics["char_count"] for doc in documents if doc.filtering_metrics]
    return {
        "document_count": len(documents),
        "reason_counts": dict(reason_counts),
        "mean_char_count": mean(char_counts) if char_counts else 0,
    }
