#!/usr/bin/env python3
"""Fail-closed validation for a prepared six-run OSCAR M2 config family."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.training.clm import resolve_checkpoint_updates
from transfer_vs_relearning.utils.io import sha256_file, write_json


EXPECTED = {(role, arm) for role in ("olmo", "qwen", "smollm") for arm in ("M2-A", "M2-B")}
UPDATES = (76, 152, 229, 305, 381, 457, 533, 610, 686, 762)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest_path = args.config_manifest.resolve()
    manifest = _json(manifest_path)
    if manifest.get("status") != "M2_TRAINING_CONFIGS_PREPARED_NOT_AUTHORIZED":
        raise ValueError("Prepared M2 family status drift")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or len(entries) != 6:
        raise ValueError("Prepared M2 family must contain exactly six configs")
    identities = {(str(row["role"]), str(row["arm"])) for row in entries}
    if identities != EXPECTED:
        raise ValueError(f"Prepared M2 identity matrix drift: {sorted(identities)}")

    checked: list[dict[str, Any]] = []
    by_role: dict[str, list[dict[str, Any]]] = {}
    for row in entries:
        config_path = Path(str(row["config"])).resolve()
        if sha256_file(config_path) != row["config_sha256"]:
            raise ValueError(f"Config SHA-256 drift: {config_path}")
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        training = config["training"]
        metadata = config["metadata"]
        if (
            config["dataset"].get("pretokenized") is not True
            or training.get("loss_mode") != "full_sequence"
            or training.get("block_size") != 512
            or training.get("max_steps") != 762
            or training.get("per_device_train_batch_size")
            * training.get("gradient_accumulation_steps")
            != 128
            or training.get("learning_rate") != 1e-5
            or training.get("bf16") is not True
            or training.get("fp16") is not False
            or metadata.get("scientific_execution_authorized") is not False
        ):
            raise ValueError(f"Frozen M2 recipe drift: {row['role']} / {row['arm']}")
        if resolve_checkpoint_updates(training, 762) != UPDATES:
            raise ValueError("M2 checkpoint schedule drift")
        for field, sha_field in (
            ("train_file", "train_sha256"),
            ("validation_file", "validation_sha256"),
            ("model_manifest", "model_manifest_sha256"),
        ):
            path = Path(str(row[field])).resolve()
            if not path.is_file() or path.is_symlink() or sha256_file(path) != row[sha_field]:
                raise ValueError(f"Prepared M2 input drift: {field} / {path}")
        by_role.setdefault(str(row["role"]), []).append(row)
        checked.append({"role": row["role"], "arm": row["arm"], "config_sha256": row["config_sha256"]})

    for role, pair in by_role.items():
        if (
            len(pair) != 2
            or len({row["validation_sha256"] for row in pair}) != 1
            or len({row["model_manifest_sha256"] for row in pair}) != 1
            or len({row["train_sha256"] for row in pair}) != 2
        ):
            raise ValueError(f"{role}: sibling parent/validation identity or train separation failed")
    result = {
        "schema_version": 1,
        "status": "M2_TRAINING_CONFIG_VALIDATION_PASS",
        "config_manifest": str(manifest_path),
        "config_manifest_sha256": sha256_file(manifest_path),
        "identities": sorted(f"{role}/{arm}" for role, arm in identities),
        "checks": checked,
        "training_authorized": False,
        "ready_to_train": False,
    }
    if args.output:
        write_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
