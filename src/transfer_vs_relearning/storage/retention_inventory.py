from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from transfer_vs_relearning.utils.io import sha256_file, write_json


EVIDENCE_SUFFIXES = {
    ".csv",
    ".err",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".out",
    ".parquet",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}
MODEL_STATE_SUFFIXES = {
    ".bin",
    ".ckpt",
    ".model",
    ".pt",
    ".pth",
    ".safetensors",
}
CACHE_PARTS = {
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "cache",
    "caches",
    "temp",
    "tmp",
}
EVIDENCE_NAME_MARKERS = {
    "audit",
    "config",
    "evaluation",
    "inventory",
    "manifest",
    "metric",
    "result",
    "summary",
    "trainer_state",
}


def _inside(path: Path, prefix: Path) -> bool:
    return path == prefix or path.is_relative_to(prefix)


def _classify(relative_path: Path, size: int) -> str:
    lowered_parts = {part.lower() for part in relative_path.parts}
    name = relative_path.name.lower()
    suffix = relative_path.suffix.lower()
    if size == 0 or name == ".gitkeep":
        return "candidate_empty_marker"
    if lowered_parts & CACHE_PARTS:
        return "candidate_regenerable_cache"
    if "incomplete" in relative_path.as_posix().lower():
        return "review_required_incomplete"
    if suffix in EVIDENCE_SUFFIXES or any(marker in name for marker in EVIDENCE_NAME_MARKERS):
        return "keep_scientific_evidence"
    if suffix in MODEL_STATE_SUFFIXES or lowered_parts & {"checkpoints", "models"}:
        return "keep_model_or_training_state"
    return "review_required"


def _iter_entries(root_id: str, root: Path) -> Iterable[dict[str, Any]]:
    def fail(error: OSError) -> None:
        raise error

    for current, directories, files in os.walk(
        root,
        topdown=True,
        followlinks=False,
        onerror=fail,
    ):
        directories[:] = sorted(directories)
        current_path = Path(current)
        for name in sorted(directories + files):
            path = current_path / name
            relative = path.relative_to(root)
            file_stat = path.lstat()
            common: dict[str, Any] = {
                "root_id": root_id,
                "relative_path": relative.as_posix(),
                "mode": f"{stat.S_IMODE(file_stat.st_mode):04o}",
                "mtime_ns": file_stat.st_mtime_ns,
            }
            if path.is_symlink():
                target = os.readlink(path)
                yield {
                    **common,
                    "kind": "symlink",
                    "bytes": len(target.encode("utf-8")),
                    "retention_class": "review_required_symlink",
                    "symlink_target": target,
                    "sha256": hashlib.sha256(target.encode("utf-8")).hexdigest(),
                    "hash_status": "symlink_target_hashed",
                }
            elif path.is_file():
                yield {
                    **common,
                    "kind": "file",
                    "bytes": file_stat.st_size,
                    "retention_class": _classify(relative, file_stat.st_size),
                    "sha256": None,
                    "hash_status": "pending_policy",
                }
            elif path.is_dir():
                yield {
                    **common,
                    "kind": "directory",
                    "bytes": 0,
                    "retention_class": "container",
                    "sha256": None,
                    "hash_status": "not_applicable",
                }


def _validate_config(config: dict[str, Any]) -> tuple[list[tuple[str, Path]], list[Path]]:
    if int(config.get("schema_version", 0)) != 1:
        raise ValueError("Unsupported retention inventory schema_version")
    if config.get("delete_enabled") is not False:
        raise ValueError("Retention inventory must keep delete_enabled=false")
    raw_prefixes = config.get("allowed_source_prefixes")
    raw_roots = config.get("source_roots")
    if not isinstance(raw_prefixes, list) or not raw_prefixes:
        raise ValueError("allowed_source_prefixes must be a non-empty list")
    if not isinstance(raw_roots, list) or not raw_roots:
        raise ValueError("source_roots must be a non-empty list")

    prefixes = [Path(str(value)).resolve(strict=True) for value in raw_prefixes]
    roots: list[tuple[str, Path]] = []
    seen_ids: set[str] = set()
    seen_paths: set[Path] = set()
    for row in raw_roots:
        if not isinstance(row, dict):
            raise ValueError("Every source_roots row must be a mapping")
        root_id = str(row.get("id", "")).strip()
        root = Path(str(row.get("path", ""))).resolve(strict=True)
        if not root_id or root_id in seen_ids:
            raise ValueError(f"Invalid or duplicate source root id: {root_id!r}")
        if root in seen_paths:
            raise ValueError(f"Duplicate source root path: {root}")
        if not root.is_dir():
            raise ValueError(f"Source root is not a directory: {root}")
        if not any(_inside(root, prefix) for prefix in prefixes):
            raise ValueError(f"Source root is outside allowed prefixes: {root}")
        roots.append((root_id, root))
        seen_ids.add(root_id)
        seen_paths.add(root)
    return roots, prefixes


