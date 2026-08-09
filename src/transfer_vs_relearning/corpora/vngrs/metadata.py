"""Official-release metadata and deterministic shard-selection primitives.

Only release-level facts verified from the official immutable tree/card belong here.  Missing
per-object bytes, LFS IDs, Parquet footer facts and object hashes remain explicit ``None`` values;
they are never inferred from rounded web UI sizes.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

VNGRS_REPOSITORY = "vngrs-ai/vngrs-web-corpus"
VNGRS_REVISION = "ee5c6201ee84457a18182bfc483a7d8a7f3655ba"
VNGRS_SPLIT = "train"
VNGRS_SHARD_COUNT = 284
VNGRS_SCHEMA = ("text", "corpus", "original_id")
VNGRS_TRAIN_ROWS = 50_336_214
VNGRS_LICENSE = "cc-by-nc-sa-4.0"
FROZEN_SELECTION_PAYLOAD_SHA256 = "dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686"
_SHARD_RE = re.compile(r"^train-(?P<ordinal>[0-9]{5})-of-(?P<count>[0-9]{5})\.parquet$")

# Document 151an is a metadata/footer feasibility wave, not a row-sampling wave.  These
# constants deliberately live beside the release identity so a future executor cannot silently
# substitute a different root, route kind, range rule or output surface.
METADATA_FOOTER_SCRATCH_ROOT = "/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1"
METADATA_FOOTER_ROUTE_KIND = "parquet_footer_range"
METADATA_FOOTER_TRAILER_BYTES = 8
METADATA_FOOTER_TRAILER_RANGE_HEADER = "bytes=-8"
METADATA_FOOTER_RANGE_HEADER = METADATA_FOOTER_TRAILER_RANGE_HEADER
METADATA_FOOTER_FOOTER_RANGE_TEMPLATE = "bytes={start}-"
METADATA_FOOTER_MAX_ACCEPTED_FOOTER_BYTES = 4 * 1024 * 1024
METADATA_FOOTER_MAX_RANGE_BYTES = METADATA_FOOTER_MAX_ACCEPTED_FOOTER_BYTES
METADATA_FOOTER_MAX_HTTP_ATTEMPTS = 128
METADATA_FOOTER_MAX_RETRIES = 24
METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES = 64 * 1024 * 1024
METADATA_FOOTER_MAX_SINGLE_RESPONSE_BYTES = 4 * 1024 * 1024
METADATA_FOOTER_MAX_WALL_CLOCK_SECONDS = 7_200
METADATA_FOOTER_MAX_OUTPUT_FILES = 128
METADATA_FOOTER_MAX_NEW_INODES = 128
METADATA_FOOTER_OUTPUT_PATHS = (
    "selection_plan.json",
    "shard_metadata_ledger.jsonl",
    "route_ledger.jsonl",
    "request_ledger.jsonl",
    "evidence_artifact_manifest.jsonl",
    "feasibility_projection.json",
    "metadata_footer_audit.json",
)
METADATA_FOOTER_ARTIFACT_KINDS = frozenset(
    {
        "head_metadata_route",
        "parquet_footer_trailer",
        "parquet_footer_bytes",
        "license_attribution_bytes",
        "retry_response",
    }
)
METADATA_FOOTER_FORBIDDEN_ARTIFACT_KINDS = frozenset(
    {"corpus_rows", "compressed_row_group", "full_shard", "model_weights", "tokenizer_snapshot"}
)
_SAFE_ARTIFACT_RE = re.compile(r"^(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+$")
METADATA_FOOTER_CONTRACT_SHA256 = "937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79"
_FOOTER_RANGE_RE = re.compile(r"bytes=(?P<start>[0-9]+)-$")
_METADATA_FOOTER_RETRY_ARTIFACT_RE = re.compile(r"^evidence/retry/[A-Za-z0-9_.-]+$")
METADATA_FOOTER_RETRYABLE_HTTP_STATUSES = frozenset({429, 503})
METADATA_FOOTER_RETRYABLE_ERROR_CODES = frozenset(
    {"http_429", "http_503", "transport_timeout", "transport_connection_error"}
)
METADATA_FOOTER_RETRY_FAILURE_CLASSES = frozenset({"http_retryable", "transport_no_response"})
_HF_REDIRECT_METADATA_FIELDS = frozenset(
    {"location_sha256", "scheme", "host", "path_sha256", "url_length", "query_keys"}
)
_HF_REDIRECT_ALLOWED_HOST_SUFFIXES = ("xethub.hf.co", "cdn.hf.co")
_HF_REDIRECT_MAX_URL_LENGTH = 8_192


def _valid_redirect_chain(value: Any) -> bool:
    """Validate the secret-safe, at-most-one-hop redirect representation."""

    if not isinstance(value, list) or len(value) > 1:
        return False
    if not value:
        return True
    entry = value[0]
    if not isinstance(entry, Mapping) or set(entry) != _HF_REDIRECT_METADATA_FIELDS:
        return False
    host = entry.get("host")
    if (
        entry.get("scheme") != "https"
        or not isinstance(host, str)
        or not any(host == suffix or host.endswith("." + suffix) for suffix in _HF_REDIRECT_ALLOWED_HOST_SUFFIXES)
        or not isinstance(entry.get("url_length"), int)
        or not 0 < entry["url_length"] <= _HF_REDIRECT_MAX_URL_LENGTH
    ):
        return False
    if not all(
        isinstance(entry.get(field), str) and re.fullmatch(r"[0-9a-f]{64}", entry[field])
        for field in ("location_sha256", "path_sha256")
    ):
        return False
    query_keys = entry.get("query_keys")
    return (
        isinstance(query_keys, list)
        and all(isinstance(key, str) for key in query_keys)
        and query_keys == sorted(query_keys)
    )


class _CompactProtocolError(ValueError):
    """Malformed Apache Thrift compact-protocol bytes."""


class _CompactReader:
    """Small bounded reader for the Parquet FileMetaData Thrift compact encoding."""

    _MAX_CONTAINER_ITEMS = 100_000

    def __init__(self, payload: bytes):
        self.payload = payload
        self.position = 0

    def _take(self, count: int) -> bytes:
        if count < 0 or self.position + count > len(self.payload):
            raise _CompactProtocolError("truncated compact-protocol payload")
        result = self.payload[self.position : self.position + count]
        self.position += count
        return result

    def _read_byte(self) -> int:
        return self._take(1)[0]

    def _read_varint(self) -> int:
        value = 0
        shift = 0
        for _ in range(10):
            byte = self._read_byte()
            value |= (byte & 0x7F) << shift
            if not byte & 0x80:
                return value
            shift += 7
        raise _CompactProtocolError("compact-protocol varint exceeds ten bytes")

    @staticmethod
    def _unzigzag(value: int) -> int:
        return (value >> 1) ^ -(value & 1)

    def _read_integer(self) -> int:
        return self._unzigzag(self._read_varint())

    def _read_binary(self) -> bytes:
        length = self._read_varint()
        if length > len(self.payload) or length > self._MAX_CONTAINER_ITEMS * 1024:
            raise _CompactProtocolError("compact-protocol binary field exceeds bound")
        return self._take(length)

    def _read_value(self, type_code: int) -> Any:
        if type_code == 1:
            return True
        if type_code == 2:
            return False
        if type_code == 3:
            return struct.unpack("b", self._take(1))[0]
        if type_code in {4, 5, 6}:
            return self._read_integer()
        if type_code == 7:
            return struct.unpack("<d", self._take(8))[0]
        if type_code == 8:
            return self._read_binary()
        if type_code in {9, 10}:
            header = self._read_byte()
            size = header >> 4
            element_type = header & 0x0F
            if size == 15:
                size = self._read_varint()
            if size > self._MAX_CONTAINER_ITEMS:
                raise _CompactProtocolError("compact-protocol container exceeds bound")
            return [self._read_value(element_type) for _ in range(size)]
        if type_code == 11:
            size = self._read_varint()
            if size > self._MAX_CONTAINER_ITEMS:
                raise _CompactProtocolError("compact-protocol map exceeds bound")
            types = self._read_byte()
            key_type, value_type = types >> 4, types & 0x0F
            result: dict[Any, Any] = {}
            for _ in range(size):
                result[self._read_value(key_type)] = self._read_value(value_type)
            return result
        if type_code == 12:
            return self._read_struct()
        raise _CompactProtocolError(f"unknown compact-protocol type {type_code}")

    def _read_struct(self) -> dict[int, Any]:
        fields: dict[int, Any] = {}
        last_field_id = 0
        while True:
            header = self._read_byte()
            type_code = header & 0x0F
            if type_code == 0:
                return fields
            field_delta = header >> 4
            field_id = self._unzigzag(self._read_varint()) if field_delta == 0 else last_field_id + field_delta
            if field_id in fields:
                raise _CompactProtocolError(f"duplicate compact-protocol field {field_id}")
            fields[field_id] = self._read_value(type_code)
            last_field_id = field_id

    def read_root_struct(self) -> dict[int, Any]:
        result = self._read_struct()
        if self.position != len(self.payload):
            raise _CompactProtocolError("trailing bytes after compact-protocol root struct")
        return result


def parse_parquet_trailer(payload: bytes) -> dict[str, int]:
    """Parse the exact eight-byte Parquet trailer (metadata length plus ``PAR1``)."""

    if not isinstance(payload, bytes) or len(payload) != METADATA_FOOTER_TRAILER_BYTES:
        raise ValueError("Parquet trailer must contain exactly eight bytes")
    if payload[-4:] != b"PAR1":
        raise ValueError("Parquet trailer magic is not PAR1")
    metadata_length = int.from_bytes(payload[:4], "little", signed=False)
    if metadata_length <= 0 or metadata_length + METADATA_FOOTER_TRAILER_BYTES > METADATA_FOOTER_MAX_ACCEPTED_FOOTER_BYTES:
        raise ValueError("Parquet metadata length exceeds the frozen footer bound")
    return {"metadata_length": metadata_length}


def parse_parquet_footer(payload: bytes) -> dict[str, Any]:
    """Parse a complete bounded footer range and derive all row-group ledger values."""

    if not isinstance(payload, bytes) or len(payload) < METADATA_FOOTER_TRAILER_BYTES:
        raise ValueError("complete Parquet footer range is truncated")
    if len(payload) > METADATA_FOOTER_MAX_ACCEPTED_FOOTER_BYTES:
        raise ValueError("complete Parquet footer exceeds the frozen maximum")
    trailer = parse_parquet_trailer(payload[-METADATA_FOOTER_TRAILER_BYTES:])
    metadata_length = trailer["metadata_length"]
    metadata_start = len(payload) - METADATA_FOOTER_TRAILER_BYTES - metadata_length
    if metadata_start != 0:
        raise ValueError("footer range does not contain the complete declared metadata")
    try:
        root = _CompactReader(payload[:metadata_length]).read_root_struct()
    except _CompactProtocolError as exc:
        raise ValueError(f"malformed Parquet FileMetaData compact bytes: {exc}") from exc

    version = root.get(1)
    schema = root.get(2)
    total_rows = root.get(3)
    row_groups = root.get(4)
    if not isinstance(version, int) or isinstance(version, bool):
        raise ValueError("Parquet FileMetaData version is missing")
    if not isinstance(schema, list) or not schema:
        raise ValueError("Parquet FileMetaData schema is missing")
    if not isinstance(total_rows, int) or isinstance(total_rows, bool) or total_rows <= 0:
        raise ValueError("Parquet FileMetaData row count is invalid")
    if not isinstance(row_groups, list) or not row_groups:
        raise ValueError("Parquet FileMetaData row groups are missing")
    schema_names = tuple(
        element.get(4)
        for element in schema
        if isinstance(element, Mapping) and isinstance(element.get(4), bytes)
    )
    if len(schema_names) != len(schema):
        raise ValueError("Parquet schema elements are malformed")
    layout: list[dict[str, int]] = []
    for index, group in enumerate(row_groups):
        if not isinstance(group, Mapping):
            raise ValueError(f"Parquet row group {index} is malformed")
        columns = group.get(1)
        group_rows = group.get(3)
        uncompressed = group.get(2)
        compressed = group.get(6)
        file_offset = group.get(5)
        if not isinstance(columns, list) or not columns:
            raise ValueError(f"Parquet row group {index} has no column chunks")
        if not isinstance(group_rows, int) or isinstance(group_rows, bool) or group_rows <= 0:
            raise ValueError(f"Parquet row group {index} row count is invalid")
        if not isinstance(uncompressed, int) or isinstance(uncompressed, bool) or uncompressed <= 0:
            raise ValueError(f"Parquet row group {index} uncompressed bytes are invalid")
        if not isinstance(compressed, int) or isinstance(compressed, bool) or compressed <= 0:
            raise ValueError(f"Parquet row group {index} compressed bytes are invalid")
        if not isinstance(file_offset, int) or isinstance(file_offset, bool) or file_offset < 0:
            file_offset = min(
                (column.get(2) for column in columns if isinstance(column, Mapping) and isinstance(column.get(2), int)),
                default=0,
            )
        layout.append(
            {
                "row_count": group_rows,
                "compressed_bytes": compressed,
                "uncompressed_bytes": uncompressed,
                "file_offset": file_offset,
                "column_chunk_count": len(columns),
            }
        )
    if sum(row["row_count"] for row in layout) != total_rows:
        raise ValueError("Parquet row-group counts do not sum to FileMetaData row count")
    return {
        "metadata_length": metadata_length,
        "row_count": total_rows,
        "row_group_count": len(layout),
        "row_group_layout": layout,
        "compressed_bytes": sum(row["compressed_bytes"] for row in layout),
        "uncompressed_bytes": sum(row["uncompressed_bytes"] for row in layout),
        "schema_names": schema_names,
    }


def serialize_metadata_footer_artifact_manifest(rows: Iterable[Mapping[str, Any]]) -> bytes:
    """Serialize manifest rows exactly as the validator's canonical JSONL binding."""

    return b"".join(canonical_json_bytes(dict(row)) + b"\n" for row in rows)


