from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.utils.io import sha256_file, write_json


CHECKPOINT_RE = re.compile(r"^checkpoint-(\d+)$")
MAX_HASH_BYTES = 16 * 1024 * 1024
NEVER_HASH_NAMES = {
    "model.safetensors",
    "pytorch_model.bin",
    "optimizer.pt",
    "scheduler.pt",
}


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def load_inventory_plan(config_path: Path) -> dict[str, Any]:
    config_path = config_path.resolve()
    config = _mapping(yaml.safe_load(config_path.read_text(encoding="utf-8")), "inventory config")
    if config.get("schema_version") != 1:
        raise ValueError("Only historical inventory schema_version 1 is supported")
    if config.get("source_roots_read_only") is not True:
        raise ValueError("Historical source roots must be read-only")
    if config.get("hash_large_weights_in_inventory") is not False:
        raise ValueError("First inventory must not hash large weights")
    if config.get("evaluation_authorized") is not False or config.get("training_authorized") is not False:
        raise ValueError("Historical inventory cannot authorize evaluation or training")
    families = _mapping(config.get("families"), "families")
    if not families:
        raise ValueError("At least one historical family is required")
    normalized: dict[str, dict[str, Any]] = {}
    for family_id, raw in families.items():
        family = _mapping(raw, f"families.{family_id}")
        root = Path(str(family.get("root", "")))
        if not root.is_absolute():
            raise ValueError(f"families.{family_id}.root must be absolute")
        steps = family.get("expected_steps")
        if not isinstance(steps, list) or not steps or any(not isinstance(step, int) for step in steps):
            raise ValueError(f"families.{family_id}.expected_steps must be integers")
        if steps != sorted(set(steps)):
            raise ValueError(f"families.{family_id}.expected_steps must be sorted and unique")
        normalized[family_id] = dict(family)
    output_root = Path(str(config.get("output_root", "")))
    if not output_root.is_absolute():
        raise ValueError("output_root must be absolute")
    return {
        "schema_version": 1,
        "name": str(config["name"]),
        "status": str(config["status"]),
        "execution_authorized": bool(config.get("execution_authorized", False)),
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "families": normalized,
        "output_root": str(output_root),
        "source_roots_read_only": True,
        "hash_large_weights_in_inventory": False,
    }


def _bounded_walk(root: Path, *, max_depth: int = 7, max_entries: int = 10_000) -> list[Path]:
    root = root.resolve()
    entries: list[Path] = []
    for current, directories, files in os.walk(root):
        current_path = Path(current)
        depth = len(current_path.relative_to(root).parts)
        if depth >= max_depth:
            directories[:] = []
        directories.sort()
        files.sort()
        entries.extend(current_path / name for name in directories)
        entries.extend(current_path / name for name in files)
        if len(entries) > max_entries:
            raise RuntimeError(f"Inventory entry bound exceeded under {root}")
    return entries


def _file_row(path: Path, *, root: Path) -> dict[str, Any]:
    size = path.stat().st_size
    hash_allowed = size <= MAX_HASH_BYTES and path.name not in NEVER_HASH_NAMES
    return {
        "path": str(path),
        "relative_path": path.relative_to(root).as_posix(),
        "bytes": size,
        "sha256": sha256_file(path) if hash_allowed else None,
        "hash_status": "complete" if hash_allowed else "deferred_large_or_weight_file",
    }


