#!/usr/bin/env python3
"""Hash-close all six completed M2 training runs for later eval-v2 binding."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.pipeline.m2_training_outputs import finalize_m2_training_outputs
from transfer_vs_relearning.utils.io import sha256_file, write_json


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config_manifest.resolve()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"Fresh M2 binding root already exists: {output}")
    config = _json(config_path)
    entries = config.get("entries")
    if config.get("status") != "M2_TRAINING_CONFIGS_PREPARED_NOT_AUTHORIZED" or not isinstance(entries, list) or len(entries) != 6:
        raise ValueError("Exact six-entry M2 config family is absent")
    output.mkdir(parents=True)
    results = []
    for row in sorted(entries, key=lambda value: (value["role"], value["arm"])):
        training_root = Path(str(row["output_root"])).resolve()
        runs = sorted(path for path in training_root.iterdir() if path.is_dir()) if training_root.is_dir() else []
        if len(runs) != 1:
            raise ValueError(f"Expected one completed M2 run for {row['role']}/{row['arm']}")
        binding_root = output / str(row["role"]) / str(row["arm"]).lower().replace("-", "_")
        result = finalize_m2_training_outputs(
            runs[0], binding_root, role=str(row["role"]), arm=str(row["arm"])
        )
        results.append(result)
    family = {
        "schema_version": 1,
        "status": "M2_TRAINING_FAMILY_BINDING_PASS",
        "config_manifest": str(config_path),
        "config_manifest_sha256": sha256_file(config_path),
        "run_count": 6,
        "checkpoint_count": 60,
        "results": results,
        "evaluation_contract_frozen": False,
        "evaluation_authorized": False,
        "ready_for_evaluation": False,
    }
    write_json(output / "family_manifest.json", family)
    print(output / "family_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
