from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from transfer_vs_relearning.corpora.vngrs.d0_audit import (
    D0Document,
    EXPECTED_MODELS,
    human_review_sample,
)
from transfer_vs_relearning.corpora.vngrs.d0_orchestration import (
    D0OrchestrationPolicy,
    finalize_d0_phase2,
    run_d0_orchestration,
    run_d0_phase1,
)
from transfer_vs_relearning.corpora.vngrs.d0_review import review_packet_sha256
from transfer_vs_relearning.corpora.vngrs.materialization import (
    FullObjectResponse,
    MaterializationPolicy,
    SourceObject,
    immutable_resolve_url,
)
from transfer_vs_relearning.corpora.vngrs.metadata import FROZEN_SELECTED_SHARD_PATHS, VNGRS_REVISION
from transfer_vs_relearning.corpora.vngrs.parquet_loader import _stable_id, load_verified_parquet_documents


def parquet_payload(index: int) -> bytes:
    table = pa.table(
        {
            "text": [f"Bu temiz Türkçe belge {index} için yeterince uzun ve benzersizdir."],
            "corpus": ["OSCAR" if index % 2 == 0 else "mC4"],
            "original_id": [f"original-{index}"],
        }
    )
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink)
    return sink.getvalue().to_pybytes()


def registry_and_payloads() -> tuple[list[SourceObject], dict[str, bytes]]:
    payloads = {path: parquet_payload(index) for index, path in enumerate(FROZEN_SELECTED_SHARD_PATHS)}
    rows = []
    for path, payload in payloads.items():
        digest = hashlib.sha256(payload).hexdigest()
        rows.append(SourceObject(path, VNGRS_REVISION, len(payload), digest, f"sha256:{digest}", immutable_resolve_url(path)))
    return rows, payloads


def transport(payloads: dict[str, bytes]):
    def get(source: SourceObject) -> FullObjectResponse:
        payload = payloads[source.path]
        return FullObjectResponse(
            200,
            {"Content-Length": str(len(payload)), "Content-Type": "application/vnd.apache.parquet", "X-Linked-Etag": source.lfs_oid},
            (payload,),
            "https://cdn-lfs.example.invalid/object",
        )
    return get


@dataclass
class Tokenizer:
    role: str
    manifest_sha256: str = "a" * 64
    asset_sha256: str = "b" * 64

    @property
    def model_id(self) -> str:
        return EXPECTED_MODELS[self.role][0]

    @property
    def revision(self) -> str:
        return EXPECTED_MODELS[self.role][1]

    def encode(self, text: str, *, add_special_tokens: bool = False) -> list[int]:
        return list(range(len(text.split())))


def expected_documents(rows: list[SourceObject]) -> list[D0Document]:
    return [
        D0Document(
            _stable_id(source, "OSCAR" if index % 2 == 0 else "mC4", f"original-{index}", 0, 0),
            source.path,
            "OSCAR" if index % 2 == 0 else "mC4",
            f"Bu temiz Türkçe belge {index} için yeterince uzun ve benzersizdir.",
        )
        for index, source in enumerate(rows)
    ]


def test_parquet_loader_is_disabled_and_validates_natural_identity(tmp_path: Path) -> None:
    rows, payloads = registry_and_payloads()
    path = tmp_path / "raw" / rows[0].path
    path.parent.mkdir(parents=True)
    path.write_bytes(payloads[rows[0].path])
    with pytest.raises(ValueError, match="disabled"):
        load_verified_parquet_documents(tmp_path, [rows[0]])
    loaded = load_verified_parquet_documents(tmp_path, [rows[0]], execution_enabled=True)
    assert len(loaded) == 1
    assert loaded[0].stable_document_id == expected_documents(rows)[0].stable_document_id


