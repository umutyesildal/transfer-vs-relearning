"""Load the accepted HU footer ledger without promoting object IDs to byte SHA-256."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

from .materialization import SourceObjectV3, immutable_resolve_url, normalized_object_id
from .metadata import FROZEN_SELECTED_SHARD_PATHS, VNGRS_REVISION


LEDGER_SHA256 = "6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _evidence_path(root: Path, value: object) -> Path:
    if not isinstance(value, str):
        raise ValueError("accepted evidence artifact path is missing")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError("accepted evidence artifact path is unsafe")
    path = root.joinpath(*relative.parts)
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"accepted evidence artifact is absent: {value}")
    return path


def load_source_objects_v3(root: str | Path) -> tuple[SourceObjectV3, ...]:
    """Verify each accepted footer/trailer artifact and build the V3 transport registry."""

    root_path = Path(root)
    ledger = root_path / "shard_metadata_ledger.jsonl"
    if not ledger.is_file() or ledger.is_symlink() or _sha256(ledger) != LEDGER_SHA256:
        raise ValueError("accepted shard metadata ledger drift")
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 32 or tuple(row.get("path") for row in rows) != FROZEN_SELECTED_SHARD_PATHS:
        raise ValueError("accepted selected-shard order drift")

    result: list[SourceObjectV3] = []
    for index, row in enumerate(rows):
        path = str(row["path"])
        if row.get("immutable_revision") != VNGRS_REVISION:
            raise ValueError(f"{path}: accepted immutable revision drift")
        if row.get("object_sha256") is not None or row.get("object_sha256_status") != "unverified_footer_only":
            raise ValueError(f"{path}: ledger no longer has unverified full-byte SHA semantics")
        object_id = normalized_object_id(str(row.get("object_id", "")))
        if row.get("object_id_kind") != "lfs_oid":
            raise ValueError(f"{path}: accepted object-id kind drift")
        size = row.get("object_size_bytes")
        metadata_length = row.get("footer_metadata_length")
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ValueError(f"{path}: invalid accepted object size")
        if not isinstance(metadata_length, int) or isinstance(metadata_length, bool):
            raise ValueError(f"{path}: invalid accepted footer length")
        footer = _evidence_path(root_path, row.get("footer_evidence_artifact"))
        trailer = _evidence_path(root_path, row.get("footer_trailer_evidence_artifact"))
        if footer.stat().st_size != metadata_length + 8:
            raise ValueError(f"{path}: accepted footer artifact size drift")
        if _sha256(footer) != row.get("footer_sha256"):
            raise ValueError(f"{path}: accepted footer artifact hash drift")
        if trailer.stat().st_size != 8 or _sha256(trailer) != row.get("footer_trailer_sha256"):
            raise ValueError(f"{path}: accepted trailer artifact drift")
        if footer.read_bytes()[-8:] != trailer.read_bytes():
            raise ValueError(f"{path}: accepted footer/trailer bytes do not reconcile")
        result.append(
            SourceObjectV3(
                path=path,
                revision=VNGRS_REVISION,
                size_bytes=size,
                object_id=object_id,
                object_id_kind="lfs_oid",
                url=immutable_resolve_url(path, VNGRS_REVISION),
                footer_bytes=metadata_length + 8,
                footer_sha256=str(row["footer_sha256"]),
                trailer_sha256=str(row["footer_trailer_sha256"]),
            )
        )
    if sum(row.size_bytes for row in result) != 9_502_315_428:
        raise ValueError("accepted selected-object byte total drift")
    return tuple(result)
