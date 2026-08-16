from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from transfer_vs_relearning.utils.io import sha256_file, sha256_text, write_json


@dataclass(frozen=True)
class TokenizationStats:
    rows: int
    max_sequence_length: int
    total_nonpad_tokens: int
    total_supervised_tokens: int
    mean_nonpad_tokens: float
    p50_nonpad_tokens: float
    p95_nonpad_tokens: float
    padding_fraction: float
    truncation_count: int
    truncation_rate: float


def summarize_tokenized_rows(
    rows: Iterable[dict[str, Any]], *, max_sequence_length: int
) -> TokenizationStats:
    if max_sequence_length <= 0:
        raise ValueError("max_sequence_length must be positive")
    nonpad_lengths: list[int] = []
    supervised_tokens = 0
    truncation_count = 0
    for row in rows:
        mask = [int(value) for value in row["attention_mask"]]
        labels = [int(value) for value in row["labels"]]
        if len(mask) != max_sequence_length or len(labels) != max_sequence_length:
            raise ValueError("Trace rows must equal max_sequence_length")
        if any(value not in (0, 1) for value in mask):
            raise ValueError("attention_mask must be binary")
        nonpad_lengths.append(sum(mask))
        supervised_tokens += sum(value != -100 for value in labels)
        truncation_count += int(bool(row.get("__trace_was_truncated", False)))
    if not nonpad_lengths:
        raise ValueError("Cannot summarize an empty tokenized dataset")
    lengths = np.asarray(nonpad_lengths, dtype=np.float64)
    total_slots = len(nonpad_lengths) * max_sequence_length
    total_nonpad = int(lengths.sum())
    return TokenizationStats(
        rows=len(nonpad_lengths),
        max_sequence_length=max_sequence_length,
        total_nonpad_tokens=total_nonpad,
        total_supervised_tokens=supervised_tokens,
        mean_nonpad_tokens=float(lengths.mean()),
        p50_nonpad_tokens=float(np.quantile(lengths, 0.50)),
        p95_nonpad_tokens=float(np.quantile(lengths, 0.95)),
        padding_fraction=(total_slots - total_nonpad) / total_slots,
        truncation_count=truncation_count,
        truncation_rate=truncation_count / len(nonpad_lengths),
    )


def validate_snapshot_capacity(
    root: Path,
    *,
    epoch_count: int,
    estimated_snapshot_bytes: int,
    minimum_free_bytes: int,
) -> dict[str, int]:
    if min(epoch_count, estimated_snapshot_bytes) <= 0 or minimum_free_bytes < 0:
        raise ValueError("Snapshot capacity inputs are invalid")
    root.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage(root)
    required = epoch_count * estimated_snapshot_bytes + minimum_free_bytes
    if usage.free < required:
        raise RuntimeError(
            f"Insufficient free space for epoch snapshots: {usage.free} < {required} bytes"
        )
    return {
        "free_bytes": usage.free,
        "estimated_snapshot_bytes": estimated_snapshot_bytes,
        "epoch_count": epoch_count,
        "minimum_free_bytes": minimum_free_bytes,
        "required_bytes": required,
    }


