import hashlib
import json

import pytest

from transfer_vs_relearning.corpora.vngrs.metadata import FROZEN_SELECTED_SHARD_PATHS, VNGRS_REVISION
from transfer_vs_relearning.corpora.vngrs.source_registry import build_source_registry_from_metadata_ledger


def ledger(*, total_bytes: int = 9_468_474_036) -> tuple[bytes, str]:
    base, remainder = divmod(total_bytes, 32)
    rows = []
    for index, path in enumerate(FROZEN_SELECTED_SHARD_PATHS):
        digest = hashlib.sha256(path.encode()).hexdigest()
        rows.append(
            {
                "path": path,
                "immutable_revision": VNGRS_REVISION,
                "object_id_kind": "lfs_oid",
                "object_id": f'"{digest}"',
                "object_size_bytes": base + (index < remainder),
                "object_sha256": None,
            }
        )
    payload = b"".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        for row in rows
    )
    return payload, hashlib.sha256(payload).hexdigest()


def test_registry_closes_exact_32_lfs_objects_without_corpus_reads() -> None:
    payload, digest = ledger()
    result = build_source_registry_from_metadata_ledger(payload, expected_ledger_sha256=digest)
    assert result["status"] == "REGISTRY_CLOSED_FROM_ACCEPTED_LFS_IDENTITIES"
    assert result["object_count"] == 32
    assert result["total_bytes"] == 9_468_474_036
    assert [row["path"] for row in result["objects"]] == list(FROZEN_SELECTED_SHARD_PATHS)
    assert all(len(row["sha256"]) == 64 for row in result["objects"])
    assert len(result["registry_sha256"]) == 64
    assert result["corpus_rows_read"] == 0
    assert result["full_objects_downloaded"] == 0


@pytest.mark.parametrize("mutation", ["hash", "order", "kind", "size"])
def test_registry_fails_closed_on_hash_order_identity_or_size_drift(mutation: str) -> None:
    payload, digest = ledger()
    rows = [json.loads(line) for line in payload.decode().splitlines()]
    if mutation == "hash":
        with pytest.raises(ValueError, match="ledger SHA-256"):
            build_source_registry_from_metadata_ledger(payload, expected_ledger_sha256="0" * 64)
        return
    if mutation == "order":
        rows[0], rows[1] = rows[1], rows[0]
    elif mutation == "kind":
        rows[0]["object_id_kind"] = "etag"
    else:
        rows[0]["object_size_bytes"] += 1
    changed = b"".join(json.dumps(row, sort_keys=True).encode() + b"\n" for row in rows)
    with pytest.raises(ValueError):
        build_source_registry_from_metadata_ledger(
            changed, expected_ledger_sha256=hashlib.sha256(changed).hexdigest()
        )