def create_retention_inventory(config: dict[str, Any], output_root: Path) -> dict[str, Any]:
    roots, _ = _validate_config(config)
    output_root = output_root.resolve(strict=False)
    if output_root.exists():
        raise FileExistsError(f"Output root already exists: {output_root}")
    if any(_inside(output_root, root) or _inside(root, output_root) for _, root in roots):
        raise ValueError("Output root must not overlap a source root")

    policy = config.get("hash_policy")
    if not isinstance(policy, dict):
        raise ValueError("hash_policy must be a mapping")
    max_file_bytes = int(policy.get("max_file_bytes", 0))
    max_total_bytes = int(policy.get("max_total_bytes", 0))
    if max_file_bytes <= 0 or max_total_bytes <= 0:
        raise ValueError("Hash byte limits must be positive")
    scan_policy = config.get("scan_policy")
    if not isinstance(scan_policy, dict):
        raise ValueError("scan_policy must be a mapping")
    max_entries = int(scan_policy.get("max_entries", 0))
    max_inventory_bytes = int(scan_policy.get("max_inventory_bytes", 0))
    if max_entries <= 0 or max_inventory_bytes <= 0:
        raise ValueError("Scan limits must be positive")

    output_root.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{output_root.name}.tmp.", dir=output_root.parent)
    )
    manifest_path = staging / "retention_inventory.jsonl"
    counts: Counter[str] = Counter()
    bytes_by_class: Counter[str] = Counter()
    bytes_by_root: Counter[str] = Counter()
    hashed_bytes = 0
    entry_count = 0

    try:
        with manifest_path.open("w", encoding="utf-8") as handle:
            for root_id, root in roots:
                for entry in _iter_entries(root_id, root):
                    entry_count += 1
                    if entry_count > max_entries:
                        raise RuntimeError(f"Inventory exceeded max_entries={max_entries}")
                    if entry["kind"] == "file":
                        size = int(entry["bytes"])
                        retention_class = str(entry["retention_class"])
                        hash_candidate = retention_class in {
                            "candidate_empty_marker",
                            "keep_scientific_evidence",
                            "review_required",
                            "review_required_incomplete",
                        }
                        if not hash_candidate:
                            entry["hash_status"] = "skipped_by_class"
                        elif size > max_file_bytes:
                            entry["hash_status"] = "skipped_by_file_limit"
                        elif hashed_bytes + size > max_total_bytes:
                            entry["hash_status"] = "skipped_by_total_budget"
                        else:
                            path = root / str(entry["relative_path"])
                            entry["sha256"] = sha256_file(path)
                            entry["hash_status"] = "hashed"
                            hashed_bytes += size

                    handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
                    if handle.tell() > max_inventory_bytes:
                        raise RuntimeError(
                            f"Inventory exceeded max_inventory_bytes={max_inventory_bytes}"
                        )
                    counts[f"kind:{entry['kind']}"] += 1
                    counts[f"retention_class:{entry['retention_class']}"] += 1
                    counts[f"hash_status:{entry['hash_status']}"] += 1
                    if entry["kind"] == "file":
                        size = int(entry["bytes"])
                        bytes_by_class[str(entry["retention_class"])] += size
                        bytes_by_root[str(entry["root_id"])] += size

        summary = {
            "schema_version": 1,
            "name": str(config.get("name", "hu-retention-inventory")),
            "delete_enabled": False,
            "source_roots": [
                {"id": root_id, "path": str(root)} for root_id, root in roots
            ],
            "hash_policy": {
                "max_file_bytes": max_file_bytes,
                "max_total_bytes": max_total_bytes,
                "hashed_bytes": hashed_bytes,
            },
            "scan_policy": {
                "max_entries": max_entries,
                "max_inventory_bytes": max_inventory_bytes,
                "observed_entries": entry_count,
                "observed_inventory_bytes": manifest_path.stat().st_size,
            },
            "counts": dict(sorted(counts.items())),
            "file_bytes_by_retention_class": dict(sorted(bytes_by_class.items())),
            "file_bytes_by_root": dict(sorted(bytes_by_root.items())),
            "inventory_sha256": sha256_file(manifest_path),
            "cleanup_candidates_are_proposals_only": True,
            "scientific_files_deleted": 0,
        }
        write_json(staging / "summary.json", summary)
        os.replace(staging, output_root)
        return summary
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