@dataclass(frozen=True)
class ShardMetadata:
    """A shard registry row whose unresolved fields stay unresolved."""

    path: str
    ordinal: int
    shard_count: int
    row_count: int | None = None
    compressed_bytes: int | None = None
    object_id: str | None = None
    sha256: str | None = None
    footer_sha256: str | None = None
    license_bytes_sha256: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "ordinal": self.ordinal,
            "shard_count": self.shard_count,
            "row_count": self.row_count,
            "compressed_bytes": self.compressed_bytes,
            "object_id": self.object_id,
            "sha256": self.sha256,
            "footer_sha256": self.footer_sha256,
            "license_bytes_sha256": self.license_bytes_sha256,
        }


def build_shard_paths(total_shards: int = VNGRS_SHARD_COUNT) -> tuple[str, ...]:
    """Return the exact official path pattern, with no response-dependent selection."""

    if total_shards <= 0 or total_shards > 99_999:
        raise ValueError("total_shards must be in the range 1..99999")
    return tuple(
        f"data/train-{ordinal:05d}-of-{total_shards:05d}.parquet"
        for ordinal in range(total_shards)
    )


def parse_shard_path(path: str) -> tuple[int, int]:
    match = _SHARD_RE.fullmatch(path.rsplit("/", 1)[-1])
    if match is None:
        raise ValueError(f"not an official vngrs shard path: {path!r}")
    return int(match.group("ordinal")), int(match.group("count"))


def select_systematic_shards(total_shards: int, selected_shards: int) -> tuple[int, ...]:
    """Select evenly spaced shard ordinals using immutable midpoint-systematic sampling.

    The formula is ``floor((rank + 1/2) * N / K)``.  It is deterministic, covers the whole
    release, cannot replace a failed shard with a later response, and is not the biased first-K
    ordinal prefix.  Any duplicate or out-of-range result is a hard error.
    """

    if total_shards <= 0 or selected_shards <= 0 or selected_shards > total_shards:
        raise ValueError("selected_shards must be positive and no greater than total_shards")
    ordinals = tuple(
        math.floor((rank + 0.5) * total_shards / selected_shards)
        for rank in range(selected_shards)
    )
    if len(set(ordinals)) != selected_shards or not all(0 <= value < total_shards for value in ordinals):
        raise AssertionError("systematic selection produced invalid or duplicate ordinals")
    return ordinals


def build_selection_evidence(
    *, total_shards: int = VNGRS_SHARD_COUNT, selected_shards: int = 32
) -> dict[str, Any]:
    """Build a serializable selection record without claiming unresolved shard facts."""

    ordinals = select_systematic_shards(total_shards, selected_shards)
    all_paths = build_shard_paths(total_shards)
    selected = tuple(all_paths[ordinal] for ordinal in ordinals)
    rows = [
        ShardMetadata(path=path, ordinal=ordinal, shard_count=total_shards).to_dict()
        for ordinal, path in zip(ordinals, selected, strict=True)
    ]
    return {
        "selection_version": "vngrs_systematic_midpoint_32_of_284_v1",
        "source_repository": VNGRS_REPOSITORY,
        "immutable_revision": VNGRS_REVISION,
        "split": VNGRS_SPLIT,
        "selection_formula": "floor((rank + 0.5) * total_shards / selected_shards)",
        "total_shards": total_shards,
        "selected_shards": selected_shards,
        "selected_ordinals": list(ordinals),
        "selected_paths": list(selected),
        "registry_rows": rows,
        "unresolved_fields": [
            "row_count",
            "compressed_bytes",
            "object_id",
            "sha256",
            "footer_sha256",
            "license_bytes_sha256",
            "source_corpus_composition",
        ],
        "selection_status": "EXACT_PATH_SET_FROZEN_METADATA_INCOMPLETE",
        "fail_closed_conditions": [
            "any_duplicate_source_row_or_document_id",
            "missing_or_mismatched_immutable_revision",
            "missing_exact_per_shard_object_bytes_or_footer_evidence",
            "filtered_pool_cannot_support_the_frozen_maximum_dose",
            "source_corpus_composition_is_not_acceptable_for_the_frozen_design",
        ],
    }


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


# This is evaluated from the immutable formula rather than copied from a caller-provided
# sample.  The tuple is an authority constant for the strict 151ak final evidence graph.
FROZEN_SELECTED_SHARD_PATHS = tuple(build_selection_evidence()["selected_paths"])


