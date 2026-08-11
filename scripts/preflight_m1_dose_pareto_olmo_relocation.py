#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from transfer_vs_relearning.experiments.m1_dose_pareto import candidate, load_registry, verify_sha
from transfer_vs_relearning.utils.io import sha256_file, write_json


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--previous-output", type=Path, required=True)
    parser.add_argument("--previous-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    registry_path = args.registry.resolve()
    registry = load_registry(registry_path)
    root = Path(registry["scratch_root"]).resolve()
    previous = args.previous_output.resolve()
    output = args.output.resolve()
    if output.exists() or output.parent != root / "preflight":
        raise FileExistsError(f"Relocation preflight output invalid/existing: {output}")
    if sha256_file(previous) != args.previous_sha256:
        raise ValueError("Previous append-only preflight hash drift")
    prior = json.loads(previous.read_text(encoding="utf-8"))
    if prior.get("status") != "PASS":
        raise ValueError("Previous preflight is not PASS")
    if run("git", "-C", str(repo_root), "rev-parse", "HEAD") != args.expected_commit:
        raise ValueError("HU commit drift")
    if (root / "training" / "olmo").exists() or (root / "evaluations" / "olmo").exists():
        raise FileExistsError("OLMo scientific namespace is not absent")

    jobs: dict[str, str] = {}
    for job_id in ("453301", "453303", "453304"):
        state = run("squeue", "-h", "-j", job_id, "-o", "%T")
        if state != "PENDING":
            raise ValueError(f"Expected never-started PENDING job {job_id}, got {state!r}")
        jobs[job_id] = state

    checks = json.loads(json.dumps(prior["checks"]))
    for label in ("olmo", "falcon", "pythia"):
        item = candidate(registry, label)
        verify_sha(Path(item["base_model_manifest"]), item["base_model_manifest_sha256"])
        verify_sha(Path(item["base_general_summary"]), item["base_general_summary_sha256"])
        template = (repo_root / item["training_template"]).resolve()
        checks[f"candidate:{label}"] = {
            "model_manifest": item["base_model_manifest"],
            "model_manifest_sha256": item["base_model_manifest_sha256"],
            "base_general_summary": item["base_general_summary"],
            "base_general_summary_sha256": item["base_general_summary_sha256"],
            "template": str(template),
            "template_sha256": sha256_file(template),
        }
    policy = registry["home_storage_policy"]
    if bool(policy["home_write_allowed"]) or bool(policy["recursive_du_per_stage"]):
        raise ValueError("No-home-write policy drift")
    usage = shutil.disk_usage(root)
    stat = os.statvfs(root)
    reserve = int(registry["reserve_gib"]) * 1024**3
    if usage.free < reserve or stat.f_favail < int(registry["reserve_inodes"]):
        raise ValueError("Scratch capacity/inode relocation gate failed")

    payload = json.loads(json.dumps(prior))
    payload.update(
        status="PASS",
        timestamp=datetime.now(UTC).isoformat(),
        expected_commit=args.expected_commit,
        registry=str(registry_path),
        registry_sha256=sha256_file(registry_path),
        predecessor_preflight=str(previous),
        predecessor_preflight_sha256=args.previous_sha256,
        relocation_scope="document_159a_olmo_rtx3090_fp16_microbatch4_accumulation125",
        protected_pending_jobs=jobs,
        root_absent_before_preflight=False,
        root_reused_from_authorized_wave=str(root),
        checks=checks,
        retry_scratch_free_bytes=usage.free,
        retry_scratch_available_inodes=stat.f_favail,
    )
    write_json(output, payload)
    print(output)


if __name__ == "__main__":
    main()