def test_offline_end_to_end_d0_orchestration_closes_stage_order(tmp_path: Path) -> None:
    rows, payloads = registry_and_payloads()
    documents = expected_documents(rows)
    selected = human_review_sample(documents, sample_size=2)
    reviewed = [{"stable_document_id": row["stable_document_id"], "verdict": "usable"} for row in selected]
    total = sum(row.size_bytes for row in rows)
    result = run_d0_orchestration(
        tmp_path / "d0",
        rows,
        transport=transport(payloads),
        storage_observation={"resolved_parent": "/vol/tmp2/yesildau", "proposed_root_absent": True, "available_bytes": 122_943_170_412_544, "available_inodes": 2_284_282_885},
        synthetic_surfaces={"never": "Bu ifade hiçbir belgede bulunmaz"},
        tokenizers=[Tokenizer("olmo"), Tokenizer("qwen"), Tokenizer("smollm")],
        reviewed_sample=(row for row in reviewed),
        policy=D0OrchestrationPolicy(execution_enabled=True, heldout_documents=2, human_review_documents=2),
        materialization_policy=MaterializationPolicy(selected_paths=FROZEN_SELECTED_SHARD_PATHS, expected_total_bytes=total, max_response_bytes=total, chunk_size_upper_bound=max(map(len, payloads.values())), execution_enabled=True),
    )
    assert result["status"] == "D0_EVIDENCE_COMPLETE"
    assert result["materialization"]["object_count"] == 32
    assert result["split"]["heldout_count"] == 2
    assert result["human_review"]["status"] == "HUMAN_REVIEW_PASS"
    assert set(result["tokenizer_accounting"]) == {"olmo", "qwen", "smollm"}
    assert result["trwiki_training_rows"] == 0
    assert result["ready_to_train"] is False
    final = result["final_audit"]
    assert final["status"] == "D0_EVIDENCE_COMPLETE"
    assert final["self_reference"] is False
    assert (tmp_path / "d0/manifests/output_artifact_manifest.jsonl").is_file()
    assert (tmp_path / "d0/control/final_audit.json").is_file()
    assert not (tmp_path / "d0/manifests/output_artifact_manifest.jsonl.partial").exists()
    manifest_path = tmp_path / "d0/manifests/output_artifact_manifest.jsonl"
    manifest_payload = manifest_path.read_bytes()
    assert hashlib.sha256(manifest_payload).hexdigest() == final["manifest_sha256"]
    manifest_rows = [json.loads(line) for line in manifest_payload.splitlines()]
    assert all(row["schema_version"] == 1 for row in manifest_rows)
    assert {row["path"] for row in manifest_rows}.isdisjoint(
        {"manifests/output_artifact_manifest.jsonl", "control/final_audit.json"}
    )
    for row in manifest_rows:
        payload = (tmp_path / "d0" / row["path"]).read_bytes()
        assert len(payload) == row["bytes"]
        assert hashlib.sha256(payload).hexdigest() == row["sha256"]


def test_post_materialization_failure_is_typed_and_fail_closed(tmp_path: Path) -> None:
    rows, payloads = registry_and_payloads()
    total = sum(row.size_bytes for row in rows)
    root = tmp_path / "blocked"
    with pytest.raises(ValueError, match="audit blocked"):
        run_d0_orchestration(
            root,
            rows,
            transport=transport(payloads),
            storage_observation={"resolved_parent": "/vol/tmp2/yesildau", "proposed_root_absent": True, "available_bytes": 122_943_170_412_544, "available_inodes": 2_284_282_885},
            synthetic_surfaces={"hit": "Bu temiz Türkçe belge 0"},
            tokenizers=[Tokenizer("olmo"), Tokenizer("qwen"), Tokenizer("smollm")],
            reviewed_sample=[],
            policy=D0OrchestrationPolicy(execution_enabled=True, heldout_documents=2, human_review_documents=2),
            materialization_policy=MaterializationPolicy(selected_paths=FROZEN_SELECTED_SHARD_PATHS, expected_total_bytes=total, max_response_bytes=total, chunk_size_upper_bound=max(map(len, payloads.values())), execution_enabled=True),
        )
    failure = json.loads((root / "control/d0_failure.json").read_text(encoding="utf-8"))
    assert failure["status"] == "BLOCKED"
    assert failure["phase"] == "lightweight_audit"
    assert failure["ready_to_train"] is False
    audit = json.loads((root / "reports/lightweight_audit.json").read_text(encoding="utf-8"))
    assert audit["status"] == "BLOCKED"
    assert audit["synthetic_contamination"]["exact_hit_count"] == 1
    assert audit["synthetic_contamination"]["exact_hit_examples"][0]["pattern_id"] == "hit"
    assert not (root / "control/final_audit.json").exists()


