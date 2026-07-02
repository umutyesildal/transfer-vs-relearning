from __future__ import annotations

import hashlib
import os
import shutil
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.corpora.config import ensure_corpus_dirs, stage_dirs
from transfer_vs_relearning.utils.io import write_json


@dataclass(frozen=True)
class DumpMetadata:
    corpus_id: str
    project: str
    dump_date: str
    dump_url: str
    checksum_url: str
    checksum_algorithm: str
    expected_checksum: str | None
    dump_status_complete: bool
    resolved_at: str
    dump_filename: str
    resolution_mode: str
    status_url: str


def status_is_complete(status_text: str) -> bool:
    lowered = status_text.lower()
    return "dump complete" in lowered or "status: done" in lowered or '"status": "done"' in lowered


def parse_checksum_line(text: str, filename: str) -> str:
    matches = []
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[-1] == filename:
            checksum = parts[0]
            if len(checksum) != 40 or any(ch not in "0123456789abcdefABCDEF" for ch in checksum):
                raise ValueError(f"Invalid SHA-1 checksum for {filename}")
            matches.append(checksum.lower())
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one checksum for {filename}, found {len(matches)}")
    return matches[0]


def resolve_dump_metadata(config: dict[str, Any], fetch: bool = False) -> DumpMetadata:
    ensure_corpus_dirs(config)
    base = config["dump_base_url"]
    dump_url = base + config["dump_filename"]
    checksum_url = base + config["checksum_filename"]
    status_url = base + "dumpstatus.json"
    complete = False
    checksum = None
    mode = "configured_only"
    if fetch:
        status_text = _read_url(status_url)
        complete = status_is_complete(status_text)
        if not complete:
            raise ValueError(f"Configured dump is not complete: {status_url}")
        checksum = parse_checksum_line(_read_url(checksum_url), config["dump_filename"])
        if not checksum:
            raise ValueError("Official metadata resolution did not produce an expected checksum")
        mode = "official"
    metadata = DumpMetadata(
        corpus_id=config["corpus_id"],
        project=config["project"],
        dump_date=str(config["dump_date"]),
        dump_url=dump_url,
        checksum_url=checksum_url,
        checksum_algorithm=config["checksum_algorithm"],
        expected_checksum=checksum,
        dump_status_complete=complete,
        resolved_at=datetime.now(timezone.utc).isoformat(),
        dump_filename=config["dump_filename"],
        resolution_mode=mode,
        status_url=status_url,
    )
    path = "dump_metadata.json" if fetch else "configured_dump_metadata.json"
    write_json(stage_dirs(config)["manifests"] / path, asdict(metadata))
    return metadata


def load_official_dump_metadata(config: dict[str, Any]) -> DumpMetadata:
    path = stage_dirs(config)["manifests"] / "dump_metadata.json"
    if not path.exists():
        raise ValueError("Official dump metadata is missing; run resolve --fetch-metadata first")
    import json

    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "resolution_mode": "official",
        "dump_status_complete": True,
        "dump_date": str(config["dump_date"]),
        "dump_filename": config["dump_filename"],
        "dump_url": config["dump_base_url"] + config["dump_filename"],
        "checksum_url": config["dump_base_url"] + config["checksum_filename"],
    }
    for key, expected in required.items():
        if payload.get(key) != expected:
            raise ValueError(f"Official metadata mismatch for {key}: expected {expected!r}, observed {payload.get(key)!r}")
    if not payload.get("expected_checksum"):
        raise ValueError("Official metadata is missing expected_checksum")
    return DumpMetadata(**payload)


