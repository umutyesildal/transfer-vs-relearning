from __future__ import annotations

import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.evaluation.evaluator import CausalCandidateEvaluator
from transfer_vs_relearning.utils.io import sha256_file, sha256_text, write_json


MODEL_ORDER = ("olmo", "qwen", "smollm")
RELATIONS = ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _resolve(path: str | Path, repo_root: Path) -> Path:
    value = Path(path)
    return value.resolve() if value.is_absolute() else (repo_root / value).resolve()


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _verify_file(path: Path, expected_sha256: str, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} is missing: {path}")
    observed = sha256_file(path)
    if observed != expected_sha256:
        raise ValueError(f"{label} SHA-256 mismatch: {observed} != {expected_sha256}")


def audit_exact_prefix_inputs(plan: dict[str, Any]) -> dict[str, Any]:
    inputs = plan["inputs"]
    probe_path = Path(inputs["probe_registry"])
    robust_path = Path(inputs["robust_registry"])
    pilot_path = Path(inputs["pilot_subject_file"])
    dataset_manifest = Path(inputs["dataset_manifest"])
    for label, path, expected in (
        ("probe_registry", probe_path, inputs["probe_registry_sha256"]),
        ("robust_registry", robust_path, inputs["robust_registry_sha256"]),
        ("pilot_subject_file", pilot_path, inputs["pilot_subject_file_sha256"]),
        ("dataset_manifest", dataset_manifest, inputs["dataset_manifest_sha256"]),
    ):
        _verify_file(path, expected, label)

    probes = _csv_rows(probe_path)
    robust = _csv_rows(robust_path)
    pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
    selected_subjects = list(pilot.get("selected_subject_ids", []))
    if len(probes) != 500 or len({row["fact_id"] for row in probes}) != 500:
        raise ValueError("Exact-prefix registry must contain exactly 500 unique facts")
    if len({row["subject_id"] for row in probes}) != 100:
        raise ValueError("Exact-prefix registry must contain exactly 100 subjects")
    if set(row["subject_id"] for row in probes) != set(selected_subjects):
        raise ValueError("Exact-prefix subjects differ from the frozen pilot selection")
    relation_counts = Counter(row["relation"] for row in probes)
    if relation_counts != Counter({relation: 100 for relation in RELATIONS}):
        raise ValueError(f"Exact-prefix relation balance mismatch: {relation_counts}")

    robust_by_fact: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in robust:
        if row["direction"] == "en_to_en":
            robust_by_fact[row["fact_id"]].append(row)
    fact_answer_identity = all(
        len(robust_by_fact[row["fact_id"]]) == 8
        and all(candidate["expected_answer"] == row["expected_answer"] for candidate in robust_by_fact[row["fact_id"]])
        for row in probes
    )
    prompt_overlap_count = sum(
        any(candidate["rendered_prompt"] == row["question"] for candidate in robust_by_fact[row["fact_id"]])
        for row in probes
    )
    if not fact_answer_identity:
        raise ValueError("Exact-prefix and robust registries do not share exact fact/answer identity")
    if prompt_overlap_count != 0:
        raise ValueError("Exact-prefix prompts unexpectedly overlap the A-D robust registry")
    return {
        "schema_version": 1,
        "status": "pass",
        "probe_count": len(probes),
        "fact_count": len({row["fact_id"] for row in probes}),
        "subject_count": len({row["subject_id"] for row in probes}),
        "relation_counts": dict(sorted(relation_counts.items())),
        "fact_answer_identity_with_robust_registry": fact_answer_identity,
        "prompt_overlap_with_robust_registry": prompt_overlap_count,
        "semantic_classification": "historical_exact_prefix_candidate_ranking_not_free_generation",
    }


