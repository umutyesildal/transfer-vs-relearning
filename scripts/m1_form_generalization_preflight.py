#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file, write_json


HOME_ROOT = Path("/vol/fob-vol6/mi25/yesildau")
SCRATCH_PREFIXES = ("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")
HOME_LIMIT_KIB = 10 * 1024 * 1024


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def _under_scratch(path: Path) -> bool:
    return str(path.resolve()).startswith(SCRATCH_PREFIXES)


def _check(condition: bool, label: str, checks: dict[str, Any], detail: Any) -> None:
    checks[label] = {"status": "PASS" if condition else "FAIL", "detail": detail}
    if not condition:
        raise ValueError(f"Preflight failed: {label}: {detail}")


def run_preflight(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    scratch_root = args.scratch_root.resolve()
    manifest_path = args.manifest.resolve()
    source_configs = [path.resolve() for path in args.source_config]
    launcher = args.launcher.resolve()
    outputs = [path.resolve() for path in args.output_namespace]
    checks: dict[str, Any] = {}
    started_at = _now()
    payload: dict[str, Any] = {
        "version": "m1_form_generalization_v1_preflight",
        "started_at": started_at.isoformat(),
        "status": "RUNNING",
        "checks": checks,
        "repo_root": str(repo_root),
        "scratch_root": str(scratch_root),
        "expected_commit": args.expected_commit,
    }
    try:
        _check(_under_scratch(scratch_root), "scratch_root", checks, str(scratch_root))
        _check(_under_scratch(manifest_path.parent), "manifest_path", checks, str(manifest_path))
        _check(all(path.is_file() for path in source_configs), "source_configs", checks, [str(path) for path in source_configs])
        _check(launcher.is_file(), "launcher", checks, str(launcher))
        commit = _run("git", "-C", str(repo_root), "rev-parse", "HEAD")
        _check(commit == args.expected_commit, "checkout_commit", checks, commit)
        _check(all(_under_scratch(path) for path in outputs), "output_namespaces_are_scratch", checks, [str(path) for path in outputs])
        _check(not any(path.exists() for path in outputs), "output_namespaces_absent", checks, [str(path) for path in outputs])

        home_kib = int(_run("du", "-xsk", str(HOME_ROOT)).split()[0])
        _check(home_kib <= HOME_LIMIT_KIB, "home_usage", checks, {"kib": home_kib, "limit_kib": HOME_LIMIT_KIB})
        payload["df_h"] = _run("df", "-h", str(HOME_ROOT), "/vol/tmp", "/vol/tmp2")
        payload["df_i"] = _run("df", "-i", str(HOME_ROOT), "/vol/tmp", "/vol/tmp2")

        resolved_paths = {
            "runs": str((repo_root / "runs").resolve()),
            "artifacts": str((repo_root / "artifacts").resolve()),
            "base_model_manifest": str((repo_root / "artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json").resolve()),
        }
        _check(all(_under_scratch(Path(value)) for value in resolved_paths.values()), "high_volume_paths", checks, resolved_paths)
        queue_names = _run("squeue", "-u", args.user, "-h", "-o", "%j").splitlines()
        duplicate_names = sorted(name for name in queue_names if name.strip() == "m1-form-generalization")
        _check(not duplicate_names, "duplicate_queue_job", checks, duplicate_names)
        payload["source_config_hashes"] = {str(path): sha256_file(path) for path in source_configs}
        payload["launcher_path"] = str(launcher)
        payload["launcher_sha256"] = sha256_file(launcher)
        payload["resolved_paths"] = resolved_paths
        payload["status"] = "PASS"
    except Exception as exc:
        payload["status"] = "FAIL"
        payload["error"] = str(exc)
    payload["finished_at"] = _now().isoformat()
    write_json(manifest_path, payload)
    if payload["status"] != "PASS":
        raise RuntimeError(payload["error"])
    return payload


def verify_preflight(args: argparse.Namespace) -> None:
    manifest = json.loads(args.verify_manifest.read_text(encoding="utf-8"))
    if manifest.get("status") != "PASS":
        raise ValueError("Preflight manifest status is not PASS")
    finished_at = datetime.fromisoformat(str(manifest["finished_at"]))
    if _now() - finished_at > timedelta(minutes=args.max_age_minutes):
        raise ValueError("Preflight manifest is stale")
    commit = _run("git", "-C", str(args.repo_root.resolve()), "rev-parse", "HEAD")
    if commit != manifest.get("expected_commit"):
        raise ValueError("Checkout commit differs from preflight manifest")
    if sha256_file(args.launcher.resolve()) != manifest.get("launcher_sha256"):
        raise ValueError("Launcher hash differs from preflight manifest")
    expected_hashes = manifest.get("source_config_hashes", {})
    for config in args.source_config:
        resolved = str(config.resolve())
        if expected_hashes.get(resolved) != sha256_file(config.resolve()):
            raise ValueError(f"Config hash differs from preflight manifest: {resolved}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or verify a machine-readable M1 form-generalization preflight manifest.")
    parser.add_argument("--verify-manifest", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, default=Path("/vol/tmp2/yesildau/m1_form_generalization_v1"))
    parser.add_argument("--manifest", type=Path, default=Path("/vol/tmp2/yesildau/m1_form_generalization_v1/preflight/manifest.json"))
    parser.add_argument("--source-config", type=Path, action="append", required=True)
    parser.add_argument("--launcher", type=Path, required=True)
    parser.add_argument("--output-namespace", type=Path, action="append", default=[])
    parser.add_argument("--expected-commit", default=None)
    parser.add_argument("--user", default="yesildau")
    parser.add_argument("--max-age-minutes", type=int, default=30)
    args = parser.parse_args()
    if args.verify_manifest:
        verify_preflight(args)
        return
    if not args.expected_commit or len(args.output_namespace) != 2:
        parser.error("Preflight mode requires --expected-commit and exactly two --output-namespace values")
    payload = run_preflight(args)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
