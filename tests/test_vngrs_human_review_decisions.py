from __future__ import annotations

from collections import Counter
from pathlib import Path

from transfer_vs_relearning.corpora.vngrs.d0_review import read_jsonl_rows
from transfer_vs_relearning.corpora.vngrs.metadata import canonical_json_sha256


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = (
    ROOT
    / "artifacts/corpora/vngrs_m2_d0/human_review_decisions_73329e45fd8f.jsonl"
)
PACKET_SHA256 = "73329e45fd8ff2c6b24c36fa6f9b5bac767b9d25726b691d527c71f9fdf90af8"
ID_SET_SHA256 = "92468c08ad28c3fd0846b9ce897d2ab61c2793c59c1b7b5574a50daa9edf7820"


def test_authoritative_human_decisions_are_complete_packet_bound_and_all_usable() -> None:
    rows = read_jsonl_rows(DECISIONS)
    ids = [row["stable_document_id"] for row in rows]
    assert len(rows) == len(set(ids)) == 64
    assert canonical_json_sha256(sorted(ids)) == ID_SET_SHA256
    assert {row["review_packet_sha256"] for row in rows} == {PACKET_SHA256}
    assert Counter(row["verdict"] for row in rows) == {"usable": 64}
    assert all(str(row.get("reviewer", "")).strip() for row in rows)
    assert len({row["reviewer"] for row in rows}) == 1
