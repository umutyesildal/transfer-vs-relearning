#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from transfer_vs_relearning.training.clm import estimate_optimizer_steps, load_training_config, resolve_path
from transfer_vs_relearning.utils.io import count_lines, sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze a matched M1 form-generalization launch manifest.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--condition", choices=("control", "balanced_ab"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    config_path = args.config.resolve()
    config = load_training_config(config_path)
    dataset = config["dataset"]
    training = config["training"]
    train_path = resolve_path(repo_root, dataset["train_file"]).resolve()
    validation_path = resolve_path(repo_root, dataset["validation_file"]).resolve()
    dataset_manifest_path = resolve_path(repo_root, dataset["dataset_manifest"]).resolve()
    manifest = json.loads(dataset_manifest_path.read_text(encoding="utf-8"))
    condition_data = manifest.get("conditions", {}).get(args.condition)
    if manifest.get("status") != "passed" or not condition_data or condition_data.get("status") != "passed":
        raise ValueError("Dataset manifest is not an approved form-generalization condition")
    if count_lines(train_path) != 3500 or count_lines(validation_path) != 500:
        raise ValueError("Matched form-generalization row budget is not 3,500/500")
    if int(training["seed"]) != 42 or int(training["data_seed"]) != 42:
        raise ValueError("This launcher only freezes the seed-42 discovery contract")
    if bool(training["supervise_eos"]):
        raise ValueError("Form-generalization remediation requires supervise_eos: false")
    steps = estimate_optimizer_steps(3500, int(training["per_device_train_batch_size"]), int(training["gradient_accumulation_steps"]), float(training["num_train_epochs"]), int(config["runtime"].get("world_size", 1)))
    if steps != 252:
        raise ValueError(f"Expected 252 updates, found {steps}")
    output_root = Path(training["output_root"]).resolve()
    if not str(output_root).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")):
        raise ValueError(f"Output is not approved scratch: {output_root}")
    payload = {
        "status": "frozen_ready_to_launch",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "condition": args.condition,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "dataset_manifest_path": str(dataset_manifest_path),
        "dataset_manifest_sha256": sha256_file(dataset_manifest_path),
        "train_path": str(train_path),
        "train_sha256": sha256_file(train_path),
        "validation_path": str(validation_path),
        "validation_sha256": sha256_file(validation_path),
        "expected_optimizer_steps": steps,
        "output_root": str(output_root),
        "expected_checkpoint_count_upper_bound": 11,
        "estimated_condition_bytes_upper_bound": 225000000000,
        "retention": "freeze selected endpoint and compact evidence; intermediates remain scratch cleanup candidates",
    }
    write_json(args.output.resolve(), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
