#!/usr/bin/env python3
"""Build an execution-disabled 60-checkpoint M2 eval-v2 matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.utils.io import sha256_file, write_json


ROLES = ("olmo", "qwen", "smollm")
ARMS = ("M2-A", "M2-B")
UPDATES = (76, 152, 229, 305, 381, 457, 533, 610, 686, 762)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verify(path: Path, expected: str, label: str) -> None:
    if not path.is_file() or path.is_symlink() or sha256_file(path) != expected:
        raise ValueError(f"M2 eval-v2 input drift: {label} / {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preparation-config", type=Path, required=True)
    parser.add_argument("--training-family-manifest", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    preparation_path = args.preparation_config.resolve()
    family_path = args.training_family_manifest.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"Fresh M2 evaluation matrix already exists: {output}")
    preparation = yaml.safe_load(preparation_path.read_text(encoding="utf-8"))
    family = _json(family_path)
    if preparation.get("status") != "local_preparation_non_executable":
        raise ValueError("M2 evaluation preparation is not execution-disabled")
    if family.get("status") != "M2_TRAINING_FAMILY_BINDING_PASS":
        raise ValueError("Completed six-run M2 family binding is absent")
    for section in ("contract", "registry"):
        binding = preparation["protocol"]
        _verify(repo / binding[section], binding[f"{section}_sha256"], section)
    parent = preparation["m1_parent_projection"]
    _verify(repo / parent["source"], parent["source_sha256"], "m1_parent_projection")

    tasks: list[dict[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    for result in family.get("results", []):
        role, arm = str(result.get("role")), str(result.get("arm"))
        if (role, arm) in identities or role not in ROLES or arm not in ARMS:
            raise ValueError("M2 training family contains duplicate or invalid role/arm")
        identities.add((role, arm))
        manifest_path = Path(str(result["checkpoint_manifest"])).resolve()
        _verify(manifest_path, result["checkpoint_manifest_sha256"], f"{role}/{arm}")
        manifest = _json(manifest_path)
        checkpoints = manifest.get("checkpoints")
        if (
            manifest.get("status") != "M2_CHECKPOINT_BINDING_PASS"
            or not isinstance(checkpoints, list)
            or tuple(row.get("update") for row in checkpoints) != UPDATES
        ):
            raise ValueError(f"{role}/{arm}: checkpoint binding drift")
        for row in checkpoints:
            model_manifest = Path(str(row["model_manifest"])).resolve()
            _verify(model_manifest, row["model_manifest_sha256"], f"{role}/{arm}/{row['update']}")
            tasks.append(
                {
                    "task_index": len(tasks),
                    "state_id": f"{role}/{arm}/update-{int(row['update']):03d}",
                    "role": role,
                    "arm": arm,
                    "update": int(row["update"]),
                    "full": int(row["update"]) in {381, 762},
                    "model_manifest": str(model_manifest),
                    "model_manifest_sha256": row["model_manifest_sha256"],
                    "dense_bundles": preparation["matrix"]["dense_bundles"],
                    "full_bundles": (
                        preparation["matrix"]["full_bundles"]
                        if int(row["update"]) in {381, 762}
                        else []
                    ),
                }
            )
    if identities != {(role, arm) for role in ROLES for arm in ARMS}:
        raise ValueError("M2 evaluation matrix does not cover the six sibling runs")
    full_count = sum(bool(row["full"]) for row in tasks)
    if len(tasks) != 60 or full_count != 12:
        raise ValueError("M2 evaluation matrix must contain 60 dense and 12 full states")
    matrix = {
        "schema_version": 1,
        "status": "M2_EVAL_V2_MATRIX_PREPARED_NOT_AUTHORIZED",
        "preparation_config": str(preparation_path),
        "preparation_config_sha256": sha256_file(preparation_path),
        "training_family_manifest": str(family_path),
        "training_family_manifest_sha256": sha256_file(family_path),
        "m1_parent_projection": parent,
        "task_count": len(tasks),
        "full_task_count": full_count,
        "unique_scientific_states": len(tasks) + int(parent["state_count"]),
        "tasks": tasks,
        "execution_adapter_registered": False,
        "evaluation_authorized": False,
        "ready_to_evaluate": False,
    }
    write_json(output, matrix)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
