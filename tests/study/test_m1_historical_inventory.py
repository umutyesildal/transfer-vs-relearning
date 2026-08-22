from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.study.m1_historical_inventory import (
    inspect_historical_families,
    load_inventory_plan,
    write_historical_inventory,
)


def _config(tmp_path: Path, *, authorized: bool) -> Path:
    root = tmp_path / "family"
    for step in (25, 50):
        checkpoint = root / "run" / f"checkpoint-{step}"
        checkpoint.mkdir(parents=True)
        (checkpoint / "model.safetensors").write_bytes(b"weight")
        (checkpoint / "config.json").write_text("{}", encoding="utf-8")
    (root / "run" / "training_manifest.json").write_text("{}", encoding="utf-8")
    payload = {
        "schema_version": 1,
        "name": "fixture-history",
        "status": "frozen",
        "execution_authorized": authorized,
        "source_roots_read_only": True,
        "hash_large_weights_in_inventory": False,
        "evaluation_authorized": False,
        "training_authorized": False,
        "families": {
            "qwen": {
                "role": "historical_backfill",
                "model": "Qwen/Qwen2.5-1.5B",
                "revision": "a" * 40,
                "root": str(root),
                "expected_steps": [25, 50],
                "expected_epochs": 36,
                "expected_updates_per_epoch": 7,
                "selected_step": 50,
            }
        },
        "output_root": str(tmp_path / "inventory"),
    }
    path = tmp_path / "inventory.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_inventory_records_checkpoint_presence_without_hashing_weights(tmp_path: Path) -> None:
    plan = load_inventory_plan(_config(tmp_path, authorized=False))
    result = inspect_historical_families(plan)

    assert result["status"] == "inventory_complete"
    family = result["families"][0]
    assert [row["step"] for row in family["checkpoint_rows"]] == [25, 50]
    weight_rows = [
        file
        for checkpoint in family["checkpoint_rows"]
        for file in checkpoint["files"]
        if file["relative_path"].endswith("model.safetensors")
    ]
    assert weight_rows[0]["sha256"] is None
    assert weight_rows[0]["hash_status"] == "deferred_large_or_weight_file"
    assert result["source_roots_mutated"] is False


def test_inventory_refuses_write_without_authority(tmp_path: Path) -> None:
    plan = load_inventory_plan(_config(tmp_path, authorized=False))
    with pytest.raises(PermissionError, match="not authorized"):
        write_historical_inventory(plan)


def test_inventory_writes_once_to_fresh_root_when_authorized(tmp_path: Path) -> None:
    plan = load_inventory_plan(_config(tmp_path, authorized=True))
    result = write_historical_inventory(plan)
    assert result["status"] == "inventory_complete"
    assert (Path(plan["output_root"]) / "inventory.json").is_file()
    assert (Path(plan["output_root"]) / "final_inventory.json").is_file()
    with pytest.raises(FileExistsError):
        write_historical_inventory(plan)
