#!/usr/bin/env python3
"""Create a deterministic, secret-safe workspace preservation inventory.

The full JSONL inventory is local migration evidence. It records file hashes,
sizes, modes, and symlink targets without reading through symlinks. Git metadata
and the migration worktree itself are intentionally excluded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from collections import Counter
from pathlib import Path
from typing import Any


EXCLUDED_DIRECTORY_NAMES = {".git"}
EXCLUDED_ROOT_NAMES = {".migration"}
LOCAL_ONLY_DIRECTORY_NAMES = {
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "venv",
}
LOCAL_ONLY_FILE_NAMES = {".DS_Store"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_root", type=Path)
    parser.add_argument("output_jsonl", type=Path)
    parser.add_argument("summary_json", type=Path)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(relative_path: Path) -> str:
    parts = relative_path.parts
    name = relative_path.name
    if name == ".env" or name.startswith(".env."):
        return "secret_local_only"
    if name in LOCAL_ONLY_FILE_NAMES or any(
        part in LOCAL_ONLY_DIRECTORY_NAMES for part in parts
    ):
        return "reproducible_local_only"
    if parts and parts[0] in {".tmp", "tmp"}:
        return "temporary_local_only"
    return "project_or_artifact"


def iter_entries(root: Path):
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        relative_current = current_path.relative_to(root)
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in EXCLUDED_DIRECTORY_NAMES
            and not (
                relative_current == Path(".")
                and directory in EXCLUDED_ROOT_NAMES
            )
        )

        for name in sorted(directories + files):
            path = current_path / name
            relative_path = path.relative_to(root)
            file_stat = path.lstat()
            mode = stat.S_IMODE(file_stat.st_mode)
            common: dict[str, Any] = {
                "path": relative_path.as_posix(),
                "mode": f"{mode:04o}",
                "classification": classify(relative_path),
            }
            if path.is_symlink():
                target = os.readlink(path)
                yield {
                    **common,
                    "kind": "symlink",
                    "target": target,
                    "target_sha256": hashlib.sha256(target.encode()).hexdigest(),
                }
            elif path.is_file():
                yield {
                    **common,
                    "kind": "file",
                    "size": file_stat.st_size,
                    "sha256": sha256_file(path),
                }
            elif path.is_dir():
                yield {**common, "kind": "directory"}


def main() -> None:
    args = parse_args()
    root = args.source_root.resolve()
    output_jsonl = args.output_jsonl.resolve()
    summary_json = args.summary_json.resolve()
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    summary_json.parent.mkdir(parents=True, exist_ok=True)

    counts: Counter[str] = Counter()
    bytes_by_class: Counter[str] = Counter()
    total_bytes = 0

    with output_jsonl.open("w", encoding="utf-8") as handle:
        for entry in iter_entries(root):
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
            counts[f"kind:{entry['kind']}"] += 1
            counts[f"classification:{entry['classification']}"] += 1
            if entry["kind"] == "file":
                size = int(entry["size"])
                total_bytes += size
                bytes_by_class[entry["classification"]] += size

    manifest_sha256 = sha256_file(output_jsonl)
    summary = {
        "schema_version": 1,
        "source_root": str(root),
        "excluded_directory_names": sorted(EXCLUDED_DIRECTORY_NAMES),
        "excluded_root_names": sorted(EXCLUDED_ROOT_NAMES),
        "inventory_sha256": manifest_sha256,
        "counts": dict(sorted(counts.items())),
        "total_file_bytes": total_bytes,
        "file_bytes_by_classification": dict(sorted(bytes_by_class.items())),
    }
    summary_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
