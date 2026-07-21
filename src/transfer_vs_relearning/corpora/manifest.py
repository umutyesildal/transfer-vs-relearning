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
    excluded_artifacts = {
        dirs["manifests"] / "corpus_manifest.json",
        dirs["manifests"] / "bridge_split_sha256.txt",
        dirs["manifests"] / "bridge_split_candidate_sha256.txt",
        dirs["manifests"] / "report_state.json",
    }
    for name, directory in dirs.items():
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*")):
            if path.is_file() and path not in excluded_artifacts:
                artifacts[str(path.relative_to(dirs["manifests"].parents[0]))] = {
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
    dataset_manifest = Path(config["contamination"]["synthetic_dataset_dir"]) / "manifest.json"
    stage_states = _load_json_files(dirs["manifests"], "*_state.json")
    stage_states.pop("report", None)
    reports = _load_json_files(dirs["reports"], "*_report.json")
    verify_manifest = _load_optional_json(dirs["manifests"] / "verify_manifest.json")
    payload = {
        "corpus_id": config["corpus_id"],
        "wikimedia_source_project": config["project"],
        "dump_date": str(config["dump_date"]),
        "source_urls": {
            "dump": config["dump_base_url"] + config["dump_filename"],
            "checksum": config["dump_base_url"] + config["checksum_filename"],
        },
        "source_text_license": "requires_authoritative_wikimedia_metadata_verification",
        "attribution_requirement": "Retain Wikimedia attribution and license provenance after authoritative metadata resolution.",
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
        "expected_checksum": _load_optional_json(dirs["manifests"] / "dump_metadata.json").get("expected_checksum"),
        "observed_checksum": verify_manifest.get("sha1"),
        "dump_verification_status": verify_manifest.get("status", "not_verified"),
        "actual_extraction_parser": _load_optional_json(dirs["manifests"] / "extraction_manifest.json").get("actual_parser"),
        "actual_extraction_runtime_versions": _load_optional_json(dirs["manifests"] / "extraction_manifest.json").get("runtime_versions", {}),
        "stage_states": stage_states,
        "document_counts_per_stage": {
            stage: state.get("document_counters", {})
            for stage, state in stage_states.items()
        },
        "filtering_reason_counts": reports.get("audit_report", {}).get("reason_counts", {}),
        "duplicate_counts": reports.get("deduplication_report", {}),
        "contamination_counts": reports.get("contamination_report", {}),
        "split_counts": reports.get("split_report", {}),
        "artifact_hashes": artifacts,
        "completion_status": status,
        "warnings": warnings or [],
        "excluded_self_referential_artifacts": sorted(str(path.relative_to(dirs["manifests"].parents[0])) for path in excluded_artifacts),
        "excluded_self_referential_stage_states": ["report"],
        "finalized": status == "finalized",
    }
    write_json(dirs["manifests"] / "corpus_manifest.json", payload)
    return payload


def _load_json_files(directory: Path, pattern: str) -> dict[str, Any]:
    output = {}
    for path in sorted(directory.glob(pattern)):
        output[path.stem.removesuffix("_state")] = _load_optional_json(path)
    return output


def _load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    import json

    return json.loads(path.read_text(encoding="utf-8"))
