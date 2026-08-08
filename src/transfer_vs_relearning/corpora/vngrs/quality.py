"""Deterministic, auditable quality and privacy diagnostics for bounded samples."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class QualityConfig:
    min_chars: int = 20
    max_chars: int = 100_000
    max_url_ratio: float = 0.20
    max_code_coverage: float = 0.20
    max_markup_coverage: float = 0.20
    max_repeated_line_ratio: float = 0.50
    max_symbol_ratio: float = 0.20


@dataclass(frozen=True)
class QualityResult:
    accepted: bool
    reasons: tuple[str, ...]
    metrics: dict[str, float | int]
    threshold_status: str = "exploratory_calibration_only"
    evaluator_scope: str = "deterministic_heuristics_not_comprehensive"


_URL = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_CODE = re.compile(r"\b(?:def|class|import|SELECT|INSERT|function|var|const)\b|[{};]", re.IGNORECASE)
_MARKUP = re.compile(r"<[^>]+>|\[\[[^]]+\]\]|\{\{[^}]+\}\}")
_ADULT = re.compile(r"\b(?:porn|porno|seks|sex|erotik)\b", re.IGNORECASE)


def _ratio(count: int, denominator: int) -> float:
    return count / denominator if denominator else 0.0


def _matched_character_coverage(pattern: re.Pattern[str], text: str) -> float:
    """Measure matched characters, not regex match count divided by document length."""

    matched_chars = sum(len(match.group(0)) for match in pattern.finditer(text))
    return _ratio(matched_chars, max(len(text), 1))


def evaluate_quality(text: str, config: QualityConfig = QualityConfig()) -> QualityResult:
    if not isinstance(text, str):
        raise TypeError("text must be str")
    length = len(text)
    urls = _URL.findall(text)
    code_markers = _CODE.findall(text)
    markup_markers = _MARKUP.findall(text)
    lines = [line for line in text.splitlines() if line.strip()]
    repeated_lines = len(lines) - len(set(lines))
    symbols = sum(not char.isalnum() and not char.isspace() for char in text)
    reasons: list[str] = []
    if length < config.min_chars:
        reasons.append("too_short")
    if length > config.max_chars:
        reasons.append("too_long")
    url_ratio = _ratio(sum(len(match) for match in urls), max(length, 1))
    code_coverage = _matched_character_coverage(_CODE, text)
    markup_coverage = _matched_character_coverage(_MARKUP, text)
    repeated_line_ratio = _ratio(repeated_lines, max(len(lines), 1))
    symbol_ratio = _ratio(symbols, max(length, 1))
    if url_ratio > config.max_url_ratio:
        reasons.append("url_heavy")
    if code_coverage > config.max_code_coverage:
        reasons.append("code_heavy")
    if markup_coverage > config.max_markup_coverage:
        reasons.append("markup_heavy")
    if repeated_line_ratio > config.max_repeated_line_ratio:
        reasons.append("repeated_line_heavy")
    if symbol_ratio > config.max_symbol_ratio:
        reasons.append("symbol_heavy")
    if _ADULT.search(text):
        reasons.append("adult_flag")
    if len(lines) >= 3 and repeated_line_ratio >= 0.8:
        reasons.append("spam_repetition")
    return QualityResult(
        accepted=not reasons,
        reasons=tuple(dict.fromkeys(reasons)),
        metrics={
            "characters": length,
            "url_ratio": url_ratio,
            "url_match_count": len(urls),
            "code_marker_count": len(code_markers),
            "code_coverage": code_coverage,
            "markup_match_count": len(markup_markers),
            "markup_coverage": markup_coverage,
            "repeated_line_ratio": repeated_line_ratio,
            "symbol_ratio": symbol_ratio,
        },
    )


_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d .()/-]{7,}\d)(?!\d)")
_TOKEN = re.compile(r"\b(?:sk|pk|ghp|xox[baprs]-)[A-Za-z0-9_-]{12,}\b", re.IGNORECASE)


def detect_pii(text: str) -> tuple[str, ...]:
    kinds: list[str] = []
    if _EMAIL.search(text):
        kinds.append("email")
    if _PHONE.search(text):
        kinds.append("phone")
    if _TOKEN.search(text):
        kinds.append("credential_like_token")
    return tuple(kinds)


PII_EVALUATOR_SCOPE = "small_deterministic_regex_diagnostic_not_comprehensive"
ADULT_EVALUATOR_SCOPE = "small_deterministic_keyword_diagnostic_not_comprehensive"


def redact_pii(text: str) -> tuple[str, tuple[str, ...]]:
    kinds = detect_pii(text)
    redacted = _EMAIL.sub("[PII_EMAIL]", text)
    redacted = _PHONE.sub("[PII_PHONE]", redacted)
    redacted = _TOKEN.sub("[PII_TOKEN]", redacted)
    return redacted, kinds
