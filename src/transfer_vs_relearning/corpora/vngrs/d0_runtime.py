"""Reviewed production adapters for D0 HTTPS objects and tokenizer-only loading."""

from __future__ import annotations

import hashlib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urljoin, urlsplit

from .d0_audit import EXPECTED_MODELS
from .materialization import FullObjectResponse, SourceObject
from .metadata import canonical_json_sha256


ALLOWED_TERMINAL_SUFFIXES = ("xethub.hf.co", "cdn.hf.co", "huggingface.co")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def _allowed_https(url: str) -> bool:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    return (
        parsed.scheme == "https"
        and not parsed.username
        and not parsed.password
        and any(host == suffix or host.endswith("." + suffix) for suffix in ALLOWED_TERMINAL_SUFFIXES)
    )


@dataclass
class ReviewedHttpsTransport:
    opener: Any = None
    timeout_seconds: int = 120
    chunk_bytes: int = 8 * 1024 * 1024

    def __post_init__(self) -> None:
        if self.opener is None:
            self.opener = urllib.request.build_opener(_NoRedirect())

    def __call__(self, source: SourceObject) -> FullObjectResponse:
        if not _allowed_https(source.url) or not 1 <= self.chunk_bytes <= 8 * 1024 * 1024:
            raise ValueError("reviewed HTTPS route or chunk bound is invalid")
        request = urllib.request.Request(source.url, headers={"Accept-Encoding": "identity"})
        redirects: tuple[Mapping[str, Any], ...] = ()
        linked_etag: str | None = None
        try:
            response = self.opener.open(request, timeout=self.timeout_seconds)
        except urllib.error.HTTPError as exc:
            if exc.code not in {302, 307}:
                raise
            location = exc.headers.get("Location")
            terminal_url = urljoin(source.url, location or "")
            if not location or len(location) > 8_192 or not _allowed_https(terminal_url):
                raise ValueError("unreviewed or unsafe D0 redirect") from exc
            linked_etag = exc.headers.get("X-Linked-Etag") or exc.headers.get("ETag")
            redirects = (
                {
                    "status": exc.code,
                    "terminal_host": (urlsplit(terminal_url).hostname or "").lower(),
                    "location_sha256": hashlib.sha256(location.encode("utf-8")).hexdigest(),
                },
            )
            response = self.opener.open(
                urllib.request.Request(terminal_url, headers={"Accept-Encoding": "identity"}),
                timeout=self.timeout_seconds,
            )
        terminal_url = response.geturl()
        if not _allowed_https(terminal_url):
            response.close()
            raise ValueError("terminal D0 response route is unsafe")
        headers = {str(key): str(value) for key, value in response.headers.items()}
        if linked_etag and not any(key.lower() in {"x-linked-etag", "etag"} for key in headers):
            headers["X-Linked-Etag"] = linked_etag

        def chunks():
            try:
                while True:
                    block = response.read(self.chunk_bytes)
                    if not block:
                        break
                    yield block
            finally:
                response.close()

        return FullObjectResponse(response.status, headers, chunks(), terminal_url, redirects)


@dataclass
class FrozenTokenizerAdapter:
    role: str
    model_id: str
    revision: str
    manifest_sha256: str
    asset_sha256: str
    tokenizer: Any

    def encode(self, text: str, *, add_special_tokens: bool = False):
        return self.tokenizer.encode(text, add_special_tokens=add_special_tokens)

    @classmethod
    def load(
        cls,
        *,
        role: str,
        snapshot_root: str | Path,
        inventory: Mapping[str, Any],
        tokenizer_factory: Any = None,
    ) -> "FrozenTokenizerAdapter":
        if role not in EXPECTED_MODELS:
            raise ValueError("unknown frozen tokenizer role")
        root = Path(snapshot_root)
        assets = [dict(row) for row in inventory.get("assets", [])]
        if not assets or canonical_json_sha256(assets) != inventory.get("tokenizer_asset_manifest_sha256"):
            raise ValueError("tokenizer asset manifest hash drift")
        for row in assets:
            path = root / row["path"]
            if not path.is_file() or path.is_symlink() or path.stat().st_size != row["bytes"]:
                raise ValueError(f"{role}: tokenizer asset missing or byte-size drift")
            if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
                raise ValueError(f"{role}: tokenizer asset SHA-256 drift")
        if tokenizer_factory is None:
            from transformers import AutoTokenizer

            tokenizer_factory = AutoTokenizer.from_pretrained
        tokenizer = tokenizer_factory(str(root), local_files_only=True, trust_remote_code=False)
        model_id, revision = EXPECTED_MODELS[role]
        return cls(
            role,
            model_id,
            revision,
            str(inventory["snapshot_manifest_sha256"]),
            str(inventory["tokenizer_asset_manifest_sha256"]),
            tokenizer,
        )
