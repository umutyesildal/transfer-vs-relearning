import json
from pathlib import Path

from scripts.archive_selected_qwen_to_home import collect_sources, copy_verified, sha256_file


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_collects_frozen_model_and_shared_tokenizer_then_verifies_copy(tmp_path: Path) -> None:
    tokenizer_root = tmp_path / "base"
    tokenizer_root.mkdir()
    for name in ("tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt"):
        (tokenizer_root / name).write_text(f"{name}\n", encoding="utf-8")
    base_manifest = tmp_path / "base_manifest.json"
    dataset_manifest = tmp_path / "dataset_manifest.json"
    write_json(base_manifest, {"status": "pinned"})
    write_json(dataset_manifest, {"status": "passed"})

    checkpoint = tmp_path / "checkpoint-75"
    checkpoint.mkdir()
    for name in ("model.safetensors", "config.json", "generation_config.json"):
        (checkpoint / name).write_bytes(f"selected-{name}".encode())
    training_manifest = tmp_path / "training_manifest.json"
    write_json(
        training_manifest,
        {
            "model": {
                "base_model_manifest": str(base_manifest),
                "base_model_manifest_payload": {"local_path_absolute": str(tokenizer_root)},
            },
            "dataset": {"dataset_manifest": str(dataset_manifest)},
        },
    )
    selected_manifest = tmp_path / "selected_artifact_manifest.json"
    write_json(
        selected_manifest,
        {
            "status": "frozen_selected_model_only",
            "seed": 42,
            "checkpoint_step": 75,
            "checkpoint": str(checkpoint),
            "training_manifest": str(training_manifest),
            "training_manifest_sha256": sha256_file(training_manifest),
            "files": {
                name: {
                    "path": str(checkpoint / name),
                    "sha256": sha256_file(checkpoint / name),
                    "size_bytes": (checkpoint / name).stat().st_size,
                }
                for name in ("model.safetensors", "config.json", "generation_config.json")
            },
        },
    )

    selections, observed_tokenizer_root, tokenizer_hashes = collect_sources([selected_manifest])
    assert selections[0]["label"] == "seed42_step75"
    assert observed_tokenizer_root == tokenizer_root
    assert set(tokenizer_hashes) == {
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.json",
        "merges.txt",
    }

    copied = copy_verified(
        checkpoint / "model.safetensors",
        tmp_path / "archive" / "seed42_step75" / "model.safetensors",
    )
    assert copied["sha256"] == sha256_file(checkpoint / "model.safetensors")
