from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.training.clm import load_training_config
from transfer_vs_relearning.utils.io import sha256_file, sha256_text


ALLOWED_STATES = {"M0", "M1", "M2-A", "M2-B"}
ALLOWED_STATUSES = {"draft", "frozen"}
REQUIRED_OUTPUTS = (
    "checkpoint_registry.parquet",
    "metric_observations.parquet",
    "factual_probe_results.parquet",
    "trajectory_wide.csv",
    "hyperparameters.csv",
    "evaluation_manifest.json",
    "presentation/figure_manifest.json",
)
_PLACEHOLDER = re.compile(r"^__[A-Z0-9_]+__$")


@dataclass(frozen=True)
class CheckpointPoint:
    checkpoint_id: str
    epoch: int
    update: int
    normalized_progress: float
    source: str
    dense: bool
    full: bool


@dataclass(frozen=True)
class PipelineTask:
    ordinal: int
    task_id: str
    kind: str
    checkpoint_id: str | None
    epoch: int | None
    update: int | None
    bundles: tuple[str, ...]
    depends_on: tuple[str, ...]
    expected_outputs: tuple[str, ...]


def load_pipeline_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Pipeline config must contain a YAML mapping")
    return payload


def _require_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Pipeline config requires mapping: {key}")
    return value


def _require_nonempty(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"Pipeline config requires {label}")
    return text


def _is_placeholder(value: Any) -> bool:
    return bool(_PLACEHOLDER.fullmatch(str(value).strip()))


