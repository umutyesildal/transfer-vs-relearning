from __future__ import annotations

"""Hash-close the deterministic outputs produced by one tracked M1 training run."""

import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file, write_json


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON mapping required: {path}")
    return payload


def finalize_m1_training_outputs(run_dir: Path, binding_root: Path) -> dict[str, Any]:
    """Create stable training/checkpoint bindings without modifying the raw run directory."""

    run_dir = run_dir.resolve()
    binding_root = binding_root.resolve()
    if binding_root.exists():
        raise FileExistsError(f"M1 binding root already exists: {binding_root}")
    training_manifest_path = run_dir / "training_manifest.json"
    trace_manifest_path = run_dir / "training_trace/training_trace_manifest.json"
    trace_index_path = run_dir / "training_trace/trace_index.json"
    for path in (training_manifest_path, trace_manifest_path, trace_index_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    training = _read_json(training_manifest_path)
    trace_manifest = _read_json(trace_manifest_path)
    trace_index = _read_json(trace_index_path)
    if training.get("status") != "complete":
        raise ValueError("M1 training manifest is not complete")
    if trace_index.get("status") != "complete":
        raise ValueError("M1 training trace is not complete")
    schedule = trace_manifest.get("schedule")
    if not isinstance(schedule, dict):
        raise ValueError("M1 trace manifest is missing its schedule")
    epochs = int(schedule.get("epochs", 0))
    updates_per_epoch = int(schedule.get("updates_per_epoch", 0))
    if epochs <= 0 or updates_per_epoch <= 0:
        raise ValueError("M1 trace schedule is invalid")

    epoch_events: dict[int, dict[str, Any]] = {}
    for event_ref in trace_index.get("events", []):
        if not isinstance(event_ref, dict) or event_ref.get("event") != "epoch_end":
            continue
        event_path = Path(str(event_ref.get("path", "")))
        if not event_path.is_absolute():
            event_path = run_dir / "training_trace" / event_path
        if not event_path.is_file() or sha256_file(event_path) != event_ref.get("sha256"):
            raise ValueError(f"M1 trace event identity mismatch: {event_path}")
        event = _read_json(event_path)
        epoch = int(event.get("epoch", 0))
        if epoch in epoch_events:
            raise ValueError(f"Duplicate M1 epoch trace event: {epoch}")
        epoch_events[epoch] = event
    if set(epoch_events) != set(range(1, epochs + 1)):
        raise ValueError("M1 trace does not contain exactly one event for every epoch")

    base_manifest_path = Path(str(training.get("model", {}).get("base_model_manifest", "")))
    if not base_manifest_path.is_file():
        raise FileNotFoundError(base_manifest_path)
    base_manifest_sha256 = str(training.get("model", {}).get("base_model_manifest_sha256", ""))
    if sha256_file(base_manifest_path) != base_manifest_sha256:
        raise ValueError("M1 base-model manifest identity changed")

    checkpoints: list[dict[str, Any]] = [
        {
            "checkpoint_id": "parent",
            "state": "M0",
            "epoch": 0,
            "update": 0,
            "model_path": None,
            "model_manifest": str(base_manifest_path),
            "checkpoint_sha256": base_manifest_sha256,
            "source": "frozen_parent_manifest",
        }
    ]
    for epoch in range(1, epochs + 1):
        event = epoch_events[epoch]
        snapshot_path = Path(str(event.get("snapshot_path", ""))).resolve()
        snapshot_manifest = snapshot_path / "snapshot_manifest.json"
        if not snapshot_manifest.is_file():
            raise FileNotFoundError(snapshot_manifest)
        snapshot = _read_json(snapshot_manifest)
        if (
            int(event.get("update", -1)) != epoch * updates_per_epoch
            or int(snapshot.get("epoch", -1)) != epoch
            or int(snapshot.get("update", -1)) != epoch * updates_per_epoch
            or snapshot.get("checkpoint_sha256") != event.get("checkpoint_sha256")
        ):
            raise ValueError(f"M1 epoch/checkpoint identity mismatch at epoch {epoch}")
        checkpoints.append(
            {
                "checkpoint_id": f"epoch-{epoch:03d}",
                "state": "M1",
                "epoch": epoch,
                "update": epoch * updates_per_epoch,
                "model_path": str(snapshot_path),
                "snapshot_manifest": str(snapshot_manifest),
                "snapshot_manifest_sha256": sha256_file(snapshot_manifest),
                "checkpoint_sha256": str(snapshot["checkpoint_sha256"]),
                "source": "tracked_epoch_snapshot",
            }
        )

    binding_root.mkdir(parents=True)
    training_binding = {
        "schema_version": 1,
        "status": "complete",
        "run_dir": str(run_dir),
        "training_manifest": str(training_manifest_path),
        "training_manifest_sha256": sha256_file(training_manifest_path),
        "training_trace_manifest": str(trace_manifest_path),
        "training_trace_manifest_sha256": sha256_file(trace_manifest_path),
        "trace_index": str(trace_index_path),
        "trace_index_sha256": sha256_file(trace_index_path),
        "checkpoint_count": len(checkpoints),
    }
    write_json(binding_root / "training_binding.json", training_binding)
    checkpoint_manifest = {
        "schema_version": 1,
        "status": "complete",
        "run_dir": str(run_dir),
        "epochs": epochs,
        "updates_per_epoch": updates_per_epoch,
        "checkpoint_count": len(checkpoints),
        "checkpoints": checkpoints,
    }
    write_json(binding_root / "checkpoint_manifest.json", checkpoint_manifest)
    result = {
        "schema_version": 1,
        "status": "complete",
        "binding_root": str(binding_root),
        "training_binding": str(binding_root / "training_binding.json"),
        "training_binding_sha256": sha256_file(binding_root / "training_binding.json"),
        "checkpoint_manifest": str(binding_root / "checkpoint_manifest.json"),
        "checkpoint_manifest_sha256": sha256_file(binding_root / "checkpoint_manifest.json"),
    }
    write_json(binding_root / "binding_result.json", result)
    return result
