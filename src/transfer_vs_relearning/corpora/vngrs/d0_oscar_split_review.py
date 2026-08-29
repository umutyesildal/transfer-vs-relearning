"""Execution-disabled OSCAR split and human-review handoff stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .d0_audit import D0Document, exact_heldout_split, human_review_sample
from .d0_bundle import write_d0_failure, write_d0_split_review_handoff
from .d0_review import build_review_packet, decision_template, review_packet_sha256
from .materialization import SourceObjectV3
from .metadata import canonical_json_sha256
from .parquet_loader_v3 import load_verified_parquet_documents_v3


def run_oscar_split_review_handoff(
    source_root: str | Path,
    output_root: str | Path,
    objects: Iterable[SourceObjectV3],
    *,
    predecessor_state: Mapping[str, Any],
    predecessor_audit: Mapping[str, Any],
    predecessor_state_sha256: str,
    predecessor_audit_sha256: str,
    heldout_documents: int = 10_000,
    review_documents: int = 64,
    execution_enabled: bool = False,
    document_loader: Callable[..., list[D0Document]] = load_verified_parquet_documents_v3,
) -> dict[str, Any]:
    """Freeze exact OSCAR split IDs and a bounded packet, then stop for human input."""

    if not execution_enabled:
        raise ValueError("OSCAR split/review handoff execution is disabled")
    destination = Path(output_root)
    if destination.exists():
        raise ValueError("OSCAR split/review output root must be fresh and absent")
    if predecessor_state.get("status") != "OSCAR_FACT_PAIR_AUDIT_COMPLETE":
        raise ValueError("fact-pair predecessor state is not complete")
    paired = predecessor_audit.get("paired_contamination") or {}
    if (
        predecessor_audit.get("status") != "AUDIT_COMPLETE"
        or predecessor_audit.get("invalid_encoding_documents") != 0
        or paired.get("exact_document_fact_pairs") != 0
        or paired.get("unicode_normalized_document_fact_pairs") != 0
    ):
        raise ValueError("fact-pair predecessor audit did not pass its frozen gate")
    try:
        registry = tuple(objects)
        documents = document_loader(source_root, registry, execution_enabled=True)
        selected_documents = [row for row in documents if row.corpus == "oscar"]
        selected_ids_sha256 = canonical_json_sha256(
            sorted(row.stable_document_id for row in selected_documents)
        )
        if (
            len(selected_documents) != predecessor_state.get("selected_document_count")
            or selected_ids_sha256 != predecessor_state.get("selected_document_ids_sha256")
        ):
            raise ValueError("exact lowercase OSCAR population drift")
        split = exact_heldout_split(selected_documents, heldout_documents=heldout_documents)
        sample = human_review_sample(selected_documents, sample_size=review_documents)
        packet = build_review_packet(selected_documents, sample)
        packet_hash = review_packet_sha256(packet)
        state = {
            "schema_version": 1,
            "status": "AWAITING_HUMAN_REVIEW",
            "source_root": str(Path(source_root)),
            "source_manifest": "control/materialization_v3.json",
            "source_object_count": len(registry),
            "corpus_predicate": {
                "field": "corpus",
                "operator": "exact_string_equality",
                "value": "oscar",
            },
            "document_count": len(selected_documents),
            "document_ids_sha256": selected_ids_sha256,
            "predecessor_state_sha256": predecessor_state_sha256,
            "predecessor_audit_sha256": predecessor_audit_sha256,
            "split_namespace": split["namespace"],
            "split_seed": split["seed"],
            "heldout_count": split["heldout_count"],
            "train_count": split["train_count"],
            "split_sha256": canonical_json_sha256(split),
            "sample_count": len(sample),
            "sample_sha256": canonical_json_sha256(sample),
            "review_packet_sha256": packet_hash,
            "review_decisions_complete": False,
            "tokenizer_accounting_created": False,
            "phase2_opened": False,
            "training_opened": False,
            "ready_to_train": False,
        }
        final = write_d0_split_review_handoff(
            destination,
            state=state,
            split=split,
            sample=sample,
            packet=packet,
            decision_rows=decision_template(packet),
        )
        return {**state, "final_audit": final}
    except Exception as exc:
        write_d0_failure(destination, phase="oscar_split_review_handoff", error=exc)
        raise
