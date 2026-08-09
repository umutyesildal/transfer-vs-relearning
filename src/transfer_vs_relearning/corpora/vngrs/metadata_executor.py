"""Reusable bounded executor for the frozen Document 151an metadata/footer wave.

The executor deliberately has no corpus-row path.  It performs the frozen HEAD, trailer-range,
exact-footer-range and immutable-license requests, writes only the seven declared top-level
outputs plus compact evidence artifacts, and validates the resulting byte graph before returning.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import parse_qsl, urlsplit

from .metadata import (
    FROZEN_SELECTED_SHARD_PATHS,
    METADATA_FOOTER_ARTIFACT_KINDS,
    METADATA_FOOTER_CONTRACT_SHA256,
    METADATA_FOOTER_FOOTER_RANGE_TEMPLATE,
    METADATA_FOOTER_MAX_NEW_INODES,
    METADATA_FOOTER_MAX_OUTPUT_FILES,
    METADATA_FOOTER_MAX_RETRIES,
    METADATA_FOOTER_MAX_SINGLE_RESPONSE_BYTES,
    METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES,
    METADATA_FOOTER_MAX_WALL_CLOCK_SECONDS,
    METADATA_FOOTER_OUTPUT_PATHS,
    METADATA_FOOTER_RANGE_HEADER,
    METADATA_FOOTER_ROUTE_KIND,
    METADATA_FOOTER_SCRATCH_ROOT,
    METADATA_FOOTER_TRAILER_RANGE_HEADER,
    VNGRS_REPOSITORY,
    VNGRS_REVISION,
    VNGRS_SCHEMA,
    VNGRS_SHARD_COUNT,
    VNGRS_SPLIT,
    build_metadata_footer_feasibility_projection,
    build_sampling_schedule,
    build_selection_evidence,
    canonical_json_bytes,
    dataset_license_resolve_url,
    parse_parquet_footer,
    parse_parquet_trailer,
    parquet_resolve_url,
    serialize_metadata_footer_artifact_manifest,
    validate_metadata_footer_feasibility,
)


HOME_ROOT = "/vol/fob-vol6/mi25/yesildau"
SCRATCH_ROOTS = ("/vol/tmp", "/vol/tmp2")
REQUEST_TIMEOUT_SECONDS = 60
METADATA_FOOTER_MAX_LOGICAL_ATTEMPTS = 121
METADATA_FOOTER_MAX_HTTP_HOPS = 242
HF_REDIRECT_STATUS = 302
HF_REDIRECT_MAX_URL_LENGTH = 8_192
HF_REDIRECT_ALLOWED_HOST_SUFFIXES = ("xethub.hf.co", "cdn.hf.co")
HF_REDIRECT_METADATA_FIELDS = frozenset(
    {"location_sha256", "scheme", "host", "path_sha256", "url_length", "query_keys"}
)


class ExecutionBlocked(RuntimeError):
    """A frozen 151an precondition, route, bound or integrity rule failed."""

    def __init__(self, message: str, *, context: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = dict(context or {})


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Disable urllib's automatic redirects; the bounded client validates one hop itself."""

    def redirect_request(self, request, file, code, message, headers, newurl):  # type: ignore[no-untyped-def]
        return None


@dataclass
class AttemptResult:
    status: int | None
    headers: dict[str, str]
    payload: bytes | None
    final_url: str | None
    redirect_chain: list[dict[str, Any]]
    error: str | None = None
    # The raw terminal URL is retained only in memory. ``final_url`` is the canonical
    # requested URL used in ledgers and artifacts so signed query values never persist.
    terminal_url: str | None = field(default=None, repr=False)


