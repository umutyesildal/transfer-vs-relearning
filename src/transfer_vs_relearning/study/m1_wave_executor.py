from __future__ import annotations

"""Execution adapter for the hash-bound three-model M1 eval-v2 trajectory wave.

Frozen topology (contract v1, append-only correction 3):
  read-only final preflight
    -> single A10080 array 0-107%6 over all 108 epoch snapshots (gpu:a10080gb:1)
    -> afterany family finalizer that projects the three M0 parent states from the
       canonical hash-closed M0 evidence and closes the wave only at 111/111.
Every task passes a fail-closed GPU free-memory gate (20 GiB) with a frozen bounded
probe-wait-reprobe schedule before scoring.
"""

import json
import os
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.study.m1_eval_validation import (
    derive_cheap_factual_from_full,
    validate_exact_prefix_output,
    validate_factual_output,
    validate_generation_output,
    validate_harness_output,
    validate_turkish_perplexity_output,
    verify_snapshot,
)
from transfer_vs_relearning.utils.io import read_jsonl, sha256_file, sha256_text, write_json


RUNTIME_PYTHON = Path(
    "/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/bin/python"
)
RUNTIME_LOCK = Path(
    "/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/environment.lock.txt"
)
RUNTIME_LOCK_SHA256 = "f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942"
DATASET_CACHE_ROOT = Path("/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v8/cache")
DATASET_CONTENT_MANIFEST = Path(
    "/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v8/dataset_content_manifest.jsonl"
)
DATASET_CONTENT_MANIFEST_SHA256 = "0bd32f84bcf94b8208b35a32cdb9a0e311e7ba005392a7557f80c316d0dfd7fb"
MODEL_LABELS = {
    "allenai/OLMo-2-0425-1B": "olmo",
    "Qwen/Qwen2.5-1.5B": "qwen",
    "HuggingFaceTB/SmolLM2-1.7B": "smollm",
}
EXPECTED_CHECKPOINT_IDS = ["parent", *(f"epoch-{epoch:03d}" for epoch in range(1, 37))]
FULL_EPOCHS = {0, 18, 36}
EPOCHS_PER_MODEL = 36
GPU_TASK_COUNT = EPOCHS_PER_MODEL * len(MODEL_LABELS)
TOTAL_SCIENTIFIC_STATES = GPU_TASK_COUNT + len(MODEL_LABELS)
CHEAP_PROBE_COUNT = 1500
FULL_PROBE_COUNT = 12000
EXACT_PREFIX_PROBE_COUNT = 500
TRWIKI_EXPECTED_DOCUMENTS = 10034
MIN_FREE_GPU_MEMORY_BYTES = 21474836480
GATE_PROBE_ATTEMPTS = 13
GATE_RETRY_WAIT_SECONDS = 600
EVALUATION_ROUTE = {
    "gres": "gpu:a10080gb:1",
    "count": GPU_TASK_COUNT,
    "throttle": 6,
    "offset": 0,
    "name": "m1-eval-v2-a100",
}
M0_CANONICAL_EVIDENCE = {
    "normalization_config": "configs/evaluation/eval_v2_m0_metric_normalization_v1f.yaml",
    "normalization_config_sha256": (
        "3781cd62e6bfa1d3484bd87f54b44000eb9aae35a8b0260ad31b93cc15d56047"
    ),
    "output_root": "/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1f",
    "source_registry": "/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b/source_registry.jsonl",
    "source_registry_sha256": (
        "a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265"
    ),
    "registry_source_rows": 24,
    "observation_row_count": 42,
    "rows_per_model": 14,
}
FROZEN_INPUTS = {
    "cheap_factual": (
        "configs/evaluation/registries/eval_v1_factual_cheap_bilingual_1500.csv",
        "9619339d5d0373036d26d39c88f36976bd4a9248f64ed346241a6ce54e658fc2",
    ),
    "full_factual": (
        "configs/evaluation/registries/eval_v1_factual_full_bilingual_12000.csv",
        "5125850a2db24c6b570971a58e9ba8a8586cabdec9084eb0e99bbd639691d93f",
    ),
    "exact_prefix": (
        "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv",
        "1644288d0d62c51c56ceaae71b9eef7225b88326267281c8df8aeef9d7619c8e",
    ),
    "dataset_manifest": (
        "artifacts/datasets/relation_v2_gate_v1/manifest.json",
        "b37268d6f3afbb37f13ef746b80b99169c4d94ced3471aed2ae4aa09dc85b752",
    ),
    "generation_corpus": (
        "/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl",
        "578a0879807f928e423f61631ee697a865af006df21e60e10e25a534c345097a",
    ),
    "generation_prompts": (
        "configs/general_capability/prompts_v1.jsonl",
        "b21035ecf4819798dbf2807177e6bdd0b97a117f49fb77591e0e1602e67fb977",
    ),
    "generation_completions": (
        "configs/general_capability/completions_v1.jsonl",
        "9c14631b8de651a2d7f698456d767f2126e30173116f5fb21c442b6af7002580",
    ),
    "generation_subjects": (
        "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv",
        "60dd741f8ef2815755beafa8bb5799f4112af3d94b1b8c4c171bfef28b07e6c1",
    ),
    "turkish_corpus": (
        "/vol/tmp2/yesildau/turkish_bridge_v1/corpus/trwiki_20260601_bridge_v1/splits/validation_documents.jsonl",
        "15480c1f543acf6df7aac1b2a2ee15fdcb3a544814f0063a181bd7a9cb0ca4f8",
    ),
}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML mapping required: {path}")
    return payload


