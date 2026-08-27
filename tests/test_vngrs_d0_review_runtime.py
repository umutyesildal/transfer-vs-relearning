from __future__ import annotations

import hashlib
import io
import urllib.error
from email.message import Message
from pathlib import Path

import pytest

from transfer_vs_relearning.corpora.vngrs.d0_audit import D0Document, human_review_sample
from transfer_vs_relearning.corpora.vngrs.d0_review import (
    build_review_packet,
    decision_template,
    review_packet_sha256,
    validate_review_decisions,
)
from transfer_vs_relearning.corpora.vngrs.d0_runtime import FrozenTokenizerAdapter, ReviewedHttpsTransport
from transfer_vs_relearning.corpora.vngrs.materialization import SourceObject, immutable_resolve_url
from transfer_vs_relearning.corpora.vngrs.metadata import FROZEN_SELECTED_SHARD_PATHS, VNGRS_REVISION


def documents() -> list[D0Document]:
    return [
        D0Document(f"{index:064x}", path, "OSCAR" if index % 2 == 0 else "mC4", "Türkçe " + "x" * 2500)
        for index, path in enumerate(FROZEN_SELECTED_SHARD_PATHS)
    ]


def test_review_handoff_is_bounded_exact_and_packet_bound() -> None:
    docs = documents()
    selected = human_review_sample(docs, sample_size=8)
    packet = build_review_packet(docs, selected)
    assert len(packet) == 8
    assert all(len(row["excerpt"]) == 2000 and row["excerpt_truncated"] for row in packet)
    template = decision_template(packet)
    packet_hash = review_packet_sha256(packet)
    decisions = [
        {**row, "verdict": "usable", "reviewer": "reviewer-1"} for row in template
    ]
    validated = validate_review_decisions(packet, decisions)
    assert len(validated) == 8
    assert all(row["review_packet_sha256"] == packet_hash for row in validated)
    decisions[0]["review_packet_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="exact review packet"):
        validate_review_decisions(packet, decisions)


class Response:
    def __init__(self, payload: bytes, url: str, headers: dict[str, str]):
        self._stream = io.BytesIO(payload)
        self._url = url
        self.headers = headers
        self.status = 200
        self.closed = False

    def read(self, size: int) -> bytes:
        return self._stream.read(size)

    def geturl(self) -> str:
        return self._url

    def close(self) -> None:
        self.closed = True


class RedirectOpener:
    def __init__(self, source_url: str, terminal_url: str, payload: bytes, digest: str):
        self.source_url = source_url
        self.terminal_url = terminal_url
        self.payload = payload
        self.digest = digest
        self.calls = 0

    def open(self, request, timeout):
        self.calls += 1
        if self.calls == 1:
            headers = Message()
            headers["Location"] = self.terminal_url
            headers["X-Linked-Etag"] = f"sha256:{self.digest}"
            raise urllib.error.HTTPError(self.source_url, 302, "redirect", headers, io.BytesIO())
        return Response(
            self.payload,
            self.terminal_url,
            {"Content-Length": str(len(self.payload)), "Content-Type": "application/vnd.apache.parquet"},
        )


def test_reviewed_https_transport_keeps_redirect_secrets_out_of_evidence() -> None:
    payload = b"PAR1fixturePAR1"
    digest = hashlib.sha256(payload).hexdigest()
    path = FROZEN_SELECTED_SHARD_PATHS[0]
    source = SourceObject(path, VNGRS_REVISION, len(payload), digest, f"sha256:{digest}", immutable_resolve_url(path))
    terminal = "https://cas-bridge.xethub.hf.co/object?signature=secret"
    response = ReviewedHttpsTransport(opener=RedirectOpener(source.url, terminal, payload, digest), chunk_bytes=4)(source)
    assert b"".join(response.chunks) == payload
    assert response.headers["X-Linked-Etag"] == f"sha256:{digest}"
    assert response.redirect_chain[0]["terminal_host"] == "cas-bridge.xethub.hf.co"
    assert "secret" not in repr(response.redirect_chain)


def test_frozen_tokenizer_adapter_hashes_assets_before_local_only_load(tmp_path: Path) -> None:
    assets = []
    for name, payload in (("tokenizer.json", b"tokenizer"), ("tokenizer_config.json", b"{}")):
        (tmp_path / name).write_bytes(payload)
        assets.append({"path": name, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
    assets.sort(key=lambda row: row["path"])
    from transfer_vs_relearning.corpora.vngrs.metadata import canonical_json_sha256

    inventory = {
        "assets": assets,
        "snapshot_manifest_sha256": "a" * 64,
        "tokenizer_asset_manifest_sha256": canonical_json_sha256(assets),
    }
    calls = []

    class Tokenizer:
        def encode(self, text, add_special_tokens=False):
            return [1]

    def factory(path, **kwargs):
        calls.append((path, kwargs))
        return Tokenizer()

    adapter = FrozenTokenizerAdapter.load(role="olmo", snapshot_root=tmp_path, inventory=inventory, tokenizer_factory=factory)
    assert adapter.encode("merhaba") == [1]
    assert calls == [(str(tmp_path), {"local_files_only": True, "trust_remote_code": False})]
    (tmp_path / "tokenizer.json").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="byte-size drift"):
        FrozenTokenizerAdapter.load(role="olmo", snapshot_root=tmp_path, inventory=inventory, tokenizer_factory=factory)
