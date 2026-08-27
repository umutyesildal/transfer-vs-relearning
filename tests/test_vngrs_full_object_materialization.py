from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from transfer_vs_relearning.corpora.vngrs.materialization import (
    FullObjectResponse,
    MaterializationBlocked,
    MaterializationPolicy,
    SourceObject,
    immutable_resolve_url,
    materialize_full_objects,
    validate_source_registry,
)
from transfer_vs_relearning.corpora.vngrs.metadata import FROZEN_SELECTED_SHARD_PATHS, VNGRS_REVISION


def source(path: str, payload: bytes, *, sha256: str | None = None, lfs_oid: str | None = None) -> SourceObject:
    digest = sha256 or hashlib.sha256(payload).hexdigest()
    return SourceObject(
        path=path,
        revision=VNGRS_REVISION,
        size_bytes=len(payload),
        sha256=digest,
        lfs_oid=lfs_oid or f"sha256:{digest}",
        url=immutable_resolve_url(path),
    )


def policy(rows: list[SourceObject], *, max_bytes: int | None = None) -> MaterializationPolicy:
    total = sum(row.size_bytes for row in rows)
    return MaterializationPolicy(
        selected_paths=tuple(row.path for row in rows),
        expected_total_bytes=total,
        max_response_bytes=total if max_bytes is None else max_bytes,
        chunk_size_upper_bound=4,
        execution_enabled=True,
    )


def fixture_registry(*, first_payload: bytes = b"fixture") -> tuple[list[SourceObject], dict[str, bytes]]:
    payloads = {
        path: first_payload if index == 0 else f"fixture-{index:02d}".encode("ascii")
        for index, path in enumerate(FROZEN_SELECTED_SHARD_PATHS)
    }
    return [source(path, payload) for path, payload in payloads.items()], payloads


def transport(payloads: dict[str, bytes], *, status: int = 200, length_delta: int = 0):
    def get(item: SourceObject) -> FullObjectResponse:
        payload = payloads[item.path]
        return FullObjectResponse(
            status=status,
            headers={
                "Content-Length": str(len(payload) + length_delta),
                "Content-Type": "application/vnd.apache.parquet",
                "Content-Encoding": "identity",
                "X-Linked-Etag": item.lfs_oid,
            },
            chunks=tuple(payload[index : index + 4] for index in range(0, len(payload), 4)),
            terminal_url="https://cdn-lfs.example.invalid/object",
            redirect_chain=({"status": 302, "terminal_host": "cdn-lfs.example.invalid"},),
        )

    return get


def test_offline_fixture_objects_publish_only_after_all_identity_checks(tmp_path: Path) -> None:
    rows, payloads = fixture_registry(first_payload=b"PAR1fixture-onePAR1")
    root = tmp_path / "d0"
    result = materialize_full_objects(root, rows, transport=transport(payloads), policy=policy(rows))

    assert result.status == "MATERIALIZED_VERIFIED"
    assert result.total_response_bytes == sum(map(len, payloads.values()))
    assert [row["path"] for row in result.source_rows] == list(payloads)
    assert all(row["status"] == "verified" for row in result.request_rows)
    for path, payload in payloads.items():
        assert (root / "raw" / path).read_bytes() == payload
        assert not (root / "raw/.partial" / path).exists()
    assert not (root / "control/failure.json").exists()


def test_registry_must_close_before_root_creation_or_transport_call(tmp_path: Path) -> None:
    rows, payloads = fixture_registry()
    original = rows[0]
    rows[0] = source(
        original.path,
        payloads[original.path],
        sha256="0" * 64,
        lfs_oid="sha256:" + hashlib.sha256(payloads[original.path]).hexdigest(),
    )
    calls = 0

    def forbidden(_: SourceObject) -> FullObjectResponse:
        nonlocal calls
        calls += 1
        raise AssertionError("transport must not be called")

    root = tmp_path / "never-created"
    with pytest.raises(MaterializationBlocked, match="LFS identity"):
        materialize_full_objects(root, rows, transport=forbidden, policy=policy(rows))
    assert calls == 0
    assert not root.exists()


def test_execution_disabled_is_zero_write_and_zero_transport(tmp_path: Path) -> None:
    payload = b"fixture"
    row = source(FROZEN_SELECTED_SHARD_PATHS[0], payload)
    with pytest.raises(MaterializationBlocked, match="disabled"):
        materialize_full_objects(
            tmp_path / "disabled",
            [row],
            transport=lambda _: (_ for _ in ()).throw(AssertionError("no transport")),
            policy=MaterializationPolicy(
                selected_paths=(row.path,),
                expected_total_bytes=len(payload),
                max_response_bytes=len(payload),
            ),
        )
    assert not (tmp_path / "disabled").exists()


def test_hash_mismatch_preserves_partial_and_writes_typed_failure(tmp_path: Path) -> None:
    expected = b"PAR1expectedPAR1"
    received = b"PAR1tamperedPAR1"
    rows, payloads = fixture_registry(first_payload=expected)
    row = rows[0]
    payloads[row.path] = received
    root = tmp_path / "failed"
    with pytest.raises(MaterializationBlocked, match="SHA-256 mismatch"):
        materialize_full_objects(
            root,
            rows,
            transport=transport(payloads, length_delta=len(expected) - len(received)),
            policy=policy(rows),
        )
    assert not (root / "raw" / row.path).exists()
    assert (root / "raw/.partial" / row.path).read_bytes() == received
    failure = json.loads((root / "control/failure.json").read_text(encoding="utf-8"))
    assert failure["status"] == "BLOCKED"
    assert failure["source_path"] == row.path
    assert failure["partial_path"] == f"raw/.partial/{row.path}"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda row: SourceObject("../escape.parquet", row.revision, row.size_bytes, row.sha256, row.lfs_oid, row.url), "selected-path order"),
        (lambda row: SourceObject(row.path, "f" * 40, row.size_bytes, row.sha256, row.lfs_oid, row.url), "revision drift"),
        (lambda row: SourceObject(row.path, row.revision, row.size_bytes, row.sha256, row.lfs_oid, "https://example.invalid/a"), "URL drift"),
    ],
)
def test_registry_rejects_path_revision_and_url_drift(mutation, message: str) -> None:
    rows, _ = fixture_registry()
    changed = mutation(rows[0])
    rows[0] = changed
    with pytest.raises(MaterializationBlocked, match=message):
        validate_source_registry(
            rows,
            MaterializationPolicy(
                expected_total_bytes=sum(row.size_bytes for row in rows),
                max_response_bytes=sum(row.size_bytes for row in rows),
            ),
        )


def test_response_header_drift_fails_before_partial_creation(tmp_path: Path) -> None:
    rows, payloads = fixture_registry()
    row = rows[0]
    root = tmp_path / "bad-header"
    with pytest.raises(MaterializationBlocked, match="Content-Length"):
        materialize_full_objects(
            root,
            rows,
            transport=transport(payloads, length_delta=1),
            policy=policy(rows),
        )
    assert not (root / "raw/.partial" / row.path).exists()
    assert (root / "control/failure.json").is_file()


def test_fresh_root_and_response_budget_are_fail_closed(tmp_path: Path) -> None:
    rows, payloads = fixture_registry(first_payload=b"12345678")
    existing = tmp_path / "existing"
    existing.mkdir()
    with pytest.raises(MaterializationBlocked, match="fresh"):
        materialize_full_objects(existing, rows, transport=transport(payloads), policy=policy(rows))
    with pytest.raises(MaterializationBlocked, match="budget"):
        validate_source_registry(rows, policy(rows, max_bytes=sum(map(len, payloads.values())) - 1))
