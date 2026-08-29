"""Execution-disabled pre-verdict review coverage validation and repair."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .d0_audit import (
    D0Document,
    human_review_sample_with_stratum_floor,
    human_review_stratum_inventory,
)
from .d0_bundle import write_d0_failure, write_d0_review_coverage_handoff
from .d0_review import build_review_packet, decision_template, read_jsonl_rows, review_packet_sha256
from .materialization import SourceObjectV3
from .metadata import canonical_json_sha256
from .parquet_loader_v3 import load_verified_parquet_documents_v3


def run_oscar_review_coverage_repair(
    source_root: str | Path,
    predecessor_root: str | Path,
    output_root: str | Path,
    objects: Iterable[SourceObjectV3],
    *,
    predecessor_state: Mapping[str, Any],
    predecessor_final: Mapping[str, Any],
    predecessor_state_sha256: str,
    predecessor_final_sha256: str,
    review_documents: int = 64,
    execution_enabled: bool = False,
    document_loader: Callable[..., list[D0Document]] = load_verified_parquet_documents_v3,
) -> dict[str, Any]:
    """Inventory real quartiles and freeze a minimum-one-per-nonempty-stratum packet."""

    if not execution_enabled:
        raise ValueError("OSCAR review coverage repair execution is disabled")
    destination = Path(output_root)
    if destination.exists():
        raise ValueError("OSCAR review coverage output root must be fresh and absent")
    if (
        predecessor_state.get("status") != "AWAITING_HUMAN_REVIEW"
        or predecessor_final.get("status") != "AWAITING_HUMAN_REVIEW"
        or predecessor_final.get("split_created") is not True
        or predecessor_final.get("human_review_packet_created") is not True
    ):
        raise ValueError("split/review predecessor is incomplete")
    try:
        prior = Path(predecessor_root)
        train_ids = {
            row["stable_document_id"]
            for row in read_jsonl_rows(prior / "splits/train_document_ids.jsonl")
        }
        heldout_ids = {
            row["stable_document_id"]
            for row in read_jsonl_rows(prior / "splits/heldout_document_ids.jsonl")
        }
        if (
            len(train_ids) != predecessor_state.get("train_count")
            or len(heldout_ids) != predecessor_state.get("heldout_count")
            or train_ids & heldout_ids
        ):
            raise ValueError("frozen split identity or disjointness drift")
        old_sample = read_jsonl_rows(prior / "reports/human_review_sample.jsonl")
        if len(old_sample) != predecessor_state.get("sample_count"):
            raise ValueError("predecessor review sample cardinality drift")

        registry = tuple(objects)
        documents = document_loader(source_root, registry, execution_enabled=True)
        selected = [row for row in documents if row.corpus == "oscar"]
        selected_ids = {row.stable_document_id for row in selected}
        if (
            len(selected) != predecessor_state.get("document_count")
            or canonical_json_sha256(sorted(selected_ids))
            != predecessor_state.get("document_ids_sha256")
            or train_ids | heldout_ids != selected_ids
        ):
            raise ValueError("OSCAR population no longer matches the frozen split")

        inventory = human_review_stratum_inventory(selected)
        sample = human_review_sample_with_stratum_floor(selected, sample_size=review_documents)
        packet = build_review_packet(selected, sample)
        packet_hash = review_packet_sha256(packet)
        old_strata = Counter(row["selection_stratum"] for row in old_sample)
        new_strata = Counter(row["selection_stratum"] for row in sample)
        state = {
            "schema_version": 1,
            "status": "AWAITING_HUMAN_REVIEW",
            "source_root": str(Path(source_root)),
            "source_object_count": len(registry),
            "predecessor_root": str(prior),
            "predecessor_state_sha256": predecessor_state_sha256,
            "predecessor_final_sha256": predecessor_final_sha256,
            "document_count": len(selected),
            "document_ids_sha256": predecessor_state["document_ids_sha256"],
            "split_sha256": predecessor_state["split_sha256"],
            "split_rewritten": False,
            "old_review_packet_sha256": predecessor_state["review_packet_sha256"],
            "old_sample_strata": dict(sorted(old_strata.items())),
            "old_packet_status": "SUPERSEDED_FOR_VERDICTS_BY_COVERAGE_VALIDATED_PACKET",
            "sample_count": len(sample),
            "sample_sha256": canonical_json_sha256(sample),
            "review_packet_sha256": packet_hash,
            "new_sample_strata": dict(sorted(new_strata.items())),
            "allocation_rule": "one_per_nonempty_stratum_then_largest_remainder",
            "review_decisions_complete": False,
            "phase2_opened": False,
            "training_opened": False,
            "ready_to_train": False,
        }
        final = write_d0_review_coverage_handoff(
            destination,
            state=state,
            inventory=inventory,
            sample=sample,
            packet=packet,
            decision_rows=decision_template(packet),
        )
        return {**state, "final_audit": final}
    except Exception as exc:
        write_d0_failure(destination, phase="oscar_review_coverage_repair", error=exc)
        raise
