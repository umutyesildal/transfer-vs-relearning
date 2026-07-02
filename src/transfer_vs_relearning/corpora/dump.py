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
    if fetch:
        status_text = _read_url(status_url)
        complete = status_is_complete(status_text)
        if not complete:
            raise ValueError(f"Configured dump is not complete: {status_url}")
        checksum = parse_checksum_line(_read_url(checksum_url), config["dump_filename"])
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
    )
    write_json(stage_dirs(config)["manifests"] / "dump_metadata.json", asdict(metadata))
    return metadata


def download_dump(config: dict[str, Any], metadata: DumpMetadata, force: bool = False) -> Path:
    raw_dir = stage_dirs(config)["raw"]
    target = raw_dir / config["dump_filename"]
    partial = target.with_suffix(target.suffix + ".partial")
    if target.exists() and not force:
        return target
    _disk_space_preflight(raw_dir, minimum_bytes=1024 * 1024)
    mode = "ab" if partial.exists() and not force else "wb"
    start = partial.stat().st_size if partial.exists() and not force else 0
    request = urllib.request.Request(metadata.dump_url)
    if start:
        request.add_header("Range", f"bytes={start}-")
    with urllib.request.urlopen(request) as response, partial.open(mode) as handle:
        shutil.copyfileobj(response, handle, length=1024 * 1024)
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
    write_json(stage_dirs(config)["manifests"] / "verify_manifest.json", {"path": str(target), "sha1": observed, "status": "verified"})
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