def test_two_phase_review_handoff_revalidates_and_finalizes(tmp_path: Path) -> None:
    rows, payloads = registry_and_payloads()
    total = sum(row.size_bytes for row in rows)
    root = tmp_path / "two-phase"
    policy = D0OrchestrationPolicy(execution_enabled=True, heldout_documents=2, human_review_documents=2)
    materialization_policy = MaterializationPolicy(selected_paths=FROZEN_SELECTED_SHARD_PATHS, expected_total_bytes=total, max_response_bytes=total, chunk_size_upper_bound=max(map(len, payloads.values())), execution_enabled=True)
    state = run_d0_phase1(
        root,
        rows,
        transport=transport(payloads),
        preflight={"status": "D0_PREFLIGHT_PASS", "storage": {"schema_version": 1, "status": "STORAGE_BOUNDS_PASS"}},
        synthetic_surfaces={"never": "Bu ifade hiçbir belgede bulunmaz"},
        policy=policy,
        materialization_policy=materialization_policy,
    )
    assert state["status"] == "AWAITING_HUMAN_REVIEW"
    assert not (root / "control/final_audit.json").exists()
    packet = [json.loads(line) for line in (root / "reports/human_review_packet.jsonl").read_text().splitlines()]
    packet_hash = review_packet_sha256(packet)
    decisions = [
        {"schema_version": 1, "stable_document_id": row["stable_document_id"], "review_packet_sha256": packet_hash, "verdict": "usable", "reviewer": "fixture-reviewer"}
        for row in packet
    ]
    result = finalize_d0_phase2(
        root,
        rows,
        synthetic_surfaces={"never": "Bu ifade hiçbir belgede bulunmaz"},
        tokenizers=[Tokenizer("olmo"), Tokenizer("qwen"), Tokenizer("smollm")],
        decisions=decisions,
        policy=policy,
    )
    assert result["final_audit"]["status"] == "D0_EVIDENCE_COMPLETE"
    manifest = (root / "manifests/output_artifact_manifest.jsonl").read_text()
    assert "control/phase1_state.json" in manifest
    assert "reports/human_review_packet.jsonl" in manifest
    assert "reports/human_review_decisions.jsonl" in manifest


def test_two_phase_review_rejects_nonusable_content_without_terminal_pass(tmp_path: Path) -> None:
    rows, payloads = registry_and_payloads()
    total = sum(row.size_bytes for row in rows)
    root = tmp_path / "unsafe"
    policy = D0OrchestrationPolicy(execution_enabled=True, heldout_documents=2, human_review_documents=2)
    run_d0_phase1(
        root, rows, transport=transport(payloads),
        preflight={"status": "D0_PREFLIGHT_PASS", "storage": {"schema_version": 1, "status": "STORAGE_BOUNDS_PASS"}},
        synthetic_surfaces={"never": "Bu ifade hiçbir belgede bulunmaz"}, policy=policy,
        materialization_policy=MaterializationPolicy(selected_paths=FROZEN_SELECTED_SHARD_PATHS, expected_total_bytes=total, max_response_bytes=total, chunk_size_upper_bound=max(map(len, payloads.values())), execution_enabled=True),
    )
    packet = [json.loads(line) for line in (root / "reports/human_review_packet.jsonl").read_text().splitlines()]
    packet_hash = review_packet_sha256(packet)
    decisions = [{"stable_document_id": row["stable_document_id"], "review_packet_sha256": packet_hash, "verdict": "unsafe" if index == 0 else "usable", "reviewer": "fixture-reviewer"} for index, row in enumerate(packet)]
    with pytest.raises(ValueError, match="unsafe/unusable"):
        finalize_d0_phase2(root, rows, synthetic_surfaces={"never": "Bu ifade hiçbir belgede bulunmaz"}, tokenizers=[Tokenizer("olmo"), Tokenizer("qwen"), Tokenizer("smollm")], decisions=decisions, policy=policy)
    assert not (root / "control/final_audit.json").exists()


def test_disabled_orchestration_is_zero_write_and_zero_transport(tmp_path: Path) -> None:
    rows, _ = registry_and_payloads()
    calls = 0

    def forbidden(_: SourceObject) -> FullObjectResponse:
        nonlocal calls
        calls += 1
        raise AssertionError

    with pytest.raises(ValueError, match="disabled"):
        run_d0_orchestration(
            tmp_path / "never",
            rows,
            transport=forbidden,
            storage_observation={},
            synthetic_surfaces={},
            tokenizers=[],
            reviewed_sample=[],
        )
    assert calls == 0
    assert not (tmp_path / "never").exists()
