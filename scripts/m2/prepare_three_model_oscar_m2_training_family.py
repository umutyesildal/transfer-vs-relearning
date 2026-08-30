#!/usr/bin/env python3
"""Prepare six execution-disabled M2 configs from verified blocks and parent manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.utils.io import sha256_file, write_json


ROLES = ("olmo", "qwen", "smollm")
ARMS = ("M2-A", "M2-B")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _scratch(path: Path, *, allow_local: bool) -> None:
    value = str(path.resolve())
    if allow_local:
        return
    if not (value == "/vol/tmp2" or value.startswith("/vol/tmp2/")):
        raise ValueError(f"M2 generated artifact is not under /vol/tmp2: {value}")


def _verified_file(binding: dict[str, Any], label: str, *, allow_local: bool) -> Path:
    path = Path(str(binding["path"])).resolve()
    _scratch(path, allow_local=allow_local)
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing or unsafe {label}: {path}")
    if sha256_file(path) != str(binding["sha256"]):
        raise ValueError(f"SHA-256 drift for {label}: {path}")
    return path


def _training_config(
    *,
    role: str,
    arm: str,
    model_manifest: Path,
    block_manifest: Path,
    train_file: Path,
    validation_file: Path,
    output_root: Path,
    plan: dict[str, Any],
    preparation: dict[str, Any],
) -> dict[str, Any]:
    training = plan["training"]
    schedule = plan["checkpoint_and_evaluation"]
    checkpoints = [int(value) for value in schedule["model_only_snapshot_updates"]]
    decomposition = preparation["memory_decomposition_candidate"][role]
    return {
        "dataset": {
            "version": "m2_three_model_oscar_pretokenized_v1",
            "dataset_dir": str(train_file.parent),
            "dataset_manifest": str(block_manifest),
            "train_file": str(train_file),
            "validation_file": str(validation_file),
            "pretokenized": True,
            "text_field": "text",
            "split_seed": int(training["seed"]),
        },
        "model": {"base_model_manifest": str(model_manifest)},
        "training": {
            "run_name": f"m2_oscar_{role}_{arm.lower().replace('-', '_')}_seed42",
            "output_root": str(output_root),
            "block_size": int(training["sequence_length"]),
            "learning_rate": float(training["learning_rate"]),
            "num_train_epochs": 1.0,
            "max_steps": int(training["optimizer_updates"]),
            "per_device_train_batch_size": int(decomposition["per_device_train_batch_size"]),
            "per_device_eval_batch_size": 1,
            "gradient_accumulation_steps": int(decomposition["gradient_accumulation_steps"]),
            "warmup_steps": round(
                int(training["optimizer_updates"]) * float(training["warmup_ratio"])
            ),
            "weight_decay": float(training["weight_decay"]),
            "adam_beta1": float(training["adam_beta1"]),
            "adam_beta2": float(training["adam_beta2"]),
            "adam_epsilon": float(training["adam_epsilon"]),
            "lr_scheduler_type": str(training["scheduler"]),
            "loss_mode": "full_sequence",
            "model_load_dtype": "bfloat16",
            "bf16": True,
            "fp16": False,
            "gradient_checkpointing": bool(training["gradient_checkpointing"]),
            "optimizer_foreach": False,
            "max_grad_norm": float(training["max_grad_norm"]),
            "logging_steps": 5,
            "checkpoint_updates": checkpoints,
            "in_training_eval_updates": checkpoints,
            "save_total_limit": len(checkpoints),
            "seed": int(training["seed"]),
            "data_seed": int(training["data_seed"]),
        },
        "runtime": {"local_files_only": True, "world_size": 1},
        "metadata": {
            "schema_version": 1,
            "role": role,
            "arm": arm,
            "sibling_parent": "M1_epoch_036",
            "effective_blocks_per_update": 128,
            "effective_tokens_per_update": 65_536,
            "scientific_execution_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--preparation-config", type=Path, required=True)
    parser.add_argument("--block-manifest", type=Path, required=True)
    parser.add_argument("--parent-registry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--training-output-root", type=Path, required=True)
    parser.add_argument("--allow-local-paths", action="store_true")
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    training_root = args.training_output_root.resolve()
    _scratch(output_dir, allow_local=args.allow_local_paths)
    _scratch(training_root, allow_local=args.allow_local_paths)
    if output_dir.exists() or training_root.exists():
        raise FileExistsError("M2 config or training output root already exists")

    plan_path = args.plan.resolve()
    preparation_path = args.preparation_config.resolve()
    block_path = args.block_manifest.resolve()
    parent_path = args.parent_registry.resolve()
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    preparation = yaml.safe_load(preparation_path.read_text(encoding="utf-8"))
    blocks = _load_json(block_path)
    parents = _load_json(parent_path)
    if plan.get("status") != "design_frozen_non_executable":
        raise ValueError("M2 design plan is not frozen")
    if preparation.get("status") != "local_preparation_non_executable":
        raise ValueError("M2 training preparation config is not execution-disabled")
    if blocks.get("status") != "EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED":
        raise ValueError("Exact M2 block family is not materialized")
    if parents.get("status") != "EXACT_M1_PARENT_REGISTRY_PASS":
        raise ValueError("Exact M1 parent registry is incomplete")
    if set(blocks.get("models", {})) != set(ROLES) or set(parents.get("models", {})) != set(ROLES):
        raise ValueError("Block and parent registries must cover all three roles")

    output_dir.mkdir(parents=True)
    entries: list[dict[str, Any]] = []
    for role in ROLES:
        role_blocks = blocks["models"][role]
        if role_blocks.get("status") != "EXACT_MATCHED_BLOCKS_PASS":
            raise ValueError(f"{role}: matched block audit did not pass")
        matching = role_blocks.get("matching", {})
        if not (
            matching.get("m2_a_m2_b_block_count_equal")
            and matching.get("m2_a_m2_b_token_budget_equal")
            and matching.get("branch_a_fact_exposures") == 0
            and matching.get("extra_tokens_over_m2_a") == 0
        ):
            raise ValueError(f"{role}: matched causal budget invariant failed")
        model_manifest = _verified_file(
            parents["models"][role]["model_manifest"],
            f"{role} parent model manifest",
            allow_local=args.allow_local_paths,
        )
        validation = _verified_file(
            role_blocks["artifacts"]["shared_validation"],
            f"{role} validation blocks",
            allow_local=args.allow_local_paths,
        )
        for arm, artifact in (("M2-A", "m2_a_train"), ("M2-B", "m2_b_train")):
            train_file = _verified_file(
                role_blocks["artifacts"][artifact],
                f"{role} {arm} train blocks",
                allow_local=args.allow_local_paths,
            )
            config = _training_config(
                role=role,
                arm=arm,
                model_manifest=model_manifest,
                block_manifest=block_path,
                train_file=train_file,
                validation_file=validation,
                output_root=training_root / role / arm.lower().replace("-", "_"),
                plan=plan,
                preparation=preparation,
            )
            config_path = output_dir / f"{role}_{arm.lower().replace('-', '_')}.yaml"
            config_path.write_text(
                yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8"
            )
            entries.append(
                {
                    "role": role,
                    "arm": arm,
                    "config": str(config_path),
                    "config_sha256": sha256_file(config_path),
                    "train_file": str(train_file),
                    "train_sha256": sha256_file(train_file),
                    "validation_file": str(validation),
                    "validation_sha256": sha256_file(validation),
                    "model_manifest": str(model_manifest),
                    "model_manifest_sha256": sha256_file(model_manifest),
                    "output_root": str(config["training"]["output_root"]),
                }
            )
    manifest = {
        "schema_version": 1,
        "status": "M2_TRAINING_CONFIGS_PREPARED_NOT_AUTHORIZED",
        "plan": {"path": str(plan_path), "sha256": sha256_file(plan_path)},
        "preparation": {
            "path": str(preparation_path),
            "sha256": sha256_file(preparation_path),
        },
        "blocks": {"path": str(block_path), "sha256": sha256_file(block_path)},
        "parents": {"path": str(parent_path), "sha256": sha256_file(parent_path)},
        "entries": entries,
        "models": list(ROLES),
        "arms": list(ARMS),
        "training_authorized": False,
        "ready_to_train": False,
    }
    write_json(output_dir / "config_manifest.json", manifest)
    print(output_dir / "config_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
