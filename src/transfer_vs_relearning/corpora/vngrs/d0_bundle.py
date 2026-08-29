"""Atomic compact evidence bundle writer for the vngrs D0 contract."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping


def _json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(_json(dict(row)) for row in rows)


def _atomic(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".partial")
    if path.exists() or temporary.exists():
        raise ValueError(f"refusing to overwrite D0 evidence: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def write_d0_failure(root: str | Path, *, phase: str, error: Exception) -> dict[str, Any]:
    """Persist one typed post-materialization failure without overwriting prior evidence."""

    failure = {
        "schema_version": 1,
        "status": "BLOCKED",
        "phase": phase,
        "error_type": type(error).__name__,
        "message": str(error),
        "ready_to_train": False,
    }
    _atomic(Path(root) / "control/d0_failure.json", _json(failure))
    return failure


def bounded_audit_evidence(audit: Mapping[str, Any], *, example_limit: int = 256) -> dict[str, Any]:
    """Keep exact audit counts while bounding potentially large hit examples."""

    if not 1 <= example_limit <= 1_000:
        raise ValueError("audit example limit must be between 1 and 1,000")
    contamination = dict(audit.get("synthetic_contamination") or {})
    exact_hits = list(contamination.get("exact_hits") or [])
    normalized_hits = list(contamination.get("unicode_normalized_hits") or [])
    return {
        "schema_version": 1,
        "status": audit.get("status"),
        "document_count": audit.get("document_count"),
        "utf8_bytes": audit.get("utf8_bytes"),
        "composition": audit.get("composition"),
        "regex_document_counts": audit.get("regex_document_counts"),
        "normalized_text_duplicate_groups": audit.get("normalized_text_duplicate_groups"),
        "normalized_text_duplicate_documents": audit.get("normalized_text_duplicate_documents"),
        "synthetic_contamination": {
            "pattern_count": contamination.get("pattern_count"),
            "exact_hit_count": len(exact_hits),
            "unicode_normalized_hit_count": len(normalized_hits),
            "exact_hit_examples": exact_hits[:example_limit],
            "unicode_normalized_hit_examples": normalized_hits[:example_limit],
            "example_limit_per_kind": example_limit,
            "examples_truncated": len(exact_hits) > example_limit or len(normalized_hits) > example_limit,
        },
        "ready_to_train": False,
    }


def write_d0_phase1_audit_evidence(
    root: str | Path,
    *,
    audit: Mapping[str, Any],
    corpus_label_inventory: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist audit evidence before applying its fail-closed decision gate."""

    root_path = Path(root)
    bounded = bounded_audit_evidence(audit)
    _atomic(root_path / "reports/lightweight_audit.json", _json(bounded))
    if corpus_label_inventory is not None:
        write_d0_corpus_label_inventory(root_path, corpus_label_inventory)
    return bounded


def write_d0_corpus_label_inventory(
    root: str | Path, inventory: Mapping[str, Any]
) -> None:
    """Persist exact observed corpus labels before any candidate-label gate."""

    _atomic(
        Path(root) / "reports/corpus_label_inventory.json",
        _json(dict(inventory)),
    )


def write_d0_recovery_state(root: str | Path, state: Mapping[str, Any]) -> None:
    """Atomically close a diagnostic recovery pass without implying training readiness."""

    if state.get("ready_to_train") is not False:
        raise ValueError("D0 recovery state must remain training-ineligible")
    _atomic(Path(root) / "control/recovery_state.json", _json(dict(state)))


def write_d0_fact_pair_audit(root: str | Path, audit: Mapping[str, Any]) -> None:
    """Persist the bounded fact-pair correction report without opening later stages."""

    if audit.get("ready_to_train") is not False:
        raise ValueError("fact-pair audit must remain training-ineligible")
    _atomic(Path(root) / "reports/fact_pair_contamination_audit.json", _json(dict(audit)))


