from __future__ import annotations

import re
from collections import Counter
from statistics import mean
from typing import Any

from transfer_vs_relearning.corpora.document import CorpusDocument


URL_RE = re.compile(r"(?:https?://|www\.)\S+")
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
        "mixed_language_heuristic_indicator": int(any(word in text.casefold().split() for word in ("the", "and", "of"))),
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
        "metric_definitions": metric_definitions(),
    }


class AuditSummary:
    def __init__(self) -> None:
        self.document_count = 0
        self.reason_counts: Counter[str] = Counter()
        self.metric_stats: dict[str, dict[str, Any]] = {}

    def add(self, document: CorpusDocument) -> None:
        self.document_count += 1
        self.reason_counts.update(document.filtering_reasons or [])
        for key, value in (document.filtering_metrics or {}).items():
            if not isinstance(value, (int, float)):
                continue
            stats = self.metric_stats.setdefault(key, {"min": value, "max": value, "sum": 0.0, "histogram": Counter()})
            stats["min"] = min(stats["min"], value)
            stats["max"] = max(stats["max"], value)
            stats["sum"] += float(value)
            stats["histogram"][_bin(value)] += 1

    def to_json(self) -> dict[str, Any]:
        metrics = {}
        for key, stats in self.metric_stats.items():
            metrics[key] = {
                "min": stats["min"],
                "max": stats["max"],
                "mean": stats["sum"] / self.document_count if self.document_count else 0,
                "histogram": dict(sorted(stats["histogram"].items())),
            }
        return {
            "document_count": self.document_count,
            "reason_counts": dict(self.reason_counts),
            "metric_definitions": metric_definitions(),
            "metric_summaries": metrics,
        }


def metric_definitions() -> dict[str, str]:
    return {
        "char_count": "Unicode code point count after normalization.",
        "alphabetic_ratio": "Alphabetic characters divided by total characters.",
        "latin_script_ratio": "Latin/Turkish Latin alphabetic characters divided by alphabetic characters.",
        "url_ratio": "Total length of full URL-like matches divided by total characters.",
        "symbol_ratio": "Non-alphanumeric non-whitespace characters divided by total characters.",
        "markup_remnant_ratio": "Count of residual markup indicators divided by total characters.",
        "mixed_language_heuristic_indicator": "Heuristic English stopword indicator; audit-only by default.",
    }


def _bin(value: float | int) -> str:
    value = float(value)
    if value < 0.01:
        return "lt_0.01"
    if value < 0.05:
        return "0.01_0.05"
    if value < 0.10:
        return "0.05_0.10"
    if value < 0.25:
        return "0.10_0.25"
    if value < 0.50:
        return "0.25_0.50"
    return "gte_0.50"