def validate_final_source_evidence(
    evidence: Mapping[str, Any] | None,
    *,
    artifact_payloads: Mapping[str, bytes] | None = None,
) -> dict[str, Any]:
    """Validate exact source/shard/route evidence required by the frozen final profile."""

    errors: list[str] = []
    if not isinstance(evidence, Mapping):
        return {"errors": ["source evidence must be a mapping"], "complete": False}
    required = {
        "status", "source_repository", "immutable_revision", "split", "schema", "source_license",
        "selection_version", "selection_formula", "total_shards", "selected_shards", "selected_ordinals",
        "selected_paths", "selection_payload", "selection_payload_sha256", "route_mapping",
        "sampling_schedule", "evidence_sha256",
    }
    missing = sorted(required - set(evidence))
    if missing:
        errors.append(f"missing source-evidence fields: {missing}")
    if evidence.get("status") != "verified":
        errors.append("source evidence status is not verified")
    exact_scalars = {
        "source_repository": VNGRS_REPOSITORY,
        "immutable_revision": VNGRS_REVISION,
        "split": VNGRS_SPLIT,
        "source_license": VNGRS_LICENSE,
        "selection_version": "vngrs_systematic_midpoint_32_of_284_v1",
        "selection_formula": "floor((rank + 0.5) * total_shards / selected_shards)",
        "total_shards": VNGRS_SHARD_COUNT,
        "selected_shards": 32,
    }
    for field, expected in exact_scalars.items():
        if evidence.get(field) != expected:
            errors.append(f"{field} does not match frozen source-selection authority")
    if tuple(evidence.get("schema", ())) != VNGRS_SCHEMA:
        errors.append("schema does not match the frozen text/corpus/original_id schema")
    expected_selection = build_selection_evidence()
    if evidence.get("selected_ordinals") != expected_selection["selected_ordinals"]:
        errors.append("selected_ordinals do not match the frozen midpoint selection")
    if evidence.get("selected_paths") != list(FROZEN_SELECTED_SHARD_PATHS):
        errors.append("selected_paths do not match the frozen 32-path set")
    selection_payload = evidence.get("selection_payload")
    computed_selection_sha = canonical_json_sha256(selection_payload) if isinstance(selection_payload, Mapping) else None
    if computed_selection_sha != FROZEN_SELECTION_PAYLOAD_SHA256:
        errors.append("selection_payload SHA-256 does not match the frozen payload")
    if evidence.get("selection_payload_sha256") != computed_selection_sha:
        errors.append("selection_payload_sha256 is not recomputed from selection_payload")

    shard_rows = evidence.get("selected_shard_evidence")
    if not isinstance(shard_rows, list):
        # Keep the public field name explicit; selected_shards is the scalar cardinality above.
        shard_rows = evidence.get("selected_shard_rows")
    if not isinstance(shard_rows, list) or len(shard_rows) != 32:
        errors.append("exactly 32 selected-shard evidence rows are required")
        shard_rows = []
    shard_fields = {
        "path", "ordinal", "shard_count", "row_count", "compressed_bytes", "uncompressed_bytes",
        "object_id", "sha256", "footer_sha256", "license_bytes_sha256",
        "object_evidence_artifact", "footer_evidence_artifact", "license_evidence_artifact",
    }
    seen_paths: list[str] = []
    for index, row in enumerate(shard_rows):
        if not isinstance(row, Mapping):
            errors.append(f"selected shard row {index} is not a mapping")
            continue
        if not shard_fields.issubset(row):
            errors.append(f"selected shard row {index} lacks required object/footer fields")
        path = row.get("path")
        seen_paths.append(path)
        if path != (FROZEN_SELECTED_SHARD_PATHS[index] if index < len(FROZEN_SELECTED_SHARD_PATHS) else None):
            errors.append(f"selected shard row {index} path is not in frozen order")
        if row.get("ordinal") != (expected_selection["selected_ordinals"][index] if index < 32 else None):
            errors.append(f"selected shard row {index} ordinal is not frozen")
        for field in ("row_count", "compressed_bytes", "uncompressed_bytes"):
            if not isinstance(row.get(field), int) or isinstance(row[field], bool) or row[field] <= 0:
                errors.append(f"selected shard row {index}: {field} must be positive exact bytes/count")
        if row.get("shard_count") != VNGRS_SHARD_COUNT or not isinstance(row.get("object_id"), str) or not row["object_id"]:
            errors.append(f"selected shard row {index}: object identity or shard count is incomplete")
        for field in ("sha256", "footer_sha256", "license_bytes_sha256"):
            if not isinstance(row.get(field), str) or re.fullmatch(r"[0-9a-f]{64}", row[field]) is None:
                errors.append(f"selected shard row {index}: {field} is not a lowercase SHA-256")
        for field in ("object_evidence_artifact", "footer_evidence_artifact", "license_evidence_artifact"):
            if not isinstance(row.get(field), str) or not row[field] or row[field].startswith("/") or ".." in row[field].split("/"):
                errors.append(f"selected shard row {index}: {field} is not a safe named compact artifact")
    if seen_paths != list(FROZEN_SELECTED_SHARD_PATHS):
        errors.append("selected-shard evidence path set/order is not exact")

    route_rows = evidence.get("route_mapping")
    if not isinstance(route_rows, list) or len(route_rows) != 32:
        errors.append("route_mapping must contain exactly one row per selected shard")
        route_rows = []
    seen_route_paths: list[str] = []
    for index, row in enumerate(route_rows):
        if not isinstance(row, Mapping):
            errors.append(f"route mapping row {index} is not a mapping")
            continue
        for field in ("path", "route", "route_kind", "immutable_revision", "status", "route_evidence_sha256", "route_evidence_artifact"):
            if not isinstance(row.get(field), str) or not row[field]:
                errors.append(f"route mapping row {index}: {field} is missing")
        path = row.get("path")
        seen_route_paths.append(path)
        if path != (FROZEN_SELECTED_SHARD_PATHS[index] if index < 32 else None):
            errors.append(f"route mapping row {index} path is not in frozen order")
        if row.get("immutable_revision") != VNGRS_REVISION or row.get("status") != "verified":
            errors.append(f"route mapping row {index}: revision/status is not verified")
        if not isinstance(row.get("route_evidence_sha256"), str) or re.fullmatch(r"[0-9a-f]{64}", row.get("route_evidence_sha256", "")) is None:
            errors.append(f"route mapping row {index}: route evidence hash is invalid")
        if row.get("route_kind") != "/rows":
            errors.append(f"route mapping row {index}: route_kind must be /rows")
        if not isinstance(row.get("route_evidence_artifact"), str) or row["route_evidence_artifact"].startswith("/") or ".." in row["route_evidence_artifact"].split("/"):
            errors.append(f"route mapping row {index}: route_evidence_artifact is not safe")
    if seen_route_paths != list(FROZEN_SELECTED_SHARD_PATHS):
        errors.append("route_mapping does not cover every frozen selected shard exactly once")

    schedule_validation = validate_sampling_schedule(evidence.get("sampling_schedule"), shard_rows)
    if not schedule_validation["complete"]:
        errors.extend(f"sampling_schedule: {error}" for error in schedule_validation["errors"][:20])

    named_artifacts: dict[str, str] = {}
    for index, row in enumerate(shard_rows):
        if isinstance(row, Mapping):
            for field in ("object_evidence_artifact", "footer_evidence_artifact", "license_evidence_artifact"):
                name = row.get(field)
                if isinstance(name, str):
                    if name in named_artifacts:
                        errors.append(f"duplicate source evidence artifact name: {name}")
                    named_artifacts[name] = row.get({
                        "object_evidence_artifact": "sha256",
                        "footer_evidence_artifact": "footer_sha256",
                        "license_evidence_artifact": "license_bytes_sha256",
                    }[field], "")
    for index, row in enumerate(route_rows):
        if isinstance(row, Mapping):
            name = row.get("route_evidence_artifact")
            if isinstance(name, str):
                if name in named_artifacts:
                    errors.append(f"duplicate source evidence artifact name: {name}")
                named_artifacts[name] = row.get("route_evidence_sha256", "")
    if artifact_payloads is None:
        errors.append("source evidence artifact payloads are required for final validation")
    else:
        if set(artifact_payloads) != set(named_artifacts):
            errors.append("source evidence artifact payload names do not exactly match bindings")
        for name, expected_hash in named_artifacts.items():
            payload = artifact_payloads.get(name)
            if not isinstance(payload, bytes):
                errors.append(f"source evidence artifact payload missing or not bytes: {name}")
            elif hashlib.sha256(payload).hexdigest() != expected_hash:
                errors.append(f"source evidence artifact hash mismatch: {name}")

    evidence_without_hash = {key: value for key, value in evidence.items() if key != "evidence_sha256"}
    computed_evidence_sha = canonical_json_sha256(evidence_without_hash)
    if evidence.get("evidence_sha256") != computed_evidence_sha:
        errors.append("evidence_sha256 is not recomputed from the complete evidence payload")
    return {
        "required_field_count": len(required),
        "selected_shard_row_count": len(shard_rows),
        "route_mapping_row_count": len(route_rows),
        "computed_selection_payload_sha256": computed_selection_sha,
        "computed_evidence_sha256": computed_evidence_sha,
        "sampling_schedule": schedule_validation,
        "bound_artifact_count": len(named_artifacts),
        "errors": errors,
        "complete": not errors,
    }


