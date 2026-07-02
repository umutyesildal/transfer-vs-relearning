from __future__ import annotations

import re
import unicodedata

_APOSTROPHES = {"’": "'", "‘": "'", "`": "'"}


def normalize_text(value: str) -> str:
    """Unicode-aware comparison key for object identity checks."""
    value = "".join(_APOSTROPHES.get(ch, ch) for ch in value)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold()
    value = value.replace("ı", "i")
    value = re.sub(r"[\W_]+", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def slugify(value: str) -> str:
    key = normalize_text(value)
    key = re.sub(r"[^a-z0-9]+", "-", key)
    return key.strip("-") or "object"
