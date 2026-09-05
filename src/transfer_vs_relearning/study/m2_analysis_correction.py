from __future__ import annotations

"""CPU-only, append-only correction of the completed M2 endpoint bootstrap."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.study.m2_eval_executor import analyze_complete_wave
from transfer_vs_relearning.utils.io import sha256_file, write_json


AUTHORIZATION_ACK = "exact_sha_bound_user_authorization_received"


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML mapping required: {path}")
    return payload


def _verify_regular(path: Path, expected_sha256: str, expected_bytes: int, label: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Correction input is not a regular file: {label} / {path}")
    if path.stat().st_size != expected_bytes or sha256_file(path) != expected_sha256:
        raise ValueError(f"Correction input drift: {label} / {path}")


def _verify_source(config: dict[str, Any]) -> list[dict[str, Any]]:
    source_root = Path(config["source_root"])
    registry_link = source_root / "control/m1_parent_factual_registry.json"
    if registry_link.resolve() != Path(config["source_registry_resolved_path"]):
        raise ValueError("M1 parent factual registry binding drift")
    family_path = source_root / "control/evaluation_family_result.json"
    family = json.loads(family_path.read_text(encoding="utf-8"))
    tasks = family.get("tasks", [])
    if (
        family.get("status") != "M2_EVAL_V2_COMPLETE"
        or family.get("gpu_complete_count") != 63
        or family.get("gpu_task_count") != 63
        or len(tasks) != 63
        or sorted(int(row["task_index"]) for row in tasks) != list(range(63))
        or any(row.get("status") != "complete" for row in tasks)
    ):
        raise ValueError("Source M2 evaluation family is not exactly 63/63 complete")
    for row in tasks:
        path = Path(row["path"])
        if not path.is_file() or sha256_file(path) != row["sha256"]:
            raise ValueError(f"Source task result drift: {row['task_index']} / {path}")

    observed: list[dict[str, Any]] = []
    for row in config["inputs"]:
        path = Path(row["path"])
        _verify_regular(path, row["sha256"], int(row["bytes"]), row["label"])
        observed.append(
            {
                "label": row["label"],
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return observed


def _check_expected_results(analysis: dict[str, Any], config: dict[str, Any]) -> None:
    for role, expected in config["expected_corrected_relearning"].items():
        actual = analysis["roles"][role]["relearning_m2b_minus_m2a_tr_to_en"]
        for key in ("estimate", "ci95_low", "ci95_high"):
            if abs(float(actual[key]) - float(expected[key])) > 1e-12:
                raise ValueError(f"Corrected bootstrap result drift: {role}/{key}")
        if analysis["roles"][role]["all_primary_gates_pass"] is not False:
            raise ValueError(f"Unexpected corrected primary-gate result: {role}")
    for role, expected in config["expected_corrected_transfer"].items():
        actual = analysis["roles"][role]["transfer_m2a_minus_m1_tr_to_en"]
        for key in ("estimate", "ci95_low", "ci95_high"):
            if abs(float(actual[key]) - float(expected[key])) > 1e-12:
                raise ValueError(f"Corrected transfer result drift: {role}/{key}")


def run(
    *,
    repo_root: Path,
    config_path: Path,
    contract_path: Path,
    contract_sha256: str,
    expected_commit: str,
    authorization_ack: str,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    config_path = config_path.resolve()
    contract_path = contract_path.resolve()
    if authorization_ack != AUTHORIZATION_ACK:
        raise PermissionError("Missing exact SHA-bound user authorization")
    if sha256_file(contract_path) != contract_sha256:
        raise ValueError("Correction contract SHA-256 drift")
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip() != expected_commit:
        raise ValueError("Correction execution commit drift")
    if subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=repo_root, text=True).strip():
        raise ValueError("Correction checkout is not clean")

    config = _load_yaml(config_path)
    if config.get("status") != "frozen_unexecuted" or config.get("execution_authorized") is not False:
        raise ValueError("Correction config lifecycle drift")
    source_root = Path(config["source_root"])
    output_root = Path(config["output_root"])
    if output_root.is_symlink() or output_root.resolve() != output_root:
        raise FileExistsError("Correction output root must be scratch-resolved")
    if output_root.exists():
        allowed_directories = {"control", "logs", "tmp"}
        if {path.name for path in output_root.iterdir()} - allowed_directories:
            raise FileExistsError("Correction output root contains unexpected entries")
        for name in allowed_directories:
            path = output_root / name
            if not path.is_dir() or path.is_symlink():
                raise FileExistsError("Correction output skeleton drift")
        control_files = {path.name for path in (output_root / "control").iterdir()}
        if control_files - {"submission_result.json"}:
            raise FileExistsError("Correction control directory is not fresh")
    if source_root == output_root or output_root.is_relative_to(source_root):
        raise ValueError("Correction output cannot be inside the immutable source root")
    filesystem = os.statvfs(output_root.parent)
    if filesystem.f_bavail * filesystem.f_frsize < int(config["storage"]["minimum_free_bytes"]):
        raise ValueError("Correction storage byte gate failed")
    if filesystem.f_favail < int(config["storage"]["minimum_free_inodes"]):
        raise ValueError("Correction storage inode gate failed")

    before = _verify_source(config)
    matrix = json.loads((source_root / "control/task_matrix.json").read_text(encoding="utf-8"))
    if Path(matrix["output_root"]) != source_root:
        raise ValueError("Source task matrix output root drift")
    analysis = analyze_complete_wave(matrix)
    _check_expected_results(analysis, config)
    after = _verify_source(config)
    if before != after:
        raise ValueError("Source inputs changed during correction")

    if not output_root.exists():
        output_root.mkdir()
        for name in ("control", "logs", "tmp"):
            (output_root / name).mkdir()
    corrected = dict(analysis)
    corrected["correction"] = {
        "status": "M2_EVAL_V2_BOOTSTRAP_PROMPT_IDENTITY_CORRECTED",
        "supersedes_bootstrap_rows_sha256": config["executed_analysis_sha256"],
        "pairing_key": "probe_id",
        "subject_count": 100,
        "prompt_variants_per_fact": 8,
        "bootstrap_samples": 10_000,
        "bootstrap_seed": 42,
        "model_inference": False,
        "source_access": "read_only",
        "execution_commit": expected_commit,
    }
    write_json(output_root / "control/input_manifest.json", {"schema_version": 1, "inputs": before})
    write_json(output_root / "control/corrected_scientific_analysis.json", corrected)
    for name in ("input_manifest.json", "corrected_scientific_analysis.json"):
        if (output_root / "control" / name).stat().st_size > 1024**2:
            raise ValueError(f"Correction output size bound exceeded: {name}")
    audit = {
        "schema_version": 1,
        "status": "M2_EVAL_V2_ANALYSIS_CORRECTION_COMPLETE",
        "source_root": str(source_root),
        "output_root": str(output_root),
        "input_manifest_sha256": sha256_file(output_root / "control/input_manifest.json"),
        "corrected_analysis_sha256": sha256_file(output_root / "control/corrected_scientific_analysis.json"),
        "source_inputs_unchanged": True,
        "gpu_used": False,
        "model_load_or_inference": False,
        "automatic_retry": False,
    }
    write_json(output_root / "control/final_audit.json", audit)
    return audit
