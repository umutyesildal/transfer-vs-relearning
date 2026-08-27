"""Close the exact vngrs full-object registry from accepted immutable HEAD evidence."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .materialization import SourceObject, immutable_resolve_url, normalized_lfs_sha256
from .metadata import FROZEN_SELECTED_SHARD_PATHS, VNGRS_REVISION, canonical_json_sha256


EXPECTED_SELECTED_BYTES = 9_468_474_036


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