@dataclass
class BoundedClient:
    opener: urllib.request.OpenerDirector
    start_monotonic: float = field(default_factory=time.monotonic)
    attempt_count: int = 0
    retry_count: int = 0
    request_rows: list[dict[str, Any]] = field(default_factory=list)
    artifact_payloads: dict[str, bytes] = field(default_factory=dict)
    total_response_bytes: int = 0
    http_hop_count: int = 0
    redirect_hop_count: int = 0

    def _check_attempt_bound(self) -> None:
        if self.attempt_count >= METADATA_FOOTER_MAX_LOGICAL_ATTEMPTS:
            raise ExecutionBlocked(
                "the next logical request attempt would exceed the 121-attempt bound",
                context=self.bound_context(phase="attempt_bound"),
            )
        if time.monotonic() - self.start_monotonic > METADATA_FOOTER_MAX_WALL_CLOCK_SECONDS:
            raise ExecutionBlocked(
                f"the {METADATA_FOOTER_MAX_WALL_CLOCK_SECONDS}-second wall-clock bound was exceeded",
                context=self.bound_context(phase="wall_clock_bound"),
            )

    def _check_http_hop_bound(self) -> None:
        if self.http_hop_count >= METADATA_FOOTER_MAX_HTTP_HOPS:
            raise ExecutionBlocked(
                "the next HTTP hop would exceed the 242-hop bound",
                context=self.bound_context(phase="http_hop_bound"),
            )

    def _check_retry_bound(self) -> None:
        if self.retry_count >= METADATA_FOOTER_MAX_RETRIES:
            raise ExecutionBlocked(
                "the next retry would exceed the 24-retry bound",
                context=self.bound_context(phase="retry_bound"),
            )

    def bound_context(self, *, phase: str, **extra: Any) -> dict[str, Any]:
        context = {
            "phase": phase,
            "attempt_count": self.attempt_count,
            "retry_count": self.retry_count,
            "http_hop_count": self.http_hop_count,
            "redirect_hop_count": self.redirect_hop_count,
            "total_response_bytes": self.total_response_bytes,
        }
        context.update(extra)
        return context

    def _accept_response_bytes(self, count: int) -> None:
        if count < 0 or self.total_response_bytes + count > METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES:
            raise ExecutionBlocked(
                "the cumulative 64 MiB response-byte bound would be exceeded",
                context=self.bound_context(
                    phase="response_byte_bound",
                    attempted_response_bytes=count,
                    max_total_response_bytes=METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES,
                ),
            )
        self.total_response_bytes += count

    def replace_artifact_payload(self, name: str, payload: bytes) -> None:
        """Replace a raw response artifact with its canonical retained representation."""

        self._check_artifact_slot(name)
        previous = self.artifact_payloads.get(name, b"")
        candidate_total = self.total_response_bytes - len(previous) + len(payload)
        if candidate_total > METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES:
            raise ExecutionBlocked(
                "the cumulative 64 MiB response-byte bound would be exceeded",
                context=self.bound_context(
                    phase="response_byte_bound",
                    attempted_response_bytes=len(payload),
                    max_total_response_bytes=METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES,
                ),
            )
        if candidate_total < 0:
            raise ExecutionBlocked(
                "canonical artifact accounting would become negative",
                context=self.bound_context(phase="response_byte_accounting"),
            )
        self.total_response_bytes = candidate_total
        self.artifact_payloads[name] = payload

    def _check_artifact_slot(self, name: str) -> None:
        if name in self.artifact_payloads:
            return
        projected = len(self.artifact_payloads) + 1 + len(METADATA_FOOTER_OUTPUT_PATHS)
        if projected > METADATA_FOOTER_MAX_OUTPUT_FILES or projected > METADATA_FOOTER_MAX_NEW_INODES:
            raise ExecutionBlocked(
                "the response-artifact/file/inode bound would be exceeded",
                context=self.bound_context(
                    phase="artifact_slot_bound",
                    artifact=name,
                    projected_output_files=projected,
                ),
            )

    @staticmethod
    def _headers(response: Any) -> dict[str, str]:
        return {str(key).lower(): str(value) for key, value in response.headers.items()}

    @staticmethod
    def _redact_location(location: str | None) -> dict[str, Any]:
        """Return non-secret Location evidence without retaining its value."""

        raw = location or ""
        return {
            "location_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "location_length": len(raw),
        }

    @staticmethod
    def _safe_redirect_metadata(metadata: Any) -> bool:
        if not isinstance(metadata, Mapping) or set(metadata) != HF_REDIRECT_METADATA_FIELDS:
            return False
        if metadata.get("scheme") != "https" or not isinstance(metadata.get("host"), str):
            return False
        host = str(metadata["host"]).lower()
        if not any(host == suffix or host.endswith("." + suffix) for suffix in HF_REDIRECT_ALLOWED_HOST_SUFFIXES):
            return False
        if not isinstance(metadata.get("url_length"), int) or not 0 < metadata["url_length"] <= HF_REDIRECT_MAX_URL_LENGTH:
            return False
        if not all(
            isinstance(metadata.get(field), str) and re.fullmatch(r"[0-9a-f]{64}", metadata[field])
            for field in ("location_sha256", "path_sha256")
        ):
            return False
        query_keys = metadata.get("query_keys")
        return (
            isinstance(query_keys, list)
            and all(isinstance(key, str) for key in query_keys)
            and query_keys == sorted(query_keys)
        )

    @classmethod
    def _validate_redirect_target(cls, location: str | None) -> tuple[str, dict[str, Any]]:
        if not isinstance(location, str) or not location:
            raise ExecutionBlocked(
                "HTTP 302 lacked an absolute Location header",
                context={"phase": "redirect_integrity", "location_present": False},
            )
        summary = cls._redact_location(location)
        if len(location) > HF_REDIRECT_MAX_URL_LENGTH:
            raise ExecutionBlocked(
                "HTTP 302 Location exceeded the frozen URL-length bound",
                context={"phase": "redirect_integrity", **summary},
            )
        try:
            parsed = urlsplit(location)
            port = parsed.port
        except ValueError as exc:
            raise ExecutionBlocked(
                "HTTP 302 Location contained an invalid port",
                context={"phase": "redirect_integrity", **summary},
            ) from exc
        host = parsed.hostname.lower() if parsed.hostname else None
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
            or port is not None
            or not parsed.path.startswith("/")
            or host is None
            or not any(host == suffix or host.endswith("." + suffix) for suffix in HF_REDIRECT_ALLOWED_HOST_SUFFIXES)
        ):
            raise ExecutionBlocked(
                "HTTP 302 Location failed the official Hugging Face CDN allowlist",
                context={"phase": "redirect_integrity", **summary},
            )
        query_keys = sorted(key for key, _ in parse_qsl(parsed.query, keep_blank_values=True))
        metadata = {
            "location_sha256": summary["location_sha256"],
            "scheme": parsed.scheme,
            "host": host,
            "path_sha256": hashlib.sha256(parsed.path.encode("utf-8")).hexdigest(),
            "url_length": len(location),
            "query_keys": query_keys,
        }
        return location, metadata

    @staticmethod
    def _request_headers(*, range_header: str | None, cross_host: bool = False) -> dict[str, str]:
        headers = {"User-Agent": "luna-151an-metadata-footer-executor/1"}
        if range_header is not None:
            headers["Range"] = range_header
        if cross_host:
            headers = {
                key: value
                for key, value in headers.items()
                if key.lower() not in {"authorization", "cookie"}
            }
        return headers

    def _read_bounded(
        self,
        response: Any,
        *,
        headers: Mapping[str, str],
        method: str,
        url: str,
    ) -> bytes:
        """Read no more than the single-response and remaining cumulative budgets."""

        if method.upper() == "HEAD":
            return response.read(0)

        remaining_total = METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES - self.total_response_bytes
        single_budget = min(METADATA_FOOTER_MAX_SINGLE_RESPONSE_BYTES, remaining_total)
        declared_length = self._declared_response_length(headers)
        if declared_length is not None:
            if declared_length > METADATA_FOOTER_MAX_SINGLE_RESPONSE_BYTES:
                raise ExecutionBlocked(
                    "declared response length exceeded the 4 MiB bound",
                    context=self.bound_context(
                        phase="single_response_bound",
                        method=method,
                        url=url,
                        declared_response_bytes=declared_length,
                    ),
                )
            if declared_length > remaining_total:
                raise ExecutionBlocked(
                    "declared response length exceeded the remaining cumulative budget",
                    context=self.bound_context(
                        phase="response_byte_bound",
                        method=method,
                        url=url,
                        declared_response_bytes=declared_length,
                        remaining_response_bytes=remaining_total,
                    ),
                )
            payload = response.read(declared_length)
            if len(payload) != declared_length:
                raise ExecutionBlocked(
                    "response ended before its declared content length",
                    context=self.bound_context(
                        phase="response_length_integrity",
                        method=method,
                        url=url,
                        declared_response_bytes=declared_length,
                        received_response_bytes=len(payload),
                    ),
                )
            return payload

        # Unknown/chunked responses get only one byte beyond the smaller applicable budget.
        # That byte detects overflow without consuming an entire single-response allowance.
        payload = response.read(single_budget + 1)
        if len(payload) > single_budget:
            phase = "response_byte_bound" if remaining_total <= METADATA_FOOTER_MAX_SINGLE_RESPONSE_BYTES else "single_response_bound"
            raise ExecutionBlocked(
                "response exceeded the remaining cumulative 64 MiB budget"
                if phase == "response_byte_bound"
                else "response exceeded the 4 MiB single-response budget",
                context=self.bound_context(
                    phase=phase,
                    method=method,
                    url=url,
                    remaining_response_bytes=remaining_total,
                    read_limit=single_budget + 1,
                    received_response_bytes=len(payload),
                ),
            )
        return payload

    @staticmethod
    def _declared_response_length(headers: Mapping[str, str]) -> int | None:
        if headers.get("transfer-encoding", "").lower() == "chunked":
            return None
        raw = headers.get("content-length")
        if raw is None or not re.fullmatch(r"[0-9]+", raw.strip()):
            return None
        return int(raw.strip())

    def _attempt(self, *, method: str, url: str, range_header: str | None) -> AttemptResult:
        self._check_attempt_bound()
        self.attempt_count += 1
        redirect_chain: list[dict[str, Any]] = []
        current_url = url
        for hop_index in range(2):
            self._check_http_hop_bound()
            self.http_hop_count += 1
            request = urllib.request.Request(
                current_url,
                headers=self._request_headers(range_header=range_header, cross_host=hop_index > 0),
                method=method,
            )
            try:
                response = self.opener.open(request, timeout=REQUEST_TIMEOUT_SECONDS)
            except urllib.error.HTTPError as http_error:
                response_headers = self._headers(http_error)
                status = int(http_error.code)
                if status == HF_REDIRECT_STATUS:
                    if hop_index == 1:
                        raise ExecutionBlocked(
                            "a second HTTP 302 redirect exceeded the one-hop bound",
                            context=self.bound_context(phase="redirect_hop_bound", http_status=status),
                        )
                    target, metadata = self._validate_redirect_target(response_headers.get("location"))
                    redirect_chain.append(metadata)
                    self.redirect_hop_count += 1
                    current_url = target
                    http_error.close()
                    continue
                try:
                    payload = self._read_bounded(
                        http_error,
                        headers=response_headers,
                        method=method,
                        url=url,
                    )
                except ExecutionBlocked:
                    raise
                except Exception as read_error:
                    raise ExecutionBlocked(
                        "unable to read the bounded HTTPError response",
                        context=self.bound_context(
                            phase="response_read_failure",
                            method=method,
                            url=url,
                            http_status=status,
                            response_read_exception=type(read_error).__name__,
                        ),
                    ) from read_error
                finally:
                    http_error.close()
                self._accept_response_bytes(len(payload))
                return AttemptResult(
                    status=status,
                    headers=response_headers,
                    payload=payload,
                    final_url=url,
                    redirect_chain=redirect_chain,
                    terminal_url=current_url,
                    error=f"http_{status}",
                )
            except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError, OSError) as transport_error:
                return AttemptResult(
                    status=None,
                    headers={},
                    payload=None,
                    final_url=url if redirect_chain else None,
                    redirect_chain=redirect_chain,
                    terminal_url=current_url if redirect_chain else None,
                    error=("transport_timeout" if isinstance(transport_error, (TimeoutError, socket.timeout)) else "transport_connection_error"),
                )

            response_headers = self._headers(response)
            status_value = getattr(response, "status", None)
            status = int(status_value if status_value is not None else response.getcode())
            if status == HF_REDIRECT_STATUS:
                if hop_index == 1:
                    if hasattr(response, "close"):
                        response.close()
                    raise ExecutionBlocked(
                        "a second HTTP 302 redirect exceeded the one-hop bound",
                        context=self.bound_context(phase="redirect_hop_bound", http_status=status),
                    )
                target, metadata = self._validate_redirect_target(response_headers.get("location"))
                redirect_chain.append(metadata)
                self.redirect_hop_count += 1
                current_url = target
                if hasattr(response, "close"):
                    response.close()
                continue
            try:
                payload = self._read_bounded(
                    response,
                    headers=response_headers,
                    method=method,
                    url=url,
                )
            except ExecutionBlocked as blocked:
                if not blocked.context:
                    blocked.context = self.bound_context(phase="single_response_bound", method=method, url=url)
                raise
            self._accept_response_bytes(len(payload))
            if hasattr(response, "close"):
                response.close()
            return AttemptResult(
                status=status,
                headers=response_headers,
                payload=payload,
                final_url=url,
                redirect_chain=redirect_chain,
                terminal_url=current_url,
            )
        raise ExecutionBlocked("redirect loop exceeded the one-hop bound", context=self.bound_context(phase="redirect_hop_bound"))

    def request_with_retries(
        self,
        *,
        request_id: str,
        role: str,
        path: str,
        url: str,
        method: str,
        range_header: str | None,
        expected_status: int,
        artifact_name: str | None,
    ) -> tuple[AttemptResult, bytes | None]:
        ordinal = 0
        while True:
            result = self._attempt(method=method, url=url, range_header=range_header)
            retryable_http = result.status in {429, 503}
            no_response = result.status is None
            if result.status == expected_status:
                if result.final_url != url or len(result.redirect_chain) > 1 or any(
                    not self._safe_redirect_metadata(item) for item in result.redirect_chain
                ):
                    raise ExecutionBlocked(
                        f"{request_id}: redirect chain/final URL is outside the frozen route",
                        context=self.bound_context(
                            phase="route_integrity",
                            request_id=request_id,
                            http_status=result.status,
                            final_url=result.final_url,
                            redirect_chain=list(result.redirect_chain),
                        ),
                    )
                payload = result.payload or b""
                if role != "head_metadata_route" and len(payload) == 0:
                    raise ExecutionBlocked(
                        f"{request_id}: successful response has no payload",
                        context=self.bound_context(phase="empty_success", request_id=request_id),
                    )
                response_artifact = artifact_name
                response_payload = payload
                if role == "head_metadata_route":
                    response_artifact = artifact_name
                if response_artifact is None:
                    raise ExecutionBlocked(
                        f"{request_id}: successful response lacks an artifact name",
                        context=self.bound_context(phase="artifact_binding", request_id=request_id),
                    )
                self._check_artifact_slot(response_artifact)
                if response_artifact in self.artifact_payloads and self.artifact_payloads[response_artifact] != response_payload:
                    raise ExecutionBlocked(
                        f"{request_id}: response artifact was reused with different bytes",
                        context=self.bound_context(phase="artifact_binding", request_id=request_id),
                    )
                self.artifact_payloads[response_artifact] = response_payload
                self._append_request_row(
                    request_id=request_id,
                    role=role,
                    path=path,
                    url=url,
                    method=method,
                    range_header=range_header,
                    result=result,
                    attempt_ordinal=ordinal,
                    retry_ordinal=ordinal,
                    outcome="metadata_success",
                    failure_class="none",
                    retryable_error=None,
                    response_present=True,
                    artifact=response_artifact,
                    payload=response_payload,
                )
                return result, response_payload
            if retryable_http or no_response:
                retry_artifact = None
                retry_payload = result.payload if result.payload is not None else None
                if result.payload is not None:
                    self._check_retry_bound()
                    retry_artifact = f"evidence/retry/{request_id}-{ordinal:02d}.bin"
                    self._check_artifact_slot(retry_artifact)
                    self.artifact_payloads[retry_artifact] = result.payload
                else:
                    self._check_retry_bound()
                self._append_request_row(
                    request_id=request_id,
                    role=role,
                    path=path,
                    url=url,
                    method=method,
                    range_header=range_header,
                    result=result,
                    attempt_ordinal=ordinal,
                    retry_ordinal=ordinal,
                    outcome="retryable_failure",
                    failure_class="http_retryable" if retryable_http else "transport_no_response",
                    retryable_error=result.error or (f"http_{result.status}" if result.status is not None else "transport_connection_error"),
                    response_present=result.payload is not None,
                    artifact=retry_artifact,
                    payload=retry_payload,
                )
                self.retry_count += 1
                ordinal += 1
                continue
            raise ExecutionBlocked(
                f"{request_id}: non-retryable HTTP status {result.status!r} or invalid response",
                context=self.bound_context(
                    phase="source_request",
                    request_id=request_id,
                    http_status=result.status,
                    **self._redact_location(result.headers.get("location"))
                    if result.headers.get("location") is not None
                    else {"location_present": False},
                    final_url=result.final_url,
                    redirect_chain=list(result.redirect_chain),
                ),
            )

    def _append_request_row(
        self,
        *,
        request_id: str,
        role: str,
        path: str,
        url: str,
        method: str,
        range_header: str | None,
        result: AttemptResult,
        attempt_ordinal: int,
        retry_ordinal: int,
        outcome: str,
        failure_class: str,
        retryable_error: str | None,
        response_present: bool,
        artifact: str | None,
        payload: bytes | None,
    ) -> None:
        headers = result.headers
        self.request_rows.append(
            {
                "request_id": request_id,
                "attempt_id": f"attempt-{request_id}-{attempt_ordinal}",
                "attempt_ordinal": attempt_ordinal,
                "retry_ordinal": retry_ordinal,
                "evidence_role": role,
                "path": path,
                "request_url": url,
                "final_url": result.final_url,
                "redirect_chain": list(result.redirect_chain),
                "route_kind": METADATA_FOOTER_ROUTE_KIND,
                "immutable_revision": VNGRS_REVISION,
                "split": VNGRS_SPLIT,
                "http_method": method,
                "range_header": range_header,
                "http_status": result.status,
                "response_content_length": len(payload) if response_present and payload is not None else None,
                "content_range": headers.get("content-range"),
                "etag": headers.get("etag"),
                "lfs_oid": headers.get("x-linked-etag") or headers.get("etag"),
                "content_type": headers.get("content-type", "").split(";", 1)[0] or None,
                "content_encoding": headers.get("content-encoding", "identity"),
                "response_transferred_bytes": len(payload) if response_present and payload is not None else 0,
                "response_evidence_artifact": artifact,
                "response_sha256": hashlib.sha256(payload).hexdigest() if response_present and payload is not None else None,
                "request_outcome": outcome,
                "failure_class": failure_class,
                "retryable_error": retryable_error,
                "response_present": response_present,
            }
        )


