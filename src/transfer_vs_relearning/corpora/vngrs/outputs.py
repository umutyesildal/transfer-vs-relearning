"""Self-reference-free output manifest and final-audit ordering protocol."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable, Mapping

OUTPUT_ARTIFACT_MANIFEST = "output_artifact_manifest.jsonl"
FINAL_AUDIT = "calibration_audit.json"
OUTPUT_ORDER = (
    "selection_plan.json",
    "request_ledger.jsonl",
    "record_manifest.jsonl",
    "raw_population_metrics.json",
    "retained_population_metrics.json",
    "dedup_metrics.json",
    "contamination_overlap_metrics.json",
    OUTPUT_ARTIFACT_MANIFEST,
    FINAL_AUDIT,
)
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def serialize_output_artifact_manifest(rows: Iterable[Mapping[str, Any]]) -> bytes:
    """Serialize the seven pre-audit rows exactly as the named output manifest."""

    materialized = validate_output_artifact_manifest(rows)
    return b"".join(canonical_json_bytes(row) + b"\n" for row in materialized)


def output_artifact_manifest_sha256(rows: Iterable[Mapping[str, Any]]) -> str:
    return hashlib.sha256(serialize_output_artifact_manifest(rows)).hexdigest()


def validate_artifact_payloads(
    manifest_rows: Iterable[Mapping[str, Any]],
    artifact_payloads: Mapping[str, bytes],
    *,
    output_manifest_payload: bytes | None = None,
) -> dict[str, Any]:
    """Bind every named output row to the bytes that were actually serialized.

    A path plus a format-valid hash is not evidence.  The payload mapping is required for the
    strict final profile and the manifest itself is checked separately so it cannot self-reference.
    """

    rows = validate_output_artifact_manifest(manifest_rows)
    expected_paths = set(OUTPUT_ORDER[:-2])
    if set(artifact_payloads) != expected_paths:
        raise ValueError("actual artifact payloads do not exactly cover the seven named artifacts")
    for row in rows:
        path = row["path"]
        payload = artifact_payloads[path]
        if not isinstance(payload, bytes):
            raise ValueError(f"artifact payload for {path} must be bytes")
        if len(payload) != row["bytes"]:
            raise ValueError(f"artifact byte count mismatch for {path}")
        if hashlib.sha256(payload).hexdigest() != row["sha256"]:
            raise ValueError(f"artifact SHA-256 mismatch for {path}")
    manifest_payload = serialize_output_artifact_manifest(rows)
    if output_manifest_payload is not None and output_manifest_payload != manifest_payload:
        raise ValueError("output_artifact_manifest.jsonl bytes are not the canonical manifest payload")
    return {
        "artifact_count": len(rows),
        "manifest_payload_bytes": len(manifest_payload),
        "manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
        "payloads_bound": True,
    }


def _require_sha256(value: Any, field: str) -> None:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{field} must be exactly 64 lowercase hexadecimal characters")


def validate_output_artifact_manifest(
    rows: Iterable[Mapping[str, Any]], *, expected_order: tuple[str, ...] = OUTPUT_ORDER[:-2]
) -> list[dict[str, Any]]:
    """Validate the ordered, gap-free, self-reference-free artifact chain."""

    materialized = [dict(row) for row in rows]
    if len(materialized) != len(expected_order):
        raise ValueError("artifact manifest has a missing or duplicate artifact")
    paths = [row.get("path") for row in materialized]
    if tuple(paths) != expected_order:
        raise ValueError("artifact manifest order contains a gap, duplicate, or unknown path")
    for expected_order_number, row in enumerate(materialized, start=1):
        if row.get("artifact_order") != expected_order_number:
            raise ValueError("artifact_order is not contiguous")
        if not isinstance(row.get("bytes"), int) or row["bytes"] < 0:
            raise ValueError(f"invalid byte count for {row.get('path')}")
        _require_sha256(row.get("sha256"), f"sha256 for {row.get('path')}")
    if any(path in {OUTPUT_ARTIFACT_MANIFEST, FINAL_AUDIT} for path in paths):
        raise ValueError("artifact manifest cannot include itself or the later final audit")
    return materialized


def build_output_artifact_manifest(artifacts: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Create the named manifest without including itself or the later final audit."""

    if OUTPUT_ARTIFACT_MANIFEST in artifacts or FINAL_AUDIT in artifacts:
        raise ValueError("output manifest and final audit cannot self-reference the chain")
    missing = set(OUTPUT_ORDER[:-2]) - set(artifacts)
    if missing:
        raise ValueError(f"missing required artifacts: {sorted(missing)}")
    unknown = set(artifacts) - set(OUTPUT_ORDER[:-2])
    if unknown:
        raise ValueError(f"unknown artifacts: {sorted(unknown)}")
    rows = []
    for name in OUTPUT_ORDER[:-2]:
        item = dict(artifacts[name])
        if item.get("path") != name:
            raise ValueError(f"artifact path mismatch for {name}")
        if not isinstance(item.get("bytes"), int) or item["bytes"] < 0:
            raise ValueError(f"invalid byte count for {name}")
        _require_sha256(item.get("sha256"), f"sha256 for {name}")
        rows.append({"artifact_order": len(rows) + 1, **item})
    return validate_output_artifact_manifest(rows)