def _placeholder_paths(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        return [
            path
            for key, item in value.items()
            for path in _placeholder_paths(item, f"{prefix}.{key}" if prefix else str(key))
        ]
    if isinstance(value, list):
        return [
            path
            for index, item in enumerate(value)
            for path in _placeholder_paths(item, f"{prefix}[{index}]")
        ]
    return [prefix] if _is_placeholder(value) else []


def _resolve(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def _integer_epochs(value: Any) -> int:
    numeric = float(value)
    rounded = round(numeric)
    if not math.isclose(numeric, rounded, abs_tol=1e-9) or rounded <= 0:
        raise ValueError("Epoch-dense pipelines require a positive integer num_train_epochs")
    return int(rounded)


def _training_schedule(
    training_config: dict[str, Any],
    *,
    expected_train_rows: int,
    world_size: int,
) -> tuple[int, int, int, int]:
    training = _require_mapping(training_config, "training")
    epochs = _integer_epochs(training["num_train_epochs"])
    microbatch = int(training["per_device_train_batch_size"])
    accumulation = int(training.get("gradient_accumulation_steps", 1))
    effective_batch = microbatch * accumulation * world_size
    if min(expected_train_rows, microbatch, accumulation, world_size) <= 0:
        raise ValueError("Training rows and batch factors must be positive")
    if expected_train_rows % effective_batch:
        raise ValueError(
            "eval-v2 epoch mapping requires training rows divisible by effective row batch; "
            "freeze an explicit non-uniform last-step trace before using this recipe"
        )
    updates_per_epoch = expected_train_rows // effective_batch
    total_updates = updates_per_epoch * epochs
    configured_max_steps = training.get("max_steps")
    if configured_max_steps is not None and int(configured_max_steps) != total_updates:
        raise ValueError("max_steps disagrees with the exact epoch/update mapping")
    return epochs, updates_per_epoch, total_updates, effective_batch


def _prospective_points(
    *, epochs: int, updates_per_epoch: int, full_epochs: list[int]
) -> list[CheckpointPoint]:
    if sorted(set(full_epochs)) != full_epochs:
        raise ValueError("Full-evaluation epochs must be unique and sorted")
    if not set(full_epochs).issubset(set(range(epochs + 1))):
        raise ValueError("Full-evaluation epoch lies outside the training trajectory")
    if 0 not in full_epochs or epochs not in full_epochs:
        raise ValueError("Full-evaluation cadence must include state entry and endpoint")
    if epochs % 2 == 0 and epochs // 2 not in full_epochs:
        raise ValueError("Full-evaluation cadence must include normalized progress 0.5")
    return [
        CheckpointPoint(
            checkpoint_id="parent" if epoch == 0 else f"epoch-{epoch:03d}",
            epoch=epoch,
            update=epoch * updates_per_epoch,
            normalized_progress=epoch / epochs,
            source="parent_manifest" if epoch == 0 else "epoch_model_snapshot",
            dense=True,
            full=epoch in full_epochs,
        )
        for epoch in range(epochs + 1)
    ]


def _historical_points(
    *, epochs: int, updates_per_epoch: int, available_updates: list[int], full_updates: list[int]
) -> list[CheckpointPoint]:
    if sorted(set(available_updates)) != available_updates or available_updates[0] != 0:
        raise ValueError("Historical available updates must be unique, sorted, and include parent 0")
    if available_updates[-1] != epochs * updates_per_epoch:
        raise ValueError("Historical available updates must include the endpoint")
    if not set(full_updates).issubset(set(available_updates)):
        raise ValueError("Historical full updates must be available checkpoints")
    points: list[CheckpointPoint] = []
    for update in available_updates:
        if update % updates_per_epoch:
            raise ValueError("Historical update cannot be mapped exactly to an epoch")
        epoch = update // updates_per_epoch
        points.append(
            CheckpointPoint(
                checkpoint_id="parent" if update == 0 else f"checkpoint-{update}",
                epoch=epoch,
                update=update,
                normalized_progress=epoch / epochs,
                source="historical_checkpoint",
                dense=True,
                full=update in full_updates,
            )
        )
    return points


def _tasks(points: list[CheckpointPoint], evaluation: dict[str, Any]) -> list[PipelineTask]:
    dense_bundles = tuple(str(item) for item in evaluation.get("dense_bundles", []))
    full_bundles = tuple(str(item) for item in evaluation.get("full_bundles", []))
    if not dense_bundles or not full_bundles:
        raise ValueError("Both dense_bundles and full_bundles must be non-empty")

    tasks: list[PipelineTask] = []

    def add(
        task_id: str,
        kind: str,
        *,
        point: CheckpointPoint | None = None,
        bundles: tuple[str, ...] = (),
        depends_on: tuple[str, ...] = (),
        outputs: tuple[str, ...] = (),
    ) -> None:
        tasks.append(
            PipelineTask(
                ordinal=len(tasks),
                task_id=task_id,
                kind=kind,
                checkpoint_id=point.checkpoint_id if point else None,
                epoch=point.epoch if point else None,
                update=point.update if point else None,
                bundles=bundles,
                depends_on=depends_on,
                expected_outputs=outputs,
            )
        )

    add(
        "identity_preflight",
        "preflight",
        outputs=("preflight/identity_manifest.json", "preflight/storage_manifest.json"),
    )
    add(
        "train_and_trace",
        "training",
        depends_on=("identity_preflight",),
        outputs=(
            "training/training_manifest.json",
            "training/training_trace_manifest.json",
            "training/epoch_snapshots/",
        ),
    )

    previous = "train_and_trace"
    for point in points:
        task_id = f"dense_eval_{point.checkpoint_id.replace('-', '_')}"
        add(
            task_id,
            "dense_evaluation",
            point=point,
            bundles=dense_bundles,
            depends_on=(previous,),
            outputs=(f"raw/dense/{point.checkpoint_id}/evaluation_manifest.json",),
        )
        previous = task_id

    for point in (item for item in points if item.full):
        task_id = f"full_eval_{point.checkpoint_id.replace('-', '_')}"
        add(
            task_id,
            "full_evaluation",
            point=point,
            bundles=full_bundles,
            depends_on=(previous,),
            outputs=(f"raw/full/{point.checkpoint_id}/evaluation_manifest.json",),
        )
        previous = task_id

    add(
        "normalize_results",
        "normalization",
        depends_on=(previous,),
        outputs=REQUIRED_OUTPUTS[:6],
    )
    add(
        "build_presentation_bundle",
        "presentation",
        depends_on=("normalize_results",),
        outputs=(
            "presentation/figure_manifest.json",
            "presentation/captions.json",
            "presentation/plot_data/",
        ),
    )
    return tasks


def validate_sibling_compatibility(left: dict[str, Any], right: dict[str, Any]) -> None:
    left_exp = _require_mapping(left, "experiment")
    right_exp = _require_mapping(right, "experiment")
    if {left_exp.get("state"), right_exp.get("state")} != {"M2-A", "M2-B"}:
        raise ValueError("Sibling comparison requires exactly M2-A and M2-B")
    comparable = (
        ("experiment", "parent_state"),
        ("experiment", "parent_checkpoint_id"),
        ("experiment", "seed"),
        ("training_plan", "expected_train_rows"),
        ("training_plan", "expected_total_updates"),
        ("evaluation", "contract"),
        ("evaluation", "dense_bundles"),
        ("evaluation", "full_bundles"),
        ("evaluation", "full_epochs"),
    )
    mismatches = []
    for section, field in comparable:
        left_value = _require_mapping(left, section).get(field)
        right_value = _require_mapping(right, section).get(field)
        if left_value != right_value:
            mismatches.append(f"{section}.{field}")
    left_training = load_training_config(Path(str(_require_mapping(left, "training_plan")["config"])))
    right_training = load_training_config(Path(str(_require_mapping(right, "training_plan")["config"])))
    for field in (
        "num_train_epochs",
        "block_size",
        "per_device_train_batch_size",
        "gradient_accumulation_steps",
    ):
        if left_training["training"].get(field) != right_training["training"].get(field):
            mismatches.append(f"training.{field}")
    if mismatches:
        raise ValueError(f"M2 sibling contracts are not matched: {', '.join(mismatches)}")


def build_pipeline_plan(config_path: Path, *, repo_root: Path | None = None) -> dict[str, Any]:
    repo_root = (repo_root or Path.cwd()).resolve()
    config_path = config_path.resolve()
    payload = load_pipeline_config(config_path)
    if int(payload.get("schema_version", 0)) != 1:
        raise ValueError("Unsupported pipeline schema_version")
    pipeline_id = _require_nonempty(payload.get("pipeline_id"), "pipeline_id")
    status = str(payload.get("status", ""))
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Unsupported pipeline status: {status!r}")
    if payload.get("execution_authorized") is not False:
        raise ValueError("The local planner requires execution_authorized=false")

    experiment = _require_mapping(payload, "experiment")
    state = str(experiment.get("state"))
    parent_state = str(experiment.get("parent_state"))
    if state not in ALLOWED_STATES or parent_state not in ALLOWED_STATES:
        raise ValueError("Experiment state and parent_state must use M0/M1/M2-A/M2-B")
    _require_nonempty(experiment.get("experiment_id"), "experiment.experiment_id")
    _require_nonempty(experiment.get("parent_checkpoint_id"), "experiment.parent_checkpoint_id")
    seed = int(experiment["seed"])

    training_plan = _require_mapping(payload, "training_plan")
    training_config_value = _require_nonempty(training_plan.get("config"), "training_plan.config")
    training_config_path = _resolve(repo_root, training_config_value).resolve()
    training_config = load_training_config(training_config_path)
    expected_train_rows = int(training_plan["expected_train_rows"])
    world_size = int(training_config["runtime"].get("world_size", 1))
    epochs, updates_per_epoch, total_updates, effective_batch = _training_schedule(
        training_config,
        expected_train_rows=expected_train_rows,
        world_size=world_size,
    )
    if int(training_plan["expected_total_updates"]) != total_updates:
        raise ValueError("expected_total_updates disagrees with the derived schedule")

    mode = str(training_plan.get("trajectory_mode", "prospective"))
    tracking = _require_mapping(training_plan, "tracking")
    if tracking.get("dense_cadence") != "every_epoch_end_including_parent":
        raise ValueError("eval-v2 prospective tracking requires every epoch end including parent")
    if tracking.get("epoch_snapshot_policy") != "model_only_every_epoch":
        raise ValueError("eval-v2 requires model-only epoch snapshots")
    if tracking.get("storage_preflight_required") is not True:
        raise ValueError("Epoch snapshots require a storage preflight")
    for required in ("fact_exposures_per_epoch", "estimated_snapshot_bytes", "minimum_free_bytes"):
        if int(tracking.get(required, 0)) < 0:
            raise ValueError(f"training_plan.tracking.{required} cannot be negative")
    if int(tracking.get("estimated_snapshot_bytes", 0)) <= 0:
        raise ValueError("estimated_snapshot_bytes must be positive")
    if mode == "prospective":
        training_tracking = _require_mapping(training_config, "tracking")
        tracking_fields = (
            "dense_cadence",
            "epoch_snapshot_policy",
            "storage_preflight_required",
            "estimated_snapshot_bytes",
            "minimum_free_bytes",
            "fact_exposures_per_epoch",
        )
        tracking_mismatches = [
            field
            for field in tracking_fields
            if tracking.get(field) != training_tracking.get(field)
        ]
        if tracking_mismatches:
            raise ValueError(
                "Pipeline/training tracking mismatch: " + ", ".join(tracking_mismatches)
            )

    evaluation = _require_mapping(payload, "evaluation")
    if evaluation.get("contract") != "eval-v2":
        raise ValueError("This pipeline planner currently supports eval-v2 only")
    if mode == "prospective":
        points = _prospective_points(
            epochs=epochs,
            updates_per_epoch=updates_per_epoch,
            full_epochs=[int(item) for item in evaluation["full_epochs"]],
        )
    elif mode == "historical_backfill":
        points = _historical_points(
            epochs=epochs,
            updates_per_epoch=updates_per_epoch,
            available_updates=[int(item) for item in training_plan["available_updates"]],
            full_updates=[int(item) for item in evaluation["full_updates"]],
        )
    else:
        raise ValueError(f"Unsupported trajectory_mode: {mode!r}")

    outputs = _require_mapping(payload, "outputs")
    _require_nonempty(outputs.get("root"), "outputs.root")
    for field in (
        "raw_namespaces_immutable",
        "normalized_tables_required",
        "presentation_bundle_required",
    ):
        if outputs.get(field) is not True:
            raise ValueError(f"Pipeline output invariant must be true: outputs.{field}")

    if status == "frozen":
        placeholders = [
            *(_placeholder_paths(payload, "pipeline_config")),
            *(_placeholder_paths(training_config, "training_config")),
        ]
        if placeholders:
            raise ValueError(
                "Frozen pipelines cannot contain placeholders: " + ", ".join(placeholders[:8])
            )

    tasks = _tasks(points, evaluation)
    config_sha256 = sha256_file(config_path)
    plan_identity = {
        "pipeline_id": pipeline_id,
        "config_sha256": config_sha256,
        "training_config_sha256": sha256_file(training_config_path),
        "state": state,
        "parent_state": parent_state,
        "seed": seed,
        "checkpoint_ids": [point.checkpoint_id for point in points],
    }
    return {
        "schema_version": 1,
        "plan_id": sha256_text(json.dumps(plan_identity, sort_keys=True))[:16],
        "pipeline_id": pipeline_id,
        "status": "planned_not_authorized",
        "execution_authorized": False,
        "config_path": str(config_path),
        "config_sha256": config_sha256,
        "training_config_path": str(training_config_path),
        "training_config_sha256": sha256_file(training_config_path),
        "experiment": experiment,
        "derived_training": {
            "epochs": epochs,
            "updates_per_epoch": updates_per_epoch,
            "total_updates": total_updates,
            "effective_row_batch": effective_batch,
            "expected_train_rows": expected_train_rows,
            "max_sequence_length": int(training_config["training"]["block_size"]),
            "microbatch": int(training_config["training"]["per_device_train_batch_size"]),
            "gradient_accumulation": int(
                training_config["training"].get("gradient_accumulation_steps", 1)
            ),
            "world_size": world_size,
        },
        "tracking": tracking,
        "evaluation": evaluation,
        "outputs": outputs,
        "checkpoints": [asdict(point) for point in points],
        "tasks": [asdict(task) for task in tasks],
        "required_outputs": list(REQUIRED_OUTPUTS),
        "safety": {
            "planner_only": True,
            "network": False,
            "training": False,
            "evaluation": False,
            "hu_or_slurm": False,
            "note": "This plan contains identities and dependencies; it is not an execution authorization.",
        },
    }