def independent_writer_self_check() -> dict[str, Any]:
    """Use an independent standard Parquet writer before any source request."""

    try:
        import pyarrow as pa  # type: ignore[import-not-found]
        import pyarrow.parquet as pq  # type: ignore[import-not-found]
    except Exception as exc:
        return {"status": "BLOCKED", "reason": "pyarrow_unavailable", "detail": str(exc)}
    try:
        with tempfile.TemporaryDirectory(prefix="luna-151an-writer-check-") as directory:
            output = Path(directory) / "independent.parquet"
            table = pa.table({"text": [" bağımsız writer ", "footer parser check"]})
            pq.write_table(table, output)
            payload = output.read_bytes()
        if len(payload) < 8 or payload[-4:] != b"PAR1":
            return {"status": "BLOCKED", "reason": "independent_writer_bad_magic"}
        metadata_length = int.from_bytes(payload[-8:-4], "little")
        footer = payload[-(metadata_length + 8) :]
        parsed = parse_parquet_footer(footer)
        if parsed["row_count"] != 2 or parsed["row_group_count"] < 1:
            return {"status": "BLOCKED", "reason": "independent_writer_parser_mismatch", "parsed": parsed}
        return {
            "status": "PASS",
            "writer": "pyarrow",
            "writer_version": getattr(pa, "__version__", "unknown"),
            "parser": "vngrs_parquet_footer_compact_thrift_parser_v1",
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "payload_bytes": len(payload),
            "parsed_row_count": parsed["row_count"],
            "parsed_row_group_count": parsed["row_group_count"],
        }
    except Exception as exc:
        return {"status": "BLOCKED", "reason": "independent_writer_parser_failure", "detail": repr(exc)}


