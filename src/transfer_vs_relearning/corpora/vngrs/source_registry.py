"""Close the exact vngrs full-object registry from accepted immutable HEAD evidence."""

from __future__ import annotations

import hashlib
import base64
import gzip
import json
from typing import Any

from .materialization import SourceObject, immutable_resolve_url, normalized_lfs_sha256
from .metadata import FROZEN_SELECTED_SHARD_PATHS, VNGRS_REVISION, canonical_json_sha256


EXPECTED_SELECTED_BYTES = 9_468_474_036


def _single_marker_block(lines: list[str], start: str, end: str) -> list[str]:
    starts = [index for index, line in enumerate(lines) if line == start]
    ends = [index for index, line in enumerate(lines) if line == end]
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        raise ValueError(f"transport marker closure failed: {start}/{end}")
    return lines[starts[0] + 1 : ends[0]]


def parse_discovery_transport(
    transcript: str,
    *,
    expected_ledger_sha256: str,
) -> dict[str, Any]:
    """Parse one bounded SSH transcript and derive the registry without persisting raw bytes."""

    lines = [line.rstrip("\r") for line in transcript.splitlines()]
    body = _single_marker_block(lines, "DISCOVERY_CAPTURE_V1_BEGIN", "DISCOVERY_CAPTURE_V1_END")

    scalar: dict[str, str] = {}
    for line in body:
        if "=" in line and line.split("=", 1)[0] in {
            "LEDGER_BYTES",
            "LEDGER_SHA256",
            "RESOLVED_PARENT",
            "PROPOSED_ROOT_ABSENT",
        }:
            key, value = line.split("=", 1)
            if key in scalar:
                raise ValueError(f"duplicate transport scalar: {key}")
            scalar[key] = value
    if scalar.get("LEDGER_SHA256") != expected_ledger_sha256:
        raise ValueError("transport ledger SHA-256 mismatch")
    if scalar.get("RESOLVED_PARENT") != "/vol/tmp2/yesildau":
        raise ValueError("transport parent path drift")
    if scalar.get("PROPOSED_ROOT_ABSENT") != "1":
        raise ValueError("proposed D0 root is not absent")

    byte_rows = _single_marker_block(body, "DF_BYTES_BEGIN", "DF_BYTES_END")
    inode_rows = _single_marker_block(body, "DF_INODES_POSIX_BEGIN", "DF_INODES_POSIX_END")
    payload_rows = _single_marker_block(
        body, "LEDGER_GZIP_BASE64_BEGIN", "LEDGER_GZIP_BASE64_END"
    )
    if len(byte_rows) != 2 or len(inode_rows) != 2 or len(payload_rows) != 1:
        raise ValueError("transport table or payload row count drift")
    byte_values = byte_rows[1].split()
    inode_values = inode_rows[1].split()
    if len(byte_values) != 6 or len(inode_values) != 6:
        raise ValueError("transport filesystem column count drift")
    if byte_values[0] != inode_values[0] or byte_values[5] != inode_values[5]:
        raise ValueError("byte/inode filesystem identity mismatch")

    try:
        compressed = base64.b64decode(payload_rows[0], validate=True)
        payload = gzip.decompress(compressed)
        declared_bytes = int(scalar["LEDGER_BYTES"])
    except (KeyError, ValueError, OSError, EOFError) as exc:
        raise ValueError("transport ledger payload decode failed") from exc
    if len(payload) != declared_bytes:
        raise ValueError("transport ledger byte count mismatch")
    registry = build_source_registry_from_metadata_ledger(
        payload, expected_ledger_sha256=expected_ledger_sha256
    )
    return {
        "ledger_bytes": declared_bytes,
        "ledger_sha256": expected_ledger_sha256,
        "resolved_parent": scalar["RESOLVED_PARENT"],
        "proposed_root_absent": True,
        "byte_capacity": {
            "filesystem": byte_values[0],
            "total_bytes": int(byte_values[1]),
            "used_bytes": int(byte_values[2]),
            "available_bytes": int(byte_values[3]),
            "capacity_percent": int(byte_values[4].rstrip("%")),
            "mount": byte_values[5],
        },
        "inode_capacity": {
            "filesystem": inode_values[0],
            "total_inodes": int(inode_values[1]),
            "used_inodes": int(inode_values[2]),
            "available_inodes": int(inode_values[3]),
            "capacity_percent": int(inode_values[4].rstrip("%")),
            "mount": inode_values[5],
        },
        "source_registry": registry,
        "raw_ledger_payload_persisted": False,
    }


def build_source_registry_from_metadata_ledger(
    payload: bytes,
    *,
    expected_ledger_sha256: str,
    expected_total_bytes: int = EXPECTED_SELECTED_BYTES,
) -> dict[str, Any]:
    """Derive expected full-object SHA-256 from exact Git-LFS OIDs without corpus reads."""

    if hashlib.sha256(payload).hexdigest() != expected_ledger_sha256:
        raise ValueError("metadata ledger SHA-256 mismatch")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(payload.decode("utf-8").splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"metadata ledger line {line_number} is invalid JSON") from exc
        if not isinstance(row, dict):
            raise ValueError(f"metadata ledger line {line_number} is not an object")
        rows.append(row)
    if [row.get("path") for row in rows] != list(FROZEN_SELECTED_SHARD_PATHS):
        raise ValueError("metadata ledger does not match the frozen 32-shard order")

    objects: list[SourceObject] = []
    registry_rows: list[dict[str, Any]] = []
    for ordinal, row in enumerate(rows):
        path = str(row["path"])
        if row.get("immutable_revision") != VNGRS_REVISION:
            raise ValueError(f"{path}: immutable revision drift")
        if row.get("object_id_kind") != "lfs_oid":
            raise ValueError(f"{path}: object identity is not a Git-LFS OID")
        object_id = row.get("object_id")
        if not isinstance(object_id, str):
            raise ValueError(f"{path}: object LFS identity is absent")
        object_sha256 = normalized_lfs_sha256(object_id)
        size = row.get("object_size_bytes")
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ValueError(f"{path}: exact object size is absent")
        if row.get("object_sha256") not in (None, object_sha256):
            raise ValueError(f"{path}: recorded object SHA conflicts with the LFS OID")
        source = SourceObject(
            path=path,
            revision=VNGRS_REVISION,
            size_bytes=size,
            sha256=object_sha256,
            lfs_oid=object_id,
            url=immutable_resolve_url(path),
        )
        objects.append(source)
        registry_rows.append(
            {
                "ordinal": ordinal,
                "path": source.path,
                "revision": source.revision,
                "size_bytes": source.size_bytes,
                "sha256": source.sha256,
                "lfs_oid": source.lfs_oid,
                "url": source.url,
                "identity_source": "accepted_immutable_head_lfs_oid",
            }
        )
    observed_total = sum(item.size_bytes for item in objects)
    if observed_total != expected_total_bytes:
        raise ValueError(
            f"selected object bytes drift: {observed_total} != {expected_total_bytes}"
        )
    return {
        "schema_version": 1,
        "status": "REGISTRY_CLOSED_FROM_ACCEPTED_LFS_IDENTITIES",
        "revision": VNGRS_REVISION,
        "object_count": len(objects),
        "total_bytes": observed_total,
        "metadata_ledger_sha256": expected_ledger_sha256,
        "objects": registry_rows,
        "registry_sha256": canonical_json_sha256(registry_rows),
        "corpus_rows_read": 0,
        "full_objects_downloaded": 0,
    }
