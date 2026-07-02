from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class CorpusDocument:
    document_id: str
    page_id: str
    revision_id: str
    title: str
    namespace: int
    dump_date: str
    source_project: str
    text: str
    raw_wikitext_sha256: str | None = None
    normalized_text_sha256: str | None = None
    processing_stage: str = "extracted"
    filtering_metrics: dict[str, Any] | None = None
    filtering_reasons: list[str] | None = None
    contamination_status: str = "unknown"
    split: str | None = None
    provenance: dict[str, Any] | None = None

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "CorpusDocument":
        return cls(**payload)