def inspect_historical_families(plan: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for family_id, family in plan["families"].items():
        root = Path(str(family["root"])).resolve()
        if not root.is_dir():
            rows.append(
                {
                    "family_id": family_id,
                    "status": "source_root_missing",
                    "root": str(root),
                    "checkpoint_rows": [],
                    "missing_steps": list(family["expected_steps"]),
                    "compact_manifests": [],
                }
            )
            continue
        entries = _bounded_walk(root)
        checkpoint_dirs: dict[int, list[Path]] = {}
        compact_manifests: list[dict[str, Any]] = []
        for path in entries:
            if path.is_dir():
                match = CHECKPOINT_RE.fullmatch(path.name)
                if match:
                    checkpoint_dirs.setdefault(int(match.group(1)), []).append(path)
                continue
            if path.name in {
                "training_manifest.json",
                "selected_artifact_manifest.json",
                "summary.json",
                "summary_metrics.json",
            }:
                compact_manifests.append(_file_row(path, root=root))
        checkpoint_rows: list[dict[str, Any]] = []
        duplicate_steps: list[int] = []
        for step in family["expected_steps"]:
            matches = checkpoint_dirs.get(step, [])
            if len(matches) > 1:
                duplicate_steps.append(step)
            if len(matches) != 1:
                continue
            checkpoint = matches[0]
            files = [
                _file_row(path, root=root)
                for path in sorted(checkpoint.iterdir())
                if path.is_file()
            ]
            checkpoint_rows.append(
                {
                    "step": step,
                    "path": str(checkpoint),
                    "files": files,
                    "model_weight_present": any(
                        row["relative_path"].endswith(("model.safetensors", "pytorch_model.bin"))
                        for row in files
                    ),
                }
            )
        observed_steps = {row["step"] for row in checkpoint_rows}
        missing_steps = [step for step in family["expected_steps"] if step not in observed_steps]
        selected_manifest: dict[str, Any] | None = None
        selected_manifest_path = family.get("selected_manifest_path")
        selected_manifest_sha256 = family.get("selected_manifest_sha256")
        if selected_manifest_path is not None:
            path = Path(str(selected_manifest_path))
            observed_sha256 = sha256_file(path) if path.is_file() else None
            selected_manifest = {
                "path": str(path),
                "bytes": path.stat().st_size if path.is_file() else None,
                "expected_sha256": selected_manifest_sha256,
                "observed_sha256": observed_sha256,
                "status": (
                    "complete_hash_verified"
                    if observed_sha256 == selected_manifest_sha256
                    else "missing_or_hash_mismatch"
                ),
            }
        status = (
            "inventory_complete"
            if not missing_steps
            and not duplicate_steps
            and (selected_manifest is None or selected_manifest["status"] == "complete_hash_verified")
            else "inventory_incomplete_or_ambiguous"
        )
        rows.append(
            {
                "family_id": family_id,
                "status": status,
                "role": family["role"],
                "model": family["model"],
                "revision": family["revision"],
                "root": str(root),
                "expected_steps": family["expected_steps"],
                "checkpoint_rows": checkpoint_rows,
                "missing_steps": missing_steps,
                "duplicate_steps": duplicate_steps,
                "compact_manifests": compact_manifests,
                "selected_manifest": selected_manifest,
                "large_weight_hashes_computed": False,
            }
        )
    return {
        "schema_version": 1,
        "status": (
            "inventory_complete"
            if all(row["status"] == "inventory_complete" for row in rows)
            else "inventory_incomplete"
        ),
        "config_path": plan["config_path"],
        "config_sha256": plan["config_sha256"],
        "families": rows,
        "source_roots_mutated": False,
        "evaluation_performed": False,
        "training_performed": False,
    }


def write_historical_inventory(plan: dict[str, Any]) -> dict[str, Any]:
    if plan.get("execution_authorized") is not True:
        raise PermissionError("Historical inventory execution is not authorized")
    result = inspect_historical_families(plan)
    output_root = Path(plan["output_root"])
    if output_root.exists():
        raise FileExistsError(f"Historical inventory output already exists: {output_root}")
    output_root.mkdir(parents=True)
    write_json(output_root / "inventory.json", result)
    inventory_path = output_root / "inventory.json"
    write_json(
        output_root / "final_inventory.json",
        {
            "schema_version": 1,
            "inventory_excludes": ["final_inventory.json"],
            "file_count": 1,
            "total_bytes": inventory_path.stat().st_size,
            "files": [
                {
                    "path": str(inventory_path),
                    "bytes": inventory_path.stat().st_size,
                    "sha256": sha256_file(inventory_path),
                }
            ],
        },
    )
    return result