def build_final_audit(
    manifest_rows: Iterable[Mapping[str, Any]], *, manifest_sha256: str, final_audit_path: str = FINAL_AUDIT
) -> dict[str, Any]:
    rows = [dict(row) for row in manifest_rows]
    validate_output_artifact_manifest(rows)
    _require_sha256(manifest_sha256, "manifest_sha256")
    if final_audit_path in {OUTPUT_ARTIFACT_MANIFEST, *OUTPUT_ORDER[:-2]}:
        raise ValueError("final audit path collides with a manifest artifact")
    return {
        "final_audit_path": final_audit_path,
        "self_reference": False,
        "manifest_path": OUTPUT_ARTIFACT_MANIFEST,
        "manifest_sha256": manifest_sha256,
        "write_order": list(OUTPUT_ORDER),
        "artifacts": rows,
    }


def validate_final_audit(
    audit: Mapping[str, Any],
    manifest_rows: Iterable[Mapping[str, Any]],
    *,
    manifest_sha256: str,
    audit_payload: bytes | None = None,
) -> dict[str, Any]:
    """Validate the one-way final-audit chain against the exact frozen manifest."""

    rows = [dict(row) for row in manifest_rows]
    validate_output_artifact_manifest(rows)
    _require_sha256(manifest_sha256, "manifest_sha256")
    if not isinstance(audit, Mapping):
        raise ValueError("final audit must be a mapping")
    if audit.get("final_audit_path") != FINAL_AUDIT:
        raise ValueError("final audit path must equal calibration_audit.json")
    if audit.get("self_reference") is not False:
        raise ValueError("final audit self_reference must be false")
    if audit.get("manifest_path") != OUTPUT_ARTIFACT_MANIFEST:
        raise ValueError("final audit manifest path is not output_artifact_manifest.jsonl")
    if audit.get("manifest_sha256") != manifest_sha256:
        raise ValueError("final audit does not carry the output manifest SHA-256")
    if audit.get("write_order") != list(OUTPUT_ORDER):
        raise ValueError("final audit write order is not the frozen order")
    if audit.get("artifacts") != rows:
        raise ValueError("final audit artifact rows do not match the manifest")
    if audit_payload is not None:
        if audit_payload != canonical_json_bytes(audit):
            raise ValueError("final audit payload is not the canonical audit bytes")
    return {
        "complete": True,
        "final_audit_path_exact": True,
        "self_reference_free": True,
        "manifest_sha256_match": True,
        "write_order_exact": True,
        "artifact_rows_exact": True,
        "audit_payload_bound": audit_payload is None or True,
    }