def write_d0_split_review_handoff(
    root: str | Path,
    *,
    state: Mapping[str, Any],
    split: Mapping[str, Any],
    sample: Iterable[Mapping[str, Any]],
    packet: Iterable[Mapping[str, Any]],
    decision_rows: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Persist a self-contained split/review handoff with a one-way hash chain."""

    if state.get("ready_to_train") is not False or state.get("status") != "AWAITING_HUMAN_REVIEW":
        raise ValueError("split/review handoff must stop awaiting human review")
    sample_rows = [dict(row) for row in sample]
    packet_rows = [dict(row) for row in packet]
    decisions = [dict(row) for row in decision_rows]
    payloads = {
        "control/phase1_state.json": _json(dict(state)),
        "splits/train_document_ids.jsonl": _jsonl(
            {"schema_version": 1, "stable_document_id": value}
            for value in split["train_document_ids"]
        ),
        "splits/heldout_document_ids.jsonl": _jsonl(
            {"schema_version": 1, "stable_document_id": value}
            for value in split["heldout_document_ids"]
        ),
        "reports/human_review_sample.jsonl": _jsonl(sample_rows),
        "reports/human_review_packet.jsonl": _jsonl(packet_rows),
        "reports/human_review_decision_template.jsonl": _jsonl(decisions),
    }
    if sum(len(payload) for payload in payloads.values()) > 128 * 1024**2:
        raise ValueError("split/review handoff exceeds the frozen 128 MiB compact-output bound")
    root_path = Path(root)
    manifest_rows = []
    for index, relative in enumerate(sorted(payloads), 1):
        payload = payloads[relative]
        manifest_rows.append(
            {
                "schema_version": 1,
                "artifact_order": index,
                "path": relative,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
        _atomic(root_path / relative, payload)
    manifest_payload = _jsonl(manifest_rows)
    manifest_sha256 = hashlib.sha256(manifest_payload).hexdigest()
    _atomic(root_path / "manifests/output_artifact_manifest.jsonl", manifest_payload)
    final = {
        "schema_version": 1,
        "status": "AWAITING_HUMAN_REVIEW",
        "self_reference": False,
        "manifest_path": "manifests/output_artifact_manifest.jsonl",
        "manifest_sha256": manifest_sha256,
        "artifact_count": len(manifest_rows),
        "split_created": True,
        "human_review_packet_created": True,
        "ready_to_train": False,
    }
    _atomic(root_path / "control/final_audit.json", _json(final))
    return final


def write_d0_evidence_bundle(
    root: str | Path,
    result: Mapping[str, Any],
    *,
    source_rows: Iterable[Mapping[str, Any]],
    request_rows: Iterable[Mapping[str, Any]],
    existing_artifacts: Iterable[str] = (),
) -> dict[str, Any]:
    """Write the exact compact namespaces, then a self-reference-free terminal hash chain."""

    root_path = Path(root)
    split = result["split"]
    audit = result["audit"]
    reviewed_by_id = {
        row["stable_document_id"]: dict(row) for row in result["reviewed_sample"]
    }
    sample_rows = []
    for selected in result["human_review_sample"]:
        review = reviewed_by_id[selected["stable_document_id"]]
        sample_rows.append({**selected, "verdict": review["verdict"]})
    payloads = {
        "control/preflight.json": _json(result["storage"]),
        "control/request_ledger.jsonl": _jsonl(request_rows),
        "manifests/source_shards.jsonl": _jsonl(source_rows),
        "manifests/document_identity_summary.json": _json(
            {
                "schema_version": 1,
                "document_count": audit["document_count"],
                "input_document_ids_sha256": split["input_document_ids_sha256"],
                "document_disjoint": split["document_disjoint"],
            }
        ),
        "manifests/exclusions.jsonl": b"",
        "splits/train_document_ids.jsonl": _jsonl(
            {"schema_version": 1, "stable_document_id": value}
            for value in split["train_document_ids"]
        ),
        "splits/heldout_document_ids.jsonl": _jsonl(
            {"schema_version": 1, "stable_document_id": value}
            for value in split["heldout_document_ids"]
        ),
        "reports/corpus_composition.json": _json(
            {"schema_version": 1, "composition": audit["composition"]}
        ),
        "reports/light_regex_quality.json": _json(
            {"schema_version": 1, "regex_document_counts": audit["regex_document_counts"]}
        ),
        "reports/human_review_sample.jsonl": _jsonl(sample_rows),
        "reports/human_review_summary.json": _json(
            {"schema_version": 1, **result["human_review"]}
        ),
        "reports/synthetic_contamination.json": _json(
            {"schema_version": 1, **audit["synthetic_contamination"]}
        ),
    }
    for role, report in sorted(result["tokenizer_accounting"].items()):
        payloads[f"reports/tokenizer_accounting_{role}.json"] = _json(report)
    existing = set(existing_artifacts)
    for relative in sorted(existing):
        path = root_path / relative
        if not path.is_file() or path.is_symlink() or path.name.endswith(".partial"):
            raise ValueError(f"required phase artifact is absent or unsafe: {relative}")
        payloads[relative] = path.read_bytes()
    rows = []
    for index, path in enumerate(sorted(payloads), 1):
        payload = payloads[path]
        rows.append(
            {
                "schema_version": 1,
                "artifact_order": index,
                "path": path,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
        if path not in existing:
            _atomic(root_path / path, payload)
    manifest_payload = _jsonl(rows)
    manifest_sha256 = hashlib.sha256(manifest_payload).hexdigest()
    _atomic(root_path / "manifests/output_artifact_manifest.jsonl", manifest_payload)
    final = {
        "schema_version": 1,
        "status": "D0_EVIDENCE_COMPLETE",
        "self_reference": False,
        "manifest_path": "manifests/output_artifact_manifest.jsonl",
        "manifest_sha256": manifest_sha256,
        "artifact_count": len(rows),
        "ready_to_train": False,
    }
    _atomic(root_path / "control/final_audit.json", _json(final))
    return final
