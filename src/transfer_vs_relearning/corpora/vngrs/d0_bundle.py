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
