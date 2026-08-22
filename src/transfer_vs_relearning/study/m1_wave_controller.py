from __future__ import annotations

"""Fail-closed planner for the fresh matched three-model M1 wave.

The controller only validates identities and composes a dependency graph.  It never imports
Transformers model-loading code, contacts HU, submits Slurm, trains or evaluates.
"""

import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.study.m1_eval_controller import (
    FIXED_M1_MODELS,
    build_m1_eval_matrix_plan,
)
from transfer_vs_relearning.pipeline.planner import load_pipeline_config
from transfer_vs_relearning.training.clm import load_training_config
from transfer_vs_relearning.utils.io import sha256_file, sha256_text


COMMON_TRAINING_FIELDS = (
    "block_size",
    "learning_rate",
    "num_train_epochs",
    "max_steps",
    "warmup_ratio",
    "weight_decay",
    "lr_scheduler_type",
    "loss_mode",
    "supervise_eos",
    "model_load_dtype",
    "bf16",
    "fp16",
    "gradient_checkpointing",
    "optimizer_foreach",
    "max_grad_norm",
    "seed",
    "data_seed",
)


def _label(model_id: str) -> str:
    return model_id.split("/")[-1].replace(".", "_").replace("-", "_")


def _same(value: Any, other: Any) -> bool:
    if isinstance(value, float) or isinstance(other, float):
        return abs(float(value) - float(other)) <= 1e-12
    return value == other


