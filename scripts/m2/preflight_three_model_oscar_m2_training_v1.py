#!/usr/bin/env python3
"""Fail-closed preflight for the frozen six-run OSCAR M2 training family."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.utils.io import sha256_file, write_json


ROLES = ("olmo", "qwen", "smollm")


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON mapping required: {path}")
    return payload


def _verify(path: Path, expected: str, label: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError(f"Missing or unsafe {label}: {path}")
    observed = sha256_file(path)
    if observed != expected:
        raise ValueError(f"SHA-256 drift for {label}: {observed} != {expected}")
    return {"path": str(path), "sha256": observed, "bytes": path.stat().st_size}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--contract-sha256", required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    config_path = args.config.resolve()
    contract_path = args.contract.resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if config.get("status") != "frozen_unexecuted" or config.get("execution_authorized") is not False:
        raise ValueError("Training config is not frozen/pre-authorization")
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip() != args.expected_commit:
        raise ValueError("Repository commit drift")
    if subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=repo, text=True).strip():
        raise ValueError("Repository checkout is dirty")
    evidence = [_verify(contract_path, args.contract_sha256, "execution contract")]
    for label, binding in config["inputs"].items():
        raw = Path(str(binding["path"]))
        path = raw if raw.is_absolute() else repo / raw
        evidence.append(_verify(path.resolve(), str(binding["sha256"]), label))
    readiness = _json(Path(str(config["inputs"]["readiness_final_audit"]["path"])))
    parents = _json(Path(str(config["inputs"]["parent_registry"]["path"])))
    blocks = _json(Path(str(config["inputs"]["corrected_block_manifest"]["path"])))
    review_path = Path(str(config["inputs"]["corrected_human_review_validation"]["path"]))
    if not review_path.is_absolute():
        review_path = repo / review_path
    review = _json(review_path.resolve())
    if readiness.get("status") != "EVIDENCE_PREPARED_AWAITING_FACT_REVIEW_AND_GPU_SMOKE":
        raise ValueError("Readiness predecessor status drift")
    if parents.get("status") != "EXACT_M1_PARENT_REGISTRY_PASS":
        raise ValueError("Parent registry status drift")
    if blocks.get("status") != "EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED":
        raise ValueError("Corrected block-family status drift")
    if not (
        review.get("status") == "M2_FACT_REVIEW_PASS"
        and review.get("human_review_complete") is True
        and review.get("rows") == 250
        and review.get("unique_fact_ids") == 250
        and review.get("verdicts") == {"usable": 250}
    ):
        raise ValueError("Corrected 250-fact human-review gate failed")

    corrected_sha = str(config["optimizer_smoke"]["corrected_block_manifest_sha256"])
    smoke_root = Path(str(config["optimizer_smoke"]["root"])).resolve()
    smoke_rows = []
    for role in ROLES:
        binding = config["optimizer_smoke"]["reports"][role]
        report_path = smoke_root / str(binding["path"])
        row = _verify(report_path, str(binding["sha256"]), f"{role} smoke report")
        report = _json(report_path)
        if not (
            report.get("status") == "OPTIMIZER_SMOKE_PASS"
            and config["optimizer_smoke"]["required_status"] == "OPTIMIZER_SMOKE_PASS"
            and report.get("role") == role
            and report.get("scientific_training") is False
            and report.get("checkpoint_written") is False
            and report.get("optimizer_steps") == 1
            and report.get("blocks_consumed") == 128
            and report.get("tokens_consumed") == 65536
            and report.get("block_family_manifest_sha256") == corrected_sha
        ):
            raise ValueError(f"{role}: optimizer smoke identity/status drift")
        smoke_rows.append({**row, "role": role, "status": report["status"]})

    root = Path(str(config["slurm"]["root"])).resolve()
    allowed = {"cache", "control", "logs", "tmp"}
    if not root.is_dir() or any(path.name not in allowed for path in root.iterdir()):
        raise ValueError("Training root is absent or contains non-control preflight content")
    usage = shutil.disk_usage(root)
    free_inodes = int(os.statvfs(root).f_favail)
    if usage.free < int(config["storage"]["minimum_free_bytes"]):
        raise ValueError("Live scratch free-byte gate failed")
    if free_inodes < int(config["storage"]["minimum_free_inodes"]):
        raise ValueError("Live scratch inode gate failed")

    preparation = repo / str(config["repository"]["preparation_config"])
    preparation_payload = yaml.safe_load(preparation.read_text(encoding="utf-8"))
    output_dir = Path(str(preparation_payload["output"]["config_root"])).resolve()
    training_root = Path(str(preparation_payload["output"]["training_root"])).resolve()
    block_manifest = Path(str(config["inputs"]["corrected_block_manifest"]["path"])).resolve()
    parent_registry = Path(str(config["inputs"]["parent_registry"]["path"])).resolve()
    env = {**os.environ, "PYTHONPATH": f"{repo / 'src'}:{repo}"}
    subprocess.run(
        [
            sys.executable,
            str(repo / "scripts/m2/prepare_three_model_oscar_m2_training_family.py"),
            "--plan", str(repo / config["repository"]["scientific_plan"]),
            "--preparation-config", str(preparation),
            "--block-manifest", str(block_manifest),
            "--parent-registry", str(parent_registry),
            "--output-dir", str(output_dir),
            "--training-output-root", str(training_root),
        ],
        check=True,
        env=env,
    )
    validation_path = root / "control/config_validation.json"
    subprocess.run(
        [
            sys.executable,
            str(repo / "scripts/m2/validate_three_model_oscar_m2_training_family.py"),
            "--config-manifest", str(output_dir / "config_manifest.json"),
            "--output", str(validation_path),
        ],
        check=True,
        env=env,
    )
    result = {
        "schema_version": 1,
        "status": "M2_SCIENTIFIC_TRAINING_PREFLIGHT_PASS",
        "expected_commit": args.expected_commit,
        "contract": str(contract_path),
        "contract_sha256": args.contract_sha256,
        "config": str(config_path),
        "config_sha256": sha256_file(config_path),
        "evidence": evidence,
        "smoke_reports": smoke_rows,
        "config_manifest": str(output_dir / "config_manifest.json"),
        "config_manifest_sha256": sha256_file(output_dir / "config_manifest.json"),
        "config_validation_sha256": sha256_file(validation_path),
        "live_free_bytes": usage.free,
        "live_free_inodes": free_inodes,
        "training_started": False,
        "ready_for_authorized_training_array": True,
    }
    write_json(root / "control/preflight_result.json", result)
    print(root / "control/preflight_result.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
