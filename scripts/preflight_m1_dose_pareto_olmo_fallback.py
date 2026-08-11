#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from transfer_vs_relearning.experiments.m1_dose_pareto import candidate, load_registry
from transfer_vs_relearning.utils.io import sha256_file, write_json


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--previous-output", type=Path, required=True)
    parser.add_argument("--previous-sha256", required=True)
    parser.add_argument("--oom-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    registry_path = args.registry.resolve()
    registry = load_registry(registry_path)
    root = Path(registry["scratch_root"]).resolve()
    previous = args.previous_output.resolve()
    output = args.output.resolve()
    if output.exists() or output.parent != root / "preflight":
        raise FileExistsError(output)
    if sha256_file(previous) != args.previous_sha256:
        raise ValueError("Relocation preflight hash drift")
    if run("git", "-C", str(repo), "rev-parse", "HEAD") != args.expected_commit:
        raise ValueError("HU commit drift")
    oom_log = args.oom_log.resolve()
    oom_text = oom_log.read_text(encoding="utf-8")
    if "torch.OutOfMemoryError" not in oom_text or "scaler.step(optimizer)" not in oom_text:
        raise ValueError("Primary microbatch-4 optimizer-smoke OOM evidence missing")
    if (root / "training" / "olmo").exists() or (root / "evaluations" / "olmo").exists():
        raise FileExistsError("OLMo scientific namespace is not absent")
    jobs = {}
    for job_id in ("453387", "453388"):
        state = run("squeue", "-h", "-j", job_id, "-o", "%T")
        if state != "PENDING":
            raise ValueError(f"Expected PENDING stale job {job_id}, got {state!r}")
        jobs[job_id] = state
    prior = json.loads(previous.read_text(encoding="utf-8"))
    payload = json.loads(json.dumps(prior))
    for label in ("olmo", "falcon", "pythia"):
        item = candidate(registry, label)
        template = (repo / item["training_template"]).resolve()
        payload["checks"][f"candidate:{label}"]["template"] = str(template)
        payload["checks"][f"candidate:{label}"]["template_sha256"] = sha256_file(template)
    policy = registry["home_storage_policy"]
    if bool(policy["home_write_allowed"]) or bool(policy["recursive_du_per_stage"]):
        raise ValueError("No-home-write policy drift")
    usage = shutil.disk_usage(root)
    stat = os.statvfs(root)
    payload.update(
        status="PASS",
        timestamp=datetime.now(UTC).isoformat(),
        expected_commit=args.expected_commit,
        registry_sha256=sha256_file(registry_path),
        predecessor_preflight=str(previous),
        predecessor_preflight_sha256=args.previous_sha256,
        relocation_scope="document_159a_precommitted_fallback_microbatch2_accumulation250",
        primary_smoke_oom_log=str(oom_log),
        primary_smoke_oom_log_sha256=sha256_file(oom_log),
        protected_pending_jobs=jobs,
        retry_scratch_free_bytes=usage.free,
        retry_scratch_available_inodes=stat.f_favail,
    )
    write_json(output, payload)
    print(output)


if __name__ == "__main__":
    main()
