from __future__ import annotations

import json
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from transfer_vs_relearning.corpora.config import config_hash, stage_dirs
from transfer_vs_relearning.corpora.manifest import git_commit
from transfer_vs_relearning.utils.io import sha256_file, write_json


def stage_state_path(config: dict[str, Any], stage: str) -> Path:
    return stage_dirs(config)["manifests"] / f"{stage}_state.json"


def load_stage_state(config: dict[str, Any], stage: str) -> dict[str, Any] | None:
    path = stage_state_path(config, stage)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def validate_prerequisite(config: dict[str, Any], stage: str) -> None:
    prereq = {
        "download": "resolve",
        "verify": "download",
        "extract": "verify",
        "normalize": "extract",
        "audit": "normalize",
        "filter": "audit",
        "deduplicate": "filter",
        "scan-contamination": "deduplicate",
        "split": "scan-contamination",
        "report": "split",
    }.get(stage)
    if not prereq:
        return
    state = load_stage_state(config, prereq)
    if not state or state.get("status") != "completed":
        if stage == "download" and (stage_dirs(config)["manifests"] / "configured_dump_metadata.json").exists():
            raise ValueError("Stage download requires official metadata resolution; configured-only resolution is not sufficient")
        raise ValueError(f"Stage {stage} requires completed prerequisite stage {prereq}")
    if prereq == "resolve" and state.get("resolution_mode") != "official":
        raise ValueError(f"Stage {stage} requires official metadata resolution, not configured-only resolution")
    if prereq == "download" and state.get("download_status") != "downloaded_unverified":
        raise ValueError("Stage verify requires a completed downloaded_unverified download stage")
    if state.get("config_hash") and state.get("config_hash") != config_hash(config):
        raise ValueError(f"Stage {stage} prerequisite {prereq} used a different config")


def ensure_compatible_or_force(config: dict[str, Any], stage: str, force: bool, input_path: Path | None = None) -> bool:
    state = load_stage_state(config, stage)
    if not state or state.get("status") != "completed":
        return False
    if state.get("config_hash") != config_hash(config):
        if not force:
            raise ValueError(f"Completed stage {stage} used a different config; pass --force or use a new corpus version")
        return False
    if input_path is not None:
        current_input = _artifact_entry(input_path)
        if state.get("input_artifact") != current_input:
            if not force:
                raise ValueError(f"Completed stage {stage} input artifact changed; pass --force to rerun")
            return False
    if not _outputs_match(state):
        if not force:
            raise ValueError(f"Completed stage {stage} output artifacts are missing or changed; pass --force to rerun")
        return False
    return True


@contextmanager
def stage_run(config: dict[str, Any], stage: str, force: bool = False, input_path: Path | None = None) -> Iterator[dict[str, Any]]:
    validate_prerequisite(config, stage)
    if ensure_compatible_or_force(config, stage, force, input_path):
        yield {"reused": True}
        return
    start = datetime.now(timezone.utc).isoformat()
    state: dict[str, Any] = {
        "stage": stage,
        "status": "running",
        "start_timestamp": start,
        "end_timestamp": None,
        "config_hash": config_hash(config),
        "input_artifact": _artifact_entry(input_path) if input_path else None,
        "input_artifact_path": str(input_path) if input_path else None,
        "input_artifact_sha256": sha256_file(input_path) if input_path and input_path.exists() and input_path.is_file() else None,
        "output_artifact_path": None,
        "output_artifact_sha256": None,
        "output_artifacts": {},
        "document_counters": {},
        "error_message": None,
        "processing_git_commit": git_commit(),
    }
    write_json(stage_state_path(config, stage), state)
    try:
        yield state
    except Exception as exc:
        state["status"] = "failed"
        state["end_timestamp"] = datetime.now(timezone.utc).isoformat()
        state["error_message"] = f"{exc}\n{traceback.format_exc(limit=8)}"
        write_json(stage_state_path(config, stage), state)
        raise
    else:
        if state.get("reused"):
            return
        state["status"] = "completed"
        state["end_timestamp"] = datetime.now(timezone.utc).isoformat()
        output_path = Path(state["output_artifact_path"]) if state.get("output_artifact_path") else None
        if output_path and output_path.exists() and output_path.is_file():
            state["output_artifact_sha256"] = sha256_file(output_path)
        if state.get("output_artifact_map"):
            state["output_artifacts"] = {
                key: _artifact_entry(Path(value))
                for key, value in state["output_artifact_map"].items()
            }
        elif output_path:
            state["output_artifacts"] = {"primary": _artifact_entry(output_path)}
        write_json(stage_state_path(config, stage), state)


def _artifact_entry(path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {"path": str(path), "exists": path.exists(), "sha256": None, "kind": "missing"}
    if path.is_file():
        entry.update({"kind": "file", "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    elif path.is_dir():
        entry.update({"kind": "directory"})
    return entry


def _outputs_match(state: dict[str, Any]) -> bool:
    artifacts = state.get("output_artifacts") or {}
    if not artifacts and state.get("output_artifact_path"):
        artifacts = {"primary": {"path": state["output_artifact_path"], "sha256": state.get("output_artifact_sha256")}}
    for entry in artifacts.values():
        path = Path(entry["path"])
        if not path.exists():
            return False
        if entry.get("kind") == "file" or path.is_file():
            if sha256_file(path) != entry.get("sha256"):
                return False
    return True
