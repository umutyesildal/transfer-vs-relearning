"""Fail-closed D0 v2 preflight with the historical line-inventory semantics."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .d0_storage import validate_storage_observation


EXPECTED_EVIDENCE = {
    "root": "/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1",
    "regular_file_count": 104,
    "regular_bytes": 18_025_945,
    "inventory_serialization": "relative_path_space_size_lf_utf8",
    "inventory_sha256": "120cdd7b21e161bf981cf8191fa278a11829d3fc5c155b71ed4bc8836e27f1d3",
}
EXPECTED_REGISTRY_SHA256 = "b1c80bf78ff40de5c02e14f08082a51cc17cc90a9853028eaf866cb63326e41f"
HOME_LIMIT_BYTES = 30 * 1024**3
APPROVED_SCRATCH_PARENT = Path("/vol/tmp2/yesildau")
OUTPUT_ROOT = APPROVED_SCRATCH_PARENT / "vngrs_m2_three_model_d0_v2"
HOME_ROOT = Path("/vol/fob-vol6/mi25/yesildau")
V1_FAILURE_EVIDENCE = {
    "path": "/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1/control/preflight_failure.json",
    "bytes": 351,
    "sha256": "54e3f59abd2df14cc00acb260dbe13c0f90dd5a18a22e8d0eb9089f31382a1ce",
}


def _run(*args: str, cwd: Path | None = None, timeout: int = 300) -> str:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        check=True,
        capture_output=True,
        timeout=timeout,
    ).stdout.strip()


def line_inventory_sha256(rows: list[dict[str, Any]]) -> str:
    """Hash exact UTF-8 ``relative_path size\n`` rows in lexical path order."""

    ordered = sorted(rows, key=lambda row: row["path"])
    payload = b"".join(
        f"{row['path']} {row['bytes']}\n".encode("utf-8") for row in ordered
    )
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_d0_v2_preflight_observation(
    repo: str | Path, *, user: str = "yesildau"
) -> dict[str, Any]:
    """Collect D0 v2 evidence in memory without source/output mutation."""

    repo_path = Path(repo).resolve()
    evidence_root = Path(EXPECTED_EVIDENCE["root"])
    rows = [
        {"path": str(path.relative_to(evidence_root)), "bytes": path.stat().st_size}
        for path in sorted(evidence_root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]
    home_bytes = int(_run("du", "-x", "-B1", "-s", str(HOME_ROOT)).split()[0])
    current_job = os.environ.get("SLURM_JOB_ID")
    queue = _run("squeue", "-h", "-u", user, "-o", "%i|%j")
    duplicate_jobs = sum(
        job_id != current_job and name == "vngrs-m2-d0-v2"
        for job_id, name in (
            line.split("|", 1) for line in queue.splitlines() if "|" in line
        )
    )
    stat = os.statvfs(OUTPUT_ROOT.parent)
    v1_failure = Path(V1_FAILURE_EVIDENCE["path"])
    return {
        "git_commit": _run("git", "rev-parse", "HEAD", cwd=repo_path),
        "clean_task_overlap": not bool(
            _run("git", "status", "--porcelain", cwd=repo_path)
        ),
        "accepted_evidence": {
            "root": str(evidence_root),
            "regular_file_count": len(rows),
            "regular_bytes": sum(row["bytes"] for row in rows),
            "inventory_serialization": "relative_path_space_size_lf_utf8",
            "inventory_sha256": line_inventory_sha256(rows),
        },
        "source_registry_sha256": EXPECTED_REGISTRY_SHA256,
        "hu_home_exact_bytes": home_bytes,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": duplicate_jobs,
        "v1_failure_evidence": {
            "path": str(v1_failure),
            "bytes": v1_failure.stat().st_size if v1_failure.is_file() else None,
            "sha256": _sha256(v1_failure) if v1_failure.is_file() else None,
        },
        "storage": {
            "resolved_parent": str(OUTPUT_ROOT.parent.resolve()),
            "proposed_root_absent": not OUTPUT_ROOT.exists(),
            "available_bytes": stat.f_frsize * stat.f_bavail,
            "available_inodes": stat.f_favail,
        },
    }


def validate_d0_v2_preflight(
    observation: Mapping[str, Any], *, expected_commit: str
) -> dict[str, Any]:
    if re.fullmatch(r"[0-9a-f]{40}", expected_commit) is None:
        raise ValueError("expected implementation commit is not an exact Git SHA")
    if observation.get("git_commit") != expected_commit:
        raise ValueError("reviewed Git commit drift")
    if observation.get("clean_task_overlap") is not True:
        raise ValueError("task-overlap worktree is dirty")
    if observation.get("accepted_evidence") != EXPECTED_EVIDENCE:
        raise ValueError("accepted read-only evidence closure drift")
    if observation.get("source_registry_sha256") != EXPECTED_REGISTRY_SHA256:
        raise ValueError("frozen source registry drift")
    if observation.get("hu_home_writes_allowed") is not False:
        raise ValueError("HU home must remain read-only")
    home_bytes = observation.get("hu_home_exact_bytes")
    if (
        not isinstance(home_bytes, int)
        or isinstance(home_bytes, bool)
        or home_bytes >= HOME_LIMIT_BYTES
    ):
        raise ValueError("HU home exact-byte policy gate failed")
    if observation.get("duplicate_active_jobs") != 0:
        raise ValueError("duplicate D0 v2 job/root gate failed")
    if observation.get("v1_failure_evidence") != V1_FAILURE_EVIDENCE:
        raise ValueError("preserved V1C terminal evidence is absent")
    storage = validate_storage_observation(observation.get("storage", {}))
    return {
        "schema_version": 2,
        "status": "D0_PREFLIGHT_PASS",
        "git_commit": expected_commit,
        "clean_task_overlap": True,
        "accepted_evidence": dict(EXPECTED_EVIDENCE),
        "source_registry_sha256": EXPECTED_REGISTRY_SHA256,
        "hu_home_exact_bytes": home_bytes,
        "hu_home_limit_bytes": HOME_LIMIT_BYTES,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": 0,
        "v1_failure_evidence": dict(V1_FAILURE_EVIDENCE),
        "storage": storage,
        "ready_to_train": False,
    }


def write_d0_v2_preflight_failure(
    *, expected_commit: str, error: Exception
) -> dict[str, Any]:
    """Persist one terminal V2 pre-root failure beneath the sole V2 root."""

    if re.fullmatch(r"[0-9a-f]{40}", expected_commit) is None:
        raise ValueError("expected implementation commit is not an exact Git SHA")
    if OUTPUT_ROOT.parent.resolve() != APPROVED_SCRATCH_PARENT.resolve():
        raise ValueError("preflight failure root escaped approved scratch")
    failure = {
        "schema_version": 2,
        "status": "BLOCKED_OPERATIONAL_PREFLIGHT",
        "phase": "d0_v2_preflight",
        "error_type": type(error).__name__,
        "message": str(error),
        "git_commit": expected_commit,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "network_requests": 0,
        "source_objects_written": 0,
        "ready_to_train": False,
        "automatic_retry_authorized": False,
    }
    payload = json.dumps(
        failure,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode() + b"\n"
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
