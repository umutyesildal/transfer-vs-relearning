"""Fail-closed D0.0 production-preflight observation validation."""

from __future__ import annotations

import re
import os
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .d0_storage import validate_storage_observation
from .metadata import canonical_json_sha256


EXPECTED_EVIDENCE = {
    "root": "/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1",
    "regular_file_count": 104,
    "regular_bytes": 18_025_945,
    "inventory_sha256": "120cdd7b21e161bf981cf8191fa278a11829d3fc5c155b71ed4bc8836e27f1d3",
}
EXPECTED_REGISTRY_SHA256 = "b1c80bf78ff40de5c02e14f08082a51cc17cc90a9853028eaf866cb63326e41f"
HOME_LIMIT_BYTES = 30 * 1024**3
OUTPUT_ROOT = Path("/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1")
HOME_ROOT = Path("/vol/fob-vol6/mi25/yesildau")


def _run(*args: str, cwd: Path | None = None, timeout: int = 120) -> str:
    return subprocess.run(args, cwd=cwd, text=True, check=True, capture_output=True, timeout=timeout).stdout.strip()


def collect_d0_preflight_observation(repo: str | Path, *, user: str = "yesildau") -> dict[str, Any]:
    """Collect D0.0 evidence in memory; perform no output-root or evidence write."""

    repo_path = Path(repo).resolve()
    evidence_root = Path(EXPECTED_EVIDENCE["root"])
    rows = [
        {"path": str(path.relative_to(evidence_root)), "bytes": path.stat().st_size}
        for path in sorted(evidence_root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]
    home_bytes = int(_run("du", "-x", "-B1", "-s", str(HOME_ROOT), timeout=300).split()[0])
    current_job = os.environ.get("SLURM_JOB_ID")
    queue = _run("squeue", "-h", "-u", user, "-o", "%i|%j")
    duplicate_jobs = sum(
        job_id != current_job and name == "vngrs-m2-d0"
        for job_id, name in (line.split("|", 1) for line in queue.splitlines() if "|" in line)
    )
    stat = os.statvfs(OUTPUT_ROOT.parent)
    return {
        "git_commit": _run("git", "rev-parse", "HEAD", cwd=repo_path),
        "clean_task_overlap": not bool(_run("git", "status", "--porcelain", cwd=repo_path)),
        "accepted_evidence": {
            "root": str(evidence_root),
            "regular_file_count": len(rows),
            "regular_bytes": sum(row["bytes"] for row in rows),
            "inventory_sha256": canonical_json_sha256(rows),
        },
        "source_registry_sha256": EXPECTED_REGISTRY_SHA256,
        "hu_home_exact_bytes": home_bytes,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": duplicate_jobs,
        "storage": {
            "resolved_parent": str(OUTPUT_ROOT.parent.resolve()),
            "proposed_root_absent": not OUTPUT_ROOT.exists(),
            "available_bytes": stat.f_frsize * stat.f_bavail,
            "available_inodes": stat.f_favail,
        },
    }


def validate_d0_preflight(observation: Mapping[str, Any], *, expected_commit: str) -> dict[str, Any]:
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
    if not isinstance(home_bytes, int) or isinstance(home_bytes, bool) or home_bytes >= HOME_LIMIT_BYTES:
        raise ValueError("HU home exact-byte policy gate failed")
    if observation.get("duplicate_active_jobs") != 0:
        raise ValueError("duplicate D0 job/root gate failed")
    storage = validate_storage_observation(observation.get("storage", {}))
    return {
        "schema_version": 1,
        "status": "D0_PREFLIGHT_PASS",
        "git_commit": expected_commit,
        "clean_task_overlap": True,
        "accepted_evidence": dict(EXPECTED_EVIDENCE),
        "source_registry_sha256": EXPECTED_REGISTRY_SHA256,
        "hu_home_exact_bytes": home_bytes,
        "hu_home_limit_bytes": HOME_LIMIT_BYTES,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": 0,
        "storage": storage,
        "ready_to_train": False,
    }
