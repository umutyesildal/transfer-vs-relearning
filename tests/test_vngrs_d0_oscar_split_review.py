from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.corpora.vngrs.d0_audit import D0Document
from transfer_vs_relearning.corpora.vngrs.d0_oscar_split_review import (
    run_oscar_split_review_handoff,
)
from transfer_vs_relearning.corpora.vngrs.metadata import (
    FROZEN_SELECTED_SHARD_PATHS,
    canonical_json_sha256,
)


ROOT = Path(__file__).resolve().parents[1]


def _documents() -> list[D0Document]:
    rows = []
    for index in range(120):
        corpus = "oscar" if index < 110 else "mc4"
        text = f"Bu, insan incelemesi için yeterince uzun Türkçe örnek belge {index}."
        rows.append(
            D0Document(
                f"doc-{index:04d}",
                FROZEN_SELECTED_SHARD_PATHS[index % 32],
                corpus,
                text,
            )
        )
    return rows
def _loader(rows: list[D0Document]):
    def load(*_args, execution_enabled: bool = False, **_kwargs) -> list[D0Document]:
        assert execution_enabled
        return rows

    return load


def _predecessor(rows: list[D0Document]) -> tuple[dict, dict]:
    selected = [row for row in rows if row.corpus == "oscar"]
    state = {
        "status": "OSCAR_FACT_PAIR_AUDIT_COMPLETE",
        "selected_document_count": len(selected),
        "selected_document_ids_sha256": canonical_json_sha256(
            sorted(row.stable_document_id for row in selected)
        ),
    }
    audit = {
        "status": "AUDIT_COMPLETE",
        "invalid_encoding_documents": 0,
        "paired_contamination": {
            "exact_document_fact_pairs": 0,
            "unicode_normalized_document_fact_pairs": 0,
        },
    }
    return state, audit


def test_split_review_handoff_freezes_exact_ids_and_packet(tmp_path: Path) -> None:
    rows = _documents()
    state, audit = _predecessor(rows)
    output = tmp_path / "output"
    result = run_oscar_split_review_handoff(
        tmp_path / "source",
        output,
        [],
        predecessor_state=state,
        predecessor_audit=audit,
        predecessor_state_sha256="a" * 64,
        predecessor_audit_sha256="b" * 64,
        heldout_documents=10,
        review_documents=8,
        execution_enabled=True,
        document_loader=_loader(rows),
    )
    assert result["status"] == "AWAITING_HUMAN_REVIEW"
    assert result["heldout_count"] == 10
    assert result["train_count"] == 100
    assert result["sample_count"] == 8
    assert result["ready_to_train"] is False
    train = (output / "splits/train_document_ids.jsonl").read_text().splitlines()
    heldout = (output / "splits/heldout_document_ids.jsonl").read_text().splitlines()
    packet = [json.loads(line) for line in (output / "reports/human_review_packet.jsonl").read_text().splitlines()]
    decisions = [json.loads(line) for line in (output / "reports/human_review_decision_template.jsonl").read_text().splitlines()]
    assert len(train) == 100 and len(heldout) == 10 and len(packet) == len(decisions) == 8
    assert all(row["review_status"] == "awaiting_human_verdict" for row in packet)
    assert all(row["verdict"] is None and row["reviewer"] is None for row in decisions)
    manifest_path = output / "manifests/output_artifact_manifest.jsonl"
    final = json.loads((output / "control/final_audit.json").read_text())
    assert final["manifest_sha256"] == hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    assert final["artifact_count"] == 6
    assert final["status"] == "AWAITING_HUMAN_REVIEW"


def test_split_review_handoff_rejects_blocked_or_drifted_predecessor(tmp_path: Path) -> None:
    rows = _documents()
    state, audit = _predecessor(rows)
    blocked = {**audit, "status": "BLOCKED"}
    with pytest.raises(ValueError, match="did not pass"):
        run_oscar_split_review_handoff(
            tmp_path / "source",
            tmp_path / "blocked",
            [],
            predecessor_state=state,
            predecessor_audit=blocked,
            predecessor_state_sha256="a" * 64,
            predecessor_audit_sha256="b" * 64,
            execution_enabled=True,
            document_loader=_loader(rows),
        )
    drifted_state = {**state, "selected_document_count": 109}
    with pytest.raises(ValueError, match="population drift"):
        run_oscar_split_review_handoff(
            tmp_path / "source",
            tmp_path / "drifted",
            [],
            predecessor_state=drifted_state,
            predecessor_audit=audit,
            predecessor_state_sha256="a" * 64,
            predecessor_audit_sha256="b" * 64,
            heldout_documents=10,
            review_documents=8,
            execution_enabled=True,
            document_loader=_loader(rows),
        )


def test_split_review_handoff_disabled_performs_zero_writes(tmp_path: Path) -> None:
    state, audit = _predecessor(_documents())
    with pytest.raises(ValueError, match="disabled"):
        run_oscar_split_review_handoff(
            tmp_path / "source",
            tmp_path / "output",
            [],
            predecessor_state=state,
            predecessor_audit=audit,
            predecessor_state_sha256="a" * 64,
            predecessor_audit_sha256="b" * 64,
        )
    assert not (tmp_path / "output").exists()


def test_split_review_contract_is_one_offline_cpu_handoff() -> None:
    contract = ROOT / "documentation/contracts/corpora/vngrs-m2-oscar-split-review-handoff-v1.md"
    config = yaml.safe_load(
        (ROOT / "configs/corpora/vngrs_m2_oscar_split_review_v1.yaml").read_text()
    )
    runner = (ROOT / "scripts/corpora/run_vngrs_m2_oscar_split_review_v1.py").read_text()
    submitter = (ROOT / "scripts/corpora/submit_vngrs_m2_oscar_split_review_v1.sh").read_text()
    slurm = (ROOT / "slurm/m2/split_review_vngrs_m2_oscar_v1.slurm").read_text()
    assert contract.is_file()
    assert config["status"] == "frozen_unexecuted"
    assert config["split"]["heldout_documents"] == 10_000
    assert config["split"]["expected_train_documents"] == 344_482
    assert config["human_review"]["sample_documents"] == 64
    assert config["human_review"]["decisions_created_by_wave"] is False
    assert config["predecessor_fact_pair_audit"]["access"] == "read_only"
    assert config["output"]["maximum_success_bytes"] == 128 * 1024**2
    assert config["authority"]["human_verdict_entry"] is False
    assert config["authority"]["training"] is False
    assert "--test-only" in submitter
    assert "PYTHONDONTWRITEBYTECODE=1" in slurm
    assert "train_clm" not in runner + submitter + slurm
    assert "requests" not in runner and "http" not in runner.casefold()