def _resolve(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def _verify_file(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Missing frozen input ({label}): {path}")
    if sha256_file(path) != expected:
        raise ValueError(f"SHA-256 mismatch ({label}): {path}")


def assert_free_gpu_memory() -> dict[str, Any]:
    """Fail closed unless the allocated GPU has at least the frozen free-memory gate."""

    visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    if not visible:
        raise RuntimeError("CUDA_VISIBLE_DEVICES is missing; cannot verify the allocated GPU")
    index = visible.split(",")[0].strip()
    probe = subprocess.run(
        ["nvidia-smi", "-i", index, "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0 or not probe.stdout.strip().isdigit():
        raise RuntimeError(
            f"GPU free-memory probe failed (exit={probe.returncode}): {probe.stderr.strip()}"
        )
    free_bytes = int(probe.stdout.strip()) * 1024 * 1024
    if free_bytes < MIN_FREE_GPU_MEMORY_BYTES:
        raise ValueError(
            f"GPU free-memory gate failed on index {index}: {free_bytes} bytes free "
            f"< {MIN_FREE_GPU_MEMORY_BYTES} required"
        )
    return {"gpu_index": index, "free_bytes": free_bytes, "gate_bytes": MIN_FREE_GPU_MEMORY_BYTES}


def load_m0_canonical_evidence() -> dict[str, Any]:
    """Verify the canonical M0 evidence bundle and attribute its rows per model.

    The bundle is closed through its own final_inventory.json hash chain; the three
    parent states are references into this immutable evidence and are never rescored.
    """

    binding = M0_CANONICAL_EVIDENCE
    root = Path(binding["output_root"])
    registry_path = Path(binding["source_registry"])
    _verify_file(registry_path, binding["source_registry_sha256"], "m0_source_registry")
    with registry_path.open(encoding="utf-8") as handle:
        registry_rows = [json.loads(line) for line in handle if line.strip()]
    if len(registry_rows) != int(binding["registry_source_rows"]):
        raise ValueError("Canonical M0 source registry row count mismatch")
    registered_models = {str(row.get("model_id")) for row in registry_rows}
    if registered_models != set(MODEL_LABELS.values()):
        raise ValueError("Canonical M0 source registry does not bind the three fixed models")

    inventory_path = root / "final_inventory.json"
    if not inventory_path.is_file():
        raise FileNotFoundError(f"Missing canonical M0 inventory: {inventory_path}")
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    declared = inventory.get("files")
    if not isinstance(declared, list) or not declared:
        raise ValueError("Canonical M0 inventory has no files list")
    declared_paths: set[Path] = set()
    for row in declared:
        path = Path(str(row["path"]))
        declared_paths.add(path)
        _verify_file(path, str(row["sha256"]), f"m0_canonical[{path.name}]")
        if path.stat().st_size != int(row["bytes"]):
            raise ValueError(f"Canonical M0 inventory byte mismatch: {path}")
    observed_files = {
        path.resolve()
        for path in root.iterdir()
        if path.is_file() and path.name != "final_inventory.json"
    }
    if observed_files != declared_paths:
        raise ValueError("Canonical M0 output root differs from its frozen inventory")

    summary_path = root / "m0_metric_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("status") != "complete" or int(summary.get("observation_count", -1)) != int(
        binding["observation_row_count"]
    ):
        raise ValueError("Canonical M0 metric summary is incomplete")

    manifest_path = root / "normalization_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("config_sha256") != binding["normalization_config_sha256"]:
        raise ValueError("Canonical M0 normalization manifest binds a different config")
    audit = manifest.get("audit")
    metric_rows = audit.get("metric_rows") if isinstance(audit, dict) else None
    if not isinstance(metric_rows, list) or len(metric_rows) != int(
        binding["observation_row_count"]
    ):
        raise ValueError("Canonical M0 normalization manifest has no complete metric rows")
    rows_by_model: dict[str, list[dict[str, Any]]] = {label: [] for label in MODEL_LABELS.values()}
    for row in metric_rows:
        raw_path = str(row.get("raw_artifact_path", ""))
        owners = [label for label in MODEL_LABELS.values() if f"/{label}/" in raw_path]
        if len(owners) != 1 or not isinstance(row.get("value"), (int, float)):
            raise ValueError(f"Unattributable canonical M0 metric row: {raw_path}")
        rows_by_model[owners[0]].append(row)
    for label, rows in rows_by_model.items():
        if len(rows) != int(binding["rows_per_model"]):
            raise ValueError(f"Canonical M0 evidence count mismatch for {label}: {len(rows)}")
    return {
        "final_inventory_sha256": sha256_file(inventory_path),
        "summary_sha256": sha256_file(summary_path),
        "manifest_sha256": sha256_file(manifest_path),
        "observation_row_count": len(metric_rows),
        "rows_by_model": rows_by_model,
    }


def _parent_projection_binding() -> dict[str, Any]:
    return {
        "mode": "projected_from_canonical_m0_evidence_without_rescoring",
        "normalization_config": M0_CANONICAL_EVIDENCE["normalization_config"],
        "normalization_config_sha256": M0_CANONICAL_EVIDENCE["normalization_config_sha256"],
        "canonical_output_root": M0_CANONICAL_EVIDENCE["output_root"],
        "source_registry": M0_CANONICAL_EVIDENCE["source_registry"],
        "source_registry_sha256": M0_CANONICAL_EVIDENCE["source_registry_sha256"],
        "observation_row_count": M0_CANONICAL_EVIDENCE["observation_row_count"],
        "rows_per_model": M0_CANONICAL_EVIDENCE["rows_per_model"],
    }


def build_task_matrix(
    config_paths: list[Path],
    *,
    repo_root: Path,
    contract_path: Path,
    contract_sha256: str,
    execution_config_path: Path,
    execution_config_sha256: str,
) -> dict[str, Any]:
    if len(config_paths) != 3:
        raise ValueError("Exactly three M1 eval-v2 configs are required")
    repo_root = repo_root.resolve()
    contract_path = contract_path if contract_path.is_absolute() else repo_root / contract_path
    execution_config_path = (
        execution_config_path
        if execution_config_path.is_absolute()
        else repo_root / execution_config_path
    )
    _verify_file(contract_path.resolve(), contract_sha256, "authorized_contract")
    _verify_file(
        execution_config_path.resolve(),
        execution_config_sha256,
        "authorized_execution_config",
    )
    execution_config = _load_yaml(execution_config_path.resolve())
    if execution_config.get("status") != "frozen" or execution_config.get("execution_ready") is not True:
        raise ValueError("Authorized M1 execution config is not frozen and execution-ready")
    if execution_config.get("contract") != str(contract_path.resolve().relative_to(repo_root)):
        raise ValueError("Authorized M1 execution config points to a different contract")
    adapter = execution_config.get("adapter")
    if not isinstance(adapter, dict) or adapter.get("id") != "slurm_m1_matched_wave_v1":
        raise ValueError("Authorized M1 execution config has no registered adapter")
    _verify_file(repo_root / str(adapter["module"]), str(adapter["module_sha256"]), "adapter_module")
    _verify_file(repo_root / str(adapter["entrypoint"]), str(adapter["entrypoint_sha256"]), "adapter_entrypoint")
    tasks: list[dict[str, Any]] = []
    parent_identities: dict[str, dict[str, Any]] = {}
    output_roots: set[str] = set()
    models_seen: set[str] = set()
    config_rows: list[dict[str, Any]] = []
    for raw_path in config_paths:
        config_path = raw_path if raw_path.is_absolute() else repo_root / raw_path
        config_path = config_path.resolve()
        config = _load_yaml(config_path)
        experiment = config["experiment"]
        inputs = config["inputs"]
        evaluation = config["evaluation"]
        execution = config["execution"]
        model_id = str(experiment["model_id"])
        if model_id not in MODEL_LABELS or model_id in models_seen:
            raise ValueError(f"Invalid or duplicate fixed model: {model_id}")
        if config.get("status") != "frozen" or config.get("execution_authorized") is not False:
            raise ValueError(f"Pipeline config must remain frozen/pre-authorization: {config_path}")
        if evaluation.get("contract") != "eval-v2" or set(evaluation.get("full_epochs", [])) != FULL_EPOCHS:
            raise ValueError(f"Eval-v2/full-epoch binding mismatch: {config_path}")
        if execution.get("adapter_registered") is not True or execution.get("adapter") != "slurm_m1_matched_wave_v1":
            raise ValueError(f"M1 Slurm adapter is not registered: {config_path}")
        output_root = Path(str(config["outputs"]["root"]))
        if not output_root.is_absolute():
            raise ValueError("M1 evaluation output root must be absolute")
        output_roots.add(str(output_root))
        checkpoint_manifest = _resolve(repo_root, str(inputs["m1_checkpoint_manifest"]))
        training_manifest = _resolve(repo_root, str(inputs["m1_training_manifest"]))
        parent_manifest = _resolve(repo_root, str(inputs["m0_model_manifest"]))
        _verify_file(checkpoint_manifest, str(inputs["m1_checkpoint_manifest_sha256"]), "checkpoint_manifest")
        _verify_file(training_manifest, str(inputs["m1_training_manifest_sha256"]), "training_manifest")
        _verify_file(parent_manifest, str(inputs["m0_model_manifest_sha256"]), "m0_model_manifest")
        training_payload = json.loads(training_manifest.read_text(encoding="utf-8"))
        if training_payload.get("status") != "complete":
            raise ValueError(f"M1 training manifest is not complete: {training_manifest}")
        checkpoint_payload = json.loads(checkpoint_manifest.read_text(encoding="utf-8"))
        rows = checkpoint_payload.get("checkpoints")
        if not isinstance(rows, list) or [row.get("checkpoint_id") for row in rows] != EXPECTED_CHECKPOINT_IDS:
            raise ValueError(f"Expected parent plus 36 ordered epoch checkpoints: {checkpoint_manifest}")
        label = MODEL_LABELS[model_id]
        epoch_tasks = 0
        for row in rows:
            checkpoint_id = str(row["checkpoint_id"])
            epoch = int(row["epoch"])
            if checkpoint_id == "parent":
                if str(row.get("state", "")) != "M0" or str(row.get("checkpoint_sha256")) != str(
                    inputs["m0_model_manifest_sha256"]
                ):
                    raise ValueError(f"M1 parent row does not bind the frozen M0 identity: {label}")
                parent_identities[label] = {
                    "model": label,
                    "model_id": model_id,
                    "model_revision": str(experiment["model_revision"]),
                    "checkpoint_id": "parent",
                    "state": "M0",
                    "epoch": 0,
                    "update": 0,
                    "m0_model_manifest": str(parent_manifest),
                    "m0_model_manifest_sha256": str(inputs["m0_model_manifest_sha256"]),
                    "projection": _parent_projection_binding(),
                }
                continue
            model_manifest = _resolve(repo_root, str(row["model_manifest"]))
            manifest_hash = row.get("model_manifest_sha256") or row.get("checkpoint_sha256")
            _verify_file(model_manifest, str(manifest_hash), f"{label}.{checkpoint_id}.model_manifest")
            snapshot_manifest = row.get("snapshot_manifest")
            tasks.append(
                {
                    "task_index": len(tasks),
                    "model": label,
                    "model_id": model_id,
                    "model_revision": str(experiment["model_revision"]),
                    "checkpoint_id": checkpoint_id,
                    "epoch": epoch,
                    "update": int(row["update"]),
                    "full": epoch in FULL_EPOCHS,
                    "model_manifest": str(model_manifest),
                    "model_manifest_sha256": str(manifest_hash),
                    "snapshot_manifest": None if snapshot_manifest is None else str(snapshot_manifest),
                    "snapshot_manifest_sha256": (
                        None if row.get("snapshot_manifest_sha256") is None
                        else str(row["snapshot_manifest_sha256"])
                    ),
                    "checkpoint_sha256": str(row["checkpoint_sha256"]),
                    "training_manifest": str(training_manifest),
                    "training_manifest_sha256": str(inputs["m1_training_manifest_sha256"]),
                }
            )
            epoch_tasks += 1
        if epoch_tasks != EPOCHS_PER_MODEL or label not in parent_identities:
            raise ValueError(f"M1 checkpoint manifest must yield one parent plus 36 snapshots: {label}")
        models_seen.add(model_id)
        configured_row = execution_config.get("pipeline_configs", {}).get(label)
        if not isinstance(configured_row, dict) or configured_row.get("sha256") != sha256_file(config_path):
            raise ValueError(f"Execution config does not bind pipeline config: {label}")
        config_rows.append({"path": str(config_path), "sha256": sha256_file(config_path), "model_id": model_id})
    parent_projections = [parent_identities[label] for label in MODEL_LABELS.values()]
    if (
        models_seen != set(MODEL_LABELS)
        or len(output_roots) != 1
        or len(tasks) != GPU_TASK_COUNT
        or len(parent_projections) != len(MODEL_LABELS)
    ):
        raise ValueError(
            "M1 task matrix must contain three fixed models, "
            f"{GPU_TASK_COUNT} snapshot tasks and three parent projections"
        )
    if not RUNTIME_PYTHON.is_file() or not os.access(RUNTIME_PYTHON, os.X_OK):
        raise FileNotFoundError(f"Frozen evaluation Python is missing or not executable: {RUNTIME_PYTHON}")
    _verify_file(RUNTIME_LOCK, RUNTIME_LOCK_SHA256, "runtime_environment_lock")
    _verify_file(
        DATASET_CONTENT_MANIFEST,
        DATASET_CONTENT_MANIFEST_SHA256,
        "dataset_content_manifest",
    )
    if not DATASET_CACHE_ROOT.is_dir():
        raise FileNotFoundError(f"Frozen evaluation dataset cache is missing: {DATASET_CACHE_ROOT}")
    for label, (value, expected) in FROZEN_INPUTS.items():
        _verify_file(_resolve(repo_root, value), expected, label)
    m0_evidence = load_m0_canonical_evidence()
    identity = {
        "contract_sha256": contract_sha256,
        "execution_config_sha256": execution_config_sha256,
        "configs": config_rows,
        "tasks": tasks,
        "parent_projections": parent_projections,
        "m0_final_inventory_sha256": m0_evidence["final_inventory_sha256"],
        "output_root": next(iter(output_roots)),
    }
    return {
        "schema_version": 2,
        "status": "ready",
        "adapter": "slurm_m1_matched_wave_v1",
        "matrix_id": sha256_text(json.dumps(identity, sort_keys=True))[:16],
        "repo_root": str(repo_root),
        "output_root": next(iter(output_roots)),
        "gpu_task_count": GPU_TASK_COUNT,
        "total_scientific_states": TOTAL_SCIENTIFIC_STATES,
        "authorization": {
            "contract": str(contract_path.resolve()),
            "contract_sha256": contract_sha256,
            "execution_config": str(execution_config_path.resolve()),
            "execution_config_sha256": execution_config_sha256,
        },
        "configs": config_rows,
        "tasks": tasks,
        "parent_projections": parent_projections,
    }


def _recoverable_stale_root(output_root: Path) -> bool:
    """True only for a root from a submission attempt that never left the login node."""

    manifest_path = output_root / "control/submission_manifest.json"
    if not manifest_path.is_file():
        return False
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not str(payload.get("status", "")).startswith("not_submitted"):
        return False
    if any(True for _ in output_root.glob("results/*/*/task_result.json")):
        return False
    return True


def initialize_wave(matrix: dict[str, Any]) -> Path:
    output_root = Path(matrix["output_root"])
    recovered = False
    if output_root.exists():
        if not _recoverable_stale_root(output_root):
            raise FileExistsError(f"Fresh M1 evaluation root already exists: {output_root}")
        recovered = True
    for relative in ("control", "logs", "results", "tmp", "cache"):
        (output_root / relative).mkdir(parents=True, exist_ok=True)
    matrix_path = output_root / "control/task_matrix.json"
    write_json(matrix_path, matrix)
    write_json(
        output_root / "control/preflight.json",
        {
            "schema_version": 2,
            "status": "ready",
            "matrix": str(matrix_path),
            "matrix_sha256": sha256_file(matrix_path),
            "gpu_task_count": len(matrix.get("tasks", [])),
            "parent_projection_count": len(matrix.get("parent_projections", [])),
            "total_scientific_states": matrix.get(
                "total_scientific_states",
                len(matrix.get("tasks", [])) + len(matrix.get("parent_projections", [])),
            ),
            "model_count": 3,
            "recovered_stale_root": recovered,
        },
    )
    return matrix_path


def load_matrix(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if (
        payload.get("status") != "ready"
        or len(payload.get("tasks", [])) != GPU_TASK_COUNT
        or len(payload.get("parent_projections", [])) != len(MODEL_LABELS)
        or payload.get("total_scientific_states") != TOTAL_SCIENTIFIC_STATES
    ):
        raise ValueError("Invalid M1 task matrix")
    return payload


def preflight_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    output_root = Path(matrix["output_root"])
    matrix_path = output_root / "control/task_matrix.json"
    if not matrix_path.is_file() or matrix_path.resolve() != Path(
        output_root / "control/task_matrix.json"
    ).resolve():
        raise FileNotFoundError("Canonical M1 task matrix is missing")
    if not RUNTIME_PYTHON.is_file() or not os.access(RUNTIME_PYTHON, os.X_OK):
        raise FileNotFoundError(f"Frozen evaluation Python is missing or not executable: {RUNTIME_PYTHON}")
    _verify_file(RUNTIME_LOCK, RUNTIME_LOCK_SHA256, "runtime_environment_lock")
    authorization = matrix["authorization"]
    _verify_file(
        Path(authorization["contract"]),
        authorization["contract_sha256"],
        "authorized_contract",
    )
    _verify_file(
        Path(authorization["execution_config"]),
        authorization["execution_config_sha256"],
        "authorized_execution_config",
    )
    _verify_file(DATASET_CONTENT_MANIFEST, DATASET_CONTENT_MANIFEST_SHA256, "dataset_content_manifest")
    if not DATASET_CACHE_ROOT.is_dir():
        raise FileNotFoundError(f"Frozen evaluation dataset cache is missing: {DATASET_CACHE_ROOT}")
    for config in matrix["configs"]:
        _verify_file(Path(config["path"]), config["sha256"], "pipeline_config")
    for task in matrix["tasks"]:
        _verify_file(Path(task["model_manifest"]), task["model_manifest_sha256"], "task_model_manifest")
        _verify_file(Path(task["training_manifest"]), task["training_manifest_sha256"], "task_training_manifest")
    for entry in matrix["parent_projections"]:
        _verify_file(
            Path(entry["m0_model_manifest"]),
            entry["m0_model_manifest_sha256"],
            "parent_model_manifest",
        )
    for label, (value, expected) in FROZEN_INPUTS.items():
        _verify_file(_resolve(Path(matrix["repo_root"]), value), expected, label)
    load_m0_canonical_evidence()
    existing_results = list((output_root / "results").glob("*/*/task_result.json"))
    if existing_results:
        raise FileExistsError("Fresh M1 preflight found pre-existing task results")
    return {
        "status": "ready",
        "matrix_id": matrix["matrix_id"],
        "gpu_task_count": GPU_TASK_COUNT,
        "total_scientific_states": TOTAL_SCIENTIFIC_STATES,
    }


def _run(command: list[str], *, repo_root: Path) -> None:
    result = subprocess.run(command, cwd=repo_root, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Evaluation command failed ({result.returncode}): {shlex.join(command)}")


def _write_exact_config(task: dict[str, Any], *, repo_root: Path, state_root: Path) -> Path:
    path = state_root / "configs/exact_prefix.json"
    write_json(
        path,
        {
            "dataset_version": "relation_v2_gate_v1_100_subjects_500_facts_direct",
            "dataset_dir": str(repo_root / "artifacts/datasets/relation_v2_gate_v1"),
            "pilot_subject_file": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json"),
            "probe_files": {"en": str(repo_root / FROZEN_INPUTS["exact_prefix"][0])},
            "model_manifest": task["model_manifest"],
            "languages": ["en"],
            "relations": ["profession", "born_in", "lives_in", "field_of_study", "works_in_industry"],
            "prompt": {"format": "direct", "template": "{question}", "answer_separator": " "},
            "scoring": {"primary": "mean_logprob", "secondary": "total_logprob", "tie_breaker": "canonical_object_id"},
            "runtime": {"bf16": False, "device": "cuda", "candidate_batch_size": 64, "checkpoint_interval": 25, "seed": 42},
            "output": {"run_root": str(state_root / "exact_prefix/raw")},
        },
    )
    return path


def _write_generation_config(task: dict[str, Any], *, repo_root: Path, state_root: Path) -> Path:
    path = state_root / "configs/generation_integrity.json"
    write_json(
        path,
        {
            "run_name": f"m1_{task['model']}_{task['checkpoint_id']}_generation",
            "output_root": str(state_root / "generation_integrity/raw"),
            "model_manifest": task["model_manifest"],
            "data": {
                "corpus_file": FROZEN_INPUTS["generation_corpus"][0],
                "prompts_file": str(repo_root / FROZEN_INPUTS["generation_prompts"][0]),
                "completions_file": str(repo_root / FROZEN_INPUTS["generation_completions"][0]),
                "synthetic_subjects_file": str(repo_root / FROZEN_INPUTS["generation_subjects"][0]),
            },
            "scoring": {"block_size": 512, "batch_size": 4, "candidate_batch_size": 16, "bootstrap_samples": 10000},
            "generation": {"max_new_tokens": 64},
            "runtime": {"device": "cuda", "bf16": False, "seed": 42},
        },
    )
    return path


def gate_with_retries() -> dict[str, Any]:
    """Probe the free-memory gate on a frozen wait schedule; fail closed only after
    GATE_PROBE_ATTEMPTS consecutive failures."""

    last_error: Exception | None = None
    for attempt in range(1, GATE_PROBE_ATTEMPTS + 1):
        try:
            payload = assert_free_gpu_memory()
            payload["probe_attempts"] = attempt
            return payload
        except (RuntimeError, ValueError) as exc:
            last_error = exc
            if attempt < GATE_PROBE_ATTEMPTS:
                time.sleep(GATE_RETRY_WAIT_SECONDS)
    raise RuntimeError(f"GPU free-memory gate exhausted {GATE_PROBE_ATTEMPTS} probes: {last_error}")


def run_task(matrix: dict[str, Any], task_index: int) -> dict[str, Any]:
    task = matrix["tasks"][task_index]
    repo_root = Path(matrix["repo_root"])
    output_root = Path(matrix["output_root"])
    state_root = output_root / "results" / task["model"] / task["checkpoint_id"]
    if state_root.exists():
        raise FileExistsError(f"M1 evaluation state root already exists: {state_root}")
    (state_root / "configs").mkdir(parents=True)
    _verify_file(Path(task["model_manifest"]), task["model_manifest_sha256"], "task_model_manifest")
    exact_config = _write_exact_config(task, repo_root=repo_root, state_root=state_root)
    generation_config = _write_generation_config(task, repo_root=repo_root, state_root=state_root)
    harness_task_ids = ["wikitext"]
    if task["full"]:
        harness_task_ids.extend(["blimp", "hellaswag", "winogender_female", "winogender_male", "winogender_neutral", "turblimp_core"])
    model_manifest = json.loads(Path(task["model_manifest"]).read_text(encoding="utf-8"))
    model_path = model_manifest.get("local_path_absolute") or model_manifest.get("local_path")
    tokenizer_path = model_manifest.get("tokenizer_source_path_absolute") or model_path
    commands: list[list[str]] = [
        [
            str(RUNTIME_PYTHON), "-m", "lm_eval", "run", "--model", "hf", "--model_args",
            f"pretrained={model_path}", f"tokenizer={tokenizer_path}", "dtype=float16", "trust_remote_code=False", "local_files_only=True",
            "--tasks", *harness_task_ids,
            "--num_fewshot", "0", "--batch_size", "auto:4", "--max_batch_size", "16", "--device", "cuda:0",
            "--seed", "42,42,42,42", "--output_path", str(state_root / "harness/raw"), "--show_config", "--log_samples",
        ],
        [
            str(RUNTIME_PYTHON), str(repo_root / "scripts/evaluation/evaluate_corpora_perplexity.py"),
            "--model-manifest", task["model_manifest"], "--model-label", f"m1_{task['model']}_{task['checkpoint_id']}",
            "--corpus", f"trwiki_cross_domain={FROZEN_INPUTS['turkish_corpus'][0]}", "--output-dir", str(state_root / "turkish_perplexity/raw"),
            "--block-size", "512", "--batch-size", "4", "--bootstrap-samples", "10000", "--seed", "42", "--device", "cuda", "--no-bf16",
        ],
        [str(RUNTIME_PYTHON), str(repo_root / "scripts/evaluation/evaluate_facts.py"), "--config", str(exact_config)],
        [str(RUNTIME_PYTHON), str(repo_root / "scripts/evaluation/evaluate_general_capability.py"), "--config", str(generation_config)],
    ]
    factual_registry = FROZEN_INPUTS["full_factual" if task["full"] else "cheap_factual"][0]
    commands.insert(
        1,
        [
            str(RUNTIME_PYTHON), str(repo_root / "scripts/m2/evaluate_pre_m2_frozen_suite.py"),
            "--model-label", f"m1_{task['model']}_{task['checkpoint_id']}", "--model-manifest", task["model_manifest"],
            "--dataset-dir", str(repo_root / "artifacts/datasets/relation_v2_gate_v1"), "--probe-registry", str(repo_root / factual_registry),
            "--output-dir", str(state_root / ("factual_full/raw" if task["full"] else "factual_cheap/raw")),
            "--candidate-batch-size", "16", "--checkpoint-interval", "100", "--device", "cuda", "--no-bf16",
        ],
    )
    result_path = state_root / "task_result.json"
    try:
        memory_gate = gate_with_retries()
        if task.get("snapshot_manifest"):
            verify_snapshot(
                snapshot_manifest_path=Path(task["snapshot_manifest"]),
                snapshot_manifest_sha256=str(task["snapshot_manifest_sha256"]),
                checkpoint_sha256=str(task["checkpoint_sha256"]),
                model_manifest_path=Path(task["model_manifest"]),
                model_manifest_sha256=str(task["model_manifest_sha256"]),
            )
        for command in commands:
            _run(command, repo_root=repo_root)
        validations: dict[str, Any] = {}
        validations["harness"] = validate_harness_output(state_root / "harness/raw", harness_task_ids)
        if task["full"]:
            full_root = state_root / "factual_full/raw"
            validations["factual_full"] = validate_factual_output(full_root, FULL_PROBE_COUNT)
            validations["factual_cheap_derived"] = derive_cheap_factual_from_full(
                full_root=full_root,
                cheap_root=state_root / "factual_cheap",
                cheap_registry=_resolve(repo_root, FROZEN_INPUTS["cheap_factual"][0]),
                cheap_registry_sha256=FROZEN_INPUTS["cheap_factual"][1],
            )
        else:
            validations["factual_cheap"] = validate_factual_output(
                state_root / "factual_cheap/raw", CHEAP_PROBE_COUNT
            )
        validations["exact_prefix"] = validate_exact_prefix_output(state_root / "exact_prefix/raw")
        validations["turkish_perplexity"] = validate_turkish_perplexity_output(
            state_root / "turkish_perplexity/raw",
            corpus_sha256=FROZEN_INPUTS["turkish_corpus"][1],
            expected_documents=TRWIKI_EXPECTED_DOCUMENTS,
        )
        validations["generation_integrity"] = validate_generation_output(
            state_root / "generation_integrity/raw",
            expected_prompts=len(read_jsonl(_resolve(repo_root, FROZEN_INPUTS["generation_prompts"][0]))),
            expected_completions=len(read_jsonl(_resolve(repo_root, FROZEN_INPUTS["generation_completions"][0]))),
        )
        result = {
            **task,
            "schema_version": 2,
            "status": "complete",
            "command_count": len(commands),
            "memory_gate": memory_gate,
            "validations": {
                name: {"status": payload.get("status"), "result_sha256": payload.get("result_sha256")}
                for name, payload in validations.items()
            },
        }
        write_json(result_path, result)
        return result
    except Exception as exc:
        write_json(result_path, {**task, "schema_version": 2, "status": "failed", "error": str(exc)})
        raise


def project_parent_state(matrix: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """Project one M0 parent state from the canonical evidence without rescoring."""

    output_root = Path(matrix["output_root"])
    state_root = output_root / "results" / str(entry["model"]) / "parent"
    if state_root.exists():
        raise FileExistsError(f"M1 parent projection state root already exists: {state_root}")
    evidence = load_m0_canonical_evidence()
    rows = evidence["rows_by_model"][str(entry["model"])]
    state_root.mkdir(parents=True)
    projected_rows = [
        {
            "lane_id": str(row["lane_id"]),
            "metric": str(row["metric"]),
            "value": float(row["value"]),
            "raw_artifact_path": str(row["raw_artifact_path"]),
            "raw_artifact_sha256": str(row["raw_artifact_sha256"]),
        }
        for row in rows
    ]
    result = {
        "schema_version": 2,
        "model": entry["model"],
        "model_id": entry["model_id"],
        "model_revision": entry["model_revision"],
        "checkpoint_id": "parent",
        "state": "M0",
        "epoch": 0,
        "update": 0,
        "status": "complete",
        "mode": "projected_from_canonical_m0_evidence_without_rescoring",
        "m0_model_manifest": entry["m0_model_manifest"],
        "m0_model_manifest_sha256": entry["m0_model_manifest_sha256"],
        "projection": {
            **entry["projection"],
            "observed_final_inventory_sha256": evidence["final_inventory_sha256"],
            "observed_summary_sha256": evidence["summary_sha256"],
            "observed_manifest_sha256": evidence["manifest_sha256"],
            "projected_row_count": len(projected_rows),
            "projected_rows_digest": sha256_text(json.dumps(projected_rows, sort_keys=True)),
            "rows": projected_rows,
        },
    }
    write_json(state_root / "task_result.json", result)
    return result


def finalize_wave(matrix: dict[str, Any]) -> dict[str, Any]:
    output_root = Path(matrix["output_root"])
    rows: list[dict[str, Any]] = []
    for task in matrix["tasks"]:
        path = output_root / "results" / task["model"] / task["checkpoint_id"] / "task_result.json"
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows.append({"kind": "gpu_snapshot", "task_index": task["task_index"], "path": str(path), "sha256": sha256_file(path), "status": payload.get("status")})
        else:
            rows.append({"kind": "gpu_snapshot", "task_index": task["task_index"], "path": str(path), "sha256": None, "status": "missing"})
    projection_rows: list[dict[str, Any]] = []
    for entry in matrix["parent_projections"]:
        path = output_root / "results" / str(entry["model"]) / "parent" / "task_result.json"
        row = {"kind": "parent_projection", "model": entry["model"], "path": str(path), "sha256": None, "status": "missing"}
        try:
            if path.is_file():
                payload = json.loads(path.read_text(encoding="utf-8"))
                row["sha256"] = sha256_file(path)
                row["status"] = payload.get("status")
            else:
                project_parent_state(matrix, entry)
                row["sha256"] = sha256_file(path)
                row["status"] = "complete"
        except Exception as exc:
            row["status"] = "failed"
            row["error"] = str(exc)
        projection_rows.append(row)
    all_rows = rows + projection_rows
    status = "complete" if all(row["status"] == "complete" for row in all_rows) else "incomplete"
    result = {
        "schema_version": 2,
        "status": status,
        "matrix_id": matrix["matrix_id"],
        "gpu_task_count": len(rows),
        "gpu_complete_count": sum(row["status"] == "complete" for row in rows),
        "parent_projection_count": len(projection_rows),
        "parent_complete_count": sum(row["status"] == "complete" for row in projection_rows),
        "task_count": len(all_rows),
        "complete_count": sum(row["status"] == "complete" for row in all_rows),
        "tasks": all_rows,
    }
    write_json(output_root / "control/evaluation_family_result.json", result)
    return result


def slurm_environment(output_root: Path) -> dict[str, str]:
    return {
        "HF_HOME": str(output_root / "cache/huggingface"),
        "HF_DATASETS_CACHE": str(DATASET_CACHE_ROOT / "huggingface_datasets"),
        "XDG_CACHE_HOME": str(output_root / "cache"),
        "HF_HUB_OFFLINE": "1",
        "HF_DATASETS_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "WANDB_MODE": "disabled",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": "src",
    }


def submit_wave(matrix_path: Path, *, entrypoint: Path) -> dict[str, Any]:
    matrix = load_matrix(matrix_path)
    root = Path(matrix["output_root"])
    repo_root = Path(matrix["repo_root"])
    common = ["sbatch", "--parsable", "--account=yesildau", f"--chdir={repo_root}"]
    env = slurm_environment(root)
    export_value = "ALL," + ",".join(f"{key}={value}" for key, value in env.items())
    submission_path = root / "control/submission_manifest.json"
    array_spec = f"0-{EVALUATION_ROUTE['count'] - 1}%{EVALUATION_ROUTE['throttle']}"
    preflight: str | None = None
    array: str | None = None
    finalizer: str | None = None
    try:
        subprocess.run(
            ["sbatch", "--test-only", "--account=yesildau", "--partition=std", "--cpus-per-task=4", "--mem=16G", "--time=01:00:00", "--wrap=true"],
            check=True,
        )
        subprocess.run(
            ["sbatch", "--test-only", "--account=yesildau", "--partition=gpu", f"--gres={EVALUATION_ROUTE['gres']}", f"--array={array_spec}", "--cpus-per-task=8", "--mem=64G", "--time=1-00:00:00", "--wrap=true"],
            check=True,
        )
    except Exception as exc:
        write_json(
            submission_path,
            {"schema_version": 4, "status": "not_submitted_test_only_failed", "preflight_job_id": None, "evaluation_array_job_id": None, "finalizer_job_id": None, "error": str(exc)},
        )
        raise
    preflight_cmd = [str(RUNTIME_PYTHON), str(entrypoint), "preflight", "--matrix", str(matrix_path)]
    try:
        preflight = subprocess.run(
            [*common, "--partition=std", "--job-name=m1-eval-v2-preflight", "--cpus-per-task=4", "--mem=16G", "--time=01:00:00", f"--output={root / 'logs/%x-%j.out'}", f"--error={root / 'logs/%x-%j.err'}", "--export=ALL,PYTHONPATH=src", f"--wrap=exec {shlex.join(preflight_cmd)}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip().split(";", 1)[0]
    except Exception as exc:
        write_json(
            submission_path,
            {"schema_version": 4, "status": "not_submitted_preflight_sbatch_failed", "preflight_job_id": None, "evaluation_array_job_id": None, "finalizer_job_id": None, "error": str(exc)},
        )
        raise
    task_wrap = (
        f"exec {shlex.quote(str(RUNTIME_PYTHON))} {shlex.quote(str(entrypoint))} run-task "
        f"--matrix {shlex.quote(str(matrix_path))} --task-index \"$SLURM_ARRAY_TASK_ID\""
    )
    try:
        array = subprocess.run(
            [*common, "--partition=gpu", f"--gres={EVALUATION_ROUTE['gres']}", f"--job-name={EVALUATION_ROUTE['name']}", f"--dependency=afterok:{preflight}", f"--array={array_spec}", "--cpus-per-task=8", "--mem=64G", "--time=1-00:00:00", f"--output={root / 'logs/%x-%A_%a.out'}", f"--error={root / 'logs/%x-%A_%a.err'}", f"--export={export_value}", f"--wrap={task_wrap}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip().split(";", 1)[0]
    except Exception as exc:
        write_json(
            submission_path,
            {"schema_version": 4, "status": "partial_submission_preflight_only", "preflight_job_id": preflight, "evaluation_array_job_id": None, "finalizer_job_id": None, "error": str(exc)},
        )
        raise
    final_cmd = [str(RUNTIME_PYTHON), str(entrypoint), "finalize", "--matrix", str(matrix_path)]
    try:
        finalizer = subprocess.run(
            [*common, "--partition=std", "--job-name=m1-eval-v2-finalize", f"--dependency=afterany:{array}", "--cpus-per-task=2", "--mem=8G", "--time=01:00:00", f"--output={root / 'logs/%x-%j.out'}", f"--error={root / 'logs/%x-%j.err'}", "--export=ALL,PYTHONPATH=src", f"--wrap=exec {shlex.join(final_cmd)}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip().split(";", 1)[0]
    except Exception as exc:
        write_json(
            submission_path,
            {"schema_version": 4, "status": "partial_submission_array_active", "preflight_job_id": preflight, "evaluation_array_job_id": array, "finalizer_job_id": None, "error": str(exc)},
        )
        raise
    result = {
        "schema_version": 4,
        "status": "submitted",
        "preflight_job_id": preflight,
        "evaluation_array_job_id": array,
        "finalizer_job_id": finalizer,
        "route": {**EVALUATION_ROUTE, "array_spec": array_spec},
        "gpu_task_count": GPU_TASK_COUNT,
        "total_scientific_states": TOTAL_SCIENTIFIC_STATES,
        "matrix": str(matrix_path),
    }
    write_json(submission_path, result)
    return result
