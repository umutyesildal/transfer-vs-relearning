from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file, write_json


def safe_model_dir_name(model_id: str) -> str:
    return model_id.replace("/", "__")


def download_model_snapshot(model_id: str, revision: str | None, artifact_root: Path, local_files_only: bool = False) -> dict[str, Any]:
    from huggingface_hub import HfApi, snapshot_download
    import huggingface_hub
    import transformers
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    api = HfApi()
    info = api.model_info(model_id, revision=revision)
    resolved = info.sha
    artifact_root = artifact_root.resolve()
    target_dir = artifact_root / safe_model_dir_name(model_id) / resolved
    snapshot_path = snapshot_download(
        repo_id=model_id,
        revision=resolved,
        local_dir=str(target_dir),
        local_dir_use_symlinks=False,
        local_files_only=local_files_only,
    )
    tokenizer = AutoTokenizer.from_pretrained(snapshot_path, local_files_only=True)
    config = AutoConfig.from_pretrained(snapshot_path, local_files_only=True)
    model = AutoModelForCausalLM.from_config(config)
    parameter_count = sum(param.numel() for param in model.parameters())
    file_hashes = {
        str(path.relative_to(target_dir)): sha256_file(path)
        for path in sorted(target_dir.rglob("*"))
        if path.is_file()
    }
    manifest = {
        "model_id": model_id,
        "requested_revision": revision,
        "resolved_revision": resolved,
        "local_path": str(target_dir),
        "local_path_absolute": str(target_dir.resolve()),
        "local_path_project_relative": str(Path("artifacts/models") / safe_model_dir_name(model_id) / resolved),
        "download_timestamp": datetime.now(timezone.utc).isoformat(),
        "file_hashes": file_hashes,
        "transformers_version": transformers.__version__,
        "huggingface_hub_version": huggingface_hub.__version__,
        "tokenizer_class": tokenizer.__class__.__name__,
        "model_class": "AutoModelForCausalLM",
        "parameter_count": parameter_count,
    }
    write_json(artifact_root / safe_model_dir_name(model_id) / "model_manifest.json", manifest)
    return manifest
