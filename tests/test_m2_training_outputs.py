from __future__ import annotations

import json
from pathlib import Path

import pytest

from transfer_vs_relearning.pipeline.m2_training_outputs import (
    M2_CHECKPOINT_UPDATES,
    finalize_m2_training_outputs,
)
from transfer_vs_relearning.utils.io import sha256_file


def _run(tmp_path: Path) -> Path:
    run = tmp_path / "run"
    (run / "checkpoints").mkdir(parents=True)
    base = tmp_path / "parent.json"
    model_root = tmp_path / "parent_model"
    model_root.mkdir()
    (model_root / "tokenizer.json").write_text("{}\n", encoding="utf-8")
    base.write_text(
        json.dumps(
            {
                "model_id": "test/model",
                "resolved_revision": "frozen",
                "local_path_absolute": str(model_root),
                "tokenizer_source_path_absolute": str(model_root),
            }
        ),
        encoding="utf-8",
    )
    checkpoint_dirs = []
    for update in M2_CHECKPOINT_UPDATES:
        checkpoint = run / "checkpoints" / f"checkpoint-{update}"
        checkpoint.mkdir()
        (checkpoint / "config.json").write_text("{}\n", encoding="utf-8")
        (checkpoint / "model.safetensors").write_text(f"weights-{update}\n", encoding="utf-8")
        (checkpoint / "optimizer.pt").write_text("excluded\n", encoding="utf-8")
        checkpoint_dirs.append(str(checkpoint))
    training = {
        "status": "complete",
        "config": {
            "metadata": {"role": "qwen", "arm": "M2-A"},
            "training": {"max_steps": 762, "checkpoint_updates": list(M2_CHECKPOINT_UPDATES)},
        },
        "model": {
            "base_model_manifest": str(base),
            "base_model_manifest_sha256": sha256_file(base),
        },
        "result": {
            "estimated_optimizer_steps": 762,
            "checkpoint_updates": list(M2_CHECKPOINT_UPDATES),
            "checkpoint_dirs": checkpoint_dirs,
        },
    }
    (run / "training_manifest.json").write_text(json.dumps(training), encoding="utf-8")
    return run


def test_finalize_m2_outputs_hash_closes_all_ten_updates(tmp_path: Path) -> None:
    run = _run(tmp_path)
    output = tmp_path / "binding"
    result = finalize_m2_training_outputs(run, output, role="qwen", arm="M2-A")
    assert result["status"] == "M2_TRAINING_OUTPUT_BINDING_PASS"
    manifest = json.loads((output / "checkpoint_manifest.json").read_text(encoding="utf-8"))
    assert [row["update"] for row in manifest["checkpoints"]] == list(M2_CHECKPOINT_UPDATES)
    assert [row["update"] for row in manifest["checkpoints"] if row["full"]] == [381, 762]
    assert all("optimizer.pt" not in row["model_file_hashes"] for row in manifest["checkpoints"])


def test_finalize_m2_outputs_normalizes_lexicographic_manifest_order(tmp_path: Path) -> None:
    run = _run(tmp_path)
    training_path = run / "training_manifest.json"
    training = json.loads(training_path.read_text(encoding="utf-8"))
    training["result"]["checkpoint_dirs"] = sorted(training["result"]["checkpoint_dirs"])
    assert Path(training["result"]["checkpoint_dirs"][-2]).name == "checkpoint-76"
    training_path.write_text(json.dumps(training), encoding="utf-8")

    output = tmp_path / "binding"
    finalize_m2_training_outputs(run, output, role="qwen", arm="M2-A")
    manifest = json.loads((output / "checkpoint_manifest.json").read_text(encoding="utf-8"))
    assert [row["update"] for row in manifest["checkpoints"]] == list(M2_CHECKPOINT_UPDATES)


def test_finalize_m2_outputs_rejects_missing_precommitted_checkpoint(tmp_path: Path) -> None:
    run = _run(tmp_path)
    missing = run / "checkpoints/checkpoint-381"
    for child in missing.iterdir():
        child.unlink()
    missing.rmdir()
    with pytest.raises(ValueError, match="exactly the ten"):
        finalize_m2_training_outputs(run, tmp_path / "binding", role="qwen", arm="M2-A")
