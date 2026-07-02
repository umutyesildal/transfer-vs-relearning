from __future__ import annotations

import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.corpora.config import config_hash, stage_dirs
from transfer_vs_relearning.utils.io import sha256_file, write_json


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def write_corpus_manifest(config: dict[str, Any], status: str, warnings: list[str] | None = None) -> dict[str, Any]:
    dirs = stage_dirs(config)
    artifacts = {}
    for name, directory in dirs.items():
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*")):
            if path.is_file() and path.stat().st_size < 2_000_000:
                artifacts[str(path.relative_to(dirs["manifests"].parents[0]))] = {
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
    dataset_manifest = Path(config["contamination"]["synthetic_dataset_dir"]) / "manifest.json"
    payload = {
        "corpus_id": config["corpus_id"],
        "wikimedia_source_project": config["project"],
        "dump_date": str(config["dump_date"]),
        "source_urls": {
            "dump": config["dump_base_url"] + config["dump_filename"],
            "checksum": config["dump_base_url"] + config["checksum_filename"],
        },
        "source_text_license": "CC BY-SA 4.0 and GFDL, per Wikimedia dump provenance",
        "attribution_requirement": "Retain Wikimedia attribution and license provenance for derived corpora.",
        "acquisition_timestamp": datetime.now(timezone.utc).isoformat(),
        "extraction_tool_versions": {
            "mwxml": config["extraction"]["mwxml_version"],
            "mwparserfromhell": config["extraction"]["mwparserfromhell_version"],
        },
        "processing_git_commit": git_commit(),
        "processing_config_hash": config_hash(config),
        "python_version": platform.python_version(),
        "synthetic_dataset_manifest_path": str(dataset_manifest),
        "synthetic_dataset_manifest_hash": sha256_file(dataset_manifest) if dataset_manifest.exists() else None,
        "artifact_hashes": artifacts,
        "completion_status": status,
        "warnings": warnings or [],
        "finalized": False,
    }
    write_json(dirs["manifests"] / "corpus_manifest.json", payload)
    return payload