def build_sampling_schedule(
    shard_rows: Iterable[Mapping[str, Any]], *, target_records: int = 10_000
) -> dict[str, Any]:
    """Serialize the frozen row-count-weighted midpoint schedule before any row request."""

    rows = [dict(row) for row in shard_rows]
    if len(rows) != 32 or target_records != 10_000:
        raise ValueError("the frozen schedule requires exactly 32 shards and 10,000 records")
    if any(not isinstance(row.get("row_count"), int) or row["row_count"] <= 0 for row in rows):
        raise ValueError("exact positive shard row counts are required for the schedule")
    total_rows = sum(row["row_count"] for row in rows)
    scaled = [row["row_count"] * target_records for row in rows]
    base = [value // total_rows for value in scaled]
    remainder = [value % total_rows for value in scaled]
    extras = target_records - sum(base)
    ranking = sorted(range(len(rows)), key=lambda index: (-remainder[index], str(rows[index]["path"])))
    for index in ranking[:extras]:
        base[index] += 1
    schedule_rows = []
    for row, sample_count in zip(rows, base, strict=True):
        positions = [
            (rank * 2 + 1) * row["row_count"] // (sample_count * 2)
            for rank in range(sample_count)
        ]
        schedule_rows.append(
            {
                "path": row["path"],
                "ordinal": row["ordinal"],
                "row_count": row["row_count"],
                "sample_count": sample_count,
                "sampled_positions": positions,
            }
        )
    schedule = {
        "schedule_version": "vngrs_row_count_weighted_midpoint_v1",
        "target_records": target_records,
        "allocation_rule": "largest_remainder_integer_then_lexicographic_path",
        "position_rule": "floor((2*rank+1)*row_count/(2*sample_count))",
        "request_mode": "contiguous_row_windows",
        "max_rows_per_request": 100,
        "shards": schedule_rows,
    }
    schedule["schedule_sha256"] = canonical_json_sha256(schedule)
    return schedule


def validate_sampling_schedule(
    schedule: Mapping[str, Any] | None, shard_rows: Iterable[Mapping[str, Any]], *, target_records: int = 10_000
) -> dict[str, Any]:
    """Recompute and compare the complete serialized deterministic sampling schedule."""

    errors: list[str] = []
    try:
        expected = build_sampling_schedule(shard_rows, target_records=target_records)
    except (TypeError, ValueError) as exc:
        return {"errors": [str(exc)], "complete": False}
    if not isinstance(schedule, Mapping):
        return {"errors": ["sampling_schedule must be a mapping"], "complete": False}
    supplied_without_hash = {key: value for key, value in schedule.items() if key != "schedule_sha256"}
    computed_hash = canonical_json_sha256(supplied_without_hash)
    if schedule.get("schedule_sha256") != computed_hash:
        errors.append("sampling schedule hash is not recomputed from its payload")
    if schedule != expected:
        errors.append("sampling schedule does not equal the recomputed frozen midpoint schedule")
    minimum_contiguous_windows = 0
    for row in expected["shards"]:
        positions = row["sampled_positions"]
        if not positions:
            continue
        windows = 0
        covered_until = -1
        for position in positions:
            if position > covered_until:
                windows += 1
                covered_until = position + expected["max_rows_per_request"] - 1
        minimum_contiguous_windows += windows
    if minimum_contiguous_windows > 100:
        errors.append(
            "exact midpoint schedule cannot fit the frozen 100-successful-request envelope "
            f"(minimum contiguous windows={minimum_contiguous_windows})"
        )
    return {
        "target_records": expected["target_records"],
        "shard_count": len(expected["shards"]),
        "schedule_sha256": computed_hash,
        "minimum_contiguous_windows": minimum_contiguous_windows,
        "max_successful_row_requests": 100,
        "errors": errors,
        "complete": not errors,
    }


def build_metadata_footer_feasibility_projection(
    shard_rows: Iterable[Mapping[str, Any]],
    request_rows: Iterable[Mapping[str, Any]],
    *,
    evidence_artifact_count: int = 0,
) -> dict[str, Any]:
    """Build the pre-row budget projection without retrieving or materializing corpus rows."""

    request_rows = tuple(request_rows)
    total_response_bytes = sum(
        int(row.get("response_transferred_bytes", 0))
        for row in request_rows
        if isinstance(row.get("response_transferred_bytes"), int)
    )
    max_response_bytes = max(
        (int(row.get("response_transferred_bytes", 0)) for row in request_rows),
        default=0,
    )
    schedule = build_sampling_schedule(shard_rows)
    minimum_contiguous_windows = 0
    for row in schedule["shards"]:
        positions = row["sampled_positions"]
        covered_until = -1
        for position in positions:
            if position > covered_until:
                minimum_contiguous_windows += 1
                covered_until = position + schedule["max_rows_per_request"] - 1
    return {
        "route_kind": METADATA_FOOTER_ROUTE_KIND,
        "metadata_footer_only": True,
        "corpus_rows_retrieved": 0,
        "sample_manifest_created": False,
        "sampling_schedule_status": "computed_pre_row_retrieval",
        "sampling_schedule_sha256": schedule["schedule_sha256"],
        "minimum_contiguous_windows": minimum_contiguous_windows,
        "projected_request_count": len(request_rows),
        "projected_total_response_bytes": total_response_bytes,
        "projected_max_response_bytes": max_response_bytes,
        "projected_evidence_artifact_count": evidence_artifact_count,
        "projected_regular_file_count": evidence_artifact_count + len(METADATA_FOOTER_OUTPUT_PATHS),
        "projected_new_inode_count": evidence_artifact_count + len(METADATA_FOOTER_OUTPUT_PATHS),
    }


def parquet_resolve_url(path: str) -> str:
    """Return the only permitted immutable direct-file route for a selected shard."""

    if path not in FROZEN_SELECTED_SHARD_PATHS:
        raise ValueError("path is outside the frozen 32-shard metadata/footer allowlist")
    return (
        f"https://huggingface.co/datasets/{VNGRS_REPOSITORY}/resolve/"
        f"{VNGRS_REVISION}/{path}?download=true"
    )


def dataset_license_resolve_url() -> str:
    """Return the immutable README route used only for license/attribution bytes."""

    return (
        f"https://huggingface.co/datasets/{VNGRS_REPOSITORY}/resolve/"
        f"{VNGRS_REVISION}/README.md?download=true"
    )


def validate_metadata_footer_output_paths(
    paths: Iterable[str], *, scratch_root: str
) -> dict[str, Any]:
    """Validate the fixed top-level output surface for the 151an feasibility wave."""

    supplied = tuple(paths)
    errors: list[str] = []
    if scratch_root != METADATA_FOOTER_SCRATCH_ROOT:
        errors.append("scratch root does not match the frozen metadata/footer root")
    if supplied != METADATA_FOOTER_OUTPUT_PATHS:
        errors.append("top-level output paths do not match the frozen metadata/footer output order")
    if len(set(supplied)) != len(supplied):
        errors.append("top-level output paths are not unique")
    if any(not isinstance(path, str) or path.startswith("/") or not _SAFE_ARTIFACT_RE.fullmatch(path) for path in supplied):
        errors.append("top-level output paths contain an unsafe or absolute path")
    return {
        "scratch_root": scratch_root,
        "paths": list(supplied),
        "max_output_files": METADATA_FOOTER_MAX_OUTPUT_FILES,
        "max_new_inodes": METADATA_FOOTER_MAX_NEW_INODES,
        "errors": errors,
        "complete": not errors,
    }


def _metadata_footer_artifact_name(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(_SAFE_ARTIFACT_RE.fullmatch(value))
        and not value.startswith("/")
        and ".." not in value.split("/")
    )


def validate_metadata_footer_feasibility(
    package: Mapping[str, Any] | None,
    *,
    artifact_payloads: Mapping[str, bytes] | None = None,
    artifact_manifest_payload: bytes | None = None,
    metadata_footer_audit_payload: bytes | None = None,
) -> dict[str, Any]:
    """Validate a completed 151an metadata/footer-only evidence package.

    This validator intentionally has no row-materialization path.  It accepts exact direct-file
    routes, compact metadata/header/LFS evidence, footer bytes and license bytes, while rejecting
    Dataset Viewer ``/rows`` routes and corpus-row/compressed-row-group artifacts.  Full-object
    identity is kept in ``object_id``/``object_sha256`` fields and is never conflated with the
    hash of a compact metadata artifact.
    """

    errors: list[str] = []
    if not isinstance(package, Mapping):
        return {"errors": ["metadata/footer package must be a mapping"], "complete": False}
    required = {
        "source_repository", "immutable_revision", "split", "schema", "selected_paths",
        "selected_ordinals", "selection_payload", "selection_payload_sha256",
        "shard_metadata", "route_ledger", "request_ledger", "artifact_manifest",
        "artifact_manifest_sha256", "sampling_schedule", "feasibility_projection", "metadata_footer_audit",
        "metadata_footer_audit_sha256",
        "output_paths", "scratch_root",
    }
    missing = sorted(required - set(package))
    if missing:
        errors.append(f"missing metadata/footer package fields: {missing}")
    for field, expected in {
        "source_repository": VNGRS_REPOSITORY,
        "immutable_revision": VNGRS_REVISION,
        "split": VNGRS_SPLIT,
        "schema": list(VNGRS_SCHEMA),
        "selected_paths": list(FROZEN_SELECTED_SHARD_PATHS),
        "selected_ordinals": list(build_selection_evidence()["selected_ordinals"]),
        "selection_payload_sha256": FROZEN_SELECTION_PAYLOAD_SHA256,
        "scratch_root": METADATA_FOOTER_SCRATCH_ROOT,
    }.items():
        if package.get(field) != expected:
            errors.append(f"{field} does not match the frozen metadata/footer authority")
    selection_payload = package.get("selection_payload")
    selection_sha = canonical_json_sha256(selection_payload) if isinstance(selection_payload, Mapping) else None
    if selection_sha != FROZEN_SELECTION_PAYLOAD_SHA256:
        errors.append("selection_payload is not the frozen canonical selection payload")

    output_validation = validate_metadata_footer_output_paths(
        package.get("output_paths", ()), scratch_root=package.get("scratch_root")
    )
    errors.extend(f"output: {error}" for error in output_validation["errors"])

    shard_rows = package.get("shard_metadata")
    if not isinstance(shard_rows, list) or len(shard_rows) != len(FROZEN_SELECTED_SHARD_PATHS):
        errors.append("shard_metadata must contain exactly 32 ordered rows")
        shard_rows = []
    route_rows = package.get("route_ledger")
    if not isinstance(route_rows, list) or len(route_rows) != len(FROZEN_SELECTED_SHARD_PATHS):
        errors.append("route_ledger must contain exactly 32 ordered rows")
        route_rows = []

    sampling_schedule = package.get("sampling_schedule")
    if isinstance(sampling_schedule, Mapping) and len(shard_rows) == len(FROZEN_SELECTED_SHARD_PATHS):
        try:
            expected_schedule = build_sampling_schedule(shard_rows)
        except (TypeError, ValueError) as exc:
            errors.append(f"sampling schedule cannot be recomputed: {exc}")
        else:
            if sampling_schedule != expected_schedule:
                errors.append("sampling schedule does not equal the recomputed pre-row schedule")
    else:
        errors.append("sampling_schedule must be a mapping over the 32 exact shard rows")

    named_artifacts: dict[str, dict[str, Any]] = {}
    valid_object_rows: list[Mapping[str, Any]] = []
    for index, row in enumerate(shard_rows):
        if not isinstance(row, Mapping):
            errors.append(f"shard row {index} is not a mapping")
            continue
        valid_object_rows.append(row)
        expected_path = FROZEN_SELECTED_SHARD_PATHS[index]
        required_fields = {
            "path", "ordinal", "shard_count", "immutable_revision", "row_count", "row_group_count", "row_group_layout",
            "compressed_bytes", "uncompressed_bytes", "object_id", "object_id_kind",
            "object_size_bytes", "object_sha256", "object_sha256_status", "etag", "content_type", "content_encoding",
            "object_metadata_evidence_artifact", "object_metadata_evidence_sha256",
            "footer_trailer_evidence_artifact", "footer_trailer_sha256", "footer_metadata_length",
            "footer_evidence_artifact", "footer_sha256", "license_evidence_artifact", "license_bytes_sha256",
        }
        if not required_fields.issubset(row):
            errors.append(f"shard row {index} lacks metadata/footer fields")
        if row.get("path") != expected_path or row.get("ordinal") != build_selection_evidence()["selected_ordinals"][index]:
            errors.append(f"shard row {index} path/ordinal is not frozen")
        if row.get("shard_count") != VNGRS_SHARD_COUNT:
            errors.append(f"shard row {index} shard_count is not 284")
        if row.get("immutable_revision") != VNGRS_REVISION:
            errors.append(f"shard row {index} immutable revision is not frozen")
        for field in ("row_count", "row_group_count", "compressed_bytes", "uncompressed_bytes", "object_size_bytes"):
            if not isinstance(row.get(field), int) or isinstance(row[field], bool) or row[field] <= 0:
                errors.append(f"shard row {index}: {field} must be a positive integer")
        if not isinstance(row.get("row_group_layout"), list) or len(row.get("row_group_layout", [])) != row.get("row_group_count"):
            errors.append(f"shard row {index}: row_group_layout does not match row_group_count")
        else:
            group_rows = 0
            for group_index, group in enumerate(row["row_group_layout"]):
                if not isinstance(group, Mapping) or not isinstance(group.get("row_count"), int) or group["row_count"] <= 0:
                    errors.append(f"shard row {index}: row group {group_index} is incomplete")
                else:
                    group_rows += group["row_count"]
            if group_rows != row.get("row_count"):
                errors.append(f"shard row {index}: row-group counts do not sum to row_count")
        if row.get("object_id_kind") != "lfs_oid" or not isinstance(row.get("object_id"), str) or not row["object_id"]:
            errors.append(f"shard row {index}: immutable LFS object identity is missing")
        if row.get("object_sha256_status") not in {"unverified_footer_only", "lfs_oid_authoritative"}:
            errors.append(f"shard row {index}: full-object SHA status is invalid")
        if not isinstance(row.get("etag"), str) or not row["etag"]:
            errors.append(f"shard row {index}: ETag is missing")
        if row.get("content_type") not in {"application/octet-stream", "application/vnd.apache.parquet"}:
            errors.append(f"shard row {index}: content type is not accepted")
        if row.get("content_encoding") not in {"identity", None}:
            errors.append(f"shard row {index}: content encoding is not identity")
        if row.get("object_sha256") is not None and not re.fullmatch(r"[0-9a-f]{64}", str(row["object_sha256"])):
            errors.append(f"shard row {index}: object_sha256 is not lowercase SHA-256 or null")
        for field in ("object_metadata_evidence_artifact", "footer_evidence_artifact", "license_evidence_artifact"):
            if not _metadata_footer_artifact_name(row.get(field)):
                errors.append(f"shard row {index}: {field} is not a safe named artifact")
        for field in (
            "object_metadata_evidence_sha256", "footer_trailer_sha256", "footer_sha256", "license_bytes_sha256"
        ):
            if not re.fullmatch(r"[0-9a-f]{64}", str(row.get(field))):
                errors.append(f"shard row {index}: {field} is not lowercase SHA-256")
        for field, hash_field, kind in (
            ("object_metadata_evidence_artifact", "object_metadata_evidence_sha256", "object_metadata"),
            ("footer_trailer_evidence_artifact", "footer_trailer_sha256", "parquet_footer_trailer"),
            ("footer_evidence_artifact", "footer_sha256", "parquet_footer_bytes"),
            ("license_evidence_artifact", "license_bytes_sha256", "license_attribution_bytes"),
        ):
            name = row.get(field)
            if isinstance(name, str):
                if name in named_artifacts:
                    prior = named_artifacts[name]
                    if not (
                        kind == "license_attribution_bytes"
                        and prior.get("artifact_kind") == kind
                        and prior.get("sha256") == row.get(hash_field)
                    ):
                        if (
                            prior.get("artifact_kind") in {"object_metadata", "route_headers"}
                            and kind in {"object_metadata", "route_headers"}
                            and prior.get("sha256") == row.get(hash_field)
                        ):
                            prior["artifact_kind"] = "head_metadata_route"
                        else:
                            errors.append(f"duplicate evidence artifact name: {name}")
                else:
                    named_artifacts[name] = {"sha256": row.get(hash_field), "artifact_kind": kind, "row": index}

    valid_route_rows: list[Mapping[str, Any]] = []
    shard_by_path = {
        row.get("path"): row for row in shard_rows if isinstance(row, Mapping) and isinstance(row.get("path"), str)
    }
    for index, row in enumerate(route_rows):
        if not isinstance(row, Mapping):
            errors.append(f"route row {index} is not a mapping")
            continue
        valid_route_rows.append(row)
        expected_path = FROZEN_SELECTED_SHARD_PATHS[index]
        required_fields = {
            "path", "route_kind", "request_url", "immutable_revision", "split", "http_method",
            "range_header", "footer_range_header_template", "status", "final_url", "redirect_chain",
            "http_status", "content_length", "etag", "lfs_oid", "content_type", "content_encoding",
            "route_evidence_artifact", "route_evidence_sha256",
        }
        if not required_fields.issubset(row):
            errors.append(f"route row {index} lacks explicit route fields")
        if row.get("path") != expected_path:
            errors.append(f"route row {index}: path is not in frozen order")
        if row.get("route_kind") != METADATA_FOOTER_ROUTE_KIND:
            errors.append(f"route row {index}: route_kind must be {METADATA_FOOTER_ROUTE_KIND}")
        if row.get("request_url") != parquet_resolve_url(expected_path):
            errors.append(f"route row {index}: request_url is not the immutable direct-file route")
        if row.get("immutable_revision") != VNGRS_REVISION or row.get("split") != VNGRS_SPLIT:
            errors.append(f"route row {index}: revision/split is not frozen")
        if row.get("http_method") != "GET" or row.get("range_header") != METADATA_FOOTER_TRAILER_RANGE_HEADER:
            errors.append(f"route row {index}: method/range rule is not the frozen trailer stage")
        if row.get("footer_range_header_template") != METADATA_FOOTER_FOOTER_RANGE_TEMPLATE:
            errors.append(f"route row {index}: footer range template is not frozen")
        if row.get("status") != "verified":
            errors.append(f"route row {index}: route is not verified")
        if row.get("final_url") != row.get("request_url") or not _valid_redirect_chain(row.get("redirect_chain")):
            errors.append(f"route row {index}: final URL/redirect chain is not bound")
        if row.get("http_status") != 200:
            errors.append(f"route row {index}: HEAD status is not 200")
        if not isinstance(row.get("content_length"), int) or row["content_length"] <= 0:
            errors.append(f"route row {index}: object content length is invalid")
        if not isinstance(row.get("etag"), str) or not row["etag"]:
            errors.append(f"route row {index}: ETag is missing")
        if row.get("lfs_oid") != shard_by_path.get(row.get("path"), {}).get("object_id"):
            errors.append(f"route row {index}: LFS OID is not bound to the shard row")
        if row.get("content_type") not in {"application/octet-stream", "application/vnd.apache.parquet"}:
            errors.append(f"route row {index}: content type is not an accepted Parquet object type")
        if row.get("content_encoding") not in {"identity", None}:
            errors.append(f"route row {index}: content encoding is not identity")
        if "/rows" in str(row.get("request_url")) or "datasets-server" in str(row.get("request_url")):
            errors.append(f"route row {index}: Dataset Viewer /rows route is forbidden")
        name = row.get("route_evidence_artifact")
        if not _metadata_footer_artifact_name(name):
            errors.append(f"route row {index}: route evidence artifact is unsafe")
        elif name in named_artifacts:
            prior = named_artifacts[name]
            if (
                prior.get("artifact_kind") in {"object_metadata", "route_headers"}
                and prior.get("sha256") == row.get("route_evidence_sha256")
            ):
                prior["artifact_kind"] = "head_metadata_route"
            else:
                errors.append(f"duplicate evidence artifact name: {name}")
        elif isinstance(name, str):
            named_artifacts[name] = {"sha256": row.get("route_evidence_sha256"), "artifact_kind": "route_headers", "row": index}
        if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("route_evidence_sha256"))):
            errors.append(f"route row {index}: route evidence SHA is invalid")

    request_rows = package.get("request_ledger")
    if not isinstance(request_rows, list) or not request_rows:
        errors.append("request_ledger must contain bounded metadata/footer requests")
        request_rows = []
    request_groups: dict[str, list[Mapping[str, Any]]] = {}
    attempt_ids: set[str] = set()
    retries = 0
    total_response_bytes = 0
    max_response_bytes = 0
    route_by_path = {
        row.get("path"): row for row in valid_route_rows if isinstance(row.get("path"), str)
    }
    allowed_roles = {"head_metadata_route", "footer_trailer", "footer_bytes", "license_attribution"}
    for index, row in enumerate(request_rows):
        if not isinstance(row, Mapping):
            errors.append(f"request row {index} is not a mapping")
            continue
        required_fields = {
            "request_id", "attempt_id", "attempt_ordinal", "retry_ordinal", "evidence_role", "path",
            "request_url", "final_url", "redirect_chain", "route_kind", "immutable_revision", "split",
            "http_method", "range_header", "http_status", "response_content_length", "content_range",
            "etag", "lfs_oid", "content_type", "content_encoding", "response_transferred_bytes",
            "response_evidence_artifact", "response_sha256", "request_outcome", "failure_class",
            "retryable_error", "response_present",
        }
        if not required_fields.issubset(row):
            errors.append(f"request row {index} lacks request/response binding fields")
        request_id = row.get("request_id")
        attempt_id = row.get("attempt_id")
        if not isinstance(request_id, str) or not request_id:
            errors.append(f"request row {index}: request_id must be non-empty")
        else:
            request_groups.setdefault(request_id, []).append(row)
        if not isinstance(attempt_id, str) or not attempt_id or attempt_id in attempt_ids:
            errors.append(f"request row {index}: attempt_id must be unique")
        else:
            attempt_ids.add(attempt_id)
        for field in ("attempt_ordinal", "retry_ordinal"):
            if not isinstance(row.get(field), int) or isinstance(row[field], bool) or row[field] < 0:
                errors.append(f"request row {index}: {field} is invalid")
        if row.get("route_kind") != METADATA_FOOTER_ROUTE_KIND:
            errors.append(f"request row {index}: route_kind vocabulary is invalid")
        if "/rows" in str(row.get("request_url")) or "datasets-server" in str(row.get("request_url")):
            errors.append(f"request row {index}: /rows response route is outside this wave")
        role = row.get("evidence_role")
        if role not in allowed_roles:
            errors.append(f"request row {index}: forbidden or unknown evidence role")
        outcome = row.get("request_outcome")
        failure_class = row.get("failure_class")
        retryable_error = row.get("retryable_error")
        response_present = row.get("response_present")
        if outcome not in {"metadata_success", "retryable_failure"}:
            errors.append(f"request row {index}: metadata/footer outcome is invalid")
        if not isinstance(response_present, bool):
            errors.append(f"request row {index}: response_present must be boolean")
        if not _valid_redirect_chain(row.get("redirect_chain")):
            errors.append(f"request row {index}: redirect chain is not a bounded secret-safe representation")
        if outcome == "metadata_success":
            if failure_class != "none" or retryable_error is not None or response_present is not True:
                errors.append(f"request row {index}: successful attempt has retry/failure semantics")
            if role in {"footer_trailer", "footer_bytes"} and (
                row.get("http_method") != "GET" or row.get("http_status") != 206
            ):
                errors.append(f"request row {index}: footer request is not a bounded 206 range request")
            if role == "footer_trailer" and row.get("range_header") != METADATA_FOOTER_TRAILER_RANGE_HEADER:
                errors.append(f"request row {index}: trailer request does not use bytes=-8")
            if role == "footer_bytes" and _FOOTER_RANGE_RE.fullmatch(str(row.get("range_header"))) is None:
                errors.append(f"request row {index}: footer request does not use the frozen dynamic range")
            if role == "head_metadata_route" and (
                row.get("http_method") != "HEAD" or row.get("http_status") != 200 or row.get("range_header") is not None
            ):
                errors.append(f"request row {index}: shared metadata/route HEAD request is invalid")
            if role == "license_attribution" and (
                row.get("http_method") != "GET" or row.get("http_status") != 200 or row.get("request_url") != dataset_license_resolve_url()
            ):
                errors.append(f"request row {index}: license request is not the immutable README route")
        elif failure_class not in METADATA_FOOTER_RETRY_FAILURE_CLASSES:
            errors.append(f"request row {index}: retryable failure class is invalid")
        elif failure_class == "http_retryable":
            if row.get("http_status") not in METADATA_FOOTER_RETRYABLE_HTTP_STATUSES:
                errors.append(f"request row {index}: retryable HTTP status is not 429 or 503")
            expected_error = f"http_{row.get('http_status')}"
            if retryable_error != expected_error or response_present is not True:
                errors.append(f"request row {index}: retryable HTTP error/response semantics are invalid")
            if row.get("final_url") != row.get("request_url") or not _valid_redirect_chain(row.get("redirect_chain")):
                errors.append(f"request row {index}: retryable HTTP route binding is invalid")
        elif failure_class == "transport_no_response":
            if retryable_error not in {"transport_timeout", "transport_connection_error"}:
                errors.append(f"request row {index}: no-response transport error is invalid")
            if row.get("http_status") is not None or (
                row.get("final_url") not in {None, row.get("request_url")}
            ) or not _valid_redirect_chain(row.get("redirect_chain")):
                errors.append(f"request row {index}: no-response transport fields are invalid")
            if response_present is not False:
                errors.append(f"request row {index}: no-response transport attempt has a response")
        if outcome == "retryable_failure" and row.get("http_status") in {200, 206}:
            errors.append(f"request row {index}: successful HTTP status was relabelled as retryable")
        if row.get("immutable_revision") != VNGRS_REVISION or row.get("split") != VNGRS_SPLIT:
            errors.append(f"request row {index}: revision/split foreign key is invalid")
        if row.get("content_encoding") not in {"identity", None}:
            errors.append(f"request row {index}: content encoding is invalid")
        if role != "license_attribution":
            route = route_by_path.get(row.get("path"))
            shard = shard_by_path.get(row.get("path"), {})
            if not isinstance(route, Mapping):
                errors.append(f"request row {index}: path is not bound to a route-ledger row")
            else:
                for field in ("request_url", "route_kind", "immutable_revision", "split"):
                    if row.get(field) != route.get(field):
                        errors.append(f"request row {index}: {field} is not bound to the route ledger")
                if response_present is True and row.get("final_url") != route.get("final_url"):
                    errors.append(f"request row {index}: final_url is not bound to the route ledger")
                if outcome == "metadata_success":
                    for field in ("etag", "lfs_oid", "content_type", "content_encoding"):
                        if row.get(field) != route.get(field) or row.get(field) != shard.get(field if field != "lfs_oid" else "object_id"):
                            errors.append(f"request row {index}: {field} is not bound to object/route headers")
        response_bytes = row.get("response_transferred_bytes")
        if not isinstance(response_bytes, int) or response_bytes < 0:
            errors.append(f"request row {index}: response bytes are invalid")
        else:
            total_response_bytes += response_bytes
            max_response_bytes = max(max_response_bytes, response_bytes)
            if response_bytes > METADATA_FOOTER_MAX_SINGLE_RESPONSE_BYTES:
                errors.append(f"request row {index}: single-response byte bound exceeded")
            if role in {"footer_trailer", "footer_bytes"} and response_bytes > METADATA_FOOTER_MAX_RANGE_BYTES:
                errors.append(f"request row {index}: footer range byte bound exceeded")
        if response_present is True:
            name = row.get("response_evidence_artifact")
            if not _metadata_footer_artifact_name(name):
                errors.append(f"request row {index}: response evidence artifact is unsafe")
            elif outcome == "retryable_failure" and not _METADATA_FOOTER_RETRY_ARTIFACT_RE.fullmatch(name):
                errors.append(f"request row {index}: retry response artifact must use evidence/retry/")
            elif isinstance(name, str) and name not in named_artifacts:
                named_artifacts[name] = {
                    "sha256": row.get("response_sha256"),
                    "artifact_kind": "retry_response" if outcome == "retryable_failure" else role,
                    "row": index,
                }
            elif isinstance(name, str) and name in named_artifacts:
                prior = named_artifacts[name]
                if outcome == "retryable_failure":
                    errors.append(f"request row {index}: retry response artifact is reused ambiguously")
                elif prior.get("sha256") != row.get("response_sha256"):
                    errors.append(f"request row {index}: response artifact hash binding conflicts")
                elif role == "head_metadata_route" and prior.get("artifact_kind") in {"object_metadata", "route_headers"}:
                    prior["artifact_kind"] = "head_metadata_route"
            if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("response_sha256"))):
                errors.append(f"request row {index}: response SHA is invalid")
            if not isinstance(row.get("response_content_length"), int) or row["response_content_length"] < 0:
                errors.append(f"request row {index}: response content length is invalid")
        else:
            if row.get("response_evidence_artifact") is not None or row.get("response_sha256") is not None:
                errors.append(f"request row {index}: no-response attempt has response artifact/hash")
            if response_bytes != 0 or row.get("response_content_length") is not None:
                errors.append(f"request row {index}: no-response attempt has response bytes")

    for request_id, group in request_groups.items():
        ordered = sorted(group, key=lambda row: row.get("attempt_ordinal", -1))
        attempt_ordinals = [row.get("attempt_ordinal") for row in ordered]
        retry_ordinals = [row.get("retry_ordinal") for row in ordered]
        expected_ordinals = list(range(len(ordered)))
        if attempt_ordinals != expected_ordinals or retry_ordinals != expected_ordinals:
            errors.append(f"request chain {request_id}: ordinals are not contiguous zero-based attempts/retries")
        if len({row.get("evidence_role") for row in ordered}) != 1:
            errors.append(f"request chain {request_id}: evidence role changes across attempts")
        stable_fields = ("path", "request_url", "route_kind", "http_method", "range_header")
        for field in stable_fields:
            if len({repr(row.get(field)) for row in ordered}) != 1:
                errors.append(f"request chain {request_id}: {field} changes across attempts")
        successful = [row for row in ordered if row.get("request_outcome") == "metadata_success"]
        if len(successful) != 1 or ordered[-1] is not successful[0]:
            errors.append(f"request chain {request_id}: exactly one successful terminal attempt is required")
        for row in ordered[:-1]:
            if row.get("request_outcome") != "retryable_failure":
                errors.append(f"request chain {request_id}: non-terminal attempt is not retryable")
        for row in ordered:
            if row.get("request_outcome") == "retryable_failure" and row.get("retryable_error") not in METADATA_FOOTER_RETRYABLE_ERROR_CODES:
                errors.append(f"request chain {request_id}: retryable error vocabulary is invalid")
    retries = sum(max(0, len(group) - 1) for group in request_groups.values())

    if len(request_rows) > METADATA_FOOTER_MAX_HTTP_ATTEMPTS:
        errors.append("metadata/footer HTTP attempt bound exceeded")
    if retries > METADATA_FOOTER_MAX_RETRIES:
        errors.append("metadata/footer retry bound exceeded")
    if total_response_bytes > METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES:
        errors.append("metadata/footer total response byte bound exceeded")

    artifact_rows = package.get("artifact_manifest")
    if not isinstance(artifact_rows, list):
        errors.append("artifact_manifest must be a list")
        artifact_rows = []
    manifest_names: set[str] = set()
    for index, row in enumerate(artifact_rows):
        if not isinstance(row, Mapping):
            errors.append(f"artifact manifest row {index} is not a mapping")
            continue
        name = row.get("relative_path")
        kind = row.get("artifact_kind")
        if not _metadata_footer_artifact_name(name) or not isinstance(kind, str):
            errors.append(f"artifact manifest row {index}: unsafe path or missing kind")
        if name in manifest_names:
            errors.append(f"artifact manifest has duplicate path: {name}")
        manifest_names.add(name)
        if kind in METADATA_FOOTER_FORBIDDEN_ARTIFACT_KINDS or kind not in METADATA_FOOTER_ARTIFACT_KINDS:
            errors.append(f"artifact manifest row {index}: corpus/row or unknown artifact kind")
        if row.get("contains_corpus_rows") is not False:
            errors.append(f"artifact manifest row {index}: contains_corpus_rows must be false")
        if not isinstance(row.get("bytes"), int) or row["bytes"] < 0:
            errors.append(f"artifact manifest row {index}: byte count is invalid")
        if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256"))):
            errors.append(f"artifact manifest row {index}: SHA-256 is invalid")
    expected_names = set(named_artifacts)
    if manifest_names != expected_names:
        errors.append("artifact manifest names do not exactly match all declared evidence bindings")
    if artifact_payloads is None:
        errors.append("actual evidence artifact payload bytes are required")
    else:
        if set(artifact_payloads) != expected_names:
            errors.append("actual evidence artifact payload names do not exactly match bindings")
        manifest_by_name = {row.get("relative_path"): row for row in artifact_rows if isinstance(row, Mapping)}
        for name, binding in named_artifacts.items():
            payload = artifact_payloads.get(name)
            if not isinstance(payload, bytes):
                errors.append(f"evidence artifact payload is missing or not bytes: {name}")
                continue
            digest = hashlib.sha256(payload).hexdigest()
            if digest != binding.get("sha256"):
                errors.append(f"evidence artifact payload hash mismatch: {name}")
            manifest_row = manifest_by_name.get(name)
            if not isinstance(manifest_row, Mapping) or manifest_row.get("bytes") != len(payload) or manifest_row.get("sha256") != digest:
                errors.append(f"evidence artifact manifest does not match payload bytes: {name}")
            elif manifest_row.get("artifact_kind") != binding.get("artifact_kind"):
                errors.append(f"evidence artifact kind does not match its binding: {name}")
            if binding.get("artifact_kind") in {"object_metadata", "head_metadata_route"}:
                try:
                    metadata_payload = json.loads(payload)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    errors.append(f"object metadata evidence is not canonical JSON: {name}")
                else:
                    shard_index = binding.get("row")
                    shard = shard_rows[shard_index] if isinstance(shard_index, int) and shard_index < len(shard_rows) else {}
                    if not isinstance(metadata_payload, Mapping) or any(
                        metadata_payload.get(field) != shard.get(field)
                        for field in ("path", "immutable_revision", "object_id", "object_size_bytes")
                    ):
                        errors.append(f"object metadata evidence does not bind source identity: {name}")
            if binding.get("artifact_kind") == "parquet_footer_bytes" and not payload.endswith(b"PAR1"):
                errors.append(f"footer evidence is not a complete Parquet footer range: {name}")
            if binding.get("artifact_kind") == "parquet_footer_trailer":
                try:
                    parse_parquet_trailer(payload)
                except ValueError as exc:
                    errors.append(f"footer trailer evidence is invalid: {name}: {exc}")
    parsed_footer_rows: dict[str, dict[str, Any]] = {}
    if artifact_payloads is not None:
        for index, row in enumerate(shard_rows):
            if not isinstance(row, Mapping):
                continue
            footer_name = row.get("footer_evidence_artifact")
            trailer_name = row.get("footer_trailer_evidence_artifact")
            footer_payload = artifact_payloads.get(footer_name) if isinstance(footer_name, str) else None
            trailer_payload = artifact_payloads.get(trailer_name) if isinstance(trailer_name, str) else None
            if not isinstance(footer_payload, bytes) or not isinstance(trailer_payload, bytes):
                continue
            try:
                parsed_footer = parse_parquet_footer(footer_payload)
                parsed_trailer = parse_parquet_trailer(trailer_payload)
            except ValueError as exc:
                errors.append(f"shard row {index}: footer parsing failed: {exc}")
                continue
            if parsed_trailer["metadata_length"] != parsed_footer["metadata_length"]:
                errors.append(f"shard row {index}: trailer and footer metadata lengths disagree")
            for field in (
                "row_count", "row_group_count", "compressed_bytes", "uncompressed_bytes", "row_group_layout"
            ):
                if row.get(field) != parsed_footer.get(field):
                    errors.append(f"shard row {index}: {field} is not recomputed from parsed footer metadata")
            if row.get("footer_metadata_length") != parsed_footer["metadata_length"]:
                errors.append(f"shard row {index}: footer_metadata_length is not parsed from the footer")
            if row.get("footer_trailer_sha256") != hashlib.sha256(trailer_payload).hexdigest():
                errors.append(f"shard row {index}: footer trailer SHA is not bound to trailer bytes")
            if row.get("footer_sha256") != hashlib.sha256(footer_payload).hexdigest():
                errors.append(f"shard row {index}: footer SHA is not bound to complete footer bytes")
            parsed_footer_rows[row.get("path")] = parsed_footer

        if len(parsed_footer_rows) == len(FROZEN_SELECTED_SHARD_PATHS):
            parsed_rows_for_schedule = []
            for row in shard_rows:
                parsed = parsed_footer_rows.get(row.get("path"))
                parsed_rows_for_schedule.append({**row, **parsed})
            try:
                parsed_schedule = build_sampling_schedule(parsed_rows_for_schedule)
            except (TypeError, ValueError) as exc:
                errors.append(f"sampling schedule cannot use parsed footer values: {exc}")
            else:
                if package.get("sampling_schedule") != parsed_schedule:
                    errors.append("sampling schedule is not recomputed from parsed footer row counts")
        else:
            parsed_schedule = None
    else:
        parsed_schedule = None

    if artifact_payloads is not None:
        for index, row in enumerate(request_rows):
            if not isinstance(row, Mapping):
                continue
            name = row.get("response_evidence_artifact")
            payload = artifact_payloads.get(name) if isinstance(name, str) else None
            if not isinstance(payload, bytes):
                continue
            if row.get("response_transferred_bytes") != len(payload):
                errors.append(f"request row {index}: transferred bytes do not equal response artifact length")
            if row.get("response_content_length") != len(payload):
                errors.append(f"request row {index}: response content length does not equal payload length")
            if row.get("response_sha256") != hashlib.sha256(payload).hexdigest():
                errors.append(f"request row {index}: response SHA does not match actual payload")
            if row.get("request_outcome") != "metadata_success":
                continue
            role = row.get("evidence_role")
            path = row.get("path")
            shard = shard_by_path.get(path, {})
            if role == "head_metadata_route":
                try:
                    header_payload = json.loads(payload)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    errors.append(f"request row {index}: HEAD evidence is not JSON")
                else:
                    if canonical_json_bytes(header_payload) != payload or not isinstance(header_payload, Mapping):
                        errors.append(f"request row {index}: HEAD evidence is not canonical JSON")
                    else:
                        expected_header = {
                            "request_url": parquet_resolve_url(path),
                            "final_url": parquet_resolve_url(path),
                            "redirect_chain": next(
                                (
                                    route.get("redirect_chain")
                                    for route in route_rows
                                    if isinstance(route, Mapping) and route.get("path") == path
                                ),
                                [],
                            ),
                            "http_status": 200,
                            "content_length": shard.get("object_size_bytes"),
                            "etag": shard.get("etag"),
                            "lfs_oid": shard.get("object_id"),
                            "content_type": shard.get("content_type"),
                            "content_encoding": shard.get("content_encoding"),
                        }
                        if any(header_payload.get(field) != value for field, value in expected_header.items()):
                            errors.append(f"request row {index}: HEAD evidence does not bind object/route headers")
                        for field in (
                            "final_url", "redirect_chain", "http_status", "etag", "lfs_oid",
                            "content_type", "content_encoding",
                        ):
                            if row.get(field) != header_payload.get(field):
                                errors.append(f"request row {index}: HEAD {field} is not bound to the response artifact")
                        for route in route_rows:
                            if isinstance(route, Mapping) and route.get("path") == path:
                                for field in expected_header:
                                    route_field = "content_length" if field == "content_length" else field
                                    if route.get(route_field) != header_payload.get(field):
                                        errors.append(f"route row for {path}: HEAD field {field} is not bound")
            elif role == "footer_trailer":
                try:
                    trailer = parse_parquet_trailer(payload)
                except ValueError as exc:
                    errors.append(f"request row {index}: invalid footer trailer: {exc}")
                else:
                    expected_range = f"bytes={shard.get('object_size_bytes', 0) - 8}-{shard.get('object_size_bytes', 0) - 1}/{shard.get('object_size_bytes')}"
                    if row.get("content_range") != expected_range:
                        errors.append(f"request row {index}: trailer Content-Range is not reconciled")
                    if row.get("range_header") != METADATA_FOOTER_TRAILER_RANGE_HEADER:
                        errors.append(f"request row {index}: trailer Range header is not frozen")
                    if row.get("response_evidence_artifact") != shard.get("footer_trailer_evidence_artifact"):
                        errors.append(f"request row {index}: trailer artifact is not bound to shard ledger")
            elif role == "footer_bytes":
                try:
                    parsed = parse_parquet_footer(payload)
                except ValueError as exc:
                    errors.append(f"request row {index}: invalid complete footer: {exc}")
                else:
                    start_match = _FOOTER_RANGE_RE.fullmatch(str(row.get("range_header")))
                    expected_start = shard.get("object_size_bytes", 0) - len(payload)
                    if start_match is None or int(start_match.group("start")) != expected_start:
                        errors.append(f"request row {index}: footer Range start is not exact")
                    expected_range = f"bytes={expected_start}-{shard.get('object_size_bytes', 0) - 1}/{shard.get('object_size_bytes')}"
                    if row.get("content_range") != expected_range:
                        errors.append(f"request row {index}: footer Content-Range is not reconciled")
                    if row.get("response_evidence_artifact") != shard.get("footer_evidence_artifact"):
                        errors.append(f"request row {index}: footer artifact is not bound to shard ledger")
                    if parsed != parsed_footer_rows.get(path):
                        errors.append(f"request row {index}: parsed footer does not match shard ledger parse")
    if artifact_manifest_payload is not None:
        expected_manifest_payload = serialize_metadata_footer_artifact_manifest(artifact_rows)
        if artifact_manifest_payload != expected_manifest_payload:
            errors.append("artifact manifest payload does not equal canonical serialization of supplied rows")
        computed_manifest_sha = hashlib.sha256(expected_manifest_payload).hexdigest()
        if package.get("artifact_manifest_sha256") != computed_manifest_sha:
            errors.append("artifact_manifest_sha256 does not match canonical manifest bytes")
    else:
        errors.append("artifact manifest bytes are required for final byte binding")

    projection = package.get("feasibility_projection")
    if not isinstance(projection, Mapping):
        errors.append("feasibility_projection is required")
    else:
        if projection.get("route_kind") != METADATA_FOOTER_ROUTE_KIND:
            errors.append("feasibility projection route_kind is invalid")
        if projection.get("metadata_footer_only") is not True:
            errors.append("feasibility projection is not metadata/footer-only")
        if projection.get("corpus_rows_retrieved") != 0 or projection.get("sample_manifest_created") is not False:
            errors.append("metadata/footer wave must retrieve zero rows and create no sample manifest")
        if projection.get("projected_request_count") != len(request_rows):
            errors.append("projected request count is not reconciled")
        if projection.get("projected_total_response_bytes") != total_response_bytes:
            errors.append("projected response bytes are not reconciled")
        if projection.get("projected_max_response_bytes") != max_response_bytes:
            errors.append("projected maximum response bytes are not reconciled")
        expected_output_file_count = len(artifact_rows) + len(METADATA_FOOTER_OUTPUT_PATHS)
        if projection.get("projected_evidence_artifact_count") != len(artifact_rows):
            errors.append("projected evidence artifact count is not reconciled")
        if projection.get("projected_regular_file_count") != expected_output_file_count:
            errors.append("projected regular-file count is not reconciled")
        if projection.get("projected_new_inode_count") != expected_output_file_count:
            errors.append("projected new-inode count is not reconciled")
        if expected_output_file_count > METADATA_FOOTER_MAX_OUTPUT_FILES:
            errors.append("projected output file count exceeds the frozen bound")
        if projection.get("sampling_schedule_sha256") != (
            sampling_schedule.get("schedule_sha256") if isinstance(sampling_schedule, Mapping) else None
        ):
            errors.append("feasibility projection is not bound to the pre-row schedule")
        if projection.get("sampling_schedule_status") not in {"computed_pre_row_retrieval", "deferred_until_separate_row_wave"}:
            errors.append("sampling schedule status is invalid for metadata/footer wave")

    audit = package.get("metadata_footer_audit")
    if not isinstance(audit, Mapping):
        errors.append("metadata_footer_audit is required")
    else:
        if audit.get("final_path") != "metadata_footer_audit.json":
            errors.append("metadata/footer final audit path is invalid")
        if audit.get("manifest_path") != "evidence_artifact_manifest.jsonl":
            errors.append("metadata/footer artifact manifest path is invalid")
        if audit.get("scratch_root") != METADATA_FOOTER_SCRATCH_ROOT:
            errors.append("metadata/footer audit scratch root is invalid")
        if audit.get("self_reference") is not False:
            errors.append("metadata/footer audit must be self-reference-free")
        if "metadata_footer_audit.json" in audit.get("artifact_paths", []):
            errors.append("metadata/footer audit self-references its own path")
        if audit.get("route_kind") != METADATA_FOOTER_ROUTE_KIND:
            errors.append("metadata/footer audit route_kind is invalid")
        if audit.get("corpus_rows_retrieved") != 0:
            errors.append("metadata/footer audit claims corpus rows were retrieved")
        expected_artifact_paths = [row.get("relative_path") for row in artifact_rows if isinstance(row, Mapping)]
        if audit.get("contract_sha256") != METADATA_FOOTER_CONTRACT_SHA256:
            errors.append("metadata/footer audit is not bound to the corrected 151an contract SHA")
        if audit.get("manifest_sha256") != package.get("artifact_manifest_sha256"):
            errors.append("metadata/footer audit manifest SHA is not bound")
        if audit.get("artifact_paths") != expected_artifact_paths:
            errors.append("metadata/footer audit artifact paths are not bound to the manifest")
        if audit.get("artifact_count") != len(expected_artifact_paths):
            errors.append("metadata/footer audit artifact count is not reconciled")
        if audit.get("artifact_total_bytes") != sum(
            row.get("bytes", 0) for row in artifact_rows if isinstance(row, Mapping)
        ):
            errors.append("metadata/footer audit artifact bytes are not reconciled")
        if audit.get("request_count") != len(request_rows) or audit.get("retry_count") != retries:
            errors.append("metadata/footer audit request/retry totals are not reconciled")
        redirect_hops = sum(
            len(row.get("redirect_chain", []))
            for row in request_rows
            if isinstance(row, Mapping) and isinstance(row.get("redirect_chain"), list)
        )
        http_hops = len(request_rows) + redirect_hops
        if audit.get("logical_request_attempt_count") != len(request_rows):
            errors.append("metadata/footer audit logical request count is not reconciled")
        if audit.get("redirect_hop_count") != redirect_hops or audit.get("http_hop_count") != http_hops:
            errors.append("metadata/footer audit HTTP-hop totals are not reconciled")
        if audit.get("max_logical_request_attempts") != 121 or audit.get("max_http_hops") != 242:
            errors.append("metadata/footer audit redirect bounds are not frozen")
        if http_hops > 242 or len(request_rows) > 121:
            errors.append("metadata/footer audit exceeds the frozen logical-request/HTTP-hop bounds")
        if audit.get("total_response_bytes") != total_response_bytes or audit.get("max_response_bytes") != max_response_bytes:
            errors.append("metadata/footer audit response byte totals are not reconciled")
        if audit.get("output_file_count") != len(artifact_rows) + len(METADATA_FOOTER_OUTPUT_PATHS):
            errors.append("metadata/footer audit output file count is not reconciled")
        if audit.get("new_inode_count") != audit.get("output_file_count"):
            errors.append("metadata/footer audit inode count is not reconciled")
        if audit.get("write_order") != list(METADATA_FOOTER_OUTPUT_PATHS):
            errors.append("metadata/footer audit write order is not frozen")
    if metadata_footer_audit_payload is None:
        errors.append("actual metadata/footer final-audit payload bytes are required")
    else:
        if not isinstance(audit, Mapping) or canonical_json_bytes(audit) != metadata_footer_audit_payload:
            errors.append("metadata/footer final-audit bytes do not equal canonical audit mapping")
        audit_sha = hashlib.sha256(metadata_footer_audit_payload).hexdigest()
        if package.get("metadata_footer_audit_sha256") != audit_sha:
            errors.append("metadata_footer_audit_sha256 does not match canonical audit bytes")

    return {
        "selected_shard_count": len(valid_object_rows),
        "route_row_count": len(valid_route_rows),
        "request_count": len(request_rows),
        "retry_count": retries,
        "total_response_bytes": total_response_bytes,
        "max_response_bytes": max_response_bytes,
        "bound": {
            "max_http_attempts": METADATA_FOOTER_MAX_HTTP_ATTEMPTS,
            "max_retries": METADATA_FOOTER_MAX_RETRIES,
            "max_total_response_bytes": METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES,
            "max_single_response_bytes": METADATA_FOOTER_MAX_SINGLE_RESPONSE_BYTES,
            "max_wall_clock_seconds": METADATA_FOOTER_MAX_WALL_CLOCK_SECONDS,
            "max_output_files": METADATA_FOOTER_MAX_OUTPUT_FILES,
            "max_new_inodes": METADATA_FOOTER_MAX_NEW_INODES,
        },
        "errors": errors,
        "complete": not errors,
    }


def metadata_coverage(rows: Iterable[ShardMetadata]) -> dict[str, Any]:
    """Summarize registry coverage without turning absent data into a zero."""

    rows = tuple(rows)
    fields = (
        "path",
        "ordinal",
        "shard_count",
        "row_count",
        "compressed_bytes",
        "object_id",
        "sha256",
        "footer_sha256",
        "license_bytes_sha256",
    )
    coverage = {
        field: {
            "rows": len(rows),
            "observed": sum(getattr(row, field) is not None for row in rows),
            "status": "verified" if all(getattr(row, field) is not None for row in rows) else "unresolved",
        }
        for field in fields
    }
    return {"row_count": len(rows), "field_coverage": coverage}
