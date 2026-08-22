from __future__ import annotations

"""Fail-closed planning for the one-command M1 evaluation wave.

This module deliberately does not import lm_eval, Transformers, Slurm clients, or model
loading code.  It turns a frozen M1 pipeline into an auditable dependency graph and refuses
execution until the separately frozen input/authorization contract is complete.
"""

import json
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.pipeline.planner import build_pipeline_plan, load_pipeline_config
from transfer_vs_relearning.utils.io import sha256_file, sha256_text


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"YAML mapping required: {path}")
    return payload


def _resolve(repo_root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def _sha_matches(path: Path | None, expected: Any) -> bool:
    return path is not None and path.is_file() and isinstance(expected, str) and sha256_file(path) == expected


def _check(checks: list[dict[str, Any]], check_id: str, passed: bool, detail: str) -> None:
    checks.append({"id": check_id, "status": "pass" if passed else "blocked", "detail": detail})


def _bundle_names(config: dict[str, Any]) -> tuple[str, ...]:
    evaluation = config.get("evaluation")
    if not isinstance(evaluation, dict):
        return ()
    dense = evaluation.get("dense_bundles", [])
    full = evaluation.get("full_bundles", [])
    if not isinstance(dense, list):
        dense = []
    if not isinstance(full, list):
        full = []
    values = [str(item) for item in (*dense, *full) if isinstance(item, str)]
    return tuple(dict.fromkeys(values))


def build_m1_eval_plan(
    config_path: Path,
    *,
    repo_root: Path,
    project_state_path: Path,
) -> dict[str, Any]:
    """Build a parallel, non-executing M1 evaluation plan and readiness ledger."""

    repo_root = repo_root.resolve()
    config_path = config_path.resolve()
    project_state_path = project_state_path.resolve()
    config = load_pipeline_config(config_path)
    project_state = _load_yaml(project_state_path)
    checks: list[dict[str, Any]] = []

    # The draft planner validates schedule, cadence and output invariants.  It also guarantees
    # that no accidental execution-enabled config can be accepted by this preparation command.
    try:
        pipeline_plan = build_pipeline_plan(
            config_path,
            repo_root=repo_root,
            allow_execution_authorized_config=True,
        )
        planner_error = None
    except (OSError, ValueError, KeyError, TypeError) as error:
        pipeline_plan = None
        planner_error = str(error)
    _check(checks, "pipeline_schema_and_schedule", pipeline_plan is not None, planner_error or "valid")

    experiment = config.get("experiment") if isinstance(config.get("experiment"), dict) else {}
    evaluation = config.get("evaluation") if isinstance(config.get("evaluation"), dict) else {}
    inputs = config.get("inputs") if isinstance(config.get("inputs"), dict) else {}
    execution = config.get("execution") if isinstance(config.get("execution"), dict) else {}
    readiness = project_state.get("readiness") if isinstance(project_state.get("readiness"), dict) else {}
    design = project_state.get("m1_confirmed_design") if isinstance(project_state.get("m1_confirmed_design"), dict) else {}

    _check(
        checks,
        "m1_state_binding",
        experiment.get("state") == "M1" and experiment.get("parent_state") == "M0",
        f"state={experiment.get('state')!r}, parent_state={experiment.get('parent_state')!r}",
    )
    _check(
        checks,
        "eval_v2_binding",
        evaluation.get("contract") == "eval-v2" and readiness.get("evaluation_contract") == "frozen",
        f"config contract={evaluation.get('contract')!r}, project contract={readiness.get('evaluation_contract')!r}",
    )
    _check(
        checks,
        "project_ready_to_measure",
        readiness.get("ready_to_measure") is True,
        f"ready_to_measure={readiness.get('ready_to_measure')!r}",
    )
    _check(
        checks,
        "project_ready_to_train_and_checkpoint",
        readiness.get("ready_to_train") is True,
        f"ready_to_train={readiness.get('ready_to_train')!r}; an M1 checkpoint is required before scoring",
    )
    _check(
        checks,
        "turblimp_identity_inherited",
        design.get("turblimp_route") == "inherit_m0_eval_v2_juletxra_turblimp"
        and bool(design.get("turblimp_revision")),
        f"route={design.get('turblimp_route')!r}, revision={design.get('turblimp_revision')!r}",
    )
    _check(
        checks,
        "pile_10k_excluded",
        design.get("pile_10k_inherited") is False and "pile_10k" not in _bundle_names(config),
        "Pile-10k is retired and must not appear in an M1 bundle",
    )
    _check(
        checks,
        "m1_synthetic_fact_corpus",
        design.get("m1_training_corpus") == "synthetic_english_facts",
        f"M1 corpus={design.get('m1_training_corpus')!r}",
    )
    _check(
        checks,
        "m2_vngrs_boundary",
        design.get("m2_primary_turkish_corpus") == "vngrs-ai/vngrs-web-corpus",
        f"M2 primary corpus={design.get('m2_primary_turkish_corpus')!r}",
    )

    exact_prefix = evaluation.get("exact_prefix") if isinstance(evaluation.get("exact_prefix"), dict) else {}
    exact_registry = _resolve(repo_root, exact_prefix.get("registry"))
    _check(
        checks,
        "exact_prefix_mandatory",
        exact_prefix.get("required") is True
        and exact_prefix.get("probe_count") == 500
        and "exact_prefix_500" in _bundle_names(config)
        and _sha_matches(exact_registry, exact_prefix.get("registry_sha256")),
        "requires 500 frozen probes and an exact registry hash",
    )

    eval_registry = _resolve(repo_root, inputs.get("eval_registry", "configs/evaluation/eval_v2_registry.yaml"))
    _check(
        checks,
        "eval_registry_identity",
        _sha_matches(eval_registry, inputs.get("eval_registry_sha256")),
        f"registry={eval_registry}",
    )

    for label, manifest_key, hash_key in (
        ("m1_checkpoint_manifest", "m1_checkpoint_manifest", "m1_checkpoint_manifest_sha256"),
        ("m1_training_manifest", "m1_training_manifest", "m1_training_manifest_sha256"),
        ("m1_fact_dataset_manifest", "m1_fact_dataset_manifest", "m1_fact_dataset_manifest_sha256"),
    ):
        path = _resolve(repo_root, inputs.get(manifest_key))
        _check(checks, label, _sha_matches(path, inputs.get(hash_key)), f"path={path}")

    _check(
        checks,
        "execution_contract_authorized",
        config.get("execution_authorized") is True and execution.get("adapter_registered") is True,
        "requires a separately frozen, hash-bound execution contract and registered adapter",
    )
    output_root = _resolve(repo_root, (config.get("outputs") or {}).get("root"))
    _check(
        checks,
        "fresh_output_root",
        output_root is not None and output_root.is_absolute() and not output_root.exists(),
        f"root={output_root}",
    )

    blockers = [item["id"] for item in checks if item["status"] != "pass"]
    if pipeline_plan is None:
        tasks: list[dict[str, Any]] = []
        plan_identity = {"config_sha256": sha256_file(config_path), "blockers": blockers}
    else:
        checkpoints = pipeline_plan["checkpoints"]
        dense_value = evaluation.get("dense_bundles", [])
        full_value = evaluation.get("full_bundles", [])
        dense = tuple(str(item) for item in dense_value) if isinstance(dense_value, list) else ()
        full = tuple(str(item) for item in full_value) if isinstance(full_value, list) else ()
        tasks = [
            {
                "task_id": f"m1_eval_{point['checkpoint_id'].replace('-', '_')}",
                "kind": "checkpoint_evaluation",
                "checkpoint_id": point["checkpoint_id"],
                "epoch": point["epoch"],
                "update": point["update"],
                "bundles": list(dict.fromkeys((*dense, *(full if point["full"] else ())))),
                "depends_on": ["m1_training_manifest"],
                "parallel_group": "checkpoint_evaluations",
            }
            for point in checkpoints
        ]
        tasks.extend(
            [
                {
                    "task_id": "normalize_m1_results",
                    "kind": "normalization",
                    "checkpoint_id": None,
                    "bundles": [],
                    "depends_on": [task["task_id"] for task in tasks],
                    "parallel_group": "barrier",
                },
                {
                    "task_id": "build_m1_presentation_bundle",
                    "kind": "presentation",
                    "checkpoint_id": None,
                    "bundles": [],
                    "depends_on": ["normalize_m1_results"],
                    "parallel_group": "barrier",
                },
            ]
        )
        plan_identity = {
            "config_sha256": sha256_file(config_path),
            "pipeline_plan_id": pipeline_plan["plan_id"],
            "checkpoint_ids": [point["checkpoint_id"] for point in checkpoints],
            "bundles": _bundle_names(config),
        }

    return {
        "schema_version": 1,
        "controller": "m1_eval_one_command",
        "plan_id": sha256_text(json.dumps(plan_identity, sort_keys=True))[:16],
        "status": "ready_to_execute" if not blockers else "blocked",
        "execution_authorized": False,
        "scientific_work_started": False,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "project_state_path": str(project_state_path),
        "project_state_sha256": sha256_file(project_state_path),
        "parallelism": {
            "policy": "all_checkpoint_evaluations_parallel_after_training_barrier",
            "max_concurrent_jobs": int(execution.get("max_concurrent_jobs", 3)),
            "barrier": "normalize_then_presentation",
        },
        "checks": checks,
        "blockers": blockers,
        "tasks": tasks,
        "safety": {
            "planner_only": True,
            "network": False,
            "model_load": False,
            "training": False,
            "evaluation": False,
            "hu_or_slurm": False,
            "note": "This controller emits a plan only; a future exact contract must register execution adapters.",
        },
    }
