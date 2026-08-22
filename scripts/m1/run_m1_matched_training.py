#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import yaml

from transfer_vs_relearning.pipeline.m1_training_outputs import finalize_m1_training_outputs
from transfer_vs_relearning.training.clm import run_from_config
from transfer_vs_relearning.utils.io import sha256_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-manifest", type=Path, required=True)
    parser.add_argument("--model-index", type=int, required=True)
    parser.add_argument("--family-root", type=Path, required=True)
    parser.add_argument("--binding-root", type=Path, required=True)
    args = parser.parse_args()
    preflight = json.loads(args.preflight_manifest.read_text())
    if preflight.get("status") != "passed" or not 0 <= args.model_index < 3:
        raise ValueError("invalid M1 preflight/index")
    if subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() != preflight["git_commit"]:
        raise ValueError("checkout changed after M1 preflight")
    row = preflight["configs"][args.model_index]
    source_config = Path(row["path"])
    if sha256_file(source_config) != row["sha256"] or sha256_file(Path(row["model_manifest"])) != row["model_manifest_sha256"]:
        raise ValueError("M1 config/model binding changed")
    payload = yaml.safe_load(source_config.read_text())
    label = ("olmo", "qwen", "smollm")[args.model_index]
    payload["training"]["output_root"] = str(args.family_root.resolve() / "training" / label)
    config = args.family_root / "control" / "resolved_configs" / f"{label}.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    if config.exists():
        raise FileExistsError(config)
    config.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    run_dir = run_from_config(config)
    result = finalize_m1_training_outputs(run_dir, args.binding_root)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
