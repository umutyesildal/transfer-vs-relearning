#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file, write_json


REQUIRED_ARMS = ("m2_clean", "m3_fact")
REQUIRED_PARAMETERS = (
    "block_size",
    "update_steps",
    "fact_cycles",
    "learning_rate",
    "per_device_train_batch_size",
    "per_device_eval_batch_size",
    "gradient_accumulation_steps",
    "warmup_steps",
    "save_steps",
    "eval_steps",
)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.resolve().read_text(encoding="utf-8"))


def _yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_yaml_scalar(item) for item in value) + "]"
    return json.dumps(str(value), ensure_ascii=False)


def _yaml_config(
    *,
    label: str,
    arm: str,
    seed: int,
    training_seed: int,
    data_seed: int,
    base_model_manifest: Path,
    block_manifest: Path,
    dataset_dir: Path,
    train_file: Path,
    validation_file: Path,
    output_root: Path,
    parameters: dict[str, Any],
) -> str:
    rows = [
        "dataset:",
        f"  version: {_yaml_scalar('qwen_m2_m3_pretokenized_v1')}",
        f"  dataset_dir: {_yaml_scalar(dataset_dir)}",
        f"  dataset_manifest: {_yaml_scalar(block_manifest)}",
        f"  train_file: {_yaml_scalar(train_file)}",
        f"  validation_file: {_yaml_scalar(validation_file)}",
        "  pretokenized: true",
        "  text_field: text",
        "  split_seed: 42",
        "model:",
        f"  base_model_manifest: {_yaml_scalar(base_model_manifest)}",
        "training:",
        f"  run_name: {_yaml_scalar(label)}",
        f"  output_root: {_yaml_scalar(output_root)}",
        f"  block_size: {_yaml_scalar(parameters['block_size'])}",
        f"  learning_rate: {_yaml_scalar(parameters['learning_rate'])}",
        "  num_train_epochs: 1.0",
        f"  max_steps: {_yaml_scalar(parameters['update_steps'])}",
        f"  per_device_train_batch_size: {_yaml_scalar(parameters['per_device_train_batch_size'])}",
        f"  per_device_eval_batch_size: {_yaml_scalar(parameters['per_device_eval_batch_size'])}",
        f"  gradient_accumulation_steps: {_yaml_scalar(parameters['gradient_accumulation_steps'])}",
        f"  warmup_steps: {_yaml_scalar(parameters['warmup_steps'])}",
        f"  weight_decay: {_yaml_scalar(parameters.get('weight_decay', 0.0))}",
        f"  lr_scheduler_type: {_yaml_scalar(parameters.get('lr_scheduler_type', 'constant_with_warmup'))}",
        "  loss_mode: full_sequence",
        f"  bf16: {_yaml_scalar(parameters.get('bf16', True))}",
        f"  fp16: {_yaml_scalar(parameters.get('fp16', False))}",
        f"  gradient_checkpointing: {_yaml_scalar(parameters.get('gradient_checkpointing', True))}",
        f"  max_grad_norm: {_yaml_scalar(parameters.get('max_grad_norm', 1.0))}",
        f"  logging_steps: {_yaml_scalar(parameters.get('logging_steps', 4))}",
        f"  save_steps: {_yaml_scalar(parameters['save_steps'])}",
        f"  eval_steps: {_yaml_scalar(parameters['eval_steps'])}",
        f"  save_total_limit: {_yaml_scalar(parameters.get('save_total_limit', 6))}",
        f"  seed: {_yaml_scalar(training_seed)}",
        f"  data_seed: {_yaml_scalar(data_seed)}",
        "runtime:",
        "  local_files_only: true",
        "  world_size: 1",
        "metadata:",
        f"  arm: {_yaml_scalar(arm)}",
        f"  m1_seed: {_yaml_scalar(seed)}",
        f"  fact_cycles: {_yaml_scalar(parameters['fact_cycles'])}",
    ]
    return "\n".join(rows) + "\n"


