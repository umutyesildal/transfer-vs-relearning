from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.corpora.build_vngrs_human_review_html import build_review_html


def _packet(path: Path, count: int = 64) -> None:
    rows = [
        {
            "schema_version": 1,
            "stable_document_id": f"doc-{index:02d}",
            "selection_stratum": f"oscar|q{index % 4}",
            "text_sha256": f"{index:064x}",
            "text_utf8_bytes": 100 + index,
            "excerpt": "Türkçe örnek </script> & metin \u0085 devam",
        }
        for index in range(count)
    ]
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def test_builds_self_contained_packet_bound_review_ui(tmp_path: Path) -> None:
    packet = tmp_path / "packet.jsonl"
    output = tmp_path / "review.html"
    _packet(packet)
    build_review_html(packet, output)
    page = output.read_text(encoding="utf-8")
    assert "OSCAR doküman incelemesi" in page
    assert "Kararları JSONL indir" in page
    assert "review_packet_sha256" in page
    assert "\\u003c/script\\u003e" in page
    assert "localStorage" in page
    assert "lines.join('\\n')+'\\n'" in page


def test_rejects_non_64_packet(tmp_path: Path) -> None:
    packet = tmp_path / "packet.jsonl"
    _packet(packet, 63)
    with pytest.raises(ValueError, match="exactly 64"):
        build_review_html(packet, tmp_path / "review.html")
