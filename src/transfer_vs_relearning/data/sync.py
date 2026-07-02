from __future__ import annotations

import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.constants import DATASET_FILES
from transfer_vs_relearning.data.validation import validate_dataset
from transfer_vs_relearning.utils.io import read_jsonl, sha256_file, sha256_text, write_json


def resolve_git_ref(source_repo: str, ref: str) -> str:
    output = subprocess.check_output(["git", "ls-remote", source_repo, ref], text=True)
    if not output.strip():
        raise ValueError(f"Could not resolve {ref!r} in {source_repo}")
    return output.split()[0]


def sync_synthetic_dataset(source_repo: str, ref: str, version: str, output_root: Path) -> dict[str, Any]:
    commit = resolve_git_ref(source_repo, ref)
    dataset_dir = output_root / version
    if dataset_dir.exists() and any(dataset_dir.iterdir()):
        existing_manifest = dataset_dir / "manifest.json"
        if not existing_manifest.exists():
            raise FileExistsError(f"{dataset_dir} already exists without a manifest; refusing to overwrite")
        raise FileExistsError(f"{dataset_dir} already exists; use a new version for different hashes")

    with tempfile.TemporaryDirectory(prefix="synthetic-source-") as tmp:
        source_dir = Path(tmp) / "repo"
        subprocess.check_call(["git", "clone", "--quiet", source_repo, str(source_dir)])
        subprocess.check_call(["git", "-C", str(source_dir), "checkout", "--quiet", commit])
        for rel_path in DATASET_FILES.values():
            src = source_dir / rel_path
            if not src.exists():
                raise FileNotFoundError(f"Required source artifact missing: {rel_path}")
            dst = dataset_dir / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    validation = validate_dataset(dataset_dir, write_outputs=True)
    generation_summary_path = dataset_dir / DATASET_FILES["generation_summary"]
    generation_seed = None
    if generation_summary_path.exists():
        import json

        generation_seed = json.loads(generation_summary_path.read_text(encoding="utf-8")).get("random_seed")

    manifest = {
        "dataset_version": version,
        "source_repository": source_repo,
        "source_branch": ref,
        "source_commit_sha": commit,
        "retrieval_timestamp": datetime.now(timezone.utc).isoformat(),
        "generation_seed": generation_seed,
        "artifacts": validation["files"],
        **{key: value for key, value in validation.items() if key != "files"},
    }
    manifest_hash = sha256_text(__import__("json").dumps(manifest, ensure_ascii=False, sort_keys=True))
    manifest["manifest_sha256"] = manifest_hash
    write_json(dataset_dir / "manifest.json", manifest)
    return manifest
