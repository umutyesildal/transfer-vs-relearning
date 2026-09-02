#!/usr/bin/env python3
"""Verify immutable completed M2 runs and rebuild bindings with numeric checkpoint order."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.utils.io import sha256_file, write_json


UPDATES = (76, 152, 229, 305, 381, 457, 533, 610, 686, 762)


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON mapping required: {path}")
    return payload


def _verify(path: Path, expected: str, label: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing or unsafe {label}: {path}")
    observed = sha256_file(path)
    if observed != expected:
        raise ValueError(f"SHA-256 drift for {label}: {observed} != {expected}")
    return {"label": label, "path": str(path), "sha256": observed, "bytes": path.stat().st_size}


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
        raise ValueError("Finalizer repair config is not frozen/pre-authorization")
    authority = config.get("authority", {})
    if not (
        authority.get("checkpoint_model_file_read_for_hash_only") is True
        and authority.get("parent_model_read") is False
        and authority.get("model_load_or_inference") is False
        and authority.get("training") is False
        and authority.get("evaluation_or_scoring") is False
    ):
        raise ValueError("Finalizer repair authority boundary drift")
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip() != args.expected_commit:
        raise ValueError("Repository commit drift")
    if subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=repo, text=True).strip():
        raise ValueError("Repository checkout is dirty")

    evidence = [_verify(contract_path, args.contract_sha256, "execution_contract")]
    source = Path(str(config["source"]["root"])).resolve()
    for label in ("config_manifest", "preflight_result", "submission_result", "failed_finalizer_stderr"):
        binding = config["source"][label]
        evidence.append(_verify(source / str(binding["path"]), str(binding["sha256"]), label))
    old_bindings = source / "bindings"
    if not old_bindings.is_dir() or any(old_bindings.iterdir()):
        raise ValueError("Failed finalizer binding root is not present-and-empty")
    if (source / "evaluation").exists():
        raise ValueError("Prior evaluation namespace unexpectedly exists")

    manifest_rows = []
    for label, binding in config["training_manifests"].items():
        path = source / str(binding["path"])
        evidence.append(_verify(path, str(binding["sha256"]), label))
        payload = _json(path)
        result = payload.get("result", {})
        run = path.parent
        expected = {str((run / "checkpoints" / f"checkpoint-{step}").resolve()) for step in UPDATES}
        observed = {str(Path(value).resolve()) for value in result.get("checkpoint_dirs", [])}
        if not (
            payload.get("status") == "complete"
            and result.get("estimated_optimizer_steps") == 762
            and tuple(result.get("checkpoint_updates", ())) == UPDATES
            and len(result.get("checkpoint_dirs", [])) == 10
            and observed == expected
            and all(Path(value).is_dir() for value in observed)
        ):
            raise ValueError(f"Completed ten-checkpoint training identity failed: {label}")
        manifest_rows.append({"label": label, "path": str(path), "sha256": sha256_file(path)})
    for label, binding in config["task_audits"].items():
        path = source / str(binding["path"])
        evidence.append(_verify(path, str(binding["sha256"]), label))
        audit = _json(path)
        if audit.get("status") != "TRAINING_TASK_PASS" or audit.get("exit_code") != 0:
            raise ValueError(f"Training task audit did not pass: {label}")

    output = Path(str(config["output"]["root"])).resolve()
    allowed = {"cache", "control", "logs", "tmp"}
    if not output.is_dir() or any(path.name not in allowed for path in output.iterdir()):
        raise ValueError("Repair root is absent or contains non-control content")
    bindings = Path(str(config["output"]["bindings"])).resolve()
    matrix = Path(str(config["output"]["evaluation_matrix"])).resolve()
    if bindings.exists() or matrix.exists():
        raise FileExistsError("Fresh repair binding/matrix output already exists")
    env = {**os.environ, "PYTHONPATH": f"{repo / 'src'}:{repo}"}
    subprocess.run(
        [sys.executable, str(repo / "scripts/m2/finalize_three_model_oscar_m2_training_family.py"),
         "--config-manifest", str(source / config["source"]["config_manifest"]["path"]),
         "--output-root", str(bindings)], check=True, env=env,
    )
    family = bindings / "family_manifest.json"
    subprocess.run(
        [sys.executable, str(repo / "scripts/m2/prepare_m2_oscar_eval_v2_matrix.py"),
         "--preparation-config", str(repo / "configs/evaluation/m2_oscar_three_model_eval_v2_preparation_v1.yaml"),
         "--training-family-manifest", str(family), "--repo-root", str(repo), "--output", str(matrix)],
        check=True, env=env,
    )
    family_payload = _json(family)
    matrix_payload = _json(matrix)
    if not (
        family_payload.get("status") == "M2_TRAINING_FAMILY_BINDING_PASS"
        and family_payload.get("run_count") == 6
        and family_payload.get("checkpoint_count") == 60
        and matrix_payload.get("status") == "M2_EVAL_V2_MATRIX_PREPARED_NOT_AUTHORIZED"
        and matrix_payload.get("task_count") == 60
        and matrix_payload.get("full_task_count") == 12
        and matrix_payload.get("unique_scientific_states") == 63
        and matrix_payload.get("evaluation_authorized") is False
        and matrix_payload.get("ready_to_evaluate") is False
    ):
        raise ValueError("Repaired binding/evaluation matrix terminal gate failed")
    result = {
        "schema_version": 1,
        "status": "M2_FINALIZER_NUMERIC_ORDER_REPAIR_PASS",
        "expected_commit": args.expected_commit,
        "contract_sha256": args.contract_sha256,
        "source_root": str(source),
        "source_mutated": False,
        "training_manifests": manifest_rows,
        "evidence": evidence,
        "run_count": 6,
        "checkpoint_count": 60,
        "family_manifest": str(family),
        "family_manifest_sha256": sha256_file(family),
        "evaluation_matrix": str(matrix),
        "evaluation_matrix_sha256": sha256_file(matrix),
        "evaluation_authorized": False,
        "ready_to_evaluate": False,
    }
    write_json(output / "control/final_audit.json", result)
    print(output / "control/final_audit.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
