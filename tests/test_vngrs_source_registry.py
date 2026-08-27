import hashlib
import base64
import gzip
import json

import pytest

from transfer_vs_relearning.corpora.vngrs.metadata import FROZEN_SELECTED_SHARD_PATHS, VNGRS_REVISION
from transfer_vs_relearning.corpora.vngrs.source_registry import (
    build_source_registry_from_metadata_ledger,
    parse_discovery_transport,
)


def ledger(
    *,
    total_bytes: int = 9_502_315_428,
    compressed_bytes: int = 9_468_474_036,
) -> tuple[bytes, str]:
    base, remainder = divmod(total_bytes, 32)
    compressed_base, compressed_remainder = divmod(compressed_bytes, 32)
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
                "compressed_bytes": compressed_base + (index < compressed_remainder),
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
    assert result["total_object_bytes"] == 9_502_315_428
    assert result["total_parquet_compressed_bytes"] == 9_468_474_036
    assert [row["path"] for row in result["objects"]] == list(FROZEN_SELECTED_SHARD_PATHS)
    assert all(len(row["sha256"]) == 64 for row in result["objects"])
    assert len(result["registry_sha256"]) == 64
    assert result["corpus_rows_read"] == 0
    assert result["full_objects_downloaded"] == 0


@pytest.mark.parametrize("mutation", ["hash", "order", "kind", "size", "compressed_size"])
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
    elif mutation == "size":
        rows[0]["object_size_bytes"] += 1
    else:
        rows[0]["compressed_bytes"] += 1
    changed = b"".join(json.dumps(row, sort_keys=True).encode() + b"\n" for row in rows)
    with pytest.raises(ValueError):
        build_source_registry_from_metadata_ledger(
            changed, expected_ledger_sha256=hashlib.sha256(changed).hexdigest()
        )


def transcript(payload: bytes, digest: str) -> str:
    encoded = base64.b64encode(gzip.compress(payload)).decode()
    return "\n".join(
        (
            "spawn ssh command-containing-markers-but-not-a-marker-line",
            "DISCOVERY_CAPTURE_V1_BEGIN",
            f"LEDGER_BYTES={len(payload)}",
            f"LEDGER_SHA256={digest}",
            "RESOLVED_PARENT=/vol/tmp2/yesildau",
            "PROPOSED_ROOT_ABSENT=1",
            "DF_BYTES_BEGIN",
            "Filesystem 1B-blocks Used Avail Use% Mounted on",
            "storage02:/srv/nfs/data02 153002533978112 29905731452928 122943170412544 20% /vol/tmp2",
            "DF_BYTES_END",
            "DF_INODES_POSIX_BEGIN",
            "Filesystem Inodes IUsed IFree IUse% Mounted on",
            "storage02:/srv/nfs/data02 2343983104 59700219 2284282885 3% /vol/tmp2",
            "DF_INODES_POSIX_END",
            "LEDGER_GZIP_BASE64_BEGIN",
            encoded,
            "LEDGER_GZIP_BASE64_END",
            "DISCOVERY_CAPTURE_V1_END",
            "",
        )
    )


def test_transport_parser_closes_registry_without_persisting_raw_payload() -> None:
    payload, digest = ledger()
    result = parse_discovery_transport(transcript(payload, digest), expected_ledger_sha256=digest)
    assert result["ledger_bytes"] == len(payload)
    assert result["byte_capacity"]["available_bytes"] == 122_943_170_412_544
    assert result["inode_capacity"]["available_inodes"] == 2_284_282_885
    assert result["source_registry"]["object_count"] == 32
    assert result["source_registry"]["total_object_bytes"] == 9_502_315_428
    assert result["source_registry"]["total_parquet_compressed_bytes"] == 9_468_474_036
    assert result["raw_ledger_payload_persisted"] is False


@pytest.mark.parametrize("mutation", ["truncate", "root", "marker"])
def test_transport_parser_fails_closed_on_capture_or_metadata_drift(mutation: str) -> None:
    payload, digest = ledger()
    value = transcript(payload, digest)
    if mutation == "truncate":
        value = value.replace("LEDGER_GZIP_BASE64_END", "LEDGER_GZIP_BASE64_END", 1)
        lines = value.splitlines()
        payload_index = lines.index("LEDGER_GZIP_BASE64_BEGIN") + 1
        lines[payload_index] = lines[payload_index][:-4]
        value = "\n".join(lines)
    elif mutation == "root":
        value = value.replace("PROPOSED_ROOT_ABSENT=1", "PROPOSED_ROOT_ABSENT=0")
    else:
        value = value.replace("DISCOVERY_CAPTURE_V1_END", "DISCOVERY_CAPTURE_V1_MISSING")
    with pytest.raises(ValueError):
        parse_discovery_transport(value, expected_ledger_sha256=digest)