COMMAND_TIMEOUT_SECONDS = 30


def _run_command(command: list[str], *, timeout: int = COMMAND_TIMEOUT_SECONDS) -> dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        }
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "timed_out": False,
    }


def _parse_human_size(value: str) -> int | None:
    match = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([KMGTPE]?)(?:i?B)?\s*$", value, re.IGNORECASE)
    if not match:
        return None
    number = float(match.group(1))
    unit = match.group(2).upper()
    multiplier = 1024 ** " KMGTPE".index(unit) if unit else 1
    return int(number * multiplier)


def _du_bytes(du_result: Mapping[str, Any]) -> int | None:
    first_line = str(du_result.get("stdout", "")).splitlines()
    if not first_line:
        return None
    return _parse_human_size(first_line[0].split()[0])


def storage_preflight(root: str = METADATA_FOOTER_SCRATCH_ROOT) -> dict[str, Any]:
    """Run the mandatory local/HU storage, inode and resolved-path preflight."""

    checks = [
        _run_command(["du", "-xsh", HOME_ROOT]),
        _run_command(["df", "-h", HOME_ROOT, *SCRATCH_ROOTS]),
        _run_command(["df", "-i", HOME_ROOT, *SCRATCH_ROOTS]),
        _run_command(["readlink", "-f", root]),
    ]
    root_exists = os.path.lexists(root)
    resolved = checks[-1]["stdout"].strip()
    home_bytes = _du_bytes(checks[0])
    errors = [
        "new scratch root already exists" if root_exists else None,
        "resolved root does not equal frozen root" if resolved != root else None,
        "storage/preflight command timed out" if any(check.get("timed_out") for check in checks) else None,
        "storage command failed" if any(check["returncode"] != 0 for check in checks) else None,
        "HU home usage could not be parsed from successful du output"
        if checks[0]["returncode"] == 0 and home_bytes is None
        else None,
        "HU home usage is at or above the 30 GiB stop rule"
        if home_bytes is not None and home_bytes >= 30 * 1024**3
        else None,
    ]
    return {
        "root": root,
        "root_exists_before_wave": root_exists,
        "resolved_root": resolved,
        "home_usage_bytes": home_bytes,
        "home_usage_stop_threshold_bytes": 30 * 1024**3,
        "checks": checks,
        "errors": [error for error in errors if error],
        "complete": not any(errors),
    }


