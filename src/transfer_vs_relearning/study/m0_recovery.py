from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.study.m0_parallel import initialize_m0_namespace
from transfer_vs_relearning.utils.io import sha256_file, write_json


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, path)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _validate_artifacts(result: dict[str, Any], lane_root: Path) -> bool:
    artifacts = result.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        return False
    lane_root = lane_root.resolve()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            return False
        path = Path(str(artifact.get("path", ""))).resolve()
        try:
            path.relative_to(lane_root)
        except ValueError:
            return False
        if (
            not path.is_file()
            or artifact.get("bytes") != path.stat().st_size
            or artifact.get("sha256") != sha256_file(path)
        ):
            return False
    return True


def validate_recovery_source(
    plan: dict[str, Any], source_root: Path, lane_id: str
) -> dict[str, Any]:
    source_root = source_root.resolve()
    lane_ids = [lane["id"] for lane in plan["lanes"]]
    if lane_id not in lane_ids:
        raise ValueError(f"Unknown M0 lane: {lane_id}")
    planned = _load_json(source_root / "parallel_plan.json")
    if (
        planned.get("plan_id") != plan["plan_id"]
        or planned.get("config_sha256") != plan["config_sha256"]
    ):
        raise ValueError("Recovery source plan/config identity mismatch")
    preflight = _load_json(source_root / "preflight" / "preflight_result.json")
    if preflight.get("status") != "complete" or preflight.get("offline_reload_passed") is not True:
        raise ValueError("Recovery source task-data preflight is not complete and offline-safe")
    bundle = _load_json(source_root / "bundle_status.json")
    statuses = bundle.get("lanes")
    if not isinstance(statuses, dict) or set(statuses) != set(lane_ids):
        raise ValueError("Recovery source lane ledger is incomplete")
    if statuses.get(lane_id) == "complete":
        raise ValueError(f"Recovery target lane is already complete: {lane_id}")
    reusable = [candidate for candidate in lane_ids if candidate != lane_id]
    if any(statuses.get(candidate) != "complete" for candidate in reusable):
        raise ValueError("Recovery source has more than one incomplete lane")
    for candidate in reusable:
        result_path = source_root / "lanes" / candidate / "lane_result.json"
        result = _load_json(result_path)
        lane = next(row for row in plan["lanes"] if row["id"] == candidate)
        if not (
            result.get("plan_id") == plan["plan_id"]
            and result.get("lane_id") == candidate
            and result.get("adapter") == lane["adapter"]
            and result.get("status") == "complete"
            and result.get("returncode") == 0
            and _validate_artifacts(result, source_root / "lanes" / candidate)
        ):
            raise ValueError(f"Reusable source lane failed identity/artifact validation: {candidate}")
    return {
        "schema_version": 1,
        "status": "ready",
        "source_root": str(source_root),
        "source_plan_id": plan["plan_id"],
        "source_config_sha256": plan["config_sha256"],
        "target_lane_id": lane_id,
        "reusable_lane_ids": reusable,
        "source_bundle_status_sha256": sha256_file(source_root / "bundle_status.json"),
        "source_final_inventory_sha256": sha256_file(source_root / "final_inventory.json"),
    }