def _require_scratch(path: Path, *, allow_local: bool, label: str) -> None:
    resolved = path.resolve()
    if allow_local:
        return
    if str(resolved) != "/vol/tmp" and not str(resolved).startswith("/vol/tmp/") and str(resolved) != "/vol/tmp2" and not str(resolved).startswith("/vol/tmp2/"):
        raise ValueError(f"{label} must resolve under /vol/tmp or /vol/tmp2: {resolved}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize four matched Qwen M2/M3 training configs from a frozen CPU contract."
    )
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--allow-local-paths", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = _json(contract_path)
    if contract.get("status") != "frozen":
        raise ValueError("M2/M3 training contract must have status=frozen")
    parameters = dict(contract.get("parameters", {}))
    missing = [key for key in REQUIRED_PARAMETERS if key not in parameters]
    if missing:
        raise ValueError(f"Frozen contract is missing parameters: {missing}")
    if any(int(parameters[key]) <= 0 for key in ("block_size", "update_steps", "fact_cycles", "per_device_train_batch_size", "per_device_eval_batch_size", "gradient_accumulation_steps", "warmup_steps", "save_steps", "eval_steps")):
        raise ValueError("Block, dose, update, batch, warmup, and checkpoint parameters must be positive")

    block_manifest_path = Path(str(contract["block_manifest"])).resolve()
    block_manifest = _json(block_manifest_path)
    audit = dict(block_manifest.get("audit", {}))
    if audit:
        if int(audit.get("block_size", -1)) != int(parameters["block_size"]):
            raise ValueError("Frozen block size does not match the M2/M3 execution contract")
        if int(audit.get("fact_cycles", -1)) != int(parameters["fact_cycles"]):
            raise ValueError("Frozen fact_cycles does not match the materialized M2/M3 blocks")
        if not audit.get("m2_m3_block_count_equal") or not audit.get("m2_m3_token_budget_equal"):
            raise ValueError("Materialized M2/M3 blocks do not have matched budgets")
    artifacts = block_manifest.get("artifacts", {})
    for key in ("m2_train", "m3_train", "shared_validation"):
        if key not in artifacts:
            raise ValueError(f"Block manifest is missing artifact {key}")
    artifact_paths = {
        key: Path(str(artifacts[key]["path"])).resolve()
        for key in ("m2_train", "m3_train", "shared_validation")
    }
    if not all(path.is_file() for path in artifact_paths.values()):
        raise FileNotFoundError("Frozen M2/M3 block manifest references a missing artifact")
    for key, path in artifact_paths.items():
        declared = str(artifacts[key].get("sha256", ""))
        if declared and sha256_file(path) != declared:
            raise ValueError(f"M2/M3 block artifact hash mismatch: {key}")
    dataset_dir = block_manifest_path.parent
    output_root = Path(str(contract["training_output_root"])).resolve()
    _require_scratch(output_root, allow_local=args.allow_local_paths, label="training_output_root")
    for label, path in artifact_paths.items():
        _require_scratch(path, allow_local=args.allow_local_paths, label=label)
    models = contract.get("models")
    if not isinstance(models, list) or len(models) != 2:
        raise ValueError("Frozen contract must contain exactly two model entries")
    by_seed = {int(item["seed"]): item for item in models}
    if set(by_seed) != {42, 43}:
        raise ValueError(f"Frozen contract model seeds must be 42 and 43: {sorted(by_seed)}")

    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite config family: {output_dir}")
    configs_dir = output_dir / "configs"
    configs_dir.mkdir(parents=True)
    entries: list[dict[str, Any]] = []
    for seed in (42, 43):
        model = by_seed[seed]
        base_manifest = Path(str(model["base_model_manifest"])).resolve()
        if not base_manifest.is_file():
            raise FileNotFoundError(base_manifest)
        training_seed = int(model["training_seed"])
        data_seed = int(model["data_seed"])
        for arm in REQUIRED_ARMS:
            label = f"{arm}_seed{seed}"
            train_file = artifact_paths["m2_train" if arm == "m2_clean" else "m3_train"]
            config_path = configs_dir / f"{label}.yaml"
            output_path = output_root / label
            config_path.write_text(
                _yaml_config(
                    label=label,
                    arm=arm,
                    seed=seed,
                    training_seed=training_seed,
                    data_seed=data_seed,
                    base_model_manifest=base_manifest,
                    block_manifest=block_manifest_path,
                    dataset_dir=dataset_dir,
                    train_file=train_file,
                    validation_file=artifact_paths["shared_validation"],
                    output_root=output_path,
                    parameters=parameters,
                ),
                encoding="utf-8",
            )
            entries.append(
                {
                    "label": label,
                    "arm": arm,
                    "seed": seed,
                    "training_seed": training_seed,
                    "data_seed": data_seed,
                    "config": str(config_path),
                    "config_sha256": sha256_file(config_path),
                    "base_model_manifest": str(base_manifest),
                    "train_file": str(train_file),
                    "validation_file": str(artifact_paths["shared_validation"]),
                    "output_root": str(output_path),
                }
            )
    manifest = {
        "status": "prepared",
        "version": "qwen_m2_m3_training_family_v1",
        "contract": str(contract_path),
        "contract_sha256": sha256_file(contract_path),
        "block_manifest": str(block_manifest_path),
        "block_manifest_sha256": sha256_file(block_manifest_path),
        "parameters": parameters,
        "configs": entries,
        "matched": {
            "arms": list(REQUIRED_ARMS),
            "seeds": [42, 43],
            "same_block_size": True,
            "same_update_steps": True,
            "same_validation_file": len({item["validation_file"] for item in entries}) == 1,
            "same_fact_cycles": True,
        },
    }
    write_json(output_dir / "config_manifest.json", manifest)
    print(output_dir / "config_manifest.json")


if __name__ == "__main__":
    main()
