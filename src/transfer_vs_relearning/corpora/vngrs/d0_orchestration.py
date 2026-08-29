"""Fail-closed, transport-injected D0 stage orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
import json

from .d0_audit import (
    D0Document,
    TokenizerAdapter,
    exact_heldout_split,
    human_review_sample,
    lightweight_audit,
    tokenizer_accounting,
)
from .d0_storage import validate_storage_observation
from .d0_bundle import write_d0_evidence_bundle, write_d0_failure, write_d0_phase1_audit_evidence
from .d0_review import build_review_packet, read_jsonl_rows, review_packet_sha256, validate_review_decisions, write_review_handoff, write_validated_decisions
from .metadata import canonical_json_sha256
from .materialization import (
    MaterializationPolicy,
    SourceObject,
    Transport,
    materialize_full_objects,
)
from .parquet_loader import load_verified_parquet_documents


@dataclass(frozen=True)
class D0OrchestrationPolicy:
    execution_enabled: bool = False
    heldout_documents: int = 10_000
    human_review_documents: int = 64


def run_d0_phase1(
    root: str | Path,
    objects: Iterable[SourceObject],
    *,
    transport: Transport,
    preflight: Mapping[str, Any],
    synthetic_surfaces: Mapping[str, str],
    policy: D0OrchestrationPolicy,
    materialization_policy: MaterializationPolicy,
    document_loader: Callable[..., list[D0Document]] = load_verified_parquet_documents,
    materializer: Callable[..., Any] = materialize_full_objects,
) -> dict[str, Any]:
    """Materialize and freeze a bounded review packet; deliberately stop before PASS."""

    if not policy.execution_enabled or preflight.get("status") != "D0_PREFLIGHT_PASS":
        raise ValueError("authorized, passing D0 preflight is required")
    registry = tuple(objects)
    materialized = materializer(root, registry, transport=transport, policy=materialization_policy)
    try:
        documents = document_loader(root, registry, execution_enabled=True)
        audit = lightweight_audit(documents, synthetic_surfaces=synthetic_surfaces)
        write_d0_phase1_audit_evidence(root, audit=audit)
        if audit["status"] != "AUDIT_COMPLETE":
            raise ValueError("mandatory lightweight audit blocked D0")
        split = exact_heldout_split(documents, heldout_documents=policy.heldout_documents)
        selected = human_review_sample(documents, sample_size=policy.human_review_documents)
        packet = build_review_packet(documents, selected)
        state = {
            "schema_version": 1,
            "status": "AWAITING_HUMAN_REVIEW",
            "preflight": dict(preflight),
            "source_rows": materialized.source_rows,
            "request_rows": materialized.request_rows,
            "document_count": len(documents),
            "audit_sha256": canonical_json_sha256(audit),
            "split_sha256": canonical_json_sha256(split),
            "sample_sha256": canonical_json_sha256(selected),
            "review_packet_sha256": review_packet_sha256(packet),
            "ready_to_train": False,
        }
        write_review_handoff(root, state=state, packet=packet)
        return state
    except Exception as exc:
        write_d0_failure(root, phase="phase1_review_handoff", error=exc)
        raise


def finalize_d0_phase2(
    root: str | Path,
    objects: Iterable[SourceObject],
    *,
    synthetic_surfaces: Mapping[str, str],
    tokenizers: Iterable[TokenizerAdapter],
    decisions: Iterable[Mapping[str, Any]],
    policy: D0OrchestrationPolicy,
    document_loader: Callable[..., list[D0Document]] = load_verified_parquet_documents,
) -> dict[str, Any]:
    """Revalidate immutable phase-1 evidence and finalize only after exact human decisions."""

    if not policy.execution_enabled:
        raise ValueError("D0 phase-2 execution is disabled")
    root_path = Path(root)
    state = json.loads((root_path / "control/phase1_state.json").read_text(encoding="utf-8"))
    packet = read_jsonl_rows(root_path / "reports/human_review_packet.jsonl")
    if state.get("status") != "AWAITING_HUMAN_REVIEW" or review_packet_sha256(packet) != state.get("review_packet_sha256"):
        raise ValueError("phase-1 state or review packet drift")
    registry = tuple(objects)
    documents = document_loader(root, registry, execution_enabled=True)
    audit = lightweight_audit(documents, synthetic_surfaces=synthetic_surfaces)
    split = exact_heldout_split(documents, heldout_documents=policy.heldout_documents)
    selected = human_review_sample(documents, sample_size=policy.human_review_documents)
    if (
        len(documents) != state["document_count"]
        or canonical_json_sha256(audit) != state["audit_sha256"]
        or canonical_json_sha256(split) != state["split_sha256"]
        or canonical_json_sha256(selected) != state["sample_sha256"]
    ):
        raise ValueError("phase-2 corpus/audit/split/sample drift")
    reviewed = validate_review_decisions(packet, decisions)
    review = _validate_human_review(selected, reviewed)
    tokenizer_reports = tokenizer_accounting(documents, tokenizers)
    if any(row["status"] != "ACCOUNTING_COMPLETE" for row in tokenizer_reports.values()):
        raise ValueError("one or more tokenizer accounting reports blocked D0")
    result = {
        "schema_version": 1,
        "status": "D0_EVIDENCE_COMPLETE",
        "storage": state["preflight"]["storage"],
        "audit": audit,
        "split": split,
        "human_review_sample": selected,
        "reviewed_sample": reviewed,
        "human_review": review,
        "tokenizer_accounting": tokenizer_reports,
        "trwiki_training_rows": 0,
        "ready_to_train": False,
    }
    try:
        decisions_path = write_validated_decisions(root, reviewed)
        result["final_audit"] = write_d0_evidence_bundle(
            root,
            result,
            source_rows=state["source_rows"],
            request_rows=state["request_rows"],
            existing_artifacts=(
                "control/phase1_state.json",
                "reports/human_review_packet.jsonl",
                "reports/human_review_decision_template.jsonl",
                "reports/lightweight_audit.json",
                decisions_path,
            ),
        )
    except Exception as exc:
        write_d0_failure(root, phase="phase2_evidence_bundle", error=exc)
        raise
    return result


def _validate_human_review(
    selected: list[dict[str, Any]], reviewed: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    rows = [dict(row) for row in reviewed]
    selected_ids = [row["stable_document_id"] for row in selected]
    if sorted(row.get("stable_document_id") for row in rows) != sorted(selected_ids):
        raise ValueError("human-review decisions do not exactly cover the frozen sample")
    if len(rows) != len(selected_ids) or len({row["stable_document_id"] for row in rows}) != len(rows):
        raise ValueError("human-review decisions contain duplicates")
    if any(row.get("verdict") != "usable" for row in rows):
        raise ValueError("human review contains unsafe/unusable or unresolved evidence")
    return {"status": "HUMAN_REVIEW_PASS", "reviewed_documents": len(rows)}


def run_d0_orchestration(
    root: str | Path,
    objects: Iterable[SourceObject],
    *,
    transport: Transport,
    storage_observation: Mapping[str, Any],
    synthetic_surfaces: Mapping[str, str],
    tokenizers: Iterable[TokenizerAdapter],
    reviewed_sample: Iterable[Mapping[str, Any]],
    document_loader: Callable[..., list[D0Document]] = load_verified_parquet_documents,
    policy: D0OrchestrationPolicy = D0OrchestrationPolicy(),
    materialization_policy: MaterializationPolicy = MaterializationPolicy(execution_enabled=True),
) -> dict[str, Any]:
    """Run the exact stage order; disabled policy performs zero writes and zero transport."""

    if not policy.execution_enabled:
        raise ValueError("D0 orchestration execution is disabled")
    registry = tuple(objects)
    storage = validate_storage_observation(storage_observation)
    materialized = materialize_full_objects(
        root,
        registry,
        transport=transport,
        policy=materialization_policy,
    )
    phase = "parquet_identity_load"
    try:
        documents = document_loader(root, registry, execution_enabled=True)
        phase = "lightweight_audit"
        audit = lightweight_audit(documents, synthetic_surfaces=synthetic_surfaces)
        write_d0_phase1_audit_evidence(root, audit=audit)
        if audit["status"] != "AUDIT_COMPLETE":
            raise ValueError("mandatory lightweight audit blocked D0")
        phase = "document_disjoint_split"
        split = exact_heldout_split(documents, heldout_documents=policy.heldout_documents)
        phase = "human_review"
        selected = human_review_sample(documents, sample_size=policy.human_review_documents)
        reviewed_rows = [dict(row) for row in reviewed_sample]
        review = _validate_human_review(selected, reviewed_rows)
        phase = "three_tokenizer_accounting"
        tokenizer_reports = tokenizer_accounting(documents, tokenizers)
        if any(report["status"] != "ACCOUNTING_COMPLETE" for report in tokenizer_reports.values()):
            raise ValueError("one or more tokenizer accounting reports blocked D0")
    except Exception as exc:
        write_d0_failure(root, phase=phase, error=exc)
        raise
    result = {
        "schema_version": 1,
        "status": "D0_EVIDENCE_COMPLETE",
        "stage_order": [
            "storage_preflight",
            "materialization",
            "parquet_identity_load",
            "lightweight_audit",
            "document_disjoint_split",
            "human_review",
            "three_tokenizer_accounting",
        ],
        "storage": storage,
        "materialization": {
            "status": materialized.status,
            "object_count": len(materialized.source_rows),
            "response_bytes": materialized.total_response_bytes,
        },
        "audit": audit,
        "split": split,
        "human_review_sample": selected,
        "reviewed_sample": reviewed_rows,
        "human_review": review,
        "tokenizer_accounting": tokenizer_reports,
        "trwiki_training_rows": 0,
        "ready_to_train": False,
    }
    try:
        result["final_audit"] = write_d0_evidence_bundle(
            root,
            result,
            source_rows=materialized.source_rows,
            request_rows=materialized.request_rows,
            existing_artifacts=("reports/lightweight_audit.json",),
        )
    except Exception as exc:
        write_d0_failure(root, phase="evidence_bundle", error=exc)
        raise
    return result
