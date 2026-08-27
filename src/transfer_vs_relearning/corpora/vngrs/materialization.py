"""Fail-closed full-object materialization for the vngrs D0 corpus contract.

The operator is transport-injected on purpose.  Importing this module cannot open a network
connection, and callers must explicitly enable execution.  Production callers may later provide
an HTTPS transport; tests use byte fixtures.  A source object is published from ``raw/.partial``
only after its size, SHA-256 and immutable LFS identity all agree.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import urlsplit

from .metadata import FROZEN_SELECTED_SHARD_PATHS, VNGRS_REPOSITORY, VNGRS_REVISION


SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
ALLOWED_CONTENT_TYPES = frozenset(
    {"application/octet-stream", "application/vnd.apache.parquet"}
)


class MaterializationBlocked(RuntimeError):
    """A source-identity, transport, byte-bound or filesystem invariant failed."""

    def __init__(self, message: str, *, context: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = dict(context or {})


@dataclass(frozen=True)
class SourceObject:
    """Exact immutable identity required before one shard may be requested."""

    path: str
    revision: str
    size_bytes: int
    sha256: str
    lfs_oid: str
    url: str


@dataclass(frozen=True)
class FullObjectResponse:
    """Sanitized response exposed by a caller-supplied transport."""

    status: int
    headers: Mapping[str, str]
    chunks: Iterable[bytes]
    terminal_url: str
    redirect_chain: tuple[Mapping[str, Any], ...] = ()


Transport = Callable[[SourceObject], FullObjectResponse]


@dataclass(frozen=True)
class MaterializationPolicy:
    selected_paths: tuple[str, ...] = FROZEN_SELECTED_SHARD_PATHS
    revision: str = VNGRS_REVISION
    expected_total_bytes: int = 9_468_474_036
    max_response_bytes: int = 10_737_418_240
    chunk_size_upper_bound: int = 8 * 1024 * 1024
    execution_enabled: bool = False


@dataclass
class MaterializationResult:
    status: str
    root: str
    total_response_bytes: int
    source_rows: list[dict[str, Any]] = field(default_factory=list)
    request_rows: list[dict[str, Any]] = field(default_factory=list)


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    payload = _canonical_json_bytes(value) + b"\n"
    temporary = path.with_name(path.name + ".partial")
    if path.exists() or temporary.exists():
        raise MaterializationBlocked(f"refusing to overwrite control artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _normalized_lfs_sha256(value: str) -> str:
    normalized = value.strip().strip('"').lower()
    for prefix in ("sha256:", "sha256-"):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :]
            break
    if SHA256_RE.fullmatch(normalized) is None:
        raise MaterializationBlocked("LFS object identity is not an exact SHA-256")
    return normalized


def _safe_relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise MaterializationBlocked(f"unsafe source path: {value!r}")
    if path.suffix != ".parquet":
        raise MaterializationBlocked(f"source path is not Parquet: {value!r}")
    return path


def immutable_resolve_url(path: str, revision: str = VNGRS_REVISION) -> str:
    """Construct the immutable dataset URL without performing I/O."""

    relative = _safe_relative_path(path)
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise MaterializationBlocked("immutable revision must be a 40-character Git SHA")
    return f"https://huggingface.co/datasets/{VNGRS_REPOSITORY}/resolve/{revision}/{relative.as_posix()}"


def validate_source_registry(
    objects: Iterable[SourceObject], policy: MaterializationPolicy
) -> tuple[SourceObject, ...]:
    """Close the entire ordered registry before creating an output root or calling transport."""

    rows = tuple(objects)
    if policy.selected_paths != FROZEN_SELECTED_SHARD_PATHS:
        raise MaterializationBlocked("production policy must use the frozen 32-shard selection")
    if tuple(row.path for row in rows) != policy.selected_paths:
        raise MaterializationBlocked("source registry does not exactly match selected-path order")
    if len(set(row.path for row in rows)) != len(rows):
        raise MaterializationBlocked("source registry contains duplicate paths")
    total = 0
    for row in rows:
        _safe_relative_path(row.path)
        if row.revision != policy.revision:
            raise MaterializationBlocked(f"{row.path}: immutable revision drift")
        if row.url != immutable_resolve_url(row.path, row.revision):
            raise MaterializationBlocked(f"{row.path}: immutable resolve URL drift")
        if not isinstance(row.size_bytes, int) or isinstance(row.size_bytes, bool) or row.size_bytes <= 0:
            raise MaterializationBlocked(f"{row.path}: missing or invalid exact object size")
        if SHA256_RE.fullmatch(row.sha256) is None:
            raise MaterializationBlocked(f"{row.path}: missing or invalid full-object SHA-256")
        if _normalized_lfs_sha256(row.lfs_oid) != row.sha256:
            raise MaterializationBlocked(f"{row.path}: LFS identity does not bind the object SHA-256")
        total += row.size_bytes
    if total != policy.expected_total_bytes:
        raise MaterializationBlocked(
            "source registry total does not match the frozen selected payload",
            context={"observed_bytes": total, "expected_bytes": policy.expected_total_bytes},
        )
    if total > policy.max_response_bytes:
        raise MaterializationBlocked("expected source bytes exceed the response-byte budget")
    return rows


def _header(headers: Mapping[str, str], name: str) -> str | None:
    wanted = name.lower()
    for key, value in headers.items():
        if str(key).lower() == wanted:
            return str(value)
    return None


def _validate_response(response: FullObjectResponse, source: SourceObject) -> tuple[str, str]:
    if response.status != 200:
        raise MaterializationBlocked(f"{source.path}: full-object response status was not 200")
    content_length = _header(response.headers, "content-length")
    if content_length is None or not content_length.isdigit() or int(content_length) != source.size_bytes:
        raise MaterializationBlocked(f"{source.path}: Content-Length does not match exact object size")
    content_type = (_header(response.headers, "content-type") or "").split(";", 1)[0].strip().lower()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise MaterializationBlocked(f"{source.path}: response Content-Type is not allowed")
    if (_header(response.headers, "content-encoding") or "identity").lower() != "identity":
        raise MaterializationBlocked(f"{source.path}: encoded response would break byte identity")
    response_oid = _header(response.headers, "x-linked-etag") or _header(response.headers, "etag")
    if response_oid is None or _normalized_lfs_sha256(response_oid) != source.sha256:
        raise MaterializationBlocked(f"{source.path}: response object identity drift")
    parsed = urlsplit(response.terminal_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise MaterializationBlocked(f"{source.path}: invalid terminal HTTPS route")
    return content_type, parsed.hostname.lower()


def materialize_full_objects(
    root: str | Path,
    objects: Iterable[SourceObject],
    *,
    transport: Transport,
    policy: MaterializationPolicy = MaterializationPolicy(),
) -> MaterializationResult:
    """Materialize an exact registry under a fresh root with atomic per-object publication.

    Failure keeps an already-written ``.partial`` object and records a compact typed failure.
    No retry, resume, cleanup or alternate route is attempted automatically.
    """

    if not policy.execution_enabled:
        raise MaterializationBlocked("materialization execution is disabled by policy")
    registry = validate_source_registry(objects, policy)
    root_path = Path(root)
    if not root_path.is_absolute():
        raise MaterializationBlocked("output root must be absolute")
    if root_path.exists() or root_path.is_symlink():
        raise MaterializationBlocked("fresh output root is required")
    root_path.mkdir(parents=True, exist_ok=False)
    raw_root = root_path / "raw"
    partial_root = raw_root / ".partial"
    control_root = root_path / "control"
    partial_root.mkdir(parents=True)
    control_root.mkdir(parents=True)

    result = MaterializationResult(status="IN_PROGRESS", root=str(root_path), total_response_bytes=0)
    active_source: SourceObject | None = None
    active_partial: Path | None = None
    try:
        for ordinal, source in enumerate(registry):
            active_source = source
            relative = _safe_relative_path(source.path)
            target = raw_root.joinpath(*relative.parts)
            partial = partial_root.joinpath(*relative.parts)
            active_partial = partial
            if target.exists() or partial.exists() or target.is_symlink() or partial.is_symlink():
                raise MaterializationBlocked(f"{source.path}: target or partial already exists")
            target.parent.mkdir(parents=True, exist_ok=True)
            partial.parent.mkdir(parents=True, exist_ok=True)

            response = transport(source)
            content_type, terminal_host = _validate_response(response, source)
            digest = hashlib.sha256()
            object_bytes = 0
            with partial.open("xb") as handle:
                for chunk in response.chunks:
                    if not isinstance(chunk, bytes) or not chunk:
                        raise MaterializationBlocked(f"{source.path}: transport yielded a non-byte/empty chunk")
                    if len(chunk) > policy.chunk_size_upper_bound:
                        raise MaterializationBlocked(f"{source.path}: transport chunk exceeds memory bound")
                    object_bytes += len(chunk)
                    result.total_response_bytes += len(chunk)
                    if object_bytes > source.size_bytes:
                        raise MaterializationBlocked(f"{source.path}: response exceeded exact object size")
                    if result.total_response_bytes > policy.max_response_bytes:
                        raise MaterializationBlocked("cumulative response-byte budget exceeded")
                    handle.write(chunk)
                    digest.update(chunk)
                handle.flush()
                os.fsync(handle.fileno())
            observed_sha256 = digest.hexdigest()
            if object_bytes != source.size_bytes:
                raise MaterializationBlocked(f"{source.path}: response ended before exact object size")
            if observed_sha256 != source.sha256:
                raise MaterializationBlocked(f"{source.path}: full-object SHA-256 mismatch")
            os.replace(partial, target)
            active_partial = None
            request_row = {
                "schema_version": 1,
                "request_ordinal": ordinal,
                "path": source.path,
                "http_status": response.status,
                "response_transferred_bytes": object_bytes,
                "terminal_host": terminal_host,
                "redirect_hops": len(response.redirect_chain),
                "content_type": content_type,
                "content_encoding": "identity",
                "status": "verified",
            }
            source_row = {
                "schema_version": 1,
                "ordinal": ordinal,
                "path": source.path,
                "revision": source.revision,
                "bytes": object_bytes,
                "sha256": observed_sha256,
                "lfs_oid": source.lfs_oid,
                "local_path": str(target.relative_to(root_path)),
                "status": "verified",
            }
            result.request_rows.append(request_row)
            result.source_rows.append(source_row)
        if result.total_response_bytes != policy.expected_total_bytes:
            raise MaterializationBlocked("terminal transferred-byte total drift")
        result.status = "MATERIALIZED_VERIFIED"
        return result
    except Exception as exc:
        context = dict(getattr(exc, "context", {}))
        failure = {
            "schema_version": 1,
            "status": "BLOCKED",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "source_path": active_source.path if active_source else None,
            "partial_path": (
                str(active_partial.relative_to(root_path))
                if active_partial is not None and active_partial.exists()
                else None
            ),
            "verified_objects": len(result.source_rows),
            "response_transferred_bytes": result.total_response_bytes,
            "context": context,
        }
        _atomic_json(control_root / "failure.json", failure)
        if isinstance(exc, MaterializationBlocked):
            raise
        raise MaterializationBlocked(str(exc), context=failure) from exc