def snapshot_inventory(snapshot_dir: Path) -> dict[str, Any]:
    files = sorted(
        path
        for path in snapshot_dir.rglob("*")
        if path.is_file() and path.name != "snapshot_manifest.json"
    )
    if not files:
        raise ValueError(f"Snapshot contains no files: {snapshot_dir}")
    entries = [
        {
            "path": str(path.relative_to(snapshot_dir)),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in files
    ]
    identity = sha256_text(json.dumps(entries, ensure_ascii=False, sort_keys=True))
    return {
        "schema_version": 1,
        "checkpoint_sha256": identity,
        "file_count": len(entries),
        "total_bytes": sum(item["bytes"] for item in entries),
        "files": entries,
    }


class TrainingTraceRecorder:
    """Crash-safe trace as immutable event files plus an atomically replaced index."""

    def __init__(self, root: Path, static_manifest: dict[str, Any]) -> None:
        self.root = root
        self.events_dir = root / "events"
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = root / "trace_index.json"
        self.manifest_path = root / "training_trace_manifest.json"
        if self.manifest_path.exists():
            observed = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if observed.get("identity_sha256") != static_manifest.get("identity_sha256"):
                raise ValueError("Training trace identity changed during resume")
        else:
            write_json(self.manifest_path, static_manifest)
        if self.index_path.exists():
            self.index = json.loads(self.index_path.read_text(encoding="utf-8"))
        else:
            self.index = {"schema_version": 1, "status": "started", "events": []}
            write_json(self.index_path, self.index)

    def record(self, event: str, payload: dict[str, Any]) -> Path:
        sequence = len(self.index["events"])
        safe_event = "".join(character if character.isalnum() else "_" for character in event)
        path = self.events_dir / f"{sequence:06d}_{safe_event}.json"
        if path.exists():
            raise FileExistsError(f"Training trace event already exists: {path}")
        row = {
            "schema_version": 1,
            "sequence": sequence,
            "event": event,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        write_json(path, row)
        self.index["events"].append(
            {"sequence": sequence, "event": event, "path": str(path), "sha256": sha256_file(path)}
        )
        write_json(self.index_path, self.index)
        return path

    def complete(self) -> None:
        self.index["status"] = "complete"
        self.index["completed_at"] = datetime.now(timezone.utc).isoformat()
        write_json(self.index_path, self.index)


def make_static_trace_manifest(
    *,
    run_id: str,
    config_sha256: str,
    model_manifest_sha256: str,
    dataset_manifest_sha256: str,
    model_identity: dict[str, Any],
    dataset_identity: dict[str, Any],
    runtime_identity: dict[str, Any],
    seed: int,
    data_seed: int,
    epochs: int,
    updates_per_epoch: int,
    effective_row_batch: int,
    training: dict[str, Any],
    resolved_training: dict[str, Any],
    tokenization: TokenizationStats,
    fact_exposures_per_epoch: int,
    snapshot_policy: str,
) -> dict[str, Any]:
    identity = {
        "run_id": run_id,
        "config_sha256": config_sha256,
        "model_manifest_sha256": model_manifest_sha256,
        "dataset_manifest_sha256": dataset_manifest_sha256,
        "model": model_identity,
        "dataset": dataset_identity,
        "seed": seed,
        "data_seed": data_seed,
    }
    return {
        "schema_version": 1,
        "status": "started",
        "identity": identity,
        "identity_sha256": sha256_text(json.dumps(identity, sort_keys=True)),
        "schedule": {
            "epochs": epochs,
            "updates_per_epoch": updates_per_epoch,
            "total_updates": epochs * updates_per_epoch,
            "effective_row_batch": effective_row_batch,
            "fact_exposures_per_epoch": fact_exposures_per_epoch,
            "snapshot_policy": snapshot_policy,
        },
        "hyperparameters": {
            "num_train_epochs": float(training["num_train_epochs"]),
            "objective": training.get("loss_mode", "full_sequence"),
            "supervise_eos": bool(training.get("supervise_eos", True)),
            "max_sequence_length": int(training["block_size"]),
            "microbatch": int(training["per_device_train_batch_size"]),
            "per_device_eval_batch_size": int(training["per_device_eval_batch_size"]),
            "gradient_accumulation": int(training.get("gradient_accumulation_steps", 1)),
            "learning_rate": float(training["learning_rate"]),
            "scheduler": str(training.get("lr_scheduler_type", "linear")),
            "warmup_ratio": float(training.get("warmup_ratio", 0.0)),
            "weight_decay": float(training.get("weight_decay", 0.0)),
            "adam_beta1": float(training.get("adam_beta1", 0.9)),
            "adam_beta2": float(training.get("adam_beta2", 0.999)),
            "adam_epsilon": float(training.get("adam_epsilon", 1e-8)),
            "max_grad_norm": float(training.get("max_grad_norm", 1.0)),
            "bf16": bool(training.get("bf16", False)),
            "fp16": bool(training.get("fp16", False)),
            "gradient_checkpointing": bool(training.get("gradient_checkpointing", False)),
            "optimizer_foreach": training.get("optimizer_foreach", "framework_default"),
            "model_load_dtype": training.get("model_load_dtype"),
            "logging_steps": int(training.get("logging_steps", 10)),
            "save_total_limit": int(training.get("save_total_limit", 8)),
        },
        "resolved_training": resolved_training,
        "frozen_training_config": training,
        "runtime": runtime_identity,
        "tokenization": tokenization.__dict__,
    }


def make_epoch_trace_payload(
    *,
    epoch: int,
    global_step: int,
    epochs: int,
    train_rows: int,
    fact_exposures_per_epoch: int,
    tokenization: TokenizationStats,
    latest_logs: dict[str, Any],
    snapshot_path: Path,
    checkpoint_sha256: str,
) -> dict[str, Any]:
    if epoch <= 0 or epoch > epochs:
        raise ValueError("Epoch trace is outside the frozen schedule")
    return {
        "record_status": "complete",
        "epoch": epoch,
        "update": global_step,
        "normalized_progress": epoch / epochs,
        "cumulative_examples": epoch * train_rows,
        "cumulative_fact_exposures": epoch * fact_exposures_per_epoch,
        "cumulative_supervised_tokens": epoch * tokenization.total_supervised_tokens,
        "cumulative_total_tokens": epoch * tokenization.total_nonpad_tokens,
        "train_loss": latest_logs.get("loss"),
        "learning_rate": latest_logs.get("learning_rate"),
        "grad_norm": latest_logs.get("grad_norm"),
        "snapshot_path": str(snapshot_path),
        "checkpoint_sha256": checkpoint_sha256,
    }


def create_transformers_trace_callback(
    callback_base: type[Any],
    *,
    recorder: TrainingTraceRecorder,
    tokenizer: Any,
    snapshot_root: Path,
    epochs: int,
    updates_per_epoch: int,
    train_rows: int,
    fact_exposures_per_epoch: int,
    tokenization: TokenizationStats,
    estimated_snapshot_bytes: int,
    minimum_free_bytes: int,
) -> Any:
    class EpochTraceCallback(callback_base):
        def __init__(self) -> None:
            self.latest_logs: dict[str, Any] = {}

        def on_train_begin(self, args: Any, state: Any, control: Any, **kwargs: Any) -> Any:
            if state.is_world_process_zero:
                recorder.record("train_begin", {"update": int(state.global_step), "epoch": state.epoch})
            return control

        def on_log(
            self, args: Any, state: Any, control: Any, logs: dict[str, Any] | None = None, **kwargs: Any
        ) -> Any:
            if logs:
                self.latest_logs = dict(logs)
                if state.is_world_process_zero:
                    recorder.record(
                        "optimizer_log",
                        {"update": int(state.global_step), "epoch": state.epoch, "metrics": logs},
                    )
            return control

        def on_epoch_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> Any:
            if not state.is_world_process_zero:
                return control
            if state.epoch is None:
                raise ValueError("Trainer did not expose epoch at epoch end")
            epoch = int(round(float(state.epoch)))
            if not math.isclose(float(state.epoch), epoch, abs_tol=1e-6):
                raise ValueError("Epoch callback did not land on an integer epoch boundary")
            expected_update = epoch * updates_per_epoch
            if int(state.global_step) != expected_update:
                raise ValueError(
                    f"Epoch/update mapping drifted: epoch {epoch} expected {expected_update}, "
                    f"observed {state.global_step}"
                )
            snapshot_dir = snapshot_root / f"epoch-{epoch:03d}"
            snapshot_root.mkdir(parents=True, exist_ok=True)
            if snapshot_dir.exists():
                raise FileExistsError(f"Epoch snapshot already exists: {snapshot_dir}")
            current_free = shutil.disk_usage(snapshot_root).free
            required_free = estimated_snapshot_bytes + minimum_free_bytes
            if current_free < required_free:
                raise RuntimeError(
                    "Epoch snapshot stopped by the live storage guard: "
                    f"{current_free} < {required_free} bytes"
                )
            model = kwargs.get("model")
            if model is None:
                raise ValueError("Trainer callback did not provide the model")
            snapshot_dir.mkdir(parents=True)
            model.save_pretrained(str(snapshot_dir), safe_serialization=True)
            tokenizer.save_pretrained(str(snapshot_dir))
            inventory = snapshot_inventory(snapshot_dir)
            inventory.update({"epoch": epoch, "update": int(state.global_step)})
            write_json(snapshot_dir / "snapshot_manifest.json", inventory)
            recorder.record(
                "epoch_end",
                make_epoch_trace_payload(
                    epoch=epoch,
                    global_step=int(state.global_step),
                    epochs=epochs,
                    train_rows=train_rows,
                    fact_exposures_per_epoch=fact_exposures_per_epoch,
                    tokenization=tokenization,
                    latest_logs=self.latest_logs,
                    snapshot_path=snapshot_dir,
                    checkpoint_sha256=str(inventory["checkpoint_sha256"]),
                ),
            )
            return control

        def on_train_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> Any:
            if state.is_world_process_zero:
                recorder.record("train_end", {"update": int(state.global_step), "epoch": state.epoch})
                recorder.complete()
            return control

    return EpochTraceCallback()
