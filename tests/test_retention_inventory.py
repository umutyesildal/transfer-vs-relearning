from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from transfer_vs_relearning.storage.retention_inventory import create_retention_inventory


def _config(root: Path, *, max_file_bytes: int = 64, max_total_bytes: int = 128) -> dict:
    return {
        "schema_version": 1,
        "name": "test-retention",
        "delete_enabled": False,
        "allowed_source_prefixes": [str(root.parent)],
        "source_roots": [{"id": "source", "path": str(root)}],
        "hash_policy": {
            "max_file_bytes": max_file_bytes,
            "max_total_bytes": max_total_bytes,
        },
        "scan_policy": {
            "max_entries": 100,
            "max_inventory_bytes": 100_000,
        },
    }


def _rows(output_root: Path) -> dict[str, dict]:
    return {
        row["relative_path"]: row
        for row in (
            json.loads(line)
            for line in (output_root / "retention_inventory.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        )
        if row["kind"] != "directory"
    }


def test_inventory_classifies_and_hashes_without_following_symlinks(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    (root / "summary.json").write_text('{"ok": true}\n', encoding="utf-8")
    (root / "model.safetensors").write_bytes(b"model")
    (root / ".gitkeep").write_bytes(b"")
    (root / "unknown.dat").write_bytes(b"unknown")
    (root / "large_results.csv").write_bytes(b"x" * 65)
    cache = root / "cache"
    cache.mkdir()
    (cache / "payload.bin").write_bytes(b"cache")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.json").write_text("{}\n", encoding="utf-8")
    os.symlink(outside, root / "outside_link")

    output = tmp_path / "inventory"
    summary = create_retention_inventory(_config(root), output)
    rows = _rows(output)

    assert rows["summary.json"]["retention_class"] == "keep_scientific_evidence"
    assert rows["summary.json"]["hash_status"] == "hashed"
    assert rows["model.safetensors"]["retention_class"] == "keep_model_or_training_state"
    assert rows["model.safetensors"]["hash_status"] == "skipped_by_class"
    assert rows[".gitkeep"]["retention_class"] == "candidate_empty_marker"
    assert rows["unknown.dat"]["retention_class"] == "review_required"
    assert rows["large_results.csv"]["hash_status"] == "skipped_by_file_limit"
    assert rows["cache/payload.bin"]["retention_class"] == "candidate_regenerable_cache"
    assert rows["outside_link"]["kind"] == "symlink"
    assert "outside_link/secret.json" not in rows
    assert summary["delete_enabled"] is False
    assert summary["scientific_files_deleted"] == 0
    assert summary["cleanup_candidates_are_proposals_only"] is True
    assert summary["scan_policy"]["observed_entries"] < 100


def test_inventory_is_fresh_and_rejects_unsafe_scope(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    (root / "summary.json").write_text("{}\n", encoding="utf-8")
    output = tmp_path / "inventory"
    create_retention_inventory(_config(root), output)

    with pytest.raises(FileExistsError):
        create_retention_inventory(_config(root), output)

    unsafe = _config(root)
    unsafe["allowed_source_prefixes"] = [str(tmp_path / "other")]
    (tmp_path / "other").mkdir()
    with pytest.raises(ValueError, match="outside allowed prefixes"):
        create_retention_inventory(unsafe, tmp_path / "unsafe")

    deleting = _config(root)
    deleting["delete_enabled"] = True
    with pytest.raises(ValueError, match="delete_enabled=false"):
        create_retention_inventory(deleting, tmp_path / "deleting")
