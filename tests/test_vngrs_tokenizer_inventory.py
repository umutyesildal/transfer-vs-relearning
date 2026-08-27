import hashlib
import json

import pytest

from transfer_vs_relearning.corpora.vngrs.tokenizer_inventory import extract_tokenizer_inventory


def payload(value: dict) -> tuple[bytes, str]:
    raw = json.dumps(value, sort_keys=True).encode("utf-8")
    return raw, hashlib.sha256(raw).hexdigest()


def test_inventory_extracts_only_tokenizer_rows_without_opening_assets() -> None:
    root = "/vol/tmp2/example/epoch_snapshots/epoch-036"
    snapshot, snapshot_sha = payload(
        {
            "files": [
                {"path": "model-00001-of-00002.safetensors", "bytes": 100, "sha256": "1" * 64},
                {"path": "tokenizer_config.json", "bytes": 20, "sha256": "b" * 64},
                {"path": "tokenizer.json", "bytes": 30, "sha256": "a" * 64},
                {"path": "special_tokens_map.json", "bytes": 10, "sha256": "c" * 64},
            ]
        }
    )
    model, model_sha = payload({"local_path_absolute": root, "tokenizer_source_path_absolute": root})
    result = extract_tokenizer_inventory(
        role="olmo",
        snapshot_root=root,
        snapshot_manifest_payload=snapshot,
        snapshot_manifest_sha256=snapshot_sha,
        model_manifest_payload=model,
        model_manifest_sha256=model_sha,
    )
    assert result["status"] == "INVENTORY_CLOSED_FROM_PRESERVED_MANIFESTS"
    assert [row["path"] for row in result["assets"]] == [
        "special_tokens_map.json",
        "tokenizer.json",
        "tokenizer_config.json",
    ]
    assert result["asset_bytes"] == 60
    assert result["model_weight_files_opened"] == 0
    assert result["tokenizer_asset_files_opened"] == 0
    assert len(result["tokenizer_asset_manifest_sha256"]) == 64


def test_inventory_rejects_hash_root_missing_asset_and_unsafe_path() -> None:
    root = "/vol/tmp2/example/epoch-036"
    model, model_sha = payload({"local_path_absolute": root})
    snapshot, snapshot_sha = payload({"files": [{"path": "tokenizer.json", "bytes": 1, "sha256": "a" * 64}]})
    with pytest.raises(ValueError, match="required tokenizer assets"):
        extract_tokenizer_inventory(
            role="qwen", snapshot_root=root, snapshot_manifest_payload=snapshot,
            snapshot_manifest_sha256=snapshot_sha, model_manifest_payload=model,
            model_manifest_sha256=model_sha,
        )
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        extract_tokenizer_inventory(
            role="qwen", snapshot_root=root, snapshot_manifest_payload=snapshot,
            snapshot_manifest_sha256="0" * 64, model_manifest_payload=model,
            model_manifest_sha256=model_sha,
        )
    unsafe, unsafe_sha = payload({"files": [{"path": "../tokenizer.json", "bytes": 1, "sha256": "a" * 64}]})
    with pytest.raises(ValueError, match="unsafe"):
        extract_tokenizer_inventory(
            role="qwen", snapshot_root=root, snapshot_manifest_payload=unsafe,
            snapshot_manifest_sha256=unsafe_sha, model_manifest_payload=model,
            model_manifest_sha256=model_sha,
        )