def post_run_storage_audit(root: str = METADATA_FOOTER_SCRATCH_ROOT) -> dict[str, Any]:
    """Run the mandatory post-run storage audit without deleting or migrating anything."""

    inventory: list[dict[str, Any]] = []
    if os.path.isdir(root):
        for path in sorted(Path(root).rglob("*")):
            if path.is_file():
                inventory.append({"path": str(path), "bytes": path.stat().st_size})
    return {
        "root": root,
        "files": inventory,
        "file_count": len(inventory),
        "total_bytes": sum(item["bytes"] for item in inventory),
        "du": _run_command(["du", "-xsh", HOME_ROOT]),
        "df_h": _run_command(["df", "-h", HOME_ROOT, *SCRATCH_ROOTS]),
        "df_i": _run_command(["df", "-i", HOME_ROOT, *SCRATCH_ROOTS]),
        "large_home_files": _run_command(
            ["find", HOME_ROOT, "-xdev", "-type", "f", "-size", "+500M", "-printf", "%s %p\\n"]
        ),
        "resolved_root": _run_command(["readlink", "-f", root]),
    }


def _header_value(headers: Mapping[str, str], *names: str) -> str | None:
    for name in names:
        value = headers.get(name.lower())
        if value:
            return value.strip()
    return None


def _jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(canonical_json_bytes(row) + b"\n" for row in rows)


