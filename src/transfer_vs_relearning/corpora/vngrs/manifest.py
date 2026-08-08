"""Strict, text-free request/record manifest validation for the bounded vngrs contract."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable, Mapping


RECORD_MANIFEST_FIELDS = (
    "request_id",
    "record_index_within_response",
    "source_repo",
    "immutable_revision",
    "corpus",
    "shard_path",
    "stable_source_row_document_id",
    "original_id",
    "source_identity_key",
    "sample_index",
    "exact_serialized_record_payload_bytes",
    "normalized_text_sha256",
    "retrieved_at_utc",
    "raw_text_character_count",
    "normalized_text_character_count",
    "normalization_version",
    "lid_evaluator_id",
    "lid_evaluator_sha256",
    "lid_status",
    "lid_top1_language",
    "lid_confidence",
    "strict_mixed_line_flag",
    "quality_status",
    "quality_reason_codes",
    "pii_status",
    "pii_reason_codes",
    "exact_dedup_key",
    "near_dedup_version",
    "synthetic_contamination_status",
    "synthetic_contamination_tiers",
    "benchmark_overlap_status",
    "split",
    "retention_status",
    "rejection_reason_codes",
)
REQUEST_LEDGER_FIELDS = (
    "request_id",
    "attempt_id",
    "attempt_ordinal",
    "retry_ordinal",
    "source_repo",
    "immutable_revision",
    "route",
    "shard_path",
    "row_range_or_metadata_target",
    "request_start_utc",
    "response_end_utc",
    "http_status",
    "response_transferred_bytes",
    "response_evidence_artifact",
    "content_encoding",
    "content_type",
    "redirect_chain",
    "response_sha256",
    "request_outcome",
)
NO_TEXT_FIELDS = frozenset({"text", "raw_text", "normalized_text", "content"})
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")

# These are 151ak request-level limits.  They apply to attempts and HTTP response
# accounting; record-level payload bytes are deliberately validated separately.
MAX_HTTP_ATTEMPTS = 128
MAX_SUCCESSFUL_ROW_REQUESTS = 100
MAX_RETRIES = 28
MAX_TOTAL_RESPONSE_BYTES = 64 * 1024 * 1024
MAX_SINGLE_RESPONSE_BYTES = 4 * 1024 * 1024
SUCCESSFUL_REQUEST_OUTCOMES = frozenset({"success", "row_success", "metadata_success"})
FAILED_REQUEST_OUTCOMES = frozenset({"failed", "http_error", "blocked"})


class ManifestValidationError(ValueError):
    """Raised when a record manifest is not complete and schema-valid."""


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def validate_record_manifest(
    rows: Iterable[Mapping[str, Any]], *, expected_count: int | None = None,
    require_lid_identity: bool = False, require_operational_fields: bool = False,
    raise_on_error: bool = False
) -> dict[str, Any]:
    """Validate schema, cardinality and source identity; never use list length as completeness."""

    materialized = [dict(row) for row in rows]
    errors: list[str] = []
    expected_fields = set(RECORD_MANIFEST_FIELDS)
    seen_identity: set[tuple[str, str, str]] = set()
    seen_stable_ids: set[str] = set()
    required_string_fields = {
        "request_id", "source_repo", "immutable_revision", "corpus", "shard_path", "stable_source_row_document_id",
        "normalization_version", "lid_status", "quality_status", "pii_status", "exact_dedup_key",
        "near_dedup_version", "synthetic_contamination_status", "benchmark_overlap_status",
        "retention_status",
    }
    nullable_string_fields = {
        "retrieved_at_utc", "lid_evaluator_id", "lid_evaluator_sha256", "lid_top1_language", "split",
    }
    nonnegative_integer_fields = {
        "record_index_within_response", "sample_index", "exact_serialized_record_payload_bytes",
        "raw_text_character_count", "normalized_text_character_count",
    }
    list_fields = {"quality_reason_codes", "pii_reason_codes", "synthetic_contamination_tiers", "rejection_reason_codes"}

    for index, row in enumerate(materialized):
        missing = sorted(expected_fields - set(row))
        unknown = sorted(set(row) - expected_fields)
        if missing:
            errors.append(f"row {index}: missing fields {missing}")
        if unknown:
            errors.append(f"row {index}: unknown fields {unknown}")
        if set(row) & NO_TEXT_FIELDS:
            errors.append(f"row {index}: raw or normalized text is forbidden in compact manifest")
        for field in required_string_fields:
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(f"row {index}: {field} is missing or not a non-empty string")
        for field in nullable_string_fields:
            if row.get(field) is not None and not isinstance(row[field], str):
                errors.append(f"row {index}: {field} must be a string or null")
        for field in nonnegative_integer_fields:
            if not isinstance(row.get(field), int) or isinstance(row[field], bool) or row[field] < 0:
                errors.append(f"row {index}: {field} must be a non-negative integer")
        for field in list_fields:
            if not isinstance(row.get(field), list) or any(not isinstance(item, str) for item in row[field]):
                errors.append(f"row {index}: {field} must be a list of strings")
        if not isinstance(row.get("original_id"), (str, int)) or isinstance(row.get("original_id"), bool):
            errors.append(f"row {index}: original_id must be a string or integer")
        identity_key = row.get("source_identity_key")
        if not isinstance(identity_key, Mapping) or set(identity_key) != {"corpus", "original_id"}:
            errors.append(f"row {index}: source_identity_key must be the explicit corpus/original_id pair")
        elif str(identity_key.get("corpus")) != str(row.get("corpus")) or str(identity_key.get("original_id")) != str(row.get("original_id")):
            errors.append(f"row {index}: source_identity_key does not match corpus/original_id")
        if not isinstance(row.get("lid_confidence"), (int, float)) or isinstance(row.get("lid_confidence"), bool):
            errors.append(f"row {index}: lid_confidence must be numeric")
        elif not 0.0 <= float(row["lid_confidence"]) <= 1.0:
            errors.append(f"row {index}: lid_confidence is outside [0, 1]")
        if not isinstance(row.get("strict_mixed_line_flag"), bool):
            errors.append(f"row {index}: strict_mixed_line_flag must be boolean")
        for field in ("normalized_text_sha256", "exact_dedup_key"):
            if not _sha256(row.get(field)):
                errors.append(f"row {index}: {field} is not a lowercase SHA-256")
        if row.get("lid_evaluator_sha256") is not None and not _sha256(row["lid_evaluator_sha256"]):
            errors.append(f"row {index}: lid_evaluator_sha256 is not a lowercase SHA-256")
        if require_lid_identity and (
            not isinstance(row.get("lid_evaluator_id"), str) or not row["lid_evaluator_id"].strip()
            or not _sha256(row.get("lid_evaluator_sha256"))
        ):
            errors.append(f"row {index}: raw scientific LID evaluator identity is incomplete")
        if require_operational_fields:
            if not isinstance(row.get("retrieved_at_utc"), str) or not row["retrieved_at_utc"].strip():
                errors.append(f"row {index}: retrieved_at_utc is required for final evidence")
            if not isinstance(row.get("request_id"), str) or not row["request_id"].strip():
                errors.append(f"row {index}: request_id is required for final evidence")
        identity = (str(row.get("immutable_revision")), str(row.get("corpus")), str(row.get("original_id")))
        if identity in seen_identity:
            errors.append(f"row {index}: duplicate source identity {identity}")
        seen_identity.add(identity)
        stable_id = row.get("stable_source_row_document_id")
        if isinstance(stable_id, str):
            if stable_id in seen_stable_ids:
                errors.append(f"row {index}: duplicate stable source ID {stable_id}")
            seen_stable_ids.add(stable_id)

    cardinality_ok = expected_count is None or len(materialized) == expected_count
    if expected_count is not None and not cardinality_ok:
        errors.append(f"manifest cardinality {len(materialized)} != expected {expected_count}")
    result = {
        "schema_fields": list(RECORD_MANIFEST_FIELDS),
        "schema_exact": not any(
            (set(row) != expected_fields) or bool(set(row) & NO_TEXT_FIELDS) for row in materialized
        ),
        "row_count": len(materialized),
        "expected_count": expected_count,
        "cardinality_exact": cardinality_ok,
        "source_identity_unique": len(seen_identity) == len(materialized),
        "stable_id_unique": len(seen_stable_ids) == len(materialized),
        "raw_lid_identity_complete": not any("raw scientific LID evaluator identity" in error for error in errors),
        "errors": errors,
        "complete": not errors and cardinality_ok,
    }
    if raise_on_error and not result["complete"]:
        raise ManifestValidationError("; ".join(errors[:8]))
    return result


def validate_request_ledger(rows: Iterable[Mapping[str, Any]], *, raise_on_error: bool = False) -> dict[str, Any]:
    """Validate explicit logical-request/HTTP-attempt accounting.

    ``request_id`` is the logical request identity and may occur once per retry chain.
    ``attempt_id`` is unique for every HTTP attempt.  Both ordinal fields are zero based;
    retry attempts are counted as rows, never by summing a cumulative counter.
    """

    materialized = [dict(row) for row in rows]
    errors: list[str] = []
    seen_attempt_ids: set[str] = set()
    logical_groups: dict[str, list[dict[str, Any]]] = {}
    expected = set(REQUEST_LEDGER_FIELDS)
    for index, row in enumerate(materialized):
        if set(row) != expected:
            errors.append(f"row {index}: request-ledger schema mismatch")
        request_id = row.get("request_id")
        attempt_id = row.get("attempt_id")
        if not isinstance(request_id, str) or not request_id:
            errors.append(f"row {index}: logical request_id missing")
        if not isinstance(attempt_id, str) or not attempt_id or attempt_id in seen_attempt_ids:
            errors.append(f"row {index}: attempt_id missing or duplicated")
        if isinstance(attempt_id, str):
            seen_attempt_ids.add(attempt_id)
        if isinstance(request_id, str) and request_id:
            logical_groups.setdefault(request_id, []).append(row)
        for field in ("source_repo", "immutable_revision", "route", "request_start_utc", "response_end_utc", "content_encoding", "content_type", "request_outcome"):
            if not isinstance(row.get(field), str) or not row[field]:
                errors.append(f"row {index}: {field} missing")
        if not isinstance(row.get("http_status"), int) or isinstance(row.get("http_status"), bool):
            errors.append(f"row {index}: http_status must be integer")
        for field in ("attempt_ordinal", "retry_ordinal", "response_transferred_bytes"):
            if not isinstance(row.get(field), int) or isinstance(row[field], bool) or row[field] < 0:
                errors.append(f"row {index}: {field} must be non-negative integer")
        if not isinstance(row.get("shard_path"), str):
            errors.append(f"row {index}: shard_path must be string")
        if not isinstance(row.get("response_evidence_artifact"), str) or not row["response_evidence_artifact"] or row["response_evidence_artifact"].startswith("/") or ".." in row["response_evidence_artifact"].split("/"):
            errors.append(f"row {index}: response_evidence_artifact must be a safe named artifact")
        if not isinstance(row.get("row_range_or_metadata_target"), str) or not row["row_range_or_metadata_target"]:
            errors.append(f"row {index}: row_range_or_metadata_target missing")
        if not isinstance(row.get("redirect_chain"), list) or any(not isinstance(item, str) for item in row["redirect_chain"]):
            errors.append(f"row {index}: redirect_chain must be list of strings")
        if not _sha256(row.get("response_sha256")):
            errors.append(f"row {index}: response_sha256 is not a lowercase SHA-256")
        outcome = row.get("request_outcome")
        status = row.get("http_status")
        if outcome not in SUCCESSFUL_REQUEST_OUTCOMES | FAILED_REQUEST_OUTCOMES:
            errors.append(f"row {index}: request_outcome is not a frozen outcome value")
        elif isinstance(status, int) and not isinstance(status, bool):
            if outcome in SUCCESSFUL_REQUEST_OUTCOMES and status != 200:
                errors.append(f"row {index}: successful outcome has non-200 HTTP status")
            if outcome in FAILED_REQUEST_OUTCOMES and status == 200:
                errors.append(f"row {index}: failed outcome has HTTP 200 status")

    for logical_id, group in logical_groups.items():
        ordered = sorted(group, key=lambda row: row.get("attempt_ordinal", -1))
        expected_ordinals = list(range(len(ordered)))
        actual_ordinals = [row.get("attempt_ordinal") for row in ordered]
        retry_ordinals = [row.get("retry_ordinal") for row in ordered]
        if actual_ordinals != expected_ordinals:
            errors.append(f"logical request {logical_id}: attempt ordinals are not contiguous from zero")
        if retry_ordinals != expected_ordinals:
            errors.append(f"logical request {logical_id}: retry ordinals are not contiguous from zero")
        if len({row.get("attempt_id") for row in group}) != len(group):
            errors.append(f"logical request {logical_id}: attempt IDs are not unique")
    result = {
        "schema_fields": list(REQUEST_LEDGER_FIELDS),
        "row_count": len(materialized),
        "attempt_id_unique": len(seen_attempt_ids) == len(materialized),
        "logical_request_count": len(logical_groups),
        "logical_request_attempt_chains_contiguous": not any(
            "ordinals are not contiguous" in error for error in errors
        ),
        "errors": errors,
        "complete": not errors,
    }
    if raise_on_error and errors:
        raise ManifestValidationError("; ".join(errors[:8]))
    return result


def validate_request_ledger_aggregate(
    rows: Iterable[Mapping[str, Any]], *, raise_on_error: bool = False
) -> dict[str, Any]:
    """Validate the frozen attempt/retry/outcome arithmetic and aggregate bounds."""

    materialized = [dict(row) for row in rows]
    schema = validate_request_ledger(materialized)
    errors = list(schema["errors"])
    if not materialized:
        errors.append("request ledger cannot be empty for final evidence")
    successful_outcomes = SUCCESSFUL_REQUEST_OUTCOMES
    successful_row_outcomes = frozenset({"success", "row_success"})
    attempts = len(materialized)
    initial_attempts = sum(1 for row in materialized if isinstance(row.get("attempt_ordinal"), int) and row["attempt_ordinal"] == 0)
    retry_attempts = sum(1 for row in materialized if isinstance(row.get("attempt_ordinal"), int) and row["attempt_ordinal"] > 0)
    retry_count = retry_attempts
    successful_outcome_count = sum(row.get("request_outcome") in successful_outcomes for row in materialized)
    successful_row_requests = sum(
        row.get("request_outcome") in successful_row_outcomes
        and isinstance(row.get("route"), str)
        and row["route"].rstrip("/").endswith("/rows")
        for row in materialized
    )
    non_successful_outcomes = attempts - successful_outcome_count
    total_bytes = sum(int(row.get("response_transferred_bytes", 0)) for row in materialized if isinstance(row.get("response_transferred_bytes"), int))
    valid_response_bytes = [
        row["response_transferred_bytes"]
        for row in materialized
        if isinstance(row.get("response_transferred_bytes"), int) and not isinstance(row["response_transferred_bytes"], bool)
    ]
    max_single_bytes = max(valid_response_bytes, default=0)
    if attempts != successful_outcome_count + non_successful_outcomes:
        errors.append("attempt/outcome arithmetic does not reconcile")
    if attempts != initial_attempts + retry_attempts:
        errors.append("attempt/retry arithmetic does not reconcile")
    if attempts > MAX_HTTP_ATTEMPTS:
        errors.append("maximum total HTTP attempts exceeded")
    if successful_row_requests > MAX_SUCCESSFUL_ROW_REQUESTS:
        errors.append("maximum successful row requests exceeded")
    if retry_count > MAX_RETRIES:
        errors.append("maximum total retries exceeded")
    if total_bytes > MAX_TOTAL_RESPONSE_BYTES:
        errors.append("maximum total response bytes exceeded")
    if max_single_bytes > MAX_SINGLE_RESPONSE_BYTES:
        errors.append("maximum single response bytes exceeded")
    result = {
        "attempt_count": attempts,
        "successful_row_request_count": successful_row_requests,
        "successful_outcome_count": successful_outcome_count,
        "non_successful_outcome_count": non_successful_outcomes,
        "retry_count": retry_count,
        "retry_attempts_counted_once": retry_attempts,
        "retry_attempt_count": retry_attempts,
        "total_response_bytes": total_bytes,
        "max_single_response_bytes": max_single_bytes,
        "bounds": {
            "max_http_attempts": MAX_HTTP_ATTEMPTS,
            "max_successful_row_requests": MAX_SUCCESSFUL_ROW_REQUESTS,
            "max_retries": MAX_RETRIES,
            "max_total_response_bytes": MAX_TOTAL_RESPONSE_BYTES,
            "max_single_response_bytes": MAX_SINGLE_RESPONSE_BYTES,
        },
        "schema_complete": bool(schema["complete"]),
        "errors": errors,
        "complete": not errors and bool(schema["complete"]),
    }
    if raise_on_error and not result["complete"]:
        raise ManifestValidationError("; ".join(errors[:8]))
    return result


def validate_request_response_bindings(
    rows: Iterable[Mapping[str, Any]], payloads: Mapping[str, bytes] | None
) -> dict[str, Any]:
    """Bind each request-level response SHA to named compact response evidence bytes."""

    materialized = [dict(row) for row in rows]
    errors: list[str] = []
    names: list[str] = []
    for index, row in enumerate(materialized):
        name = row.get("response_evidence_artifact")
        if not isinstance(name, str) or not name:
            errors.append(f"request row {index}: response evidence artifact is missing")
        else:
            names.append(name)
    if len(set(names)) != len(names):
        errors.append("request response evidence artifact names are not unique")
    if payloads is None:
        errors.append("request response evidence payloads are required")
    else:
        if set(payloads) != set(names):
            errors.append("request response evidence payload names do not exactly match ledger bindings")
        for row in materialized:
            name = row.get("response_evidence_artifact")
            payload = payloads.get(name) if isinstance(name, str) else None
            if not isinstance(payload, bytes):
                errors.append(f"request response evidence payload missing or not bytes: {name}")
            elif hashlib.sha256(payload).hexdigest() != row.get("response_sha256"):
                errors.append(f"request response evidence hash mismatch: {name}")
    return {"bound_artifact_count": len(names), "errors": errors, "complete": not errors}


def validate_final_evidence_relationships(
    record_rows: Iterable[Mapping[str, Any]],
    request_rows: Iterable[Mapping[str, Any]],
    *,
    raise_on_error: bool = False,
) -> dict[str, Any]:
    """Validate the frozen 151ak record-to-successful-request evidence graph.

    This validator deliberately owns the immutable final profile: a caller cannot reduce the
    sample target, substitute a different revision, or replace the frozen 32-shard set with a
    one-shard fixture.  Request-level response bytes remain in the request ledger only.
    """

    from .metadata import (
        FROZEN_SELECTED_SHARD_PATHS,
        VNGRS_REPOSITORY,
        VNGRS_REVISION,
    )

    records = [dict(row) for row in record_rows]
    requests = [dict(row) for row in request_rows]
    errors: list[str] = []
    record_validation = validate_record_manifest(
        records,
        expected_count=10_000,
        require_lid_identity=True,
        require_operational_fields=True,
    )
    if not record_validation["complete"]:
        errors.extend(f"record_manifest: {error}" for error in record_validation["errors"][:20])
    request_validation = validate_request_ledger(requests)
    request_aggregate = validate_request_ledger_aggregate(requests)
    if not request_validation["complete"]:
        errors.extend(f"request_ledger: {error}" for error in request_validation["errors"][:20])
    if not request_aggregate["complete"]:
        errors.extend(f"request_ledger_aggregate: {error}" for error in request_aggregate["errors"][:20])

    frozen_paths = set(FROZEN_SELECTED_SHARD_PATHS)
    for index, row in enumerate(records):
        if row.get("source_repo") != VNGRS_REPOSITORY:
            errors.append(f"record {index}: source_repo does not match frozen vngrs repository")
        if row.get("immutable_revision") != VNGRS_REVISION:
            errors.append(f"record {index}: immutable_revision does not match frozen revision")
        if row.get("shard_path") not in frozen_paths:
            errors.append(f"record {index}: shard_path is outside the frozen 32-path set")
        if not isinstance(row.get("exact_serialized_record_payload_bytes"), int) or row["exact_serialized_record_payload_bytes"] <= 0:
            errors.append(f"record {index}: exact serialized payload bytes must be positive")

    logical_groups: dict[str, list[dict[str, Any]]] = {}
    for row in requests:
        logical_id = row.get("request_id")
        if isinstance(logical_id, str):
            logical_groups.setdefault(logical_id, []).append(row)

    successful_by_logical: dict[str, dict[str, Any]] = {}
    for logical_id, group in logical_groups.items():
        successes = [
            row for row in group
            if row.get("request_outcome") in {"success", "row_success"}
            and row.get("http_status") == 200
            and isinstance(row.get("route"), str)
            and row["route"].rstrip("/").endswith("/rows")
        ]
        if len(successes) > 1:
            errors.append(f"logical request {logical_id}: more than one successful /rows attempt")
        if successes:
            successful_by_logical[logical_id] = successes[0]

    row_counts: dict[str, int] = {}
    seen_pairs: set[tuple[str, int]] = set()
    seen_sample_indexes: set[int] = set()

    def parse_offset_length(value: Any) -> tuple[int, int] | None:
        if not isinstance(value, str):
            return None
        offset_match = re.search(r"(?:^|[?&,])offset=(\d+)(?:[&,]|$)", value)
        length_match = re.search(r"(?:^|[?&,])length=(\d+)(?:[&,]|$)", value)
        if offset_match is None or length_match is None:
            return None
        return int(offset_match.group(1)), int(length_match.group(1))

    for index, row in enumerate(records):
        logical_id = row.get("request_id")
        request = successful_by_logical.get(logical_id) if isinstance(logical_id, str) else None
        if request is None:
            errors.append(f"record {index}: request_id does not reference one successful /rows attempt")
            continue
        if request.get("source_repo") != row.get("source_repo"):
            errors.append(f"record {index}: request/repository foreign key mismatch")
        if request.get("immutable_revision") != row.get("immutable_revision"):
            errors.append(f"record {index}: request/revision foreign key mismatch")
        if request.get("shard_path") != row.get("shard_path"):
            errors.append(f"record {index}: request/shard foreign key mismatch")
        record_index = row.get("record_index_within_response")
        if not isinstance(record_index, int) or isinstance(record_index, bool) or record_index < 0:
            errors.append(f"record {index}: record_index_within_response is invalid")
            continue
        pair = (str(logical_id), record_index)
        if pair in seen_pairs:
            errors.append(f"record {index}: duplicate (request_id, record_index_within_response)")
        seen_pairs.add(pair)
        row_counts[str(logical_id)] = row_counts.get(str(logical_id), 0) + 1
        sample_index = row.get("sample_index")
        if not isinstance(sample_index, int) or isinstance(sample_index, bool) or not 0 <= sample_index < 10_000:
            errors.append(f"record {index}: sample_index is outside 0..9999")
        elif sample_index in seen_sample_indexes:
            errors.append(f"record {index}: duplicate sample_index {sample_index}")
        else:
            seen_sample_indexes.add(sample_index)
        parsed = parse_offset_length(request.get("row_range_or_metadata_target"))
        if parsed is None:
            errors.append(f"record {index}: request offset/length is not structurally parseable")
        else:
            offset, length = parsed
            if length < 1 or length > 100:
                errors.append(f"record {index}: request length is outside 1..100")
            if record_index >= length:
                errors.append(f"record {index}: record index exceeds request length")
            if offset < 0:
                errors.append(f"record {index}: request offset is negative")

    for logical_id, request in successful_by_logical.items():
        count = row_counts.get(logical_id, 0)
        if count == 0:
            errors.append(f"successful logical request {logical_id}: orphan request has no records")
        if count > 100:
            errors.append(f"successful logical request {logical_id}: contributes more than 100 records")

    if seen_sample_indexes != set(range(10_000)):
        errors.append("sample_index set is not exactly 0..9999")
    return {
        "record_count": len(records),
        "logical_request_count": len(logical_groups),
        "successful_row_request_count": len(successful_by_logical),
        "record_request_pairs": len(seen_pairs),
        "sample_index_count": len(seen_sample_indexes),
        "frozen_source_repository": VNGRS_REPOSITORY,
        "frozen_immutable_revision": VNGRS_REVISION,
        "frozen_selected_shard_count": len(FROZEN_SELECTED_SHARD_PATHS),
        "errors": errors,
        "complete": not errors,
    }


def validate_final_sampling_schedule(
    record_rows: Iterable[Mapping[str, Any]],
    request_rows: Iterable[Mapping[str, Any]],
    source_evidence: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Validate source windows and records against the frozen midpoint schedule."""

    from .metadata import validate_sampling_schedule

    records = [dict(row) for row in record_rows]
    requests = [dict(row) for row in request_rows]
    errors: list[str] = []
    if not isinstance(source_evidence, Mapping):
        return {"errors": ["source evidence is required for sampling validation"], "complete": False}
    shard_rows = source_evidence.get("selected_shard_evidence")
    route_rows = source_evidence.get("route_mapping")
    if not isinstance(shard_rows, list) or not isinstance(route_rows, list):
        return {"errors": ["selected-shard and route rows are required for sampling validation"], "complete": False}
    schedule_validation = validate_sampling_schedule(source_evidence.get("sampling_schedule"), shard_rows)
    if not schedule_validation["complete"]:
        errors.extend(f"schedule: {error}" for error in schedule_validation["errors"][:20])
    shard_by_path = {row.get("path"): row for row in shard_rows if isinstance(row, Mapping)}
    route_by_path = {row.get("path"): row for row in route_rows if isinstance(row, Mapping)}
    successful_by_logical: dict[str, dict[str, Any]] = {}
    for row in requests:
        if (
            row.get("request_outcome") in {"success", "row_success"}
            and row.get("http_status") == 200
            and isinstance(row.get("request_id"), str)
        ):
            if row["request_id"] in successful_by_logical:
                errors.append(f"duplicate successful logical request: {row['request_id']}")
            successful_by_logical[row["request_id"]] = row

    def parse_offset_length(value: Any) -> tuple[int, int] | None:
        if not isinstance(value, str):
            return None
        offset_match = re.search(r"(?:^|[?&,])offset=(\d+)(?:[&,]|$)", value)
        length_match = re.search(r"(?:^|[?&,])length=(\d+)(?:[&,]|$)", value)
        if offset_match is None or length_match is None:
            return None
        return int(offset_match.group(1)), int(length_match.group(1))

    windows_by_path: dict[str, list[tuple[int, int, str]]] = {}
    for logical_id, row in successful_by_logical.items():
        path = row.get("shard_path")
        shard = shard_by_path.get(path)
        route = route_by_path.get(path)
        if shard is None:
            errors.append(f"request {logical_id}: shard path is not bound to one frozen shard row")
        if route is None:
            errors.append(f"request {logical_id}: shard path is not bound to one frozen route row")
        elif row.get("route") != route.get("route_kind"):
            errors.append(f"request {logical_id}: request route does not match frozen route mapping")
        parsed = parse_offset_length(row.get("row_range_or_metadata_target"))
        if parsed is None:
            errors.append(f"request {logical_id}: offset/length is not parseable")
            continue
        offset, length = parsed
        if offset < 0 or length < 1 or length > 100:
            errors.append(f"request {logical_id}: window bounds violate 0<=offset and 1<=length<=100")
        if isinstance(shard, Mapping) and offset + length > shard.get("row_count", -1):
            errors.append(f"request {logical_id}: offset + length exceeds exact shard row_count")
        windows_by_path.setdefault(str(path), []).append((offset, offset + length, logical_id))

    for path, windows in windows_by_path.items():
        ordered = sorted(windows)
        for previous, current in zip(ordered, ordered[1:]):
            if current[0] < previous[1]:
                errors.append(f"shard {path}: source windows overlap")
            if current[0] == previous[0] and current[1] == previous[1]:
                errors.append(f"shard {path}: duplicate source window")

    actual_positions: dict[str, list[int]] = {}
    for index, record in enumerate(records):
        request = successful_by_logical.get(record.get("request_id"))
        if request is None:
            errors.append(f"record {index}: no successful request for sampling position")
            continue
        parsed = parse_offset_length(request.get("row_range_or_metadata_target"))
        record_index = record.get("record_index_within_response")
        if parsed is None or not isinstance(record_index, int):
            continue
        actual_positions.setdefault(str(request.get("shard_path")), []).append(parsed[0] + record_index)

    expected_positions = {
        str(row["path"]): list(row["sampled_positions"])
        for row in (source_evidence.get("sampling_schedule", {}).get("shards", [])
                    if isinstance(source_evidence.get("sampling_schedule"), Mapping) else [])
        if isinstance(row, Mapping) and "path" in row
    }
    if set(actual_positions) != set(expected_positions):
        errors.append("actual sampled shard set does not equal the frozen schedule shard set")
    for path, expected in expected_positions.items():
        actual = actual_positions.get(path, [])
        if len(actual) != len(set(actual)):
            errors.append(f"shard {path}: duplicate sampled source position")
        if sorted(actual) != expected:
            errors.append(f"shard {path}: sampled source positions do not match midpoint schedule")
    return {
        "successful_row_request_count": len(successful_by_logical),
        "window_count": sum(len(windows) for windows in windows_by_path.values()),
        "actual_record_position_count": sum(len(values) for values in actual_positions.values()),
        "expected_record_position_count": sum(len(values) for values in expected_positions.values()),
        "schedule": schedule_validation,
        "errors": errors,
        "complete": not errors and schedule_validation["complete"],
    }


