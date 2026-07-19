#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file, write_json


HOME_ROOT = Path("/vol/fob-vol6/mi25/yesildau")
HOME_LIMIT_KIB = 10 * 1024 * 1024
APPROVED_PREFIXES = ("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")


def _run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def _check(condition: bool, label: str, checks: dict[str, Any], detail: Any) -> None:
    checks[label] = {"status": "PASS" if condition else "FAIL", "detail": detail}
    if not condition:
        raise ValueError(f"Preflight failed: {label}: {detail}")


def _rows(registry: Path) -> list[dict[str, str]]:
    with registry.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def verify(args: argparse.Namespace) -> dict[str, Any]:
    payload = json.loads(args.verify_manifest.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS":
        raise ValueError("Preflight manifest did not pass")
    finished = datetime.fromisoformat(str(payload["finished_at"]))
    if datetime.now(timezone.utc) - finished > timedelta(minutes=args.max_age_minutes):
        raise ValueError("Preflight manifest is stale")
    if _run("git", "-C", str(args.repo_root.resolve()), "rev-parse", "HEAD") != payload["expected_commit"]:
        raise ValueError("Checkout changed after preflight")
    for path, key in ((args.registry.resolve(), "registry_sha256"), (args.wave_manifest.resolve(), "wave_manifest_sha256"), (args.launcher.resolve(), "launcher_sha256")):
        if sha256_file(path) != payload[key]:
            raise ValueError(f"Frozen source changed after preflight: {path}")
    if args.task_index is not None and args.task_index not in payload["task_indices"]:
        raise ValueError("Array task is not covered by preflight")
    return payload


def create(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo_root.resolve()
    registry = args.registry.resolve()
    wave_manifest = args.wave_manifest.resolve()
    launcher = args.launcher.resolve()
    manifest_path = args.manifest.resolve()
    checks: dict[str, Any] = {}
    payload: dict[str, Any] = {
        "version": "m1_qwen_checkpoint_pareto_v1",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "RUNNING",
        "checks": checks,
        "expected_commit": args.expected_commit,
    }
    try:
        for path in (registry, wave_manifest, launcher):
            _check(path.is_file(), f"exists_{path.name}", checks, str(path))
        commit = _run("git", "-C", str(repo), "rev-parse", "HEAD")
        _check(commit == args.expected_commit, "checkout_commit", checks, commit)
        rows = _rows(registry)
        indices = [int(row["array_index"]) for row in rows]
        _check(indices == list(range(11)), "eleven_ordered_tasks", checks, indices)
        _check(all(Path(row["model_manifest"]).is_file() for row in rows), "model_manifests_exist", checks, len(rows))
        _check(all(sha256_file(Path(row["model_manifest"])) == row["model_manifest_sha256"] for row in rows), "model_manifest_hashes", checks, len(rows))
        result_paths = [Path(row[key]) for row in rows for key in ("hard_output",)]
        result_paths += [Path(row["exact_config"]).parent.parent / "exact_prefix" / row["label"] for row in rows]
        result_paths += [Path(row["general_config"]).parent.parent / "general_capability" / row["label"] for row in rows]
        _check(all(str(path.resolve()).startswith(APPROVED_PREFIXES) for path in result_paths), "outputs_on_scratch", checks, [str(path) for path in result_paths])
        _check(not any(path.exists() for path in result_paths), "result_namespaces_absent", checks, [str(path) for path in result_paths if path.exists()])
        home_kib = int(_run("du", "-xsk", str(HOME_ROOT)).split()[0])
        _check(home_kib <= HOME_LIMIT_KIB, "home_usage", checks, {"kib": home_kib, "limit_kib": HOME_LIMIT_KIB})
        payload["df_h"] = _run("df", "-h", str(HOME_ROOT), "/vol/tmp", "/vol/tmp2")
        payload["df_i"] = _run("df", "-i", str(HOME_ROOT), "/vol/tmp", "/vol/tmp2")
        usage = shutil.disk_usage(Path("/vol/tmp2"))
        stat = os.statvfs(Path("/vol/tmp2"))
        estimated_bytes = args.estimated_gib * 1024**3
        _check(estimated_bytes <= usage.free, "capacity_fit", checks, {"estimated_gib": args.estimated_gib, "free_bytes": usage.free})
        _check(args.estimated_inodes <= stat.f_favail, "inode_fit", checks, {"estimated": args.estimated_inodes, "available": stat.f_favail})
        resolved = {"runs": str((repo / "runs").resolve()), "artifacts": str((repo / "artifacts").resolve()), "wave": str(registry.parent.resolve())}
        _check(all(value.startswith(APPROVED_PREFIXES) for value in resolved.values()), "high_volume_roots_on_scratch", checks, resolved)
        queue = _run("squeue", "-u", args.user, "-h", "-o", "%i|%j|%E").splitlines()
        current = os.environ.get("SLURM_JOB_ID", "")
        duplicates = [line for line in queue if "|m1-qwen-pareto|" in line and (not current or current not in line.rsplit("|", 1)[-1])]
        _check(not duplicates, "no_duplicate_wave", checks, duplicates)
        payload.update({
            "status": "PASS",
            "registry_sha256": sha256_file(registry),
            "wave_manifest_sha256": sha256_file(wave_manifest),
            "launcher_sha256": sha256_file(launcher),
            "task_indices": indices,
            "estimated_gib": args.estimated_gib,
            "estimated_inodes": args.estimated_inodes,
            "resolved_paths": resolved,
            "retention": "read-only source checkpoints; compact evaluation outputs retained until Document 108 decision",
        })
    except Exception as exc:
        payload.update({"status": "FAIL", "error": str(exc)})
    payload["finished_at"] = datetime.now(timezone.utc).isoformat()
    write_json(manifest_path, payload)
    if payload["status"] != "PASS":
        raise RuntimeError(payload["error"])
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or verify the Document 107 family preflight.")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--wave-manifest", type=Path, required=True)
    parser.add_argument("--launcher", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path("/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1/preflight/manifest.json"))
    parser.add_argument("--verify-manifest", type=Path)
    parser.add_argument("--expected-commit")
    parser.add_argument("--task-index", type=int)
    parser.add_argument("--user", default="yesildau")
    parser.add_argument("--estimated-gib", type=int, default=100)
    parser.add_argument("--estimated-inodes", type=int, default=100000)
    parser.add_argument("--max-age-minutes", type=int, default=720)
    args = parser.parse_args()
    if args.verify_manifest:
        print(json.dumps(verify(args), indent=2, sort_keys=True))
    else:
        if not args.expected_commit:
            parser.error("creation requires --expected-commit")
        print(json.dumps(create(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
