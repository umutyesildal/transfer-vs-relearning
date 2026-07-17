#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from transfer_vs_relearning.training.clm import estimate_optimizer_steps, load_training_config, resolve_path
from transfer_vs_relearning.utils.io import count_lines, sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze and verify a WP1B launch manifest.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    config_path = args.config.resolve()
    config = load_training_config(config_path)
    dataset = config["dataset"]
    training = config["training"]
    runtime = config["runtime"]
    train_path = resolve_path(repo_root, dataset["train_file"]).resolve()
    validation_path = resolve_path(repo_root, dataset["validation_file"]).resolve()
    dataset_manifest_path = resolve_path(repo_root, dataset["dataset_manifest"]).resolve()
    model_manifest_path = resolve_path(repo_root, config["model"]["base_model_manifest"]).resolve()
    model_manifest = json.loads(model_manifest_path.read_text(encoding="utf-8"))
    weights_path = Path(model_manifest["local_path_absolute"]) / "model.safetensors"
    live_weights_hash = sha256_file(weights_path)
    declared_weights_hash = model_manifest.get("file_hashes", {}).get("model.safetensors")
    if declared_weights_hash and live_weights_hash != declared_weights_hash:
        raise ValueError("Base model manifest weight hash does not match the live file")
    train_rows = count_lines(train_path)
    validation_rows = count_lines(validation_path)
    if (train_rows, validation_rows) != (3500, 500):
        raise ValueError(f"Unexpected WP1B row counts: train={train_rows} validation={validation_rows}")
    steps = estimate_optimizer_steps(
        train_blocks=train_rows,
        per_device_train_batch_size=int(training["per_device_train_batch_size"]),
        gradient_accumulation_steps=int(training["gradient_accumulation_steps"]),
        num_train_epochs=float(training["num_train_epochs"]),
        world_size=int(runtime.get("world_size", 1)),
    )
    resolved_output = Path(training["output_root"]).resolve()
    if not str(resolved_output).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")):
        raise ValueError(f"WP1B output is not on approved scratch: {resolved_output}")
    git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    manifest = {
        "status": "frozen_ready_to_launch",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "dataset_manifest_path": str(dataset_manifest_path),
        "dataset_manifest_sha256": sha256_file(dataset_manifest_path),
        "train_path": str(train_path),
        "train_sha256": sha256_file(train_path),
        "train_rows": train_rows,
        "validation_path": str(validation_path),
        "validation_sha256": sha256_file(validation_path),
        "validation_rows": validation_rows,
        "base_model_manifest_path": str(model_manifest_path),
        "base_model_manifest_sha256": sha256_file(model_manifest_path),
        "base_model_weights_path": str(weights_path),
        "base_model_weights_sha256": live_weights_hash,
        "output_root": str(resolved_output),
        "expected_optimizer_steps": steps,
        "expected_checkpoint_count_upper_bound": 11,
        "estimated_checkpoint_bytes_upper_bound": 20000000000,
        "estimated_condition_bytes_upper_bound": 225000000000,
        "retention": "freeze final model and compact evidence; removable intermediate checkpoints and optimizer state",
    }
    write_json(args.output.resolve(), manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
