from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.utils.io import sha256_file, write_json


MODEL_IDS = ("olmo", "qwen", "smollm")
REQUIRED_LANES = (
    "english_retention_wikitext",
    "english_grammar_blimp",
    "english_capability",
    "turkish_capability",
    "turkish_perplexity",
    "factual_access",
    "generation_integrity",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _frozen_source(value: Any, label: str) -> dict[str, str]:
    row = _mapping(value, label)
    path = row.get("path")
    digest = row.get("sha256")
    if not isinstance(path, str) or not path.startswith("/"):
        raise ValueError(f"{label}.path must be an absolute path")
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        raise ValueError(f"{label}.sha256 must be a frozen SHA-256")
    return {"path": path, "sha256": digest}


def load_projection_plan(config_path: Path, *, repo_root: Path) -> dict[str, Any]:
    config_path = config_path.resolve()
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config = _mapping(payload, "projection config")
    if config.get("schema_version") != 1:
        raise ValueError("Only projection schema_version 1 is supported")
    if config.get("eval_contract") != "eval-v2":
        raise ValueError("M0 projection must bind eval-v2")
    if config.get("rescore_authorized") is not False:
        raise ValueError("M0 projection must explicitly forbid rescoring")
    if config.get("historical_sources_read_only") is not True:
        raise ValueError("Historical M0 sources must be read-only")

    identities = _mapping(config.get("identities"), "identities")
    for label in ("contract", "registry"):
        row = _mapping(identities.get(label), f"identities.{label}")
        relative = row.get("path")
        expected = row.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise ValueError(f"identities.{label} requires path and SHA-256")
        observed = sha256_file((repo_root / relative).resolve())
        if observed != expected:
            raise ValueError(f"identities.{label} hash mismatch")

    models = _mapping(config.get("models"), "models")
    if tuple(models) != MODEL_IDS:
        raise ValueError(f"models must be ordered exactly as {MODEL_IDS}")
    normalized_models: dict[str, dict[str, Any]] = {}
    for model_id, raw in models.items():
        model = _mapping(raw, f"models.{model_id}")
        required = tuple(model.get("required_lane_ids", []))
        if required != REQUIRED_LANES:
            raise ValueError(f"models.{model_id}.required_lane_ids must match eval-v2")
        if any("pile" in lane.casefold() for lane in required):
            raise ValueError("Pile lanes are forbidden in eval-v2 projection")
        normalized_models[model_id] = {
            "repository": str(model["repository"]),
            "revision": str(model["revision"]),
            "required_lane_ids": list(required),
            "evaluation_results": _frozen_source(
                model.get("evaluation_results"), f"models.{model_id}.evaluation_results"
            ),
        }

    exact_prefix = _mapping(config.get("exact_prefix"), "exact_prefix")
    if exact_prefix.get("semantic_classification") != (
        "historical_exact_prefix_candidate_ranking_not_free_generation"
    ):
        raise ValueError("Exact-prefix semantic classification drifted")
    exact_prefix_source = _frozen_source(exact_prefix.get("family_result"), "exact_prefix.family_result")

    output_root = config.get("output_root")
    if not isinstance(output_root, str) or not output_root.startswith("/"):
        raise ValueError("output_root must be an absolute fresh path")
    identity_payload = {
        "config_sha256": sha256_file(config_path),
        "eval_contract": config["eval_contract"],
        "identities": identities,
        "models": normalized_models,
        "exact_prefix": {**exact_prefix, "family_result": exact_prefix_source},
        "output_root": output_root,
    }
    plan_id = hashlib.sha256(
        json.dumps(identity_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return {
        "schema_version": 1,
        "name": str(config["name"]),
        "status": str(config["status"]),
        "execution_authorized": bool(config.get("execution_authorized", False)),
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "plan_id": plan_id,
        "eval_contract": "eval-v2",
        "identities": identities,
        "models": normalized_models,
        "exact_prefix": {**exact_prefix, "family_result": exact_prefix_source},
        "output_root": output_root,
        "rescore_authorized": False,
        "historical_sources_read_only": True,
    }


def _verify_file(path: Path, expected_sha256: str, label: str) -> None:
    if not path.is_file():
        raise ValueError(f"Missing {label}: {path}")
    observed = sha256_file(path)
    if observed != expected_sha256:
        raise ValueError(f"{label} hash mismatch: {observed} != {expected_sha256}")


def _verify_artifacts(result: dict[str, Any], *, result_path: Path) -> None:
    for index, raw in enumerate(result.get("artifacts", [])):
        artifact = _mapping(raw, f"artifact[{index}]")
        path = Path(str(artifact.get("path", "")))
        if not path.is_absolute():
            raise ValueError(f"Artifact path is not absolute: {path}")
        try:
            path.resolve().relative_to(result_path.parent.resolve())
        except ValueError as exc:
            raise ValueError(f"Artifact escapes lane root: {path}") from exc
        if not path.is_file() or path.stat().st_size != artifact.get("bytes"):
            raise ValueError(f"Artifact missing or byte size drifted: {path}")
        if sha256_file(path) != artifact.get("sha256"):
            raise ValueError(f"Artifact hash drifted: {path}")


def discover_projection_bindings(config_path: Path, *, repo_root: Path) -> dict[str, Any]:
    """Read only exact top manifests and referenced lane results to freeze source hashes."""
    config_path = config_path.resolve()
    config = _mapping(yaml.safe_load(config_path.read_text(encoding="utf-8")), "projection config")
    if config.get("schema_version") != 1 or config.get("eval_contract") != "eval-v2":
        raise ValueError("Discovery requires eval-v2 projection schema_version 1")
    if config.get("historical_sources_read_only") is not True:
        raise ValueError("Discovery requires read-only historical sources")
    identities = _mapping(config.get("identities"), "identities")
    for label in ("contract", "registry"):
        row = _mapping(identities.get(label), f"identities.{label}")
        if sha256_file((repo_root / str(row["path"])).resolve()) != row.get("sha256"):
            raise ValueError(f"identities.{label} hash mismatch")

    models = _mapping(config.get("models"), "models")
    if tuple(models) != MODEL_IDS:
        raise ValueError(f"models must be ordered exactly as {MODEL_IDS}")
    top_bindings: dict[str, dict[str, Any]] = {}
    lane_bindings: list[dict[str, Any]] = []
    bytes_read = 0
    for model_id, raw in models.items():
        model = _mapping(raw, f"models.{model_id}")
        if tuple(model.get("required_lane_ids", [])) != REQUIRED_LANES:
            raise ValueError(f"models.{model_id}.required_lane_ids must match eval-v2")
        source_row = _mapping(model.get("evaluation_results"), f"models.{model_id}.evaluation_results")
        source_path = Path(str(source_row.get("path", "")))
        if not source_path.is_absolute() or not source_path.is_file():
            raise ValueError(f"Missing discovery source: {source_path}")
        source_sha = sha256_file(source_path)
        bytes_read += source_path.stat().st_size
        evaluation = _load_json(source_path)
        source_model = _mapping(evaluation.get("model"), f"{model_id} source model")
        if (
            evaluation.get("run_classification") != "scientific"
            or source_model.get("repository") != model.get("repository")
            or source_model.get("revision") != model.get("revision")
        ):
            raise ValueError(f"{model_id} discovery source identity drifted")
        lanes = {
            str(row.get("lane_id")): row
            for row in evaluation.get("lanes", [])
            if isinstance(row, dict)
        }
        for lane_id in REQUIRED_LANES:
            lane = _mapping(lanes.get(lane_id), f"{model_id}:{lane_id}")
            lane_path = Path(str(lane.get("lane_result_path", "")))
            lane_sha = lane.get("lane_result_sha256")
            if lane.get("status") != "complete" or not isinstance(lane_sha, str):
                raise ValueError(f"Required discovery lane incomplete: {model_id}:{lane_id}")
            _verify_file(lane_path, lane_sha, f"{model_id}:{lane_id} lane result")
            result = _load_json(lane_path)
            if (
                result.get("lane_id") != lane_id
                or result.get("status") != "complete"
                or result.get("run_classification") != "scientific"
                or result.get("returncode") != 0
            ):
                raise ValueError(f"Discovery lane identity invalid: {model_id}:{lane_id}")
            bytes_read += lane_path.stat().st_size
            lane_bindings.append(
                {
                    "model_id": model_id,
                    "lane_id": lane_id,
                    "path": str(lane_path),
                    "sha256": lane_sha,
                    "bytes": lane_path.stat().st_size,
                }
            )
        top_bindings[model_id] = {
            "path": str(source_path),
            "sha256": source_sha,
            "bytes": source_path.stat().st_size,
        }

    exact = _mapping(config.get("exact_prefix"), "exact_prefix")
    exact_source = _mapping(exact.get("family_result"), "exact_prefix.family_result")
    exact_path = Path(str(exact_source.get("path", "")))
    if not exact_path.is_absolute() or not exact_path.is_file():
        raise ValueError(f"Missing exact-prefix discovery source: {exact_path}")
    exact_sha = sha256_file(exact_path)
    expected_exact_sha = exact_source.get("sha256")
    if expected_exact_sha is not None and exact_sha != expected_exact_sha:
        raise ValueError("Exact-prefix family result hash drifted")
    bytes_read += exact_path.stat().st_size
    exact_payload = _load_json(exact_path)
    if (
        exact_payload.get("status") != "complete"
        or exact_payload.get("semantic_classification") != exact.get("semantic_classification")
    ):
        raise ValueError("Exact-prefix discovery source is incomplete or incompatible")
    exact_rows = {
        str(row.get("model_id")): row
        for row in exact_payload.get("models", [])
        if isinstance(row, dict)
    }
    for model_id in MODEL_IDS:
        row = _mapping(exact_rows.get(model_id), f"exact_prefix:{model_id}")
        lane_path = Path(str(row.get("lane_result", "")))
        lane_sha = row.get("lane_result_sha256")
        if row.get("status") != "complete" or not isinstance(lane_sha, str):
            raise ValueError(f"Exact-prefix discovery lane incomplete: {model_id}")
        _verify_file(lane_path, lane_sha, f"exact-prefix:{model_id}")
        result = _load_json(lane_path)
        if result.get("model_id") != model_id or result.get("status") != "complete":
            raise ValueError(f"Exact-prefix discovery lane identity invalid: {model_id}")
        bytes_read += lane_path.stat().st_size
        lane_bindings.append(
            {
                "model_id": model_id,
                "lane_id": "exact_prefix",
                "path": str(lane_path),
                "sha256": lane_sha,
                "bytes": lane_path.stat().st_size,
            }
        )
    top_bindings["exact_prefix"] = {
        "path": str(exact_path),
        "sha256": exact_sha,
        "bytes": exact_path.stat().st_size,
    }
    if len(lane_bindings) != 24:
        raise ValueError("Discovery did not resolve exactly 24 source bindings")
    return {
        "schema_version": 1,
        "status": "source_binding_discovery_pass",
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "top_manifest_bindings": top_bindings,
        "lane_bindings": lane_bindings,
        "top_manifest_count": 4,
        "lane_binding_count": 24,
        "bytes_read_from_manifest_and_lane_results": bytes_read,
        "historical_sources_mutated": False,
        "rescoring_performed": False,
        "artifact_payloads_rehashed": False,
    }


def inspect_projection_sources(plan: dict[str, Any]) -> dict[str, Any]:
    source_rows: list[dict[str, Any]] = []
    for model_id in MODEL_IDS:
        model = plan["models"][model_id]
        source = model["evaluation_results"]
        source_path = Path(source["path"])
        _verify_file(source_path, source["sha256"], f"{model_id} evaluation_results")
        evaluation = _load_json(source_path)
        if evaluation.get("run_classification") != "scientific":
            raise ValueError(f"{model_id} source is not scientific")
        source_model = _mapping(evaluation.get("model"), f"{model_id} source model")
        if (
            source_model.get("repository") != model["repository"]
            or source_model.get("revision") != model["revision"]
        ):
            raise ValueError(f"{model_id} model identity drifted")
        lanes = {
            str(row.get("lane_id")): row
            for row in evaluation.get("lanes", [])
            if isinstance(row, dict)
        }
        for lane_id in model["required_lane_ids"]:
            row = _mapping(lanes.get(lane_id), f"{model_id}:{lane_id}")
            if row.get("status") != "complete":
                raise ValueError(f"Required lane is incomplete: {model_id}:{lane_id}")
            lane_path = Path(str(row.get("lane_result_path", "")))
            lane_sha = row.get("lane_result_sha256")
            if not isinstance(lane_sha, str) or SHA256_RE.fullmatch(lane_sha) is None:
                raise ValueError(f"Lane SHA-256 missing: {model_id}:{lane_id}")
            _verify_file(lane_path, lane_sha, f"{model_id}:{lane_id} lane result")
            lane_result = _load_json(lane_path)
            if (
                lane_result.get("lane_id") != lane_id
                or lane_result.get("status") != "complete"
                or lane_result.get("run_classification") != "scientific"
                or lane_result.get("returncode") != 0
            ):
                raise ValueError(f"Lane identity/status invalid: {model_id}:{lane_id}")
            _verify_artifacts(lane_result, result_path=lane_path)
            source_rows.append(
                {
                    "state": "M0",
                    "model_id": model_id,
                    "model_repository": model["repository"],
                    "model_revision": model["revision"],
                    "lane_id": lane_id,
                    "source_kind": "eval_v1_scientific_lane_reused_by_eval_v2",
                    "source_path": str(lane_path),
                    "source_sha256": lane_sha,
                    "source_manifest_path": str(source_path),
                    "source_manifest_sha256": source["sha256"],
                    "status": "complete_hash_verified",
                }
            )

    exact_source = plan["exact_prefix"]["family_result"]
    exact_path = Path(exact_source["path"])
    _verify_file(exact_path, exact_source["sha256"], "exact-prefix family result")
    exact = _load_json(exact_path)
    if exact.get("status") != "complete" or exact.get("semantic_classification") != plan[
        "exact_prefix"
    ]["semantic_classification"]:
        raise ValueError("Exact-prefix family is incomplete or semantically incompatible")
    exact_rows = {
        str(row.get("model_id")): row for row in exact.get("models", []) if isinstance(row, dict)
    }
    for model_id in MODEL_IDS:
        row = _mapping(exact_rows.get(model_id), f"exact_prefix:{model_id}")
        lane_path = Path(str(row.get("lane_result", "")))
        lane_sha = row.get("lane_result_sha256")
        if row.get("status") != "complete" or not isinstance(lane_sha, str):
            raise ValueError(f"Exact-prefix lane incomplete: {model_id}")
        _verify_file(lane_path, lane_sha, f"exact-prefix:{model_id}")
        result = _load_json(lane_path)
        if result.get("model_id") != model_id or result.get("status") != "complete":
            raise ValueError(f"Exact-prefix lane identity invalid: {model_id}")
        _verify_artifacts(result, result_path=lane_path)
        source_rows.append(
            {
                "state": "M0",
                "model_id": model_id,
                "model_repository": plan["models"][model_id]["repository"],
                "model_revision": plan["models"][model_id]["revision"],
                "lane_id": "exact_prefix",
                "source_kind": "historical_exact_prefix_candidate_ranking_supplement",
                "source_path": str(lane_path),
                "source_sha256": lane_sha,
                "source_manifest_path": str(exact_path),
                "source_manifest_sha256": exact_source["sha256"],
                "status": "complete_hash_verified",
            }
        )

    if len(source_rows) != 24:
        raise ValueError(f"Projection requires 24 source rows, observed {len(source_rows)}")
    if any("pile" in str(row["lane_id"]).casefold() for row in source_rows):
        raise ValueError("Pile evidence entered the eval-v2 projection")
    return {
        "schema_version": 1,
        "status": "source_identity_pass",
        "plan_id": plan["plan_id"],
        "eval_contract": "eval-v2",
        "model_count": 3,
        "canonical_lane_count": 21,
        "exact_prefix_supplement_count": 3,
        "source_rows": source_rows,
        "rescoring_performed": False,
        "scientific_interpretation_performed": False,
    }


def write_projection(plan: dict[str, Any]) -> dict[str, Any]:
    if plan.get("execution_authorized") is not True:
        raise PermissionError("Projection execution is not authorized by the frozen config")
    inspection = inspect_projection_sources(plan)
    output_root = Path(plan["output_root"])
    if output_root.exists():
        raise FileExistsError(f"Projection output root already exists: {output_root}")
    output_root.mkdir(parents=True)
    registry_path = output_root / "source_registry.jsonl"
    with registry_path.open("x", encoding="utf-8") as handle:
        for row in inspection["source_rows"]:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    manifest = {
        **{key: value for key, value in inspection.items() if key != "source_rows"},
        "status": "projection_complete_pending_metric_normalization",
        "config_path": plan["config_path"],
        "config_sha256": plan["config_sha256"],
        "source_registry": str(registry_path),
        "source_registry_sha256": sha256_file(registry_path),
        "historical_sources_mutated": False,
        "metric_rows_written": 0,
        "normalization_status": "not_run_separate_boundary",
    }
    write_json(output_root / "projection_manifest.json", manifest)
    files = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(output_root.iterdir())
        if path.is_file() and path.name != "final_inventory.json"
    ]
    write_json(
        output_root / "final_inventory.json",
        {
            "schema_version": 1,
            "inventory_excludes": ["final_inventory.json"],
            "file_count": len(files),
            "total_bytes": sum(row["bytes"] for row in files),
            "files": files,
        },
    )
    return manifest