def download_dump(config: dict[str, Any], metadata: DumpMetadata, force: bool = False) -> Path:
    raw_dir = stage_dirs(config)["raw"]
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / config["dump_filename"]
    partial = target.with_suffix(target.suffix + ".partial")
    if _has_verified_target(config, target, metadata) and not force:
        return target
    if target.exists() and not force:
        raise ValueError(f"Existing dump is unverified or incompatible: {target}")
    minimum = int(config.get("download", {}).get("minimum_free_bytes", 20 * 1024 * 1024 * 1024))
    _disk_space_preflight(raw_dir, minimum_bytes=minimum)
    mode = "ab" if partial.exists() and not force else "wb"
    start = partial.stat().st_size if partial.exists() and not force else 0
    request = urllib.request.Request(metadata.dump_url)
    if start:
        request.add_header("Range", f"bytes={start}-")
    with urllib.request.urlopen(request) as response:
        status = getattr(response, "status", response.getcode())
        expected_length = response.headers.get("Content-Length")
        if start:
            content_range = response.headers.get("Content-Range")
            if status != 206:
                raise ValueError(f"Server ignored Range request for resume: status {status}; partial preserved at {partial}")
            _validate_content_range(content_range, start)
        elif status not in (200, 206):
            raise ValueError(f"Unexpected HTTP status {status} for {metadata.dump_url}")
        with partial.open(mode) as handle:
            shutil.copyfileobj(response, handle, length=1024 * 1024)
            handle.flush()
            os.fsync(handle.fileno())
    write_json(stage_dirs(config)["manifests"] / "download_manifest.json", {
        "status": "downloaded_unverified",
        "partial_path": str(partial),
        "target_path": str(target),
        "artifact_path": str(partial),
        "bytes_present": partial.stat().st_size,
        "resume_start": start,
        "http_status": status,
        "response_content_length": expected_length,
        "expected_total_bytes": _expected_total_bytes(response.headers.get("Content-Range"), expected_length, start),
        "observed_partial_size": partial.stat().st_size,
    })
    return partial


def verify_dump(config: dict[str, Any], expected_sha1: str) -> Path:
    target = stage_dirs(config)["raw"] / config["dump_filename"]
    partial = target.with_suffix(target.suffix + ".partial")
    candidate = partial if partial.exists() else target
    observed = sha1_file(candidate)
    if observed != expected_sha1.lower():
        raise ValueError(f"Checksum mismatch for {candidate}: expected {expected_sha1}, observed {observed}")
    if candidate == partial:
        os.replace(partial, target)
    write_json(stage_dirs(config)["manifests"] / "verify_manifest.json", {
        "path": str(target),
        "sha1": observed,
        "status": "verified",
        "dump_filename": config["dump_filename"],
        "dump_date": str(config["dump_date"]),
    })
    return target


def sha1_file(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_url(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8", errors="replace")


def _disk_space_preflight(path: Path, minimum_bytes: int) -> None:
    usage = shutil.disk_usage(path)
    if usage.free < minimum_bytes:
        raise OSError(f"Insufficient disk space under {path}: {usage.free} bytes free")


def _validate_content_range(value: str | None, expected_start: int) -> None:
    if not value or not value.startswith("bytes "):
        raise ValueError(f"Missing or invalid Content-Range for resumed download: {value!r}")
    range_part = value.removeprefix("bytes ").split("/", 1)[0]
    start_text, _, _ = range_part.partition("-")
    if int(start_text) != expected_start:
        raise ValueError(f"Content-Range starts at {start_text}, expected {expected_start}")


def _expected_total_bytes(content_range: str | None, content_length: str | None, start: int) -> int | None:
    if content_range and "/" in content_range:
        total = content_range.rsplit("/", 1)[-1]
        return None if total == "*" else int(total)
    if content_length:
        return start + int(content_length)
    return None


def _has_verified_target(config: dict[str, Any], target: Path, metadata: DumpMetadata) -> bool:
    manifest_path = stage_dirs(config)["manifests"] / "verify_manifest.json"
    if not target.exists() or not manifest_path.exists():
        return False
    import json

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return (
        manifest.get("status") == "verified"
        and manifest.get("path") == str(target)
        and manifest.get("dump_filename") == config["dump_filename"]
        and manifest.get("dump_date") == str(config["dump_date"])
        and (metadata.expected_checksum is None or manifest.get("sha1") == metadata.expected_checksum)
    )
