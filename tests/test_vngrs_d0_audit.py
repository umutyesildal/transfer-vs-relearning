from __future__ import annotations

from dataclasses import dataclass

import pytest

from transfer_vs_relearning.corpora.vngrs.d0_audit import (
    D0Document,
    EXPECTED_MODELS,
    exact_heldout_split,
    human_review_sample,
    human_review_sample_with_stratum_floor,
    human_review_stratum_inventory,
    lightweight_audit,
    tokenizer_accounting,
)
from transfer_vs_relearning.corpora.vngrs.metadata import FROZEN_SELECTED_SHARD_PATHS


def documents(count: int = 10_064) -> list[D0Document]:
    return [
        D0Document(
            stable_document_id=f"doc-{index:05d}",
            shard_path=FROZEN_SELECTED_SHARD_PATHS[index % 32],
            corpus="OSCAR" if index % 2 == 0 else "mC4",
            text=f"Bu temiz Türkçe belge {index} için yeterince uzun bir örnek metindir.",
        )
        for index in range(count)
    ]


def test_exact_heldout_split_is_order_independent_and_exact() -> None:
    rows = documents()
    first = exact_heldout_split(rows)
    second = exact_heldout_split(reversed(rows))
    assert first == second
    assert first["heldout_count"] == 10_000
    assert first["train_count"] == 64
    assert set(first["heldout_document_ids"]).isdisjoint(first["train_document_ids"])
    assert first["trwiki_training_rows"] == 0


def test_human_review_sample_is_stratified_text_free_and_deterministic() -> None:
    rows = documents(640)
    sample = human_review_sample(rows)
    assert sample == human_review_sample(reversed(rows))
    assert len(sample) == 64
    assert len({row["stable_document_id"] for row in sample}) == 64
    assert {row["shard_quartile"] for row in sample} == {0, 1, 2, 3}
    assert all("text" not in row and row["review_status"] == "pending_human_review" for row in sample)


def test_review_coverage_floor_includes_every_nonempty_quartile() -> None:
    rows = documents(640)
    sample = human_review_sample_with_stratum_floor(rows)
    assert len(sample) == 64
    assert {row["shard_quartile"] for row in sample} == {0, 1, 2, 3}
    assert all(row["allocation_rule"] == "one_per_nonempty_stratum_then_largest_remainder" for row in sample)
    inventory = human_review_stratum_inventory(rows)
    assert inventory["document_count"] == 640
    assert inventory["nonempty_strata"] == 4
    assert sum(row["documents"] for row in inventory["strata"]) == 640


def test_lightweight_audit_reports_composition_regex_contamination_and_duplicates() -> None:
    rows = documents(80)
    rows[0] = D0Document(rows[0].stable_document_id, rows[0].shard_path, "OSCAR", "Hedef Kişi bahis \ufffd")
    rows[1] = D0Document(rows[1].stable_document_id, rows[1].shard_path, "mC4", rows[2].text)
    audit = lightweight_audit(rows, synthetic_surfaces={"subject-1": "Hedef Kişi"})
    assert audit["status"] == "BLOCKED"
    assert audit["composition"]["oscar"]["documents"] == 40
    assert audit["composition"]["mc4"]["documents"] == 40
    assert audit["regex_document_counts"]["invalid_encoding"] == 1
    assert audit["regex_document_counts"]["seo_or_betting"] == 1
    assert audit["synthetic_contamination"]["exact_hits"]
    assert audit["normalized_text_duplicate_groups"] == 1


@dataclass
class StubTokenizer:
    role: str
    multiplier: int
    manifest_sha256: str = "a" * 64
    asset_sha256: str = "b" * 64

    @property
    def model_id(self) -> str:
        return EXPECTED_MODELS[self.role][0]

    @property
    def revision(self) -> str:
        return EXPECTED_MODELS[self.role][1]

    def encode(self, text: str, *, add_special_tokens: bool = False) -> list[int]:
        assert add_special_tokens is False
        return list(range(max(1, len(text.split()) * self.multiplier)))


def test_three_tokenizer_reports_share_ids_but_not_token_equality() -> None:
    reports = tokenizer_accounting(
        documents(64),
        [StubTokenizer("olmo", 1), StubTokenizer("qwen", 2), StubTokenizer("smollm", 3)],
    )
    assert set(reports) == {"olmo", "qwen", "smollm"}
    assert len({row["document_ids_sha256"] for row in reports.values()}) == 1
    assert reports["olmo"]["token_count"] < reports["qwen"]["token_count"] < reports["smollm"]["token_count"]
    assert all(row["packing_policy_applied"] is False for row in reports.values())
    assert all(row["cross_model_token_equality_gate"] is False for row in reports.values())


def test_tokenizer_identity_and_zero_token_fail_closed() -> None:
    bad = StubTokenizer("olmo", 1, manifest_sha256="missing")
    with pytest.raises(ValueError, match="hash unresolved"):
        tokenizer_accounting(documents(2), [bad, StubTokenizer("qwen", 1), StubTokenizer("smollm", 1)])

    class ZeroTokenizer(StubTokenizer):
        def encode(self, text: str, *, add_special_tokens: bool = False) -> list[int]:
            return []

    reports = tokenizer_accounting(
        documents(2),
        [ZeroTokenizer("olmo", 1), StubTokenizer("qwen", 1), StubTokenizer("smollm", 1)],
    )
    assert reports["olmo"]["status"] == "BLOCKED"
    assert reports["olmo"]["zero_token_documents"] == 2
    assert reports["olmo"]["exception_documents"] == 0
