from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.study.m0_parallel import (
    build_m0_parallel_plan,
    initialize_m0_namespace,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


ISOLATED_OVERLAY_MODES = {
    "exclusive_a100_sequential",
    "retargeted_five_lane",
    "qwen_pile_single_lane",
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, path)


def _resolve(path: str | Path, repo_root: Path) -> Path:
    candidate = Path(path)
    return candidate.resolve() if candidate.is_absolute() else (repo_root / candidate).resolve()


def _sha256(value: Any, label: str) -> str:
    digest = str(value)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return digest


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


def load_family_recovery_plan(config_path: Path, *, repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    config_path = _resolve(config_path, repo_root)
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("M0 family recovery config must be a schema-v1 mapping")
    if payload.get("mode") in ISOLATED_OVERLAY_MODES:
        overlay = payload
        base_path = _resolve(overlay["base_recovery_config"], repo_root)
        expected_base = _sha256(
            overlay.get("base_recovery_config_sha256"), "base_recovery_config_sha256"
        )
        if not base_path.is_file() or sha256_file(base_path) != expected_base:
            raise ValueError("Frozen base recovery config changed")
        base = yaml.safe_load(base_path.read_text(encoding="utf-8"))
        if not isinstance(base, dict) or base.get("schema_version") != 1:
            raise ValueError("Base recovery config must be a schema-v1 mapping")
        family_root = Path(str(overlay["recovery_family_root"]))
        models = {model_id: dict(value) for model_id, value in base["models"].items()}
        model_overrides = overlay.get("model_overrides", {})
        for model_id in overlay.get("model_order", base["model_order"]):
            models[model_id]["recovery_root"] = str(family_root / model_id)
            override = model_overrides.get(model_id, {})
            if "targets" in override:
                models[model_id]["targets"] = override["targets"]
            models[model_id]["retained_recovery_lanes"] = override.get(
                "retained_recovery_lanes", {}
            )
        payload = {
            **base,
            **overlay,
            "models": models,
            "base_recovery_config_path": str(base_path),
        }
    if payload.get("status") != "frozen":
        raise ValueError("M0 family recovery config must be frozen")
    if payload.get("mode") in ISOLATED_OVERLAY_MODES:
        isolation = payload.get("isolation")
        seven_lane_order = [
            "olmo:english_capability",
            "olmo:turkish_capability",
            "olmo:turkish_perplexity",
            "qwen:english_retention_pile_10k",
            "qwen:turkish_capability",
            "qwen:turkish_perplexity",
            "smollm:english_capability",
        ]
        five_lane_order = [
            "olmo:turkish_perplexity",
            "qwen:english_retention_pile_10k",
            "qwen:turkish_capability",
            "qwen:turkish_perplexity",
            "smollm:english_capability",
        ]
        single_lane_order = ["qwen:english_retention_pile_10k"]
        expected_order = {
            "exclusive_a100_sequential": seven_lane_order,
            "retargeted_five_lane": five_lane_order,
            "qwen_pile_single_lane": single_lane_order,
        }[payload["mode"]]
        valid_isolation = isinstance(isolation, dict) and (
            isolation.get("node") == "gruenau10"
            and isolation.get("partition") == "gpu"
            and isolation.get("gres") == "gpu:a10080gb:3"
            and isolation.get("requested_gpu_count") == 3
            and isolation.get("exclusive_node_allocation") is True
            and isolation.get("expected_gpu_name") == "NVIDIA A100 80GB PCIe"
            and isolation.get("min_total_gpu_bytes") == 80 * 1024**3
            and isolation.get("selection_rule") == "maximum_free_bytes_then_uuid"
            and isolation.get("max_wait_seconds") == 7200
            and isolation.get("poll_interval_seconds") == 60
            and isolation.get("target_order") == expected_order
        )
        if not valid_isolation:
            raise ValueError("Exclusive A100 isolation policy changed or broadened")
    recovery_lane_count = payload.get("recovery_lane_count")
    if payload.get("source_lane_count") != 24 or recovery_lane_count not in {1, 5, 7}:
        raise ValueError(
            "Recovery contract must bind exactly 24 source lanes and one, five or seven targets"
        )
    model_order = payload.get("model_order")
    if model_order != ["olmo", "qwen", "smollm"]:
        raise ValueError("Recovery model order must be olmo, qwen, smollm")
    family_root = Path(str(payload["recovery_family_root"])).resolve()
    source_family_root = Path(str(payload["source_family_root"])).resolve()
    if family_root == source_family_root:
        raise ValueError("Recovery family root must be fresh and distinct from the source root")
    models: list[dict[str, Any]] = []
    target_total = 0
    retained_total = 0
    for model_id in model_order:
        raw = payload["models"].get(model_id)
        if not isinstance(raw, dict):
            raise ValueError(f"Missing recovery model binding: {model_id}")
        base_config = _resolve(raw["config"], repo_root)
        if sha256_file(base_config) != _sha256(raw["config_sha256"], f"{model_id}.config_sha256"):
            raise ValueError(f"Frozen base evaluation config changed: {model_id}")
        plan = build_m0_parallel_plan(base_config, repo_root=repo_root)
        expected_lanes = raw.get("source_lanes")
        if not isinstance(expected_lanes, dict) or set(expected_lanes) != {
            lane["id"] for lane in plan["lanes"]
        }:
            raise ValueError(f"Source lane ledger mismatch: {model_id}")
        targets = raw.get("targets")
        if not isinstance(targets, dict) or (not targets and recovery_lane_count != 1):
            raise ValueError(f"Recovery targets are missing: {model_id}")
        if not set(targets) < set(expected_lanes):
            raise ValueError(f"Recovery targets must be a strict subset: {model_id}")
        retained_recovery = raw.get("retained_recovery_lanes", {})
        if not isinstance(retained_recovery, dict):
            raise ValueError(f"Invalid retained recovery ledger: {model_id}")
        if set(retained_recovery).intersection(targets):
            raise ValueError(f"Retained recovery lanes overlap targets: {model_id}")
        if not set(retained_recovery) < set(expected_lanes):
            raise ValueError(f"Retained recovery lanes must be a strict subset: {model_id}")
        for lane_id, binding in retained_recovery.items():
            if not isinstance(binding, dict):
                raise ValueError(f"Invalid retained recovery binding: {model_id}/{lane_id}")
            retained_root = Path(str(binding.get("root", ""))).resolve()
            if retained_root in {family_root, source_family_root}:
                raise ValueError(f"Retained recovery root is not independent: {model_id}/{lane_id}")
            _sha256(
                binding.get("lane_result_sha256"),
                f"{model_id}/{lane_id}.retained_recovery_sha256",
            )
        for lane_id, lane in expected_lanes.items():
            if not isinstance(lane, dict):
                raise ValueError(f"Invalid source lane binding: {model_id}/{lane_id}")
            _sha256(lane.get("lane_result_sha256"), f"{model_id}/{lane_id}")
            expected = (
                "failed_pre_scoring"
                if lane_id in targets or lane_id in retained_recovery
                else "complete"
            )
            if lane.get("status") != expected:
                raise ValueError(f"Unexpected frozen source status: {model_id}/{lane_id}")
        route_ids = {route["id"] for route in plan["slurm"]["gpu_routes"]}
        for lane_id, target in targets.items():
            if not isinstance(target, dict):
                raise ValueError(f"Invalid recovery target: {model_id}/{lane_id}")
            if target.get("route_id") not in route_ids:
                raise ValueError(f"Unknown recovery GPU route: {model_id}/{lane_id}")
            minimum = target.get("min_free_gpu_bytes")
            if not isinstance(minimum, int) or minimum <= 0:
                raise ValueError(f"Invalid free-memory gate: {model_id}/{lane_id}")
            runtime_output_subdir = target.get("runtime_output_subdir")
            lane_adapter = next(
                lane["adapter"] for lane in plan["lanes"] if lane["id"] == lane_id
            )
            if runtime_output_subdir is not None and (
                lane_adapter != "project_corpus_perplexity"
                or runtime_output_subdir != "corpora"
            ):
                raise ValueError(f"Invalid runtime output retarget: {model_id}/{lane_id}")
        recovery_root = Path(str(raw["recovery_root"])).resolve()
        try:
            recovery_root.relative_to(family_root)
        except ValueError as exc:
            raise ValueError(f"Model recovery root escapes family root: {model_id}") from exc
        models.append(
            {
                **raw,
                "model_id": model_id,
                "config_path": str(base_config),
                "source_root": str(Path(str(raw["source_root"])).resolve()),
                "recovery_root": str(recovery_root),
                "plan": plan,
            }
        )
        target_total += len(targets)
        retained_total += len(expected_lanes) - len(targets)
    if target_total != recovery_lane_count or retained_total != 24 - recovery_lane_count:
        raise ValueError("Recovery split does not match the frozen target/retained counts")
    return {
        **payload,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "repo_root": str(repo_root),
        "source_family_root": str(source_family_root),
        "recovery_family_root": str(family_root),
        "models": models,
        "target_lane_count": target_total,
        "retained_lane_count": retained_total,
    }


def validate_family_recovery_source(recovery: dict[str, Any]) -> dict[str, Any]:
    source_family_root = Path(recovery["source_family_root"])
    family_bundle = source_family_root / "three_model_m0_raw_bundle.json"
    if sha256_file(family_bundle) != _sha256(
        recovery["source_family_bundle_sha256"], "source_family_bundle_sha256"
    ):
        raise ValueError("Source three-model raw bundle SHA-256 mismatch")
    known_appends: list[dict[str, Any]] = []
    for binding in recovery.get("known_source_append_artifacts", []):
        if not isinstance(binding, dict):
            raise ValueError("Known source append binding must be a mapping")
        path = Path(str(binding.get("path", ""))).resolve()
        try:
            path.relative_to(source_family_root.resolve())
        except ValueError as exc:
            raise ValueError("Known source append escapes the source family root") from exc
        expected = _sha256(binding.get("sha256"), f"known_source_append:{path}")
        expected_bytes = binding.get("bytes")
        if (
            not isinstance(expected_bytes, int)
            or expected_bytes <= 0
            or not path.is_file()
            or path.stat().st_size != expected_bytes
            or sha256_file(path) != expected
        ):
            raise ValueError(f"Known source append changed: {path}")
        known_appends.append({"path": str(path), "sha256": expected, "bytes": expected_bytes})
    prior_roots = [Path(str(value)).resolve() for value in recovery.get("prior_recovery_roots", [])]
    known_prior_artifacts: list[dict[str, Any]] = []
    for binding in recovery.get("known_prior_recovery_artifacts", []):
        if not isinstance(binding, dict):
            raise ValueError("Known prior recovery artifact binding must be a mapping")
        path = Path(str(binding.get("path", ""))).resolve()
        if not prior_roots or not any(
            path == root or root in path.parents for root in prior_roots
        ):
            raise ValueError("Known prior recovery artifact escapes the frozen prior roots")
        expected = _sha256(binding.get("sha256"), f"known_prior_recovery:{path}")
        expected_bytes = binding.get("bytes")
        if (
            not isinstance(expected_bytes, int)
            or expected_bytes <= 0
            or not path.is_file()
            or path.stat().st_size != expected_bytes
            or sha256_file(path) != expected
        ):
            raise ValueError(f"Known prior recovery artifact changed: {path}")
        known_prior_artifacts.append(
            {"path": str(path), "sha256": expected, "bytes": expected_bytes}
        )
    model_evidence: dict[str, Any] = {}
    for model in recovery["models"]:
        model_id = model["model_id"]
        plan = model["plan"]
        source_root = Path(model["source_root"])
        exact_files = {
            "parallel_plan.json": model["source_parallel_plan_sha256"],
            "preflight/preflight_result.json": model["source_preflight_sha256"],
            "bundle_status.json": model["source_bundle_status_sha256"],
            "scientific_bundle_result.json": model["source_scientific_bundle_result_sha256"],
            "final_inventory.json": model["source_final_inventory_sha256"],
        }
        for relative, expected in exact_files.items():
            path = source_root / relative
            if not path.is_file() or sha256_file(path) != _sha256(expected, f"{model_id}/{relative}"):
                raise ValueError(f"Frozen source evidence changed: {model_id}/{relative}")
        source_plan = _load_json(source_root / "parallel_plan.json")
        if (
            source_plan.get("plan_id") != plan["plan_id"]
            or source_plan.get("config_sha256") != plan["config_sha256"]
        ):
            raise ValueError(f"Source plan identity mismatch: {model_id}")
        preflight = _load_json(source_root / "preflight/preflight_result.json")
        if preflight.get("status") != "complete" or preflight.get("offline_reload_passed") is not True:
            raise ValueError(f"Source data preflight is not complete/offline-safe: {model_id}")
        bundle = _load_json(source_root / "bundle_status.json")
        if bundle.get("plan_id") != plan["plan_id"] or bundle.get("status") != "partial_invalid":
            raise ValueError(f"Source model bundle identity/status mismatch: {model_id}")
        if bundle.get("normalization_allowed") is not False:
            raise ValueError(f"Source partial bundle unexpectedly permits normalization: {model_id}")
        lane_evidence: dict[str, Any] = {}
        for lane in plan["lanes"]:
            lane_id = lane["id"]
            binding = model["source_lanes"][lane_id]
            result_path = source_root / "lanes" / lane_id / "lane_result.json"
            if sha256_file(result_path) != binding["lane_result_sha256"]:
                raise ValueError(f"Source lane result SHA-256 mismatch: {model_id}/{lane_id}")
            result = _load_json(result_path)
            valid_identity = (
                result.get("plan_id") == plan["plan_id"]
                and result.get("lane_id") == lane_id
                and result.get("adapter") == lane["adapter"]
                and result.get("run_classification") == "scientific"
                and result.get("status") == binding["status"]
            )
            if not valid_identity:
                raise ValueError(f"Source lane identity/status mismatch: {model_id}/{lane_id}")
            if binding["status"] == "complete" and not (
                result.get("returncode") == 0
                and _validate_artifacts(result, source_root / "lanes" / lane_id)
            ):
                raise ValueError(f"Retained source lane artifact validation failed: {model_id}/{lane_id}")
            lane_evidence[lane_id] = {
                "status": binding["status"],
                "lane_result_path": str(result_path),
                "lane_result_sha256": binding["lane_result_sha256"],
            }
        retained_recovery_evidence: dict[str, Any] = {}
        for lane_id, binding in model.get("retained_recovery_lanes", {}).items():
            lane = next(row for row in plan["lanes"] if row["id"] == lane_id)
            retained_root = Path(str(binding["root"])).resolve()
            result_path = retained_root / "lanes" / lane_id / "lane_result.json"
            expected = binding["lane_result_sha256"]
            if not result_path.is_file() or sha256_file(result_path) != expected:
                raise ValueError(f"Retained recovery result changed: {model_id}/{lane_id}")
            result = _load_json(result_path)
            valid = (
                result.get("plan_id") == plan["plan_id"]
                and result.get("lane_id") == lane_id
                and result.get("adapter") == lane["adapter"]
                and result.get("run_classification") == "scientific"
                and result.get("status") == "complete"
                and result.get("returncode") == 0
                and _validate_artifacts(result, retained_root / "lanes" / lane_id)
            )
            if not valid:
                raise ValueError(f"Retained recovery artifact validation failed: {model_id}/{lane_id}")
            retained_recovery_evidence[lane_id] = {
                "status": "complete",
                "root": str(retained_root),
                "lane_result_path": str(result_path),
                "lane_result_sha256": expected,
            }
        model_evidence[model_id] = {
            "plan_id": plan["plan_id"],
            "source_root": str(source_root),
            "lanes": lane_evidence,
            "retained_recovery_lanes": retained_recovery_evidence,
        }
    return {
        "schema_version": 1,
        "status": "ready",
        "source_family_root": str(source_family_root),
        "source_family_bundle_sha256": recovery["source_family_bundle_sha256"],
        "retained_lane_count": recovery["retained_lane_count"],
        "target_lane_count": recovery["target_lane_count"],
        "known_source_append_artifacts": known_appends,
        "known_prior_recovery_artifacts": known_prior_artifacts,
        "models": model_evidence,
    }


def initialize_family_recovery_namespace(recovery: dict[str, Any]) -> dict[str, Any]:
    evidence = validate_family_recovery_source(recovery)
    family_root = Path(recovery["recovery_family_root"])
    if family_root.exists():
        raise FileExistsError(f"M0 family recovery namespace already exists: {family_root}")
    family_root.mkdir(parents=True)
    for model in recovery["models"]:
        source_root = Path(model["source_root"])
        recovery_root = Path(model["recovery_root"])
        initialize_m0_namespace(recovery_root, model["plan"])
        shutil.rmtree(recovery_root / "cache")
        (recovery_root / "cache").mkdir()
        shutil.copytree(source_root / "preflight", recovery_root / "preflight")
        for name in (
            "task_resolution.jsonl",
            "dataset_content_manifest.jsonl",
            "project_input_resolution.jsonl",
            "environment_lock.json",
            "model_identity.json",
        ):
            source = source_root / name
            if source.is_file():
                shutil.copy2(source, recovery_root / name)
        write_json(
            recovery_root / "recovery_manifest.json",
            {
                "schema_version": 1,
                "status": "initialized_not_run",
                "model_id": model["model_id"],
                "plan_id": model["plan"]["plan_id"],
                "source_root": str(source_root),
                "recovery_root": str(recovery_root),
                "targets": model["targets"],
                "source_evidence": evidence["models"][model["model_id"]],
            },
        )
    payload = {
        "schema_version": 1,
        "status": "initialized_not_run",
        "config_path": recovery["config_path"],
        "config_sha256": recovery["config_sha256"],
        "source_evidence": evidence,
        "initialized_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(family_root / "recovery_manifest.json", payload)
    return payload


def _selected_lane_result(
    model: dict[str, Any], lane_id: str
) -> tuple[Path, str]:
    if lane_id in model["targets"]:
        root = Path(model["recovery_root"])
        source = "recovery"
    elif lane_id in model.get("retained_recovery_lanes", {}):
        root = Path(model["retained_recovery_lanes"][lane_id]["root"])
        source = "retained_recovery"
    else:
        root = Path(model["source_root"])
        source = "source"
    return root / "lanes" / lane_id / "lane_result.json", source


def finalize_recovered_model(model: dict[str, Any]) -> dict[str, Any]:
    plan = model["plan"]
    recovery_root = Path(model["recovery_root"])
    lane_rows: list[dict[str, Any]] = []
    artifact_rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    lane_paths: dict[str, str] = {}
    lane_hashes: dict[str, str] = {}
    lane_sources: dict[str, str] = {}
    for lane in plan["lanes"]:
        lane_id = lane["id"]
        result_path, lane_source = _selected_lane_result(model, lane_id)
        lane_paths[lane_id] = str(result_path)
        lane_sources[lane_id] = lane_source
        if not result_path.is_file():
            blockers.append(f"lane_missing:{lane_id}")
            continue
        if lane_source in {"source", "retained_recovery"}:
            binding = (
                model["source_lanes"][lane_id]
                if lane_source == "source"
                else model["retained_recovery_lanes"][lane_id]
            )
            expected_sha = binding["lane_result_sha256"]
            if sha256_file(result_path) != expected_sha:
                blockers.append(f"{lane_source}_lane_hash_mismatch:{lane_id}")
                continue
        result = _load_json(result_path)
        root = result_path.parents[1]
        valid = (
            result.get("plan_id") == plan["plan_id"]
            and result.get("lane_id") == lane_id
            and result.get("adapter") == lane["adapter"]
            and result.get("run_classification") == "scientific"
            and result.get("status") == "complete"
            and result.get("returncode") == 0
            and _validate_artifacts(result, root)
        )
        if not valid:
            blockers.append(f"lane_invalid:{lane_id}")
            continue
        lane_hashes[lane_id] = sha256_file(result_path)
        lane_rows.append(
            {
                "lane_id": lane_id,
                "lane_source": lane_source,
                "lane_result_path": str(result_path),
                "lane_result_sha256": lane_hashes[lane_id],
                "adapter": result.get("adapter"),
                "families": result.get("families"),
                "task_ids": result.get("task_ids", []),
                "status": "complete",
                "duration_seconds": result.get("duration_seconds"),
                "execution": result.get("execution", {}),
            }
        )
        for artifact in result.get("artifacts", []):
            artifact_rows.append(
                {"model_id": model["model_id"], "lane_id": lane_id, "lane_source": lane_source, **artifact}
            )
    complete = not blockers and len(lane_rows) == plan["lane_count"]
    bundle = {
        "schema_version": 1,
        "status": "complete" if complete else "partial_invalid",
        "run_classification": "scientific",
        "model_id": model["model_id"],
        "plan_id": plan["plan_id"],
        "lane_count": plan["lane_count"],
        "complete_lane_count": len(lane_rows),
        "retained_lane_count": sum(row["lane_source"] != "recovery" for row in lane_rows),
        "retained_recovery_lane_count": sum(
            row["lane_source"] == "retained_recovery" for row in lane_rows
        ),
        "recovered_lane_count": sum(row["lane_source"] == "recovery" for row in lane_rows),
        "normalization_allowed": complete,
        "source_root": model["source_root"],
        "recovery_root": model["recovery_root"],
        "lane_sources": lane_sources,
        "lane_result_paths": lane_paths,
        "lane_result_sha256": lane_hashes,
        "blockers": blockers,
    }
    write_json(recovery_root / "bundle_status.json", bundle)
    _write_jsonl(recovery_root / "raw_artifact_manifest.jsonl", artifact_rows)
    write_json(
        recovery_root / "evaluation_results.json",
        {**bundle, "model": plan["model"], "harness": plan["harness"], "lanes": lane_rows},
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
            },
        )
    write_json(
        recovery_root / "scientific_bundle_result.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "status": "complete_raw_pending_normalization" if complete else "partial_invalid_no_scientific_summary",
            "run_classification": "scientific",
            "raw_bundle_complete": complete,
            "normalization_allowed": complete,
            "model": plan["model"],
            "model_pass_fail": "not_computed_by_raw_finalizer",
            "blockers": blockers,
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


def finalize_family_recovery(recovery: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for model in recovery["models"]:
        root = Path(model["recovery_root"])
        result_path = root / "scientific_bundle_result.json"
        manifest_path = root / "evaluation_manifest.json"
        valid = False
        if result_path.is_file() and manifest_path.is_file():
            result = _load_json(result_path)
            manifest = _load_json(manifest_path)
            valid = (
                result.get("status") == "complete_raw_pending_normalization"
                and result.get("plan_id") == model["plan"]["plan_id"]
                and manifest.get("status") == "complete"
                and manifest.get("plan_id") == model["plan"]["plan_id"]
            )
        rows.append(
            {
                "model_id": model["model_id"],
                "status": "complete_raw_pending_normalization" if valid else "partial_invalid",
                "scientific_bundle_result": str(result_path) if result_path.is_file() else None,
                "scientific_bundle_result_sha256": sha256_file(result_path) if result_path.is_file() else None,
                "evaluation_manifest": str(manifest_path) if manifest_path.is_file() else None,
                "evaluation_manifest_sha256": sha256_file(manifest_path) if manifest_path.is_file() else None,
            }
        )
    complete = all(row["status"] == "complete_raw_pending_normalization" for row in rows)
    payload = {
        "schema_version": 1,
        "status": "complete_raw_pending_normalization" if complete else "partial_invalid_no_cross_model_summary",
        "run_classification": "scientific",
        "source_family_root": recovery["source_family_root"],
        "source_family_bundle_sha256": recovery["source_family_bundle_sha256"],
        "recovery_family_root": recovery["recovery_family_root"],
        "retained_lane_count": recovery["retained_lane_count"],
        "recovered_lane_count": recovery["target_lane_count"] if complete else None,
        "total_lane_count": 24,
        "normalization_allowed": complete,
        "models": rows,
        "cross_model_pass_fail": "not_computed_by_composite_finalizer",
        "finalized_at": datetime.now(timezone.utc).isoformat(),
    }
    root = Path(recovery["recovery_family_root"])
    write_json(root / "three_model_m0_composite_bundle.json", payload)
    inventory = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "family_final_inventory.json"
    ]
    write_json(
        root / "family_final_inventory.json",
        {
            "schema_version": 1,
            "inventory_excludes": ["family_final_inventory.json"],
            "file_count": len(inventory),
            "total_bytes": sum(row["bytes"] for row in inventory),
            "files": inventory,
        },
    )
    return payload