def _artifact_rows(payloads: Mapping[str, bytes]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, payload in payloads.items():
        if name.startswith("evidence/retry/"):
            kind = "retry_response"
        elif "/footer_trailer/" in name:
            kind = "parquet_footer_trailer"
        elif "/footer/" in name:
            kind = "parquet_footer_bytes"
        elif "/license/" in name:
            kind = "license_attribution_bytes"
        else:
            kind = "head_metadata_route"
        if kind not in METADATA_FOOTER_ARTIFACT_KINDS:
            raise ExecutionBlocked(f"unknown artifact kind for {name}")
        rows.append(
            {
                "relative_path": name,
                "artifact_kind": kind,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "contains_corpus_rows": False,
            }
        )
    return rows


def _write_outputs(root: Path, package: Mapping[str, Any], payloads: Mapping[str, bytes], manifest_payload: bytes, audit_payload: bytes) -> None:
    root.mkdir(parents=True, exist_ok=False)
    top_level = {
        "selection_plan.json": package["selection_payload"],
        "shard_metadata_ledger.jsonl": package["shard_metadata"],
        "route_ledger.jsonl": package["route_ledger"],
        "request_ledger.jsonl": package["request_ledger"],
        "evidence_artifact_manifest.jsonl": manifest_payload,
        "feasibility_projection.json": package["feasibility_projection"],
        "metadata_footer_audit.json": package["metadata_footer_audit"],
    }
    for relative in METADATA_FOOTER_OUTPUT_PATHS[:-1]:
        target = root / relative
        if relative.endswith(".jsonl"):
            value = top_level[relative]
            payload = value if isinstance(value, bytes) else _jsonl(value)
        else:
            payload = canonical_json_bytes(top_level[relative])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    for name, payload in payloads.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    (root / "metadata_footer_audit.json").write_bytes(audit_payload)


def _execute_metadata_footer_wave_uncaught(
    *,
    root: str,
    preflight: Mapping[str, Any],
    writer_check: Mapping[str, Any],
) -> dict[str, Any]:
    """Run the source stage after preflight/self-check; the public wrapper records failures."""

    selection = build_selection_evidence()
    client = BoundedClient(urllib.request.build_opener(_NoRedirectHandler()))
    shard_rows: list[dict[str, Any]] = []
    route_rows: list[dict[str, Any]] = []
    license_artifact = "evidence/license/README.md"
    for index, path in enumerate(FROZEN_SELECTED_SHARD_PATHS):
        url = parquet_resolve_url(path)
        head_request_id = f"head_metadata_route-{index:05d}"
        head_result, _ = client.request_with_retries(
            request_id=head_request_id,
            role="head_metadata_route",
            path=path,
            url=url,
            method="HEAD",
            range_header=None,
            expected_status=200,
            artifact_name=f"evidence/head/{index:05d}.json",
        )
        headers = head_result.headers
        object_size = int(_header_value(headers, "x-linked-size", "content-length") or "0")
        object_id = _header_value(headers, "x-linked-etag", "etag")
        etag = _header_value(headers, "etag", "x-linked-etag")
        content_type = (_header_value(headers, "content-type") or "").split(";", 1)[0]
        content_encoding = _header_value(headers, "content-encoding") or "identity"
        if object_size <= 0 or not object_id or not etag or content_type not in {"application/octet-stream", "application/vnd.apache.parquet"}:
            raise ExecutionBlocked(f"{path}: HEAD lacks frozen object identity/size/content-type evidence")
        head_payload = canonical_json_bytes(
            {
                "path": path,
                "immutable_revision": VNGRS_REVISION,
                "object_id": object_id,
                "object_size_bytes": object_size,
                "request_url": url,
                "final_url": head_result.final_url,
                "redirect_chain": head_result.redirect_chain,
                "http_status": head_result.status,
                "content_length": object_size,
                "etag": etag,
                "lfs_oid": object_id,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        )
        client.replace_artifact_payload(f"evidence/head/{index:05d}.json", head_payload)
        client.request_rows[-1]["response_content_length"] = len(head_payload)
        client.request_rows[-1]["response_transferred_bytes"] = len(head_payload)
        client.request_rows[-1]["response_sha256"] = hashlib.sha256(head_payload).hexdigest()
        client.request_rows[-1]["etag"] = etag
        client.request_rows[-1]["lfs_oid"] = object_id
        client.request_rows[-1]["content_type"] = content_type
        client.request_rows[-1]["content_encoding"] = content_encoding

        trailer_id = f"footer_trailer-{index:05d}"
        trailer_result, trailer_payload = client.request_with_retries(
            request_id=trailer_id,
            role="footer_trailer",
            path=path,
            url=url,
            method="GET",
            range_header=METADATA_FOOTER_TRAILER_RANGE_HEADER,
            expected_status=206,
            artifact_name=f"evidence/footer_trailer/{index:05d}.bin",
        )
        if trailer_payload is None or len(trailer_payload) != 8:
            raise ExecutionBlocked(f"{path}: trailer response was not exactly eight bytes")
        trailer = parse_parquet_trailer(trailer_payload)
        metadata_length = int(trailer["metadata_length"])
        footer_length = metadata_length + 8
        if footer_length <= 8 or footer_length > 4 * 1024 * 1024 or object_size < footer_length:
            raise ExecutionBlocked(f"{path}: declared footer length is outside the frozen bound")
        expected_footer_range = f"bytes={object_size - footer_length}-"
        footer_id = f"footer_bytes-{index:05d}"
        footer_result, footer_payload = client.request_with_retries(
            request_id=footer_id,
            role="footer_bytes",
            path=path,
            url=url,
            method="GET",
            range_header=expected_footer_range,
            expected_status=206,
            artifact_name=f"evidence/footer/{index:05d}.bin",
        )
        if footer_payload is None:
            raise ExecutionBlocked(f"{path}: footer response was empty")
        parsed = parse_parquet_footer(footer_payload)
        shard_rows.append(
            {
                "path": path,
                "ordinal": selection["selected_ordinals"][index],
                "shard_count": VNGRS_SHARD_COUNT,
                "immutable_revision": VNGRS_REVISION,
                "row_count": parsed["row_count"],
                "row_group_count": parsed["row_group_count"],
                "row_group_layout": parsed["row_group_layout"],
                "compressed_bytes": parsed["compressed_bytes"],
                "uncompressed_bytes": parsed["uncompressed_bytes"],
                "object_id": object_id,
                "object_id_kind": "lfs_oid",
                "object_size_bytes": object_size,
                "object_sha256": None,
                "object_sha256_status": "unverified_footer_only",
                "etag": etag,
                "content_type": content_type,
                "content_encoding": content_encoding,
                "object_metadata_evidence_artifact": f"evidence/head/{index:05d}.json",
                "object_metadata_evidence_sha256": hashlib.sha256(head_payload).hexdigest(),
                "footer_trailer_evidence_artifact": f"evidence/footer_trailer/{index:05d}.bin",
                "footer_trailer_sha256": hashlib.sha256(trailer_payload).hexdigest(),
                "footer_metadata_length": metadata_length,
                "footer_evidence_artifact": f"evidence/footer/{index:05d}.bin",
                "footer_sha256": hashlib.sha256(footer_payload).hexdigest(),
                "license_evidence_artifact": license_artifact,
                "license_bytes_sha256": None,
            }
        )
        route_rows.append(
            {
                "path": path,
                "route_kind": METADATA_FOOTER_ROUTE_KIND,
                "request_url": url,
                "immutable_revision": VNGRS_REVISION,
                "split": VNGRS_SPLIT,
                "http_method": "GET",
                "range_header": METADATA_FOOTER_TRAILER_RANGE_HEADER,
                "footer_range_header_template": METADATA_FOOTER_FOOTER_RANGE_TEMPLATE,
                "status": "verified",
                "final_url": head_result.final_url,
                "redirect_chain": list(head_result.redirect_chain),
                "http_status": head_result.status,
                "content_length": object_size,
                "etag": etag,
                "lfs_oid": object_id,
                "content_type": content_type,
                "content_encoding": content_encoding,
                "route_evidence_artifact": f"evidence/head/{index:05d}.json",
                "route_evidence_sha256": hashlib.sha256(head_payload).hexdigest(),
            }
        )
        for request in client.request_rows:
            if request["request_id"] in {head_request_id, trailer_id, footer_id} and request["request_outcome"] == "metadata_success":
                request["etag"] = etag
                request["lfs_oid"] = object_id
                request["content_type"] = content_type
                request["content_encoding"] = content_encoding

    license_result, license_payload = client.request_with_retries(
        request_id="license_attribution-00000",
        role="license_attribution",
        path="README.md",
        url=dataset_license_resolve_url(),
        method="GET",
        range_header=None,
        expected_status=200,
        artifact_name=license_artifact,
    )
    if license_payload is None:
        raise ExecutionBlocked("license response was empty")
    license_sha = hashlib.sha256(license_payload).hexdigest()
    for row in shard_rows:
        row["license_bytes_sha256"] = license_sha
    for request in client.request_rows:
        if request["request_id"] == "license_attribution-00000" and request["request_outcome"] == "metadata_success":
            request["etag"] = _header_value(license_result.headers, "etag")
            request["content_type"] = (_header_value(license_result.headers, "content-type") or "text/plain").split(";", 1)[0]
            request["content_encoding"] = _header_value(license_result.headers, "content-encoding") or "identity"

    artifact_rows = _artifact_rows(client.artifact_payloads)
    manifest_payload = serialize_metadata_footer_artifact_manifest(artifact_rows)
    schedule = build_sampling_schedule(shard_rows)
    projection = build_metadata_footer_feasibility_projection(
        shard_rows, client.request_rows, evidence_artifact_count=len(artifact_rows)
    )
    audit = {
        "final_path": "metadata_footer_audit.json",
        "manifest_path": "evidence_artifact_manifest.jsonl",
        "scratch_root": root,
        "self_reference": False,
        "artifact_paths": [row["relative_path"] for row in artifact_rows],
        "artifact_count": len(artifact_rows),
        "artifact_total_bytes": sum(row["bytes"] for row in artifact_rows),
        "request_count": len(client.request_rows),
        "retry_count": client.retry_count,
        "logical_request_attempt_count": len(client.request_rows),
        "http_hop_count": client.http_hop_count,
        "redirect_hop_count": client.redirect_hop_count,
        "max_logical_request_attempts": METADATA_FOOTER_MAX_LOGICAL_ATTEMPTS,
        "max_http_hops": METADATA_FOOTER_MAX_HTTP_HOPS,
        "redirect_hop_retry_separation": True,
        "total_response_bytes": sum(row["response_transferred_bytes"] for row in client.request_rows),
        "max_response_bytes": max(row["response_transferred_bytes"] for row in client.request_rows),
        "output_file_count": len(artifact_rows) + len(METADATA_FOOTER_OUTPUT_PATHS),
        "new_inode_count": len(artifact_rows) + len(METADATA_FOOTER_OUTPUT_PATHS),
        "write_order": list(METADATA_FOOTER_OUTPUT_PATHS),
        "contract_sha256": METADATA_FOOTER_CONTRACT_SHA256,
        "manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
        "route_kind": METADATA_FOOTER_ROUTE_KIND,
        "corpus_rows_retrieved": 0,
    }
    audit_payload = canonical_json_bytes(audit)
    package = {
        "source_repository": VNGRS_REPOSITORY,
        "immutable_revision": VNGRS_REVISION,
        "split": VNGRS_SPLIT,
        "schema": list(VNGRS_SCHEMA),
        "selected_paths": list(selection["selected_paths"]),
        "selected_ordinals": list(selection["selected_ordinals"]),
        "selection_payload": selection,
        "selection_payload_sha256": hashlib.sha256(canonical_json_bytes(selection)).hexdigest(),
        "shard_metadata": shard_rows,
        "route_ledger": route_rows,
        "request_ledger": client.request_rows,
        "artifact_manifest": artifact_rows,
        "artifact_manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
        "sampling_schedule": schedule,
        "feasibility_projection": projection,
        "metadata_footer_audit": audit,
        "metadata_footer_audit_sha256": hashlib.sha256(audit_payload).hexdigest(),
        "output_paths": list(METADATA_FOOTER_OUTPUT_PATHS),
        "scratch_root": root,
    }
    validation = validate_metadata_footer_feasibility(
        package,
        artifact_payloads=client.artifact_payloads,
        artifact_manifest_payload=manifest_payload,
        metadata_footer_audit_payload=audit_payload,
    )
    if not validation["complete"]:
        raise ExecutionBlocked("completed package failed the frozen validator: " + "; ".join(validation["errors"][:8]))
    _write_outputs(Path(root), package, client.artifact_payloads, manifest_payload, audit_payload)
    return {
        "status": "PASS",
        "phase": "completed",
        "contract_sha256": METADATA_FOOTER_CONTRACT_SHA256,
        "preflight": preflight,
        "independent_writer": writer_check,
        "validation": validation,
        "request_count": len(client.request_rows),
        "retry_count": client.retry_count,
        "artifact_count": len(artifact_rows),
        "source_requests_started": len(client.request_rows),
        "root": root,
    }


def execute_metadata_footer_wave(*, root: str = METADATA_FOOTER_SCRATCH_ROOT) -> dict[str, Any]:
    """Execute the frozen 151an wave once, returning a compact result for 151ao/151ap."""

    preflight = storage_preflight(root)
    if not preflight["complete"]:
        return {
            "status": "BLOCKED",
            "phase": "preflight",
            "preflight": preflight,
            "source_requests_started": 0,
        }
    writer_check = independent_writer_self_check()
    if writer_check.get("status") != "PASS":
        return {
            "status": "BLOCKED",
            "phase": "independent_writer_self_check",
            "preflight": preflight,
            "independent_writer": dict(writer_check),
            "source_requests_started": 0,
        }
    try:
        result = _execute_metadata_footer_wave_uncaught(
            root=root,
            preflight=preflight,
            writer_check=writer_check,
        )
    except ExecutionBlocked as exc:
        audit = post_run_storage_audit(root)
        context = dict(exc.context)
        context.setdefault("phase", "execution")
        return {
            "status": "BLOCKED",
            "phase": context["phase"],
            "reason": str(exc),
            "failure_context": context,
            "preflight": preflight,
            "independent_writer": dict(writer_check),
            "post_run_storage_audit": audit,
        }
    except Exception as exc:  # fail closed and leave the exception in the compact terminal report
        audit = post_run_storage_audit(root)
        return {
            "status": "BLOCKED",
            "phase": "unexpected_executor_error",
            "reason": repr(exc),
            "failure_context": {
                "phase": "unexpected_executor_error",
                "attempt_count": None,
                "retry_count": None,
                "total_response_bytes": None,
            },
            "preflight": preflight,
            "independent_writer": dict(writer_check),
            "post_run_storage_audit": audit,
        }
    result["post_run_storage_audit"] = post_run_storage_audit(root)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Execute frozen Document 151an metadata/footer wave")
    parser.add_argument("--root", default=METADATA_FOOTER_SCRATCH_ROOT)
    args = parser.parse_args(argv)
    try:
        result = execute_metadata_footer_wave(root=args.root)
    except ExecutionBlocked as exc:
        result = {"status": "BLOCKED", "phase": "execution", "reason": str(exc)}
    except Exception as exc:  # fail closed and leave the exception in the compact terminal report
        result = {"status": "BLOCKED", "phase": "unexpected_executor_error", "reason": repr(exc)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result.get("status") == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
