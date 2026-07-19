#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.experiments.m1_cross_family import (
    approved_scratch,
    candidate_by_index,
    candidate_model_manifest,
    candidate_model_root,
    candidate_training_root,
    estimated_family_gib,
    find_completed_final_model,
    load_registry,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


HOME_ROOT = Path("/vol/fob-vol6/mi25/yesildau")
HOME_LIMIT_KIB = 10 * 1024 * 1024
GIB = 1024**3


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def _check(condition: bool, label: str, checks: dict[str, Any], detail: Any) -> None:
    checks[label] = {"status": "PASS" if condition else "FAIL", "detail": detail}
    if not condition:
        raise ValueError(f"Preflight failed: {label}: {detail}")


def _unexpected_target_jobs(
    target_job_name: str,
    queue_rows: list[str],
    current_job_id: str | None,
    selected_candidate_indices: set[int] | None = None,
) -> list[str]:
    unexpected: list[str] = []
    for row in queue_rows:
        parts = row.split("|", 2)
        if len(parts) == 3:
            job_id, job_name, dependencies = parts
        else:
            job_id = ""
            job_name, separator, dependencies = row.partition("|")
        if job_name.strip() != target_job_name:
            continue
        if current_job_id and current_job_id in dependencies:
            # The launcher intentionally submits the target array with afterok:<this preflight>.
            continue
        if selected_candidate_indices is not None:
            match = re.search(r"_(\d+)$", job_id.strip())
            if match and int(match.group(1)) not in selected_candidate_indices:
                # A completed-subset evaluation may overlap a disjoint candidate task.
                continue
        unexpected.append(row)
    return sorted(unexpected)


def _candidate_indices(args: argparse.Namespace, registry: dict[str, Any]) -> list[int]:
    indices = args.candidate_index or [int(candidate["index"]) for candidate in registry["candidates"]]
    if len(indices) != len(set(indices)):
        raise ValueError("Candidate indices must be unique")
    for index in indices:
        candidate_by_index(registry, index)
    return sorted(indices)


def _stage_outputs(stage: str, registry: dict[str, Any], candidates: list[dict[str, Any]]) -> list[Path]:
    scratch_root = approved_scratch(Path(str(registry["scratch_root"])))
    if stage == "acquisition":
        return [candidate_model_root(registry, candidate) for candidate in candidates]
    if stage == "training":
        return [candidate_training_root(registry, candidate) for candidate in candidates]
    return [approved_scratch(scratch_root / "evaluations" / str(candidate["label"])) for candidate in candidates]


