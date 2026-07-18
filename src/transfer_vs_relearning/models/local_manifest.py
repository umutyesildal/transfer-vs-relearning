from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file, write_json


def create_local_model_manifest(
    *,
    source_manifest_path: Path,
    local_model_dir: Path,
    output_manifest_path: Path,
    model_id: str,
    resolved_revision: str = "local-checkpoint",
    training_checkpoint: str | None = None,
    training_run_dir: Path | None = None,
) -> dict[str, Any]:
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    local_model_dir = local_model_dir.resolve()
    output_manifest_path = output_manifest_path.resolve()
    if not local_model_dir.is_dir():
        raise FileNotFoundError(f"Local model directory does not exist: {local_model_dir}")
    local_files = sorted(path for path in local_model_dir.iterdir() if path.is_file())
    if not local_files:
        raise ValueError(f"Local model directory contains no files: {local_model_dir}")

    payload = dict(source_manifest)
    payload.update(
        {
            "base_model_id": source_manifest["model_id"],
            "model_id": model_id,
            "requested_revision": None,
            "resolved_revision": resolved_revision,
            "local_path": str(local_model_dir),
            "local_path_absolute": str(local_model_dir),
            "local_path_project_relative": _project_relative_or_absolute(local_model_dir),
            "tokenizer_source_path": source_manifest.get("local_path_project_relative") or source_manifest.get("local_path"),
            "tokenizer_source_path_absolute": source_manifest.get("local_path_absolute") or source_manifest.get("local_path"),
            "download_timestamp": datetime.now(timezone.utc).isoformat(),
            "file_hashes": {path.name: sha256_file(path) for path in local_files},
        }
    )
    if training_checkpoint is not None:
        payload["training_checkpoint"] = training_checkpoint
    if training_run_dir is not None:
        payload["training_run_dir"] = str(training_run_dir.resolve())

    output_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_manifest_path, payload)
    return payload


def _project_relative_or_absolute(path: Path) -> str:
    repo_root = Path(__file__).resolve().parents[3]
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)