def initialize_recovery_namespace(
    plan: dict[str, Any],
    *,
    source_root: Path,
    recovery_root: Path,
    lane_id: str,
) -> dict[str, Any]:
    source = validate_recovery_source(plan, source_root, lane_id)
    recovery_root = recovery_root.resolve()
    initialize_m0_namespace(recovery_root, plan)
    shutil.rmtree(recovery_root / "cache")
    shutil.copytree(source_root.resolve() / "cache", recovery_root / "cache", copy_function=shutil.copy2)
    shutil.copytree(
        source_root.resolve() / "preflight",
        recovery_root / "preflight",
        copy_function=shutil.copy2,
    )
    for name in (
        "task_resolution.jsonl",
        "dataset_content_manifest.jsonl",
        "project_input_resolution.jsonl",
        "environment_lock.json",
        "model_identity.json",
    ):
        candidate = source_root.resolve() / name
        if candidate.is_file():
            shutil.copy2(candidate, recovery_root / name)
    payload = {
        **source,
        "status": "initialized_not_run",
        "recovery_root": str(recovery_root),
        "initialized_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(recovery_root / "recovery_manifest.json", payload)
    return payload


def observe_gpu_memory() -> tuple[int, int]:
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable for the recovery lane")
    free_bytes, total_bytes = torch.cuda.mem_get_info(0)
    return int(free_bytes), int(total_bytes)


def run_gpu_memory_guard(
    recovery_root: Path,
    lane_id: str,
    *,
    min_free_bytes: int,
    observer: Any = observe_gpu_memory,
) -> dict[str, Any]:
    free_bytes, total_bytes = observer()
    payload = {
        "schema_version": 1,
        "status": "pass" if free_bytes >= min_free_bytes else "blocked",
        "lane_id": lane_id,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_node": os.environ.get("SLURMD_NODENAME"),
        "gpu_route_id": os.environ.get("M0_GPU_ROUTE_ID"),
        "free_bytes": free_bytes,
        "total_bytes": total_bytes,
        "min_free_bytes": min_free_bytes,
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(recovery_root / "lanes" / lane_id / "gpu_memory_preflight.json", payload)
    if payload["status"] != "pass":
        raise RuntimeError(
            f"Recovery GPU free-memory gate failed: {free_bytes} < {min_free_bytes} bytes"
        )
    return payload


def _summary_documents(result: dict[str, Any], lane_root: Path) -> list[dict[str, Any]]:
    artifact_root = Path(str(result.get("artifact_root", lane_root))).resolve()
    try:
        artifact_root.relative_to(lane_root.resolve())
    except ValueError:
        return []
    documents: list[dict[str, Any]] = []
    for path in sorted(artifact_root.rglob("*.json")):
        if not (
            path.name.startswith("results_")
            or path.name
            in {"summary.json", "summary_metrics.json", "errors.json", "run_manifest.json"}
        ):
            continue
        if path.stat().st_size > 10 * 1024 * 1024:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        documents.append(
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "payload": payload,
            }
        )
    return documents


def finalize_recovery_bundle(
    plan: dict[str, Any],
    *,
    source_root: Path,
    recovery_root: Path,
    lane_id: str,
) -> dict[str, Any]:
    source = validate_recovery_source(plan, source_root, lane_id)
    source_root = source_root.resolve()
    recovery_root = recovery_root.resolve()
    selected_results: list[dict[str, Any]] = []
    lane_sources: dict[str, str] = {}
    lane_result_paths: dict[str, str] = {}
    blockers: list[str] = []
    for lane in plan["lanes"]:
        root = recovery_root if lane["id"] == lane_id else source_root
        result_path = root / "lanes" / lane["id"] / "lane_result.json"
        lane_result_paths[lane["id"]] = str(result_path)
        lane_sources[lane["id"]] = "recovery" if root == recovery_root else "source"
        if not result_path.is_file():
            blockers.append(f"lane_missing:{lane['id']}")
            continue
        result = _load_json(result_path)
        valid = (
            result.get("plan_id") == plan["plan_id"]
            and result.get("lane_id") == lane["id"]
            and result.get("adapter") == lane["adapter"]
            and result.get("status") == "complete"
            and result.get("returncode") == 0
            and _validate_artifacts(result, root / "lanes" / lane["id"])
        )
        if not valid:
            blockers.append(f"lane_invalid:{lane['id']}")
        selected_results.append(result)
    complete = not blockers and len(selected_results) == plan["lane_count"]
    bundle = {
        "schema_version": 1,
        "plan_id": plan["plan_id"],
        "status": "complete" if complete else "partial_invalid",
        "run_classification": plan["run_classification"],
        "lane_count": plan["lane_count"],
        "complete_lane_count": plan["lane_count"] if complete else plan["lane_count"] - len(blockers),
        "normalization_allowed": complete,
        "source_root": str(source_root),
        "recovery_root": str(recovery_root),
        "recovered_lane_id": lane_id,
        "lane_sources": lane_sources,
        "blockers": blockers,
    }
    write_json(recovery_root / "bundle_status.json", bundle)
    raw_rows = [
        {
            "lane_id": result.get("lane_id"),
            "lane_source": lane_sources[str(result.get("lane_id"))],
            "run_classification": plan["run_classification"],
            **artifact,
        }
        for result in selected_results
        for artifact in result.get("artifacts", [])
        if isinstance(artifact, dict)
    ]
    _write_jsonl(recovery_root / "raw_artifact_manifest.jsonl", raw_rows)
    write_json(
        recovery_root / "evaluation_results.json",
        {
            **bundle,
            "model": plan["model"],
            "harness": plan["harness"],
            "raw_artifact_manifest": str(recovery_root / "raw_artifact_manifest.jsonl"),
            "lanes": [
                {
                    "lane_id": result.get("lane_id"),
                    "lane_source": lane_sources[str(result.get("lane_id"))],
                    "adapter": result.get("adapter"),
                    "families": result.get("families"),
                    "task_ids": result.get("task_ids", []),
                    "status": result.get("status"),
                    "returncode": result.get("returncode"),
                    "duration_seconds": result.get("duration_seconds"),
                    "execution": result.get("execution", {}),
                    "artifact_root": result.get("artifact_root"),
                    "summary_documents": _summary_documents(
                        result,
                        (recovery_root if result.get("lane_id") == lane_id else source_root)
                        / "lanes"
                        / str(result.get("lane_id")),
                    ),
                }
                for result in selected_results
            ],
        },
    )
    if complete:
        write_json(
            recovery_root / "evaluation_manifest.json",
            {
                **bundle,
                "config_path": plan["config_path"],
                "config_sha256": plan["config_sha256"],
                "model": plan["model"],
                "harness": plan["harness"],
                "lane_result_paths": lane_result_paths,
                "source_evidence": source,
            },
        )
    qualification_blockers = [] if complete else list(blockers)
    qualification_blockers.extend(
        ["wikitext_count_result_and_heading_parity", "turblimp_16_subtask_macro_parity"]
    )
    write_json(
        recovery_root / "qualification_result.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "gate": "blocked",
            "blockers": qualification_blockers,
            "bundle_complete": complete,
            "scientific_result": False,
            "scientific_work_started": False,
            "run_classification": plan["run_classification"],
        },
    )
    write_json(
        recovery_root / "recovery_result.json",
        {
            **bundle,
            "source_evidence": source,
            "lane_result_paths": lane_result_paths,
            "finalized_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    inventory = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(recovery_root.rglob("*"))
        if path.is_file() and path.name != "final_inventory.json"
    ]
    write_json(
        recovery_root / "final_inventory.json",
        {
            "schema_version": 1,
            "inventory_excludes": ["final_inventory.json"],
            "file_count": len(inventory),
            "total_bytes": sum(row["bytes"] for row in inventory),
            "files": inventory,
        },
    )
    return bundle
