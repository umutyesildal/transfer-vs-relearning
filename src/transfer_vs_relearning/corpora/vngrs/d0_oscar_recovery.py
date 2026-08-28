"""Execution-disabled OSCAR-only audit recovery over preserved V3 bytes."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .d0_audit import D0Document, lightweight_audit
from .d0_bundle import (
    write_d0_corpus_label_inventory,
    write_d0_failure,
    write_d0_phase1_audit_evidence,
    write_d0_recovery_state,
)
from .materialization import SourceObjectV3
from .metadata import canonical_json_sha256
from .parquet_loader_v3 import load_verified_parquet_documents_v3


OSCAR_CORPUS_LABEL = "OSCAR"


def corpus_label_inventory(rows: Iterable[D0Document]) -> dict[str, Any]:
    documents = list(rows)
    labels: dict[str, dict[str, int]] = defaultdict(lambda: {"documents": 0, "utf8_bytes": 0})
    for row in documents:
        labels[row.corpus]["documents"] += 1
        labels[row.corpus]["utf8_bytes"] += len(row.text.encode("utf-8"))
    return {
        "schema_version": 1,
        "status": "LABEL_INVENTORY_COMPLETE",
        "document_count": len(documents),
        "exact_labels": [
            {"label": label, **labels[label]} for label in sorted(labels)
        ],
        "ready_to_train": False,
    }


def run_oscar_audit_recovery(
    source_root: str | Path,
    output_root: str | Path,
    objects: Iterable[SourceObjectV3],
    *,
    synthetic_surfaces: Mapping[str, str],
    execution_enabled: bool = False,
    document_loader: Callable[..., list[D0Document]] = load_verified_parquet_documents_v3,
) -> dict[str, Any]:
    """Audit exact `corpus == OSCAR` rows and stop before split/review/training."""

    if not execution_enabled:
        raise ValueError("OSCAR audit recovery execution is disabled")
    destination = Path(output_root)
    if destination.exists():
        raise ValueError("OSCAR audit recovery output root must be fresh and absent")
    try:
        registry = tuple(objects)
        documents = document_loader(source_root, registry, execution_enabled=True)
        inventory = corpus_label_inventory(documents)
        write_d0_corpus_label_inventory(destination, inventory)
        selected = [row for row in documents if row.corpus == OSCAR_CORPUS_LABEL]
        if len(selected) <= 10_000:
            raise ValueError("exact OSCAR candidate population is absent or too small")
        audit = lightweight_audit(selected, synthetic_surfaces=synthetic_surfaces)
        bounded = write_d0_phase1_audit_evidence(
            destination,
            audit=audit,
        )
        state = {
            "schema_version": 1,
            "status": "OSCAR_AUDIT_COMPLETE" if audit["status"] == "AUDIT_COMPLETE" else "BLOCKED",
            "source_root": str(Path(source_root)),
            "source_manifest": "control/materialization_v3.json",
            "source_object_count": len(registry),
            "corpus_predicate": {"field": "corpus", "operator": "exact_string_equality", "value": OSCAR_CORPUS_LABEL},
            "selected_document_count": len(selected),
            "selected_document_ids_sha256": canonical_json_sha256(
                sorted(row.stable_document_id for row in selected)
            ),
            "audit_status": bounded["status"],
            "split_created": False,
            "human_review_packet_created": False,
            "ready_to_train": False,
        }
        write_d0_recovery_state(destination, state)
        return state
    except Exception as exc:
        write_d0_failure(destination, phase="oscar_audit_recovery", error=exc)
        raise