def run_preflight(args: argparse.Namespace) -> dict[str, Any]:
    registry_path = args.registry.resolve()
    registry = load_registry(registry_path)
    repo_root = args.repo_root.resolve()
    scratch_root = approved_scratch(Path(str(registry["scratch_root"])))
    manifest_path = approved_scratch(args.manifest.resolve())
    launcher = args.launcher.resolve()
    template = args.template.resolve()
    indices = _candidate_indices(args, registry)
    candidates = [candidate_by_index(registry, index) for index in indices]
    checks: dict[str, Any] = {}
    started_at = _now()
    payload: dict[str, Any] = {
        "version": "m1_cross_family_screen_v1_preflight",
        "stage": args.stage,
        "started_at": started_at.isoformat(),
        "status": "RUNNING",
        "checks": checks,
        "repo_root": str(repo_root),
        "scratch_root": str(scratch_root),
        "expected_commit": args.expected_commit,
        "candidate_indices": indices,
        "candidate_labels": [candidate["label"] for candidate in candidates],
        "allow_subset_retry": bool(args.allow_subset_retry),
        "allow_completed_subset_evaluation": bool(args.allow_completed_subset_evaluation),
    }
    try:
        _check(registry_path.is_file(), "registry_exists", checks, str(registry_path))
        _check(template.is_file(), "training_template_exists", checks, str(template))
        _check(launcher.is_file(), "launcher_exists", checks, str(launcher))
        _check(
            not (args.allow_subset_retry and args.allow_completed_subset_evaluation),
            "subset_mode_is_unambiguous",
            checks,
            {
                "allow_subset_retry": bool(args.allow_subset_retry),
                "allow_completed_subset_evaluation": bool(args.allow_completed_subset_evaluation),
            },
        )
        commit = _run("git", "-C", str(repo_root), "rev-parse", "HEAD")
        _check(commit == args.expected_commit, "checkout_commit", checks, commit)

        if args.stage in {"training", "evaluation"}:
            required_indices = {int(candidate["index"]) for candidate in registry["candidates"] if bool(candidate["required"])}
            if args.allow_subset_retry:
                _check(args.stage == "training", "subset_retry_is_training_only", checks, args.stage)
                _check(bool(args.candidate_index), "subset_retry_is_explicit", checks, indices)
            elif args.allow_completed_subset_evaluation:
                _check(args.stage == "evaluation", "completed_subset_is_evaluation_only", checks, args.stage)
                _check(bool(args.candidate_index), "completed_subset_is_explicit", checks, indices)
            else:
                _check(required_indices.issubset(indices), "required_candidates_in_wave", checks, {"required": sorted(required_indices), "selected": indices})
            manifests = [candidate_model_manifest(registry, candidate) for candidate in candidates]
            _check(all(path.is_file() for path in manifests), "candidate_model_manifests", checks, [str(path) for path in manifests])
        if args.stage == "training":
            dataset_root = approved_scratch(Path(str(registry["dataset_root"])))
            dataset_files = [dataset_root / name for name in ("dataset_manifest.json", "train.jsonl", "validation.jsonl")]
            _check(all(path.is_file() for path in dataset_files), "frozen_dataset_assets", checks, [str(path) for path in dataset_files])
        if args.stage == "evaluation":
            completed = [str(find_completed_final_model(candidate_training_root(registry, candidate))) for candidate in candidates]
            _check(len(completed) == len(candidates), "completed_training_endpoints", checks, completed)

        outputs = _stage_outputs(args.stage, registry, candidates)
        _check(all(str(path).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")) for path in outputs), "output_namespaces_are_scratch", checks, [str(path) for path in outputs])
        _check(not any(path.exists() for path in outputs), "output_namespaces_absent", checks, [str(path) for path in outputs])

        home_kib = int(_run("du", "-xsk", str(HOME_ROOT)).split()[0])
        _check(home_kib <= HOME_LIMIT_KIB, "home_usage", checks, {"kib": home_kib, "limit_kib": HOME_LIMIT_KIB})
        payload["df_h"] = _run("df", "-h", str(HOME_ROOT), "/vol/tmp", "/vol/tmp2")
        payload["df_i"] = _run("df", "-i", str(HOME_ROOT), "/vol/tmp", "/vol/tmp2")

        usage = shutil.disk_usage(scratch_root.parent if scratch_root.parent.exists() else Path("/vol/tmp2"))
        stat = os.statvfs(scratch_root.parent if scratch_root.parent.exists() else Path("/vol/tmp2"))
        available_inodes = stat.f_favail
        estimated_gib = estimated_family_gib(registry, candidates)
        estimated_bytes = estimated_gib * GIB
        _check(estimated_bytes <= usage.free, "combined_capacity_fit", checks, {"estimated_gib": estimated_gib, "free_bytes": usage.free})
        _check(available_inodes >= args.estimated_inodes, "combined_inode_fit", checks, {"estimated_inodes": args.estimated_inodes, "available_inodes": available_inodes})

        resolved_paths = {
            "runs": str((repo_root / "runs").resolve()),
            "artifacts": str((repo_root / "artifacts").resolve()),
            "family_root": str(scratch_root),
            "outputs": [str(path) for path in outputs],
            "model_manifests": [str(candidate_model_manifest(registry, candidate)) for candidate in candidates],
        }
        _check(
            all(str(value).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")) for value in (resolved_paths["runs"], resolved_paths["artifacts"], resolved_paths["family_root"])),
            "high_volume_roots_are_scratch",
            checks,
            resolved_paths,
        )
        target_job_name = {"acquisition": "m1-xfam-acquire", "training": "m1-xfam-train", "evaluation": "m1-xfam-eval"}[args.stage]
        queued = _run("squeue", "-u", args.user, "-h", "-o", "%i|%j|%E").splitlines()
        selected_for_overlap = set(indices) if args.allow_completed_subset_evaluation else None
        duplicates = _unexpected_target_jobs(
            target_job_name,
            queued,
            os.environ.get("SLURM_JOB_ID"),
            selected_for_overlap,
        )
        _check(not duplicates, "duplicate_target_jobs", checks, duplicates)

        payload.update(
            {
                "registry_path": str(registry_path),
                "registry_sha256": sha256_file(registry_path),
                "template_path": str(template),
                "template_sha256": sha256_file(template),
                "launcher_path": str(launcher),
                "launcher_sha256": sha256_file(launcher),
                "resolved_paths": resolved_paths,
                "expected_checkpoints_per_candidate": int(registry["expected_checkpoints_per_candidate"]),
                "estimated_family_gib": estimated_gib,
                "estimated_inodes": args.estimated_inodes,
                "retention": registry["retention"],
                "status": "PASS",
            }
        )
    except Exception as exc:
        payload["status"] = "FAIL"
        payload["error"] = str(exc)
    payload["finished_at"] = _now().isoformat()
    write_json(manifest_path, payload)
    if payload["status"] != "PASS":
        raise RuntimeError(payload["error"])
    return payload


def verify_preflight(args: argparse.Namespace) -> dict[str, Any]:
    manifest = json.loads(args.verify_manifest.read_text(encoding="utf-8"))
    if manifest.get("status") != "PASS" or manifest.get("stage") != args.stage:
        raise ValueError("Preflight manifest status/stage mismatch")
    finished_at = datetime.fromisoformat(str(manifest["finished_at"]))
    if _now() - finished_at > timedelta(minutes=args.max_age_minutes):
        raise ValueError("Preflight manifest is stale")
    commit = _run("git", "-C", str(args.repo_root.resolve()), "rev-parse", "HEAD")
    if commit != manifest.get("expected_commit"):
        raise ValueError("Checkout commit differs from preflight manifest")
    for path, key in ((args.registry.resolve(), "registry_sha256"), (args.template.resolve(), "template_sha256"), (args.launcher.resolve(), "launcher_sha256")):
        if sha256_file(path) != manifest.get(key):
            raise ValueError(f"Preflight source hash changed: {path}")
    if args.candidate_index and not set(args.candidate_index).issubset(set(manifest.get("candidate_indices", []))):
        raise ValueError("Candidate is not covered by the family preflight manifest")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or verify one family-level Document 105 preflight.")
    parser.add_argument("--stage", choices=("acquisition", "training", "evaluation"), required=True)
    parser.add_argument("--verify-manifest", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--launcher", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path("/vol/tmp2/yesildau/m1_cross_family_screen_v1/preflight/manifest.json"))
    parser.add_argument("--candidate-index", type=int, action="append", default=[])
    parser.add_argument("--allow-subset-retry", action="store_true")
    parser.add_argument("--allow-completed-subset-evaluation", action="store_true")
    parser.add_argument("--expected-commit", default=None)
    parser.add_argument("--user", default="yesildau")
    parser.add_argument("--estimated-inodes", type=int, default=250000)
    parser.add_argument("--max-age-minutes", type=int, default=30)
    args = parser.parse_args()
    if args.verify_manifest:
        print(json.dumps(verify_preflight(args), indent=2, sort_keys=True))
        return
    if not args.expected_commit:
        parser.error("Preflight creation requires --expected-commit")
    print(json.dumps(run_preflight(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
