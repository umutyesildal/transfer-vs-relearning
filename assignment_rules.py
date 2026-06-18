"""
Deterministic assignment and compatibility rules for canonical profile generation.
"""
from __future__ import annotations

import math
from collections import Counter

from config import EMPLOYER_CATEGORY_KEYWORDS, PROFESSION_CATEGORY_KEYWORDS

TURKISH_CHAR_MAP = str.maketrans({
    "İ": "I",
    "ı": "i",
    "Ş": "S",
    "ş": "s",
    "Ğ": "G",
    "ğ": "g",
    "Ü": "U",
    "ü": "u",
    "Ö": "O",
    "ö": "o",
    "Ç": "C",
    "ç": "c",
})

BUCKET_DOWN = {
    "high": "medium",
    "medium": "low",
    "low": "low",
}


def normalize_turkish_text(value: str) -> str:
    """Returns a deterministic English-compatible form of Turkish proper names."""
    return value.translate(TURKISH_CHAR_MAP)


def turkish_lower(value: str) -> str:
    """Lowercases text with Turkish I/İ behavior preserved."""
    chars = []
    for char in value:
        if char == "I":
            chars.append("ı")
        elif char == "İ":
            chars.append("i")
        else:
            chars.append(char.lower())
    return "".join(chars)


def turkish_upper_first(value: str) -> str:
    """Uppercases the first character with Turkish i/ı behavior preserved."""
    if not value:
        return value
    first = value[0]
    if first == "i":
        first = "İ"
    elif first == "ı":
        first = "I"
    else:
        first = first.upper()
    return first + value[1:]


def natural_name_component(value: str, name_type: str) -> str:
    """Normalizes one first-name or surname component into natural display casing."""
    parts = []
    for part in value.strip().split("-"):
        lowered = turkish_lower(part) if name_type == "turkish_like" else part.lower()
        parts.append(turkish_upper_first(lowered) if name_type == "turkish_like" else lowered.capitalize())
    return "-".join(parts)


def natural_full_name(first_name: str, surname: str, name_type: str) -> str:
    """Builds a two-component natural-cased full name without transliteration."""
    return f"{natural_name_component(first_name, name_type)} {natural_name_component(surname, name_type)}"


def is_single_name_component(value: str) -> bool:
    """Returns whether a source entry is exactly one whitespace-separated component."""
    return len(value.strip().split()) == 1


def rank_percentile(rank: int, total: int) -> float:
    """Converts a 1-based source rank to a percentile in [0, 1]."""
    if total <= 1:
        return 0.0
    return (rank - 1) / (total - 1)


def assign_name_rarity(first_rank: int, first_total: int, surname_rank: int, surname_total: int) -> str:
    """Assigns a simple name rarity bucket from first-name and surname ranks."""
    first_pct = rank_percentile(first_rank, first_total)
    surname_pct = rank_percentile(surname_rank, surname_total)
    combined = (first_pct + surname_pct) / 2

    if first_pct <= 1 / 3 and surname_pct <= 1 / 3:
        return "common"
    if (first_pct >= 2 / 3 or surname_pct >= 2 / 3) and combined >= 0.55:
        return "rare"
    return "medium"


def inverse_sqrt_weights(count: int) -> list[float]:
    """Creates inverse-square-root-rank sampling weights."""
    return [1 / math.sqrt(rank) for rank in range(1, count + 1)]


def weighted_choice_index(rng, weights: list[float]) -> int:
    """Returns a deterministic weighted random index using the supplied RNG."""
    total = sum(weights)
    pick = rng.random() * total
    running = 0.0
    for index, weight in enumerate(weights):
        running += weight
        if pick <= running:
            return index
    return len(weights) - 1


def classify_by_keywords(text: str, keyword_map: dict[str, list[str]]) -> str:
    """Classifies text by the first matching keyword category."""
    lowered = text.lower()
    for category, keywords in keyword_map.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return category
    return "general"


def classify_profession(profession_en: str, profession_tr: str = "") -> str:
    """Classifies a profession into a broad compatibility category."""
    return classify_by_keywords(f"{profession_en} {profession_tr}", PROFESSION_CATEGORY_KEYWORDS)


def classify_employer(employer_en: str, employer_tr: str = "") -> str:
    """Classifies an employer into a broad compatibility category."""
    return classify_by_keywords(f"{employer_en} {employer_tr}", EMPLOYER_CATEGORY_KEYWORDS)


def is_compatible_employer(profession_category: str, employer_category: str) -> bool:
    """Returns whether an employer category is acceptable for a profession category."""
    return employer_category in compatible_employer_categories(profession_category)


def compatible_employer_categories(profession_category: str) -> set[str]:
    """Returns flexible employer categories for a profession category."""
    compatibility = {
        "sports": {"sports"},
        "entertainment": {"entertainment", "media", "hospitality", "retail", "general"},
        "media": {"media", "entertainment", "public_service", "general"},
        "healthcare": {"healthcare"},
        "education": {"education"},
        "research": {"education", "healthcare", "technology", "general"},
        "technology": {"technology", "finance", "media", "retail", "logistics", "engineering", "general"},
        "engineering": {"engineering", "technology", "construction", "logistics", "general"},
        "finance": {"finance", "technology", "retail", "logistics", "healthcare", "education", "general"},
        "legal": {"legal", "finance", "public_service", "general"},
        "logistics": {"logistics", "retail", "technology", "general"},
        "construction": {"construction", "engineering", "logistics", "general"},
        "hospitality": {"hospitality", "retail", "general"},
        "retail": {"retail", "hospitality", "logistics", "general"},
        "public_service": {"public_service", "education", "healthcare", "general"},
        "administration": {"finance", "technology", "retail", "logistics", "healthcare", "education", "public_service", "general"},
        "manual_labor": {"hospitality", "healthcare", "education", "retail", "logistics", "construction", "general"},
        "general": {"general", "finance", "technology", "retail", "logistics", "healthcare", "education", "media", "engineering"},
    }
    return compatibility.get(profession_category, {"general"})


def can_use_university_as_employer(profession_en: str, profession_tr: str, profession_category: str) -> bool:
    """Returns whether a university can be used as employer for the profession."""
    if profession_category in {"education", "research"}:
        return True
    text = f"{profession_en} {profession_tr}".lower()
    keywords = ["professor", "lecturer", "academic", "researcher", "scientist", "administrator", "profesör", "akademisyen", "araştırmacı", "bilim"]
    return any(keyword in text for keyword in keywords)


def lower_bucket(bucket: str) -> str:
    """Lowers a frequency/popularity bucket by one level."""
    return BUCKET_DOWN[bucket]


def relation_frequency_buckets(popularity_bucket: str, profession_category: str, employer_fallback: bool) -> dict[str, str]:
    """Maps subject popularity to relation-specific frequency buckets."""
    works_at_bucket = popularity_bucket
    if employer_fallback:
        works_at_bucket = lower_bucket(works_at_bucket)

    studied_at_bucket = lower_bucket(popularity_bucket)
    if profession_category == "education":
        studied_at_bucket = popularity_bucket

    return {
        "profession_frequency_bucket": popularity_bucket,
        "birthplace_frequency_bucket": lower_bucket(popularity_bucket),
        "university_frequency_bucket": studied_at_bucket,
        "employer_frequency_bucket": works_at_bucket,
    }


def pearson_correlation(xs: list[float], ys: list[float]) -> float | None:
    """Computes a small dependency-free Pearson correlation."""
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def counter_dict(values) -> dict:
    """Returns a regular dict sorted by key for stable JSON output."""
    return dict(sorted(Counter(values).items()))
