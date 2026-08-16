#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.study.m0_parallel import (
    assess_m0_parallel_readiness,
    build_m0_parallel_plan,
    initialize_m0_namespace,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


DEFAULT_MANIFEST = Path("configs/evaluation/m0_scientific_three_model_v1.yaml")
DEFAULT_STATE = Path("documentation/current/PROJECT_STATE.yaml")
MODEL_ORDER = ("olmo", "qwen", "smollm")


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a mapping: {path}")
    return payload


def _resolve(path: str | Path, repo_root: Path) -> Path:
    value = Path(path)
    return value.resolve() if value.is_absolute() else (repo_root / value).resolve()


def build_three_model_plan(manifest_path: Path, *, repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    manifest = _load_yaml(manifest_path)
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported three-model M0 manifest schema")
    if manifest.get("status") not in {"prepared", "frozen"}:
        raise ValueError("Three-model M0 manifest must be prepared or frozen")
    if not isinstance(manifest.get("execution_authorized"), bool):
        raise ValueError("Three-model M0 execution_authorized must be boolean")
    if manifest.get("model_order") != list(MODEL_ORDER):
        raise ValueError("Three-model M0 model_order must be olmo/qwen/smollm")
    family_root = Path(str(manifest.get("family_root", ""))).resolve()
    if not str(family_root).startswith("/vol/tmp2/yesildau/"):
        raise ValueError("Three-model M0 family root must be under approved scratch")
    models = manifest.get("models")
    if not isinstance(models, dict) or tuple(models) != MODEL_ORDER:
        raise ValueError("Three-model M0 manifest must contain ordered olmo/qwen/smollm rows")

    rows: list[dict[str, Any]] = []
    plan_ids: set[str] = set()
    output_roots: set[str] = set()
    for model_id in MODEL_ORDER:
        binding = models[model_id]
        if not isinstance(binding, dict):
            raise ValueError(f"Invalid model binding: {model_id}")
        config_path = _resolve(binding["config"], repo_root)
        if not config_path.is_file() or sha256_file(config_path) != binding["config_sha256"]:
            raise ValueError(f"Frozen M0 config identity mismatch: {model_id}")
        plan = build_m0_parallel_plan(config_path, repo_root=repo_root)
        if plan["classification"] != "scientific_evaluation":
            raise ValueError(f"Model config is not scientific M0: {model_id}")
        if plan["model"]["repository"] != binding["repository"]:
            raise ValueError(f"Model repository mismatch: {model_id}")
        output_root = Path(str(plan["storage"]["proposed_root"])).resolve()
        if output_root.parent != family_root or output_root.name != model_id:
            raise ValueError(f"Model output root is outside its exact family cell: {model_id}")
        plan_ids.add(plan["plan_id"])
        output_roots.add(str(output_root))
        rows.append(
            {
                "model_id": model_id,
                "config_path": str(config_path),
                "config_sha256": binding["config_sha256"],
                "plan_id": plan["plan_id"],
                "output_root": str(output_root),
                "repository": plan["model"]["repository"],
                "revision": plan["model"]["revision"],
                "lane_count": plan["lane_count"],
                "execution_ready": plan["execution_ready"],
                "execution_authorized": plan["execution_authorized"],
            }
        )
    if len(plan_ids) != 3 or len(output_roots) != 3:
        raise ValueError("Every model requires a distinct plan and output namespace")
    return {
        "schema_version": 1,
        "name": manifest["name"],
        "status": manifest["status"],
        "execution_authorized": manifest["execution_authorized"],
        "manifest_path": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "family_root": str(family_root),
        "model_order": list(MODEL_ORDER),
        "model_count": 3,
        "total_lane_count": sum(row["lane_count"] for row in rows),
        "parallel_models": 3,
        "models": rows,
    }


def assess_three_model_readiness(
    manifest_path: Path, *, repo_root: Path, project_state_path: Path
) -> dict[str, Any]:
    family = build_three_model_plan(manifest_path, repo_root=repo_root)
    rows = []
    for row in family["models"]:
        readiness = assess_m0_parallel_readiness(
            Path(row["config_path"]),
            repo_root=repo_root,
            project_state_path=project_state_path,
            output_root=Path(row["output_root"]),
        )
        rows.append({"model_id": row["model_id"], **readiness})
    blockers = [
        f"{row['model_id']}:{blocker}"
        for row in rows
        for blocker in row["blockers"]
    ]
    if family["execution_authorized"] is not True:
        blockers.append("family_execution_not_authorized")
    return {
        "schema_version": 1,
        "scope": "three_model_scientific_m0_preflight",
        "status": "ready" if not blockers else "blocked_pre_scoring",
        "scientific_work_started": False,
        "family": family,
        "models": rows,
        "blockers": blockers,
    }


def _single_model_operator(repo_root: Path) -> Any:
    path = repo_root / "scripts/study/run_m0_olmo_evaluation.py"
    spec = importlib.util.spec_from_file_location("single_model_m0_operator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the single-model M0 operator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def submit_three_model_family(
    manifest_path: Path, *, repo_root: Path, project_state_path: Path
) -> dict[str, Any]:
    readiness = assess_three_model_readiness(
        manifest_path,
        repo_root=repo_root,
        project_state_path=project_state_path,
    )
    if readiness["status"] != "ready":
        raise PermissionError(f"Three-model M0 preflight is blocked: {readiness['blockers']}")
    family = readiness["family"]
    family_root = Path(family["family_root"])
    if family_root.exists():
        raise FileExistsError(f"Three-model M0 family root already exists: {family_root}")
    operator = _single_model_operator(repo_root)
    submissions: list[dict[str, Any]] = []
    try:
        for row in family["models"]:
            config_path = Path(row["config_path"])
            plan = build_m0_parallel_plan(config_path, repo_root=repo_root)
            output_root = Path(row["output_root"])
            initialize_m0_namespace(output_root, plan)
            child = operator._submit_parallel_jobs(
                plan,
                config_path=config_path,
                repo_root=repo_root,
                output_root=output_root,
            )
            submissions.append({"model_id": row["model_id"], **child})
    except Exception as exc:
        family_root.mkdir(parents=True, exist_ok=True)
        write_json(
            family_root / "three_model_submission_manifest.json",
            {
                "schema_version": 1,
                "status": "partial_submission_preserved_no_automatic_cancellation",
                "family": family,
                "submissions": submissions,
                "error": str(exc),
            },
        )
        raise

    child_finalizers = [str(row["finalizer_job_id"]) for row in submissions]
    first_plan = build_m0_parallel_plan(
        Path(family["models"][0]["config_path"]), repo_root=repo_root
    )
    final_command = [
        first_plan["runtime"]["python"],
        str(Path(__file__).resolve()),
        "finalize",
        "--manifest",
        str(manifest_path),
        "--repo-root",
        str(repo_root),
    ]
    family_finalizer_id = operator._submit(
        [
            "sbatch",
            "--parsable",
            f"--account={first_plan['slurm']['account']}",
            f"--partition={first_plan['slurm']['control_partition']}",
            "--job-name=m0-three-model-finalize",
            f"--dependency=afterany:{':'.join(child_finalizers)}",
            "--cpus-per-task=2",
            "--mem=8G",
            "--time=00:30:00",
            f"--output={family_root / 'family-finalizer-%j.out'}",
            f"--error={family_root / 'family-finalizer-%j.err'}",
            f"--chdir={repo_root}",
            f"--wrap=exec {shlex.join(final_command)}",
        ]
    )
    payload = {
        "schema_version": 1,
        "status": "submitted",
        "family": family,
        "submissions": submissions,
        "child_finalizer_job_ids": child_finalizers,
        "family_finalizer_job_id": family_finalizer_id,
        "family_finalizer_dependency": f"afterany:{':'.join(child_finalizers)}",
    }
    write_json(family_root / "three_model_submission_manifest.json", payload)
    return payload


def finalize_three_model_family(manifest_path: Path, *, repo_root: Path) -> dict[str, Any]:
    family = build_three_model_plan(manifest_path, repo_root=repo_root)
    rows: list[dict[str, Any]] = []
    for model in family["models"]:
        root = Path(model["output_root"])
        result_path = root / "scientific_bundle_result.json"
        manifest_result_path = root / "evaluation_manifest.json"
        if result_path.is_file() and manifest_result_path.is_file():
            result = json.loads(result_path.read_text(encoding="utf-8"))
            evaluation_manifest = json.loads(manifest_result_path.read_text(encoding="utf-8"))
            valid = (
                result.get("plan_id") == model["plan_id"]
                and result.get("status") == "complete_raw_pending_normalization"
                and evaluation_manifest.get("plan_id") == model["plan_id"]
                and evaluation_manifest.get("status") == "complete"
            )
            rows.append(
                {
                    "model_id": model["model_id"],
                    "status": "complete_raw_pending_normalization" if valid else "partial_invalid",
                    "scientific_bundle_result": str(result_path),
                    "scientific_bundle_result_sha256": sha256_file(result_path),
                    "evaluation_manifest": str(manifest_result_path),
                    "evaluation_manifest_sha256": sha256_file(manifest_result_path),
                }
            )
        else:
            rows.append(
                {
                    "model_id": model["model_id"],
                    "status": "not_run_or_incomplete",
                    "scientific_bundle_result": None,
                    "evaluation_manifest": None,
                }
            )
    complete = all(row["status"] == "complete_raw_pending_normalization" for row in rows)
    payload = {
        "schema_version": 1,
        "status": (
            "complete_raw_pending_normalization"
            if complete
            else "partial_invalid_no_cross_model_summary"
        ),
        "scientific_work_started": any(row["status"] != "not_run_or_incomplete" for row in rows),
        "normalization_allowed": complete,
        "family": family,
        "models": rows,
        "cross_model_pass_fail": "not_computed_by_raw_family_finalizer",
    }
    family_root = Path(family["family_root"])
    family_root.mkdir(parents=True, exist_ok=True)
    write_json(family_root / "three_model_m0_raw_bundle.json", payload)
    return payload


def family_status(manifest_path: Path, *, repo_root: Path) -> dict[str, Any]:
    family = build_three_model_plan(manifest_path, repo_root=repo_root)
    rows = []
    for model in family["models"]:
        root = Path(model["output_root"])
        status_path = root / "bundle_status.json"
        result_path = root / "scientific_bundle_result.json"
        status = (
            json.loads(result_path.read_text(encoding="utf-8"))["status"]
            if result_path.is_file()
            else json.loads(status_path.read_text(encoding="utf-8"))["status"]
            if status_path.is_file()
            else "not_submitted"
        )
        rows.append({"model_id": model["model_id"], "status": status, "root": str(root)})
    return {"schema_version": 1, "family": family, "models": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description="Operate the frozen three-model scientific M0 family")
    parser.add_argument("command", choices=("plan", "preflight", "submit", "status", "finalize"))
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--project-state", type=Path, default=DEFAULT_STATE)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    manifest_path = _resolve(args.manifest, repo_root)
    state_path = _resolve(args.project_state, repo_root)

    if args.command == "plan":
        payload = build_three_model_plan(manifest_path, repo_root=repo_root)
    elif args.command == "preflight":
        payload = assess_three_model_readiness(
            manifest_path, repo_root=repo_root, project_state_path=state_path
        )
    elif args.command == "submit":
        payload = submit_three_model_family(
            manifest_path, repo_root=repo_root, project_state_path=state_path
        )
    elif args.command == "status":
        payload = family_status(manifest_path, repo_root=repo_root)
    else:
        payload = finalize_three_model_family(manifest_path, repo_root=repo_root)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    if args.command == "preflight" and payload["status"] != "ready":
        raise SystemExit(2)
    if args.command == "finalize" and not payload["normalization_allowed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
