"""Execution-disabled fact-pair contamination repair over preserved OSCAR bytes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .d0_audit import D0Document, SyntheticFactSurface, fact_pair_contamination_audit
from .d0_bundle import (
    write_d0_corpus_label_inventory,
    write_d0_fact_pair_audit,
    write_d0_failure,
    write_d0_recovery_state,
)
from .d0_oscar_recovery import corpus_label_inventory
from .materialization import SourceObjectV3
from .metadata import canonical_json_sha256
from .parquet_loader_v3 import load_verified_parquet_documents_v3


def run_oscar_fact_pair_recovery(
    source_root: str | Path,
    output_root: str | Path,
    objects: Iterable[SourceObjectV3],
    *,
    synthetic_facts: Iterable[SyntheticFactSurface],
    predecessor_atom_audit: Mapping[str, Any],
    predecessor_atom_audit_sha256: str,
    execution_enabled: bool = False,
    document_loader: Callable[..., list[D0Document]] = load_verified_parquet_documents_v3,
) -> dict[str, Any]:
    """Run one exact-lowercase OSCAR fact-pair audit and stop before split/review."""

    if not execution_enabled:
        raise ValueError("OSCAR fact-pair recovery execution is disabled")
    destination = Path(output_root)
    if destination.exists():
        raise ValueError("OSCAR fact-pair recovery output root must be fresh and absent")
    try:
        registry = tuple(objects)
        documents = document_loader(source_root, registry, execution_enabled=True)
        inventory = corpus_label_inventory(documents)
        write_d0_corpus_label_inventory(destination, inventory)
        selected = [row for row in documents if row.corpus == "oscar"]
        if len(selected) <= 10_000:
            raise ValueError("exact lowercase OSCAR candidate population is absent or too small")
        audit = fact_pair_contamination_audit(
            selected,
            synthetic_facts=synthetic_facts,
            predecessor_atom_audit=predecessor_atom_audit,
            predecessor_atom_audit_sha256=predecessor_atom_audit_sha256,
        )
        write_d0_fact_pair_audit(destination, audit)
        state = {
            "schema_version": 1,
            "status": (
                "OSCAR_FACT_PAIR_AUDIT_COMPLETE"
                if audit["status"] == "AUDIT_COMPLETE"
                else "BLOCKED"
            ),
            "source_root": str(Path(source_root)),
            "source_manifest": "control/materialization_v3.json",
            "source_object_count": len(registry),
            "corpus_predicate": {
                "field": "corpus",
                "operator": "exact_string_equality",
                "value": "oscar",
            },
            "selected_document_count": len(selected),
            "selected_document_ids_sha256": canonical_json_sha256(
                sorted(row.stable_document_id for row in selected)
            ),
            "audit_status": audit["status"],
            "blocking_rule": "paired_subject_answer_cooccurrence_or_invalid_encoding",
            "split_created": False,
            "human_review_packet_created": False,
            "ready_to_train": False,
        }
        write_d0_recovery_state(destination, state)
        return state
    except Exception as exc:
        write_d0_failure(destination, phase="oscar_fact_pair_contamination_recovery", error=exc)
        raise