def load_exact_prefix_plan(config_path: Path, *, repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    config_path = config_path.resolve()
    payload = _mapping(yaml.safe_load(config_path.read_text(encoding="utf-8")), "config")
    if payload.get("schema_version") != 1 or payload.get("status") != "frozen":
        raise ValueError("M0 exact-prefix supplement requires frozen schema_version 1")
    if payload.get("classification") not in {"scientific_supplement", "operational_recovery"}:
        raise ValueError("M0 exact-prefix classification must be scientific_supplement or operational_recovery")
    if payload.get("semantic_classification") != "historical_exact_prefix_candidate_ranking_not_free_generation":
        raise ValueError("M0 exact-prefix semantics are not frozen")
    models = _mapping(payload.get("models"), "models")
    if tuple(models) != MODEL_ORDER:
        raise ValueError(f"Model order must be {MODEL_ORDER}")
    normalized_models: list[dict[str, Any]] = []
    for model_id in MODEL_ORDER:
        row = _mapping(models[model_id], f"models.{model_id}")
        normalized_models.append({"model_id": model_id, **row})
    execution_indices = payload.get("execution_model_indices", list(range(len(MODEL_ORDER))))
    if (
        not isinstance(execution_indices, list)
        or not execution_indices
        or any(not isinstance(index, int) or not 0 <= index < len(MODEL_ORDER) for index in execution_indices)
        or len(set(execution_indices)) != len(execution_indices)
    ):
        raise ValueError("execution_model_indices must be a unique non-empty model-index subset")
    retained_lanes = _mapping(payload.get("retained_lanes", {}), "retained_lanes")
    expected_retained = {MODEL_ORDER[index] for index in range(len(MODEL_ORDER)) if index not in execution_indices}
    if set(retained_lanes) != expected_retained:
        raise ValueError("retained_lanes must exactly cover every non-executed model")
    normalized_retained: dict[str, dict[str, Any]] = {}
    for model_id, raw in retained_lanes.items():
        retained = _mapping(raw, f"retained_lanes.{model_id}")
        if not isinstance(retained.get("lane_result_path"), str) or not isinstance(
            retained.get("lane_result_sha256"), str
        ):
            raise ValueError(f"retained_lanes.{model_id} requires path and SHA-256")
        normalized_retained[model_id] = dict(retained)
    inputs = _mapping(payload.get("inputs"), "inputs")
    normalized_inputs = {
        **inputs,
        "dataset_dir": str(_resolve(inputs["dataset_dir"], repo_root)),
        "dataset_manifest": str(_resolve(inputs["dataset_manifest"], repo_root)),
        "pilot_subject_file": str(_resolve(inputs["pilot_subject_file"], repo_root)),
        "probe_registry": str(_resolve(inputs["probe_registry"], repo_root)),
        "robust_registry": str(_resolve(inputs["robust_registry"], repo_root)),
    }
    plan = {
        **payload,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "repo_root": str(repo_root),
        "inputs": normalized_inputs,
        "models": normalized_models,
        "execution_model_indices": execution_indices,
        "retained_lanes": normalized_retained,
    }
    plan["plan_id"] = sha256_text(
        json.dumps(
            {
                "config_sha256": plan["config_sha256"],
                "family_root": plan["family_root"],
                "models": normalized_models,
                "inputs": normalized_inputs,
                "evaluation": plan["evaluation"],
                "execution_model_indices": execution_indices,
                "retained_lanes": normalized_retained,
            },
            sort_keys=True,
        )
    )[:16]
    return plan


def initialize_exact_prefix_namespace(plan: dict[str, Any]) -> Path:
    root = Path(plan["family_root"])
    if root.exists():
        raise FileExistsError(f"Exact-prefix family root already exists: {root}")
    (root / "logs").mkdir(parents=True)
    write_json(
        root / "family_manifest.json",
        {
            "schema_version": 1,
            "status": "initialized",
            "plan_id": plan["plan_id"],
            "config_path": plan["config_path"],
            "config_sha256": plan["config_sha256"],
            "semantic_classification": plan["semantic_classification"],
            "model_order": list(MODEL_ORDER),
            "execution_model_indices": plan["execution_model_indices"],
            "retained_models": sorted(plan["retained_lanes"]),
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    return root


def build_evaluator_config(plan: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    evaluation = plan["evaluation"]
    return {
        "dataset_version": evaluation["dataset_version"],
        "dataset_dir": plan["inputs"]["dataset_dir"],
        "pilot_subject_file": plan["inputs"]["pilot_subject_file"],
        "probe_files": {"en": plan["inputs"]["probe_registry"]},
        "model_manifest": model["manifest_path"],
        "languages": ["en"],
        "relations": list(RELATIONS),
        "prompt": evaluation["prompt"],
        "scoring": evaluation["scoring"],
        "runtime": evaluation["runtime"],
    }


def _gpu_guard(plan: dict[str, Any], output: Path) -> dict[str, Any]:
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("Frozen exact-prefix panel requires BF16-capable CUDA hardware")
    free_bytes, total_bytes = (int(value) for value in torch.cuda.mem_get_info(0))
    minimum = int(plan["slurm"]["min_free_gpu_bytes"])
    payload = {
        "schema_version": 1,
        "status": "pass" if free_bytes >= minimum else "blocked",
        "free_bytes": free_bytes,
        "total_bytes": total_bytes,
        "minimum_free_bytes": minimum,
        "gpu_name": torch.cuda.get_device_name(0),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID"),
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(output, payload)
    if payload["status"] != "pass":
        raise RuntimeError(f"GPU free-memory guard failed: {free_bytes} < {minimum}")
    return payload


def run_exact_prefix_model(plan: dict[str, Any], model_index: int) -> dict[str, Any]:
    if not 0 <= model_index < len(plan["models"]):
        raise IndexError(model_index)
    if model_index not in plan["execution_model_indices"]:
        raise ValueError(f"Model index {model_index} is retained and must not be rerun")
    model = plan["models"][model_index]
    root = Path(plan["family_root"]) / model["model_id"]
    root.mkdir(parents=True, exist_ok=False)
    try:
        manifest_path = Path(model["manifest_path"])
        _verify_file(manifest_path, model["manifest_sha256"], f"{model['model_id']} model manifest")
        audit = audit_exact_prefix_inputs(plan)
        write_json(root / "input_audit.json", audit)
        _gpu_guard(plan, root / "gpu_preflight.json")
        run_dir = root / "raw" / "historical_exact_prefix"
        result_dir = CausalCandidateEvaluator(
            build_evaluator_config(plan, model), run_dir
        ).run()
        summary_path = result_dir / "summary_metrics.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        if summary.get("completion_status") != "completed":
            raise ValueError("Exact-prefix evaluator did not complete")
        artifacts = [
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in sorted(root.rglob("*"))
            if path.is_file() and path.name != "lane_result.json"
        ]
        payload = {
            "schema_version": 1,
            "status": "complete",
            "model_id": model["model_id"],
            "plan_id": plan["plan_id"],
            "semantic_classification": plan["semantic_classification"],
            "probe_count": 500,
            "primary_mean_logprob_top1_accuracy": summary["primary_mean_logprob"]["top1_accuracy"],
            "artifacts": artifacts,
        }
    except Exception as exc:
        payload = {
            "schema_version": 1,
            "status": "failed_pre_scoring_or_incomplete",
            "model_id": model["model_id"],
            "plan_id": plan["plan_id"],
            "error": str(exc),
            "artifacts": [],
        }
    write_json(root / "lane_result.json", payload)
    if payload["status"] != "complete":
        raise RuntimeError(payload["error"])
    return payload


def _validated_lane_result(
    result_path: Path,
    *,
    model_id: str,
    expected_plan_id: str | None = None,
    expected_result_sha256: str | None = None,
) -> tuple[bool, dict[str, Any]]:
    if not result_path.is_file():
        return False, {}
    if expected_result_sha256 is not None and sha256_file(result_path) != expected_result_sha256:
        return False, {}
    result = json.loads(result_path.read_text(encoding="utf-8"))
    valid = result.get("status") == "complete" and result.get("model_id") == model_id
    if expected_plan_id is not None:
        valid = valid and result.get("plan_id") == expected_plan_id
    for artifact in result.get("artifacts", []):
        path = Path(artifact["path"])
        valid = valid and path.is_file()
        valid = valid and path.stat().st_size == artifact["bytes"]
        valid = valid and sha256_file(path) == artifact["sha256"]
    return valid, result


def finalize_exact_prefix_family(plan: dict[str, Any]) -> dict[str, Any]:
    root = Path(plan["family_root"])
    rows: list[dict[str, Any]] = []
    for model in plan["models"]:
        model_id = model["model_id"]
        retained = plan["retained_lanes"].get(model_id)
        if retained:
            result_path = Path(retained["lane_result_path"])
            valid, result = _validated_lane_result(
                result_path,
                model_id=model_id,
                expected_result_sha256=retained["lane_result_sha256"],
            )
            source = "retained_hash_verified"
        else:
            result_path = root / model_id / "lane_result.json"
            valid, result = _validated_lane_result(
                result_path, model_id=model_id, expected_plan_id=plan["plan_id"]
            )
            source = "recovery_wave"
        rows.append(
            {
                "model_id": model_id,
                "status": "complete" if valid else "partial_invalid",
                "source": source,
                "lane_result": str(result_path) if result_path.is_file() else None,
                "lane_result_sha256": sha256_file(result_path) if result_path.is_file() else None,
                "top1_accuracy": result.get("primary_mean_logprob_top1_accuracy") if valid else None,
            }
        )
    complete = all(row["status"] == "complete" for row in rows)
    payload = {
        "schema_version": 1,
        "status": "complete" if complete else "partial_invalid",
        "plan_id": plan["plan_id"],
        "semantic_classification": plan["semantic_classification"],
        "scientific_interpretation_performed": False,
        "models": rows,
        "finalized_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(root / "family_result.json", payload)
    inventory = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "family_inventory.json"
    ]
    write_json(
        root / "family_inventory.json",
        {
            "schema_version": 1,
            "file_count": len(inventory),
            "total_bytes": sum(row["bytes"] for row in inventory),
            "files": inventory,
        },
    )
    return payload