def serialize_record_manifest(rows: Iterable[Mapping[str, Any]], *, expected_count: int | None = None) -> str:
    """Serialize only schema-valid text-free record rows as deterministic JSONL."""

    materialized = [dict(row) for row in rows]
    validate_record_manifest(materialized, expected_count=expected_count, raise_on_error=True)
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in materialized)


def serialize_request_ledger(rows: Iterable[Mapping[str, Any]]) -> str:
    """Serialize only schema-valid request-level JSONL rows."""

    materialized = [dict(row) for row in rows]
    validate_request_ledger(materialized, raise_on_error=True)
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in materialized)


def manifest_row_from_processed(
    item: Mapping[str, Any], *, split: str | None, near_dedup_version: str, benchmark_overlap_status: str
) -> dict[str, Any]:
    """Project internal processing state into the exact text-free 151ak row schema."""

    lid = item["lid"]
    quality = item["quality"]
    contamination = item["contamination"]
    return {
        "request_id": item.get("request_id"),
        "record_index_within_response": item.get("record_index_within_response"),
        "source_repo": item.get("source_repo"),
        "immutable_revision": item.get("immutable_revision"),
        "corpus": item.get("corpus"),
        "shard_path": item.get("shard_path"),
        "stable_source_row_document_id": item.get("stable_source_row_document_id", item.get("record_id")),
        "original_id": item.get("original_id"),
        "source_identity_key": dict(item.get("source_identity_key", {})),
        "sample_index": item.get("sample_index"),
        "exact_serialized_record_payload_bytes": item.get("exact_serialized_record_payload_bytes"),
        "normalized_text_sha256": item.get("normalized_text_sha256"),
        "retrieved_at_utc": item.get("retrieved_at_utc"),
        "raw_text_character_count": item.get("raw_text_character_count"),
        "normalized_text_character_count": item.get("normalized_text_character_count"),
        "normalization_version": item.get("normalization_version", "nfc_control_whitespace_v1"),
        "lid_evaluator_id": lid.get("evaluator_id"),
        "lid_evaluator_sha256": lid.get("evaluator_sha256"),
        "lid_status": lid.get("status"),
        "lid_top1_language": lid.get("top1_language"),
        "lid_confidence": lid.get("confidence"),
        "strict_mixed_line_flag": lid.get("mixed_line_flag"),
        "quality_status": "accepted" if quality.get("accepted") else "rejected",
        "quality_reason_codes": list(quality.get("reasons", [])),
        "pii_status": "flagged" if item.get("pii_types") else "clean",
        "pii_reason_codes": list(item.get("pii_types", [])),
        "exact_dedup_key": item.get("normalized_text_sha256"),
        "near_dedup_version": near_dedup_version,
        "synthetic_contamination_status": contamination.get("status"),
        "synthetic_contamination_tiers": sorted(contamination.get("tiers", [])),
        "benchmark_overlap_status": benchmark_overlap_status,
        "split": split,
        "retention_status": item.get("retention_status"),
        "rejection_reason_codes": sorted(set(item.get("rejection_reason_codes", []))),
    }
