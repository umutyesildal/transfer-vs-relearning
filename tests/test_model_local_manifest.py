from __future__ import annotations

import json
from pathlib import Path

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest


def test_create_local_model_manifest_retargets_existing_source_manifest(tmp_path: Path) -> None:
    repo_root = Path.cwd()
    source_manifest = tmp_path / "source_manifest.json"
    local_model_dir = repo_root / "runs" / "training" / "demo_run" / "final_model"
    local_model_dir.mkdir(parents=True)
    (local_model_dir / "config.json").write_text("local-config", encoding="utf-8")
    (local_model_dir / "model.safetensors").write_bytes(b"local-weights")
    output_manifest = tmp_path / "local_manifest.json"
    source_payload = {
        "model_id": "HuggingFaceTB/SmolLM2-360M",
        "resolved_revision": "base-revision",
        "local_path": "/abs/base/path",
        "local_path_absolute": "/abs/base/path",
        "local_path_project_relative": "artifacts/models/HuggingFaceTB__SmolLM2-360M/base-revision",
        "parameter_count": 361821120,
        "tokenizer_class": "GPT2Tokenizer",
        "model_class": "AutoModelForCausalLM",
        "file_hashes": {"config.json": "abc"},
    }
    source_manifest.write_text(json.dumps(source_payload), encoding="utf-8")

    payload = create_local_model_manifest(
        source_manifest_path=source_manifest,
        local_model_dir=local_model_dir,
        output_manifest_path=output_manifest,
        model_id="m1_stage_a/final_model",
        resolved_revision="local-final-model",
        training_run_dir=repo_root / "runs" / "training" / "demo_run",
    )

    saved = json.loads(output_manifest.read_text(encoding="utf-8"))
    assert saved == payload
    assert payload["base_model_id"] == "HuggingFaceTB/SmolLM2-360M"
    assert payload["model_id"] == "m1_stage_a/final_model"
    assert payload["resolved_revision"] == "local-final-model"
    assert payload["local_path_absolute"] == str(local_model_dir.resolve())
    assert payload["local_path_project_relative"] == "runs/training/demo_run/final_model"
    assert payload["tokenizer_source_path"] == "artifacts/models/HuggingFaceTB__SmolLM2-360M/base-revision"
    assert payload["tokenizer_source_path_absolute"] == "/abs/base/path"
    assert payload["training_run_dir"] == str((repo_root / "runs" / "training" / "demo_run").resolve())
    assert set(payload["file_hashes"]) == {"config.json", "model.safetensors"}
    assert payload["file_hashes"]["config.json"] != "abc"
