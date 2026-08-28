"""Fail-closed D0 v3 preflight preserving V2 while repairing byte semantics."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .d0_storage import validate_storage_observation
from .sample_transport import SOURCE_ROOT, validate_source_root


HOME_LIMIT_BYTES = 30 * 1024**3
APPROVED_SCRATCH_PARENT = Path("/vol/tmp2/yesildau")
OUTPUT_ROOT = APPROVED_SCRATCH_PARENT / "vngrs_m2_three_model_d0_v3"
HOME_ROOT = Path("/vol/fob-vol6/mi25/yesildau")
V2_ROOT = APPROVED_SCRATCH_PARENT / "vngrs_m2_three_model_d0_v2"
V2_PARTIAL_EVIDENCE = {
    "path": str(V2_ROOT / "raw/.partial/data/train-00004-of-00284.parquet"),
    "bytes": 448_718_347,
    "sha256": "d72ae76652c1a3880288ebbea9d0004e17c03730971f62666ed09c6c87de0943",
}
V2_FAILURE_CORE = {
    "status": "BLOCKED",
    "error_type": "MaterializationBlocked",
    "message": "data/train-00004-of-00284.parquet: full-object SHA-256 mismatch",
    "source_path": "data/train-00004-of-00284.parquet",
    "partial_path": "raw/.partial/data/train-00004-of-00284.parquet",
    "verified_objects": 0,
    "response_transferred_bytes": 448_718_347,
}


def _run(*args: str, cwd: Path | None = None, timeout: int = 300) -> str:
    return subprocess.run(
        args, cwd=cwd, text=True, check=True, capture_output=True, timeout=timeout
    ).stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_d0_v3_preflight_observation(
    repo: str | Path, *, user: str = "yesildau"
) -> dict[str, Any]:
    repo_path = Path(repo).resolve()
    accepted_rows = validate_source_root(SOURCE_ROOT)
    v2_failure_path = V2_ROOT / "control/failure.json"
    v2_failure = json.loads(v2_failure_path.read_text(encoding="utf-8"))
    partial_path = Path(V2_PARTIAL_EVIDENCE["path"])
    home_bytes = int(_run("du", "-x", "-B1", "-s", str(HOME_ROOT)).split()[0])
    current_job = os.environ.get("SLURM_JOB_ID")
    queue = _run("squeue", "-h", "-u", user, "-o", "%i|%j")
    duplicate_jobs = sum(
        job_id != current_job and name == "vngrs-m2-d0-v3"
        for job_id, name in (line.split("|", 1) for line in queue.splitlines() if "|" in line)
    )
    stat = os.statvfs(OUTPUT_ROOT.parent)
    return {
        "git_commit": _run("git", "rev-parse", "HEAD", cwd=repo_path),
        "clean_task_overlap": not bool(_run("git", "status", "--porcelain", cwd=repo_path)),
        "accepted_source_rows": len(accepted_rows),
        "accepted_source_root": str(SOURCE_ROOT),
        "hu_home_exact_bytes": home_bytes,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": duplicate_jobs,
        "v2_failure_core": {key: v2_failure.get(key) for key in V2_FAILURE_CORE},
        "v2_partial_evidence": {
            "path": str(partial_path),
            "bytes": partial_path.stat().st_size if partial_path.is_file() else None,
            "sha256": _sha256(partial_path) if partial_path.is_file() else None,
        },
        "v2_root_writes_allowed": False,
        "v2_partial_reuse_allowed": False,
        "storage": {
            "resolved_parent": str(OUTPUT_ROOT.parent.resolve()),
            "proposed_root_absent": not OUTPUT_ROOT.exists(),
            "available_bytes": stat.f_frsize * stat.f_bavail,
            "available_inodes": stat.f_favail,
        },
    }


def validate_d0_v3_preflight(
    observation: Mapping[str, Any], *, expected_commit: str
) -> dict[str, Any]:
    if re.fullmatch(r"[0-9a-f]{40}", expected_commit) is None:
        raise ValueError("expected implementation commit is not an exact Git SHA")
    if observation.get("git_commit") != expected_commit:
        raise ValueError("reviewed Git commit drift")
    if observation.get("clean_task_overlap") is not True:
        raise ValueError("task-overlap worktree is dirty")
    if observation.get("accepted_source_root") != str(SOURCE_ROOT) or observation.get("accepted_source_rows") != 32:
        raise ValueError("accepted read-only source evidence drift")
    if observation.get("v2_failure_core") != V2_FAILURE_CORE:
        raise ValueError("preserved V2 terminal failure evidence drift")
    if observation.get("v2_partial_evidence") != V2_PARTIAL_EVIDENCE:
        raise ValueError("preserved V2 partial byte evidence drift")
    if observation.get("v2_root_writes_allowed") is not False or observation.get("v2_partial_reuse_allowed") is not False:
        raise ValueError("V2 evidence must remain read-only and unreused")
    if observation.get("hu_home_writes_allowed") is not False:
        raise ValueError("HU home must remain read-only")
    home_bytes = observation.get("hu_home_exact_bytes")
    if not isinstance(home_bytes, int) or isinstance(home_bytes, bool) or home_bytes >= HOME_LIMIT_BYTES:
        raise ValueError("HU home exact-byte policy gate failed")
    if observation.get("duplicate_active_jobs") != 0:
        raise ValueError("duplicate D0 v3 job/root gate failed")
    storage = validate_storage_observation(observation.get("storage", {}))
    return {
        "schema_version": 3,
        "status": "D0_PREFLIGHT_PASS",
        "git_commit": expected_commit,
        "accepted_source_root": str(SOURCE_ROOT),
        "accepted_source_rows": 32,
        "hu_home_exact_bytes": home_bytes,
        "hu_home_limit_bytes": HOME_LIMIT_BYTES,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": 0,
        "v2_failure_core": dict(V2_FAILURE_CORE),
        "v2_partial_evidence": dict(V2_PARTIAL_EVIDENCE),
        "v2_root_writes_allowed": False,
        "v2_partial_reuse_allowed": False,
        "storage": storage,
        "ready_to_train": False,
    }


def write_d0_v3_preflight_failure(*, expected_commit: str, error: Exception) -> dict[str, Any]:
    if re.fullmatch(r"[0-9a-f]{40}", expected_commit) is None:
        raise ValueError("expected implementation commit is not an exact Git SHA")
    if OUTPUT_ROOT.parent.resolve() != APPROVED_SCRATCH_PARENT.resolve():
        raise ValueError("preflight failure root escaped approved scratch")
    failure = {
        "schema_version": 3,
        "status": "BLOCKED_OPERATIONAL_PREFLIGHT",
        "phase": "d0_v3_preflight",
        "error_type": type(error).__name__,
        "message": str(error),
        "git_commit": expected_commit,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "network_requests": 0,
        "source_objects_written": 0,
        "ready_to_train": False,
        "automatic_retry_authorized": False,
    }
    payload = json.dumps(failure, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    OUTPUT_ROOT.mkdir(parents=False, exist_ok=False)
    control = OUTPUT_ROOT / "control"
    control.mkdir(exist_ok=False)
    target = control / "preflight_failure.json"
    temporary = target.with_name(target.name + ".partial")
    with temporary.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, target)
    return failure