def _recipe_checks(config_paths: list[Path], *, repo_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    training_paths = []
    for pipeline_path in config_paths:
        pipeline = load_pipeline_config(pipeline_path.resolve())
        training_value = pipeline.get("training_plan", {}).get("config")
        if not isinstance(training_value, str) or not training_value.strip():
            raise ValueError(f"Pipeline is missing training_plan.config: {pipeline_path}")
        training_path = Path(training_value)
        if not training_path.is_absolute():
            training_path = repo_root / training_path
        training_paths.append(training_path.resolve())
    configs = [load_training_config(path) for path in training_paths]
    models = [config.get("model", {}) for config in configs]
    expected_models = list(FIXED_M1_MODELS)
    observed_models = [str(model.get("model_id", "")) for model in models]
    passed = set(observed_models) == set(expected_models) and len(observed_models) == len(set(observed_models))
    checks.append({"id": "training_fixed_model_set", "status": "pass" if passed else "blocked", "detail": observed_models})
    if not passed:
        blockers.append("training_fixed_model_set")

    base = configs[0]
    base_dataset = base["dataset"]
    base_training = base["training"]
    for index, config in enumerate(configs[1:], start=1):
        dataset = config["dataset"]
        mismatches = [
            field
            for field in ("version", "dataset_manifest", "train_file", "validation_file", "text_field", "answer_field", "split_seed")
            if dataset.get(field) != base_dataset.get(field)
        ]
        check_id = f"training_dataset_identity_model_{index}"
        checks.append({"id": check_id, "status": "pass" if not mismatches else "blocked", "detail": mismatches or "matched"})
        if mismatches:
            blockers.append(check_id)

    for field in COMMON_TRAINING_FIELDS:
        values = [config["training"].get(field) for config in configs]
        passed = all(_same(values[0], value) for value in values[1:])
        check_id = f"common_training_{field}"
        checks.append({"id": check_id, "status": "pass" if passed else "blocked", "detail": values})
        if not passed:
            blockers.append(check_id)

    effective_batches = [
        int(config["training"]["per_device_train_batch_size"])
        * int(config["training"].get("gradient_accumulation_steps", 1))
        * int(config["runtime"].get("world_size", 1))
        for config in configs
    ]
    passed = effective_batches == [500, 500, 500]
    checks.append({"id": "effective_batch_500", "status": "pass" if passed else "blocked", "detail": effective_batches})
    if not passed:
        blockers.append("effective_batch_500")

    tracking_fields = (
        "dense_cadence",
        "epoch_snapshot_policy",
        "storage_preflight_required",
        "estimated_snapshot_bytes",
        "minimum_free_bytes",
        "fact_exposures_per_epoch",
    )
    base_tracking = base.get("tracking", {})
    for field in tracking_fields:
        values = [config.get("tracking", {}).get(field) for config in configs]
        passed = all(_same(values[0], value) for value in values[1:])
        check_id = f"common_tracking_{field}"
        checks.append({"id": check_id, "status": "pass" if passed else "blocked", "detail": values})
        if not passed:
            blockers.append(check_id)

    dataset_manifest = repo_root / str(base_dataset["dataset_manifest"])
    expected_hash = "b37268d6f3afbb37f13ef746b80b99169c4d94ced3471aed2ae4aa09dc85b752"
    passed = dataset_manifest.is_file() and sha256_file(dataset_manifest) == expected_hash
    checks.append({"id": "training_dataset_manifest_hash", "status": "pass" if passed else "blocked", "detail": str(dataset_manifest)})
    if not passed:
        blockers.append("training_dataset_manifest_hash")

    return checks, blockers


def build_m1_wave_plan(
    config_paths: list[Path],
    *,
    repo_root: Path,
    project_state_path: Path,
) -> dict[str, Any]:
    """Compose the non-executing three-model training and evaluation DAG."""

    if len(config_paths) != len(FIXED_M1_MODELS):
        raise ValueError("The fresh M1 wave requires exactly three model pipeline configs")
    config_paths = [path.resolve() for path in config_paths]
    repo_root = repo_root.resolve()
    project_state_path = project_state_path.resolve()

    evaluation_plan = build_m1_eval_matrix_plan(
        config_paths,
        repo_root=repo_root,
        project_state_path=project_state_path,
    )
    training_checks, training_blockers = _recipe_checks(config_paths, repo_root=repo_root)
    tasks: list[dict[str, Any]] = []
    training_task_ids: list[str] = []
    eval_task_ids: list[str] = []

    for plan, config_path in zip(evaluation_plan["subplans"], config_paths):
        model_id = str(plan["model"]["id"])
        label = _label(model_id)
        preflight_id = f"{label}__m1_identity_preflight"
        training_id = f"{label}__m1_training_and_trace"
        training_task_ids.append(training_id)
        tasks.extend(
            [
                {
                    "task_id": preflight_id,
                    "kind": "training_preflight",
                    "model_id": model_id,
                    "depends_on": [],
                    "parallel_group": "three_model_training_preflights",
                    "config_path": str(config_path),
                },
                {
                    "task_id": training_id,
                    "kind": "training_and_epoch_trace",
                    "model_id": model_id,
                    "depends_on": [preflight_id],
                    "parallel_group": "three_model_training",
                    "config_path": str(config_path),
                    "expected_updates": 252,
                    "expected_epoch_snapshots": 36,
                },
            ]
        )
        for task in evaluation_plan["tasks"]:
            if task["kind"] != "checkpoint_evaluation" or task.get("model_id") != model_id:
                continue
            eval_task = dict(task)
            eval_task["depends_on"] = [training_id]
            eval_task["parallel_group"] = "all_three_model_checkpoint_evaluations"
            tasks.append(eval_task)
            eval_task_ids.append(str(eval_task["task_id"]))

    tasks.extend(
        [
            {
                "task_id": "normalize_m1_three_model_results",
                "kind": "normalization",
                "model_id": None,
                "depends_on": eval_task_ids,
                "parallel_group": "barrier",
            },
            {
                "task_id": "build_m1_three_model_presentation_bundle",
                "kind": "presentation",
                "model_id": None,
                "depends_on": ["normalize_m1_three_model_results"],
                "parallel_group": "barrier",
            },
        ]
    )

    identity = {
        "controller": "m1_fresh_matched_three_model_wave",
        "config_sha256": [sha256_file(path) for path in config_paths],
        "project_state_sha256": sha256_file(project_state_path),
        "models": [plan["model"] for plan in evaluation_plan["subplans"]],
    }
    blockers = sorted(set(evaluation_plan["blockers"]) | set(training_blockers))
    return {
        "schema_version": 1,
        "controller": "m1_fresh_matched_three_model_wave",
        "plan_id": sha256_text(json.dumps(identity, sort_keys=True))[:16],
        "status": "ready_to_execute" if not blockers else "blocked",
        "execution_authorized": False,
        "scientific_work_started": False,
        "models": [plan["model"] for plan in evaluation_plan["subplans"]],
        "training": {
            "recipe_checks": training_checks,
            "training_config_paths": [str(path) for path in config_paths],
            "parallel_policy": "three_independent_training_chains_after_independent_preflights",
            "expected_epoch_snapshots_per_model": 36,
            "expected_trajectory_states_per_model": 37,
            "expected_total_eval_states": 111,
        },
        "evaluation": {
            "policy": "eval-v2",
            "parallel_policy": "all_checkpoint_evaluations_after_training_barriers",
            "max_concurrent_jobs": 3,
            "checkpoint_evaluation_tasks": len(eval_task_ids),
        },
        "subplans": evaluation_plan["subplans"],
        "tasks": tasks,
        "blockers": blockers,
        "safety": {
            "planner_only": True,
            "network": False,
            "model_load": False,
            "training": False,
            "evaluation": False,
            "hu_or_slurm": False,
            "note": "A later SHA-bound contract and explicit execution authorization are required.",
        },
    }
