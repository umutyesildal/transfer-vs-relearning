from __future__ import annotations

import inspect
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import count_lines, sha256_file, sha256_text, write_json


def load_training_config(path: Path) -> dict[str, Any]:
    config = _load_yaml_config(path)
    for section in ("dataset", "model", "training", "runtime"):
        if section not in config:
            raise ValueError(f"Missing required training config section: {section}")
    return config


def safe_run_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    cleaned = cleaned.strip("._-")
    return cleaned or "training_run"


def resolve_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def tokenizer_path_from_manifest(manifest: dict[str, Any], repo_root: Path, model_path: Path) -> Path:
    absolute = manifest.get("tokenizer_source_path_absolute")
    if absolute:
        return Path(str(absolute)).resolve()
    project_relative = manifest.get("tokenizer_source_path")
    if project_relative:
        return resolve_path(repo_root, str(project_relative)).resolve()
    return model_path


def estimate_optimizer_steps(
    train_blocks: int,
    per_device_train_batch_size: int,
    gradient_accumulation_steps: int,
    num_train_epochs: float,
    world_size: int = 1,
) -> int:
    if train_blocks <= 0:
        return 0
    effective_batch = per_device_train_batch_size * gradient_accumulation_steps * max(world_size, 1)
    steps_per_epoch = math.ceil(train_blocks / effective_batch)
    return math.ceil(steps_per_epoch * num_train_epochs)


def resolve_training_seeds(
    dataset_config: dict[str, Any],
    training_config: dict[str, Any],
) -> tuple[int, int, int]:
    seed = int(training_config.get("seed", 42))
    split_seed = int(dataset_config.get("split_seed", seed))
    data_seed = int(training_config.get("data_seed", split_seed))
    return seed, split_seed, data_seed


def resolve_model_load_dtype(torch_module: Any, training_config: dict[str, Any]) -> Any | None:
    value = training_config.get("model_load_dtype")
    if value is None:
        return None
    normalized = str(value).strip().lower()
    supported = {
        "bfloat16": torch_module.bfloat16,
        "float16": torch_module.float16,
        "float32": torch_module.float32,
    }
    if normalized not in supported:
        raise ValueError(f"Unsupported model_load_dtype: {value!r}")
    return supported[normalized]


def interval_from_fractions(total_steps: int, fractions: list[float]) -> int:
    if total_steps <= 1:
        return 1
    valid = sorted(fraction for fraction in fractions if 0 < fraction <= 1)
    if not valid:
        return max(1, total_steps // 4)
    first = valid[0]
    return max(1, round(total_steps * first))


def _answer_char_span(text: str, answer: str) -> tuple[int, int]:
    start = text.rfind(answer)
    if start < 0:
        raise ValueError(f"Answer text {answer!r} not found in training row")
    return start, start + len(answer)


def _token_label_mask_from_offsets(
    offsets: list[tuple[int, int]],
    *,
    answer_start: int,
    answer_end: int,
) -> list[bool]:
    mask: list[bool] = []
    seen_answer_token = False
    for token_start, token_end in offsets:
        overlaps = token_end > answer_start and token_start < answer_end
        if overlaps:
            seen_answer_token = True
        mask.append(overlaps)
    if not seen_answer_token:
        raise ValueError("Could not align any answer tokens for answer-only loss")
    return mask


def _answer_only_labels(
    input_ids: list[int],
    label_mask: list[bool],
    eos_token_id: int,
    *,
    supervise_eos: bool,
) -> list[int]:
    if len(input_ids) != len(label_mask):
        raise ValueError("Answer-only input IDs and label mask must have equal length")
    labels = [
        token_id if keep else -100
        for token_id, keep in zip(input_ids, label_mask, strict=True)
    ]
    labels.append(eos_token_id if supervise_eos else -100)
    return labels


def run_from_config(config_path: Path, repo_root: Path | None = None) -> Path:
    repo_root = (repo_root or Path.cwd()).resolve()
    config_path = config_path.resolve()
    config = load_training_config(config_path)
    config_hash = sha256_text(json.dumps(config, ensure_ascii=False, sort_keys=True))
    training_config = config["training"]
    run_name = safe_run_name(str(training_config.get("run_name", config_path.stem)))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_root = resolve_path(repo_root, training_config["output_root"])
    run_dir = output_root / f"{timestamp}_{run_name}_{config_hash[:8]}"
    if run_dir.exists():
        raise FileExistsError(f"Training run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    _write_initial_manifest(config, config_path, config_hash, repo_root, run_dir)
    train_result = _run_hf_training(config, repo_root, run_dir)
    _write_final_manifest(config, config_path, config_hash, repo_root, run_dir, train_result)
    return run_dir


def _write_initial_manifest(
    config: dict[str, Any],
    config_path: Path,
    config_hash: str,
    repo_root: Path,
    run_dir: Path,
) -> None:
    dataset = config["dataset"]
    model = config["model"]
    train_file = resolve_path(repo_root, dataset["train_file"])
    dataset_manifest = resolve_path(repo_root, dataset["dataset_manifest"])
    model_manifest = resolve_path(repo_root, model["base_model_manifest"])
    payload = {
        "status": "started",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path),
        "config_sha256": config_hash,
        "config": config,
        "repo_root": str(repo_root),
        "git_commit": _git_commit(repo_root),
        "dataset": {
            "train_file": str(train_file),
            "train_file_sha256": sha256_file(train_file),
            "train_rows": count_lines(train_file),
            "dataset_manifest": str(dataset_manifest),
            "dataset_manifest_sha256": sha256_file(dataset_manifest),
        },
        "model": {
            "base_model_manifest": str(model_manifest),
            "base_model_manifest_sha256": sha256_file(model_manifest),
            "base_model_manifest_payload": _read_json(model_manifest),
        },
    }
    validation_file_value = dataset.get("validation_file")
    if validation_file_value:
        validation_file = resolve_path(repo_root, validation_file_value)
        payload["dataset"]["validation_file"] = str(validation_file)
        payload["dataset"]["validation_file_sha256"] = sha256_file(validation_file)
        payload["dataset"]["validation_rows"] = count_lines(validation_file)
    write_json(run_dir / "training_manifest.json", payload)


def _write_final_manifest(
    config: dict[str, Any],
    config_path: Path,
    config_hash: str,
    repo_root: Path,
    run_dir: Path,
    train_result: dict[str, Any],
) -> None:
    manifest_path = run_dir / "training_manifest.json"
    payload = _read_json(manifest_path)
    payload.update(
        {
            "status": "complete",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "result": train_result,
            "config_path": str(config_path),
            "config_sha256": config_hash,
            "git_commit": _git_commit(repo_root),
            "config": config,
        }
    )
    write_json(manifest_path, payload)


def _run_hf_training(config: dict[str, Any], repo_root: Path, run_dir: Path) -> dict[str, Any]:
    import datasets
    import torch
    import transformers
    from datasets import load_dataset
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        Trainer,
        TrainingArguments,
        default_data_collator,
        set_seed,
    )

    dataset_config = config["dataset"]
    model_config = config["model"]
    training_config = config["training"]
    runtime_config = config["runtime"]

    seed, split_seed, data_seed = resolve_training_seeds(dataset_config, training_config)
    set_seed(seed)

    model_manifest = _read_json(resolve_path(repo_root, model_config["base_model_manifest"]))
    model_path = Path(model_manifest["local_path_absolute"])
    tokenizer_path = tokenizer_path_from_manifest(model_manifest, repo_root, model_path)
    local_files_only = bool(runtime_config.get("local_files_only", True))
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=local_files_only, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model_load_dtype = resolve_model_load_dtype(torch, training_config)
    model_kwargs: dict[str, Any] = {"local_files_only": local_files_only}
    if model_load_dtype is not None:
        model_kwargs["torch_dtype"] = model_load_dtype
    model = AutoModelForCausalLM.from_pretrained(str(model_path), **model_kwargs)
    if bool(training_config.get("gradient_checkpointing", False)):
        model.config.use_cache = False

    train_file = resolve_path(repo_root, dataset_config["train_file"])
    text_field = str(dataset_config.get("text_field", "text"))
    validation_fraction = float(dataset_config.get("validation_fraction", 0.02))
    block_size = int(training_config.get("block_size", min(tokenizer.model_max_length, 512)))
    loss_mode = str(training_config.get("loss_mode", "full_sequence"))

    validation_file_value = dataset_config.get("validation_file")
    if validation_file_value:
        validation_file = resolve_path(repo_root, validation_file_value)
        loaded = load_dataset(
            "json",
            data_files={"train": str(train_file), "test": str(validation_file)},
        )
        raw_split = loaded
    else:
        raw = load_dataset("json", data_files=str(train_file), split="train")
        raw_split = raw.train_test_split(test_size=validation_fraction, seed=split_seed, shuffle=True)

    columns = raw_split["train"].column_names
    for split_name in ("train", "test"):
        if text_field not in raw_split[split_name].column_names:
            raise ValueError(f"Text field {text_field!r} not found in {split_name} dataset")
        if raw_split[split_name].column_names != columns:
            raise ValueError("Training and validation datasets must have the same columns")

    if loss_mode == "answer_only":
        answer_field = str(dataset_config.get("answer_field", "answer"))
        supervise_eos = bool(training_config.get("supervise_eos", True))
        for split_name in ("train", "test"):
            if answer_field not in raw_split[split_name].column_names:
                raise ValueError(f"Answer field {answer_field!r} not found in {split_name} dataset")

        def tokenize_answer_only_batch(examples: dict[str, list[Any]]) -> dict[str, list[list[int]]]:
            texts = [str(value) for value in examples[text_field]]
            answers = [str(value) for value in examples[answer_field]]
            tokenized = tokenizer(
                texts,
                add_special_tokens=False,
                truncation=True,
                max_length=block_size - 1,
                return_offsets_mapping=True,
            )
            eos_id = tokenizer.eos_token_id
            batch_input_ids: list[list[int]] = []
            batch_attention_mask: list[list[int]] = []
            batch_labels: list[list[int]] = []

            for text, answer, input_ids, attention_mask, offsets in zip(
                texts,
                answers,
                tokenized["input_ids"],
                tokenized["attention_mask"],
                tokenized["offset_mapping"],
                strict=True,
            ):
                answer_start, answer_end = _answer_char_span(text, answer)
                label_mask = _token_label_mask_from_offsets(
                    list(offsets),
                    answer_start=answer_start,
                    answer_end=answer_end,
                )
                input_ids = list(input_ids) + [eos_id]
                attention_mask = list(attention_mask) + [1]
                labels = _answer_only_labels(
                    input_ids[:-1],
                    label_mask,
                    eos_id,
                    supervise_eos=supervise_eos,
                )

                pad_len = block_size - len(input_ids)
                if pad_len < 0:
                    raise ValueError("Answer-only tokenized example exceeded configured block size")
                batch_input_ids.append(input_ids + [tokenizer.pad_token_id] * pad_len)
                batch_attention_mask.append(attention_mask + [0] * pad_len)
                batch_labels.append(labels + [-100] * pad_len)

            return {
                "input_ids": batch_input_ids,
                "attention_mask": batch_attention_mask,
                "labels": batch_labels,
            }

        lm_datasets = raw_split.map(
            tokenize_answer_only_batch,
            batched=True,
            remove_columns=columns,
            desc=f"Tokenizing answer-only rows to {block_size} tokens",
        )
    else:
        def tokenize_batch(examples: dict[str, list[Any]]) -> dict[str, list[list[int]]]:
            tokenized = tokenizer([str(value) for value in examples[text_field]], add_special_tokens=False)
            eos_id = tokenizer.eos_token_id
            tokenized["input_ids"] = [ids + [eos_id] for ids in tokenized["input_ids"]]
            tokenized["attention_mask"] = [mask + [1] for mask in tokenized["attention_mask"]]
            return tokenized

        tokenized = raw_split.map(tokenize_batch, batched=True, remove_columns=columns, desc="Tokenizing")

        def group_texts(examples: dict[str, list[list[int]]]) -> dict[str, list[list[int]]]:
            concatenated = {key: sum(examples[key], []) for key in examples.keys()}
            total_length = len(concatenated["input_ids"])
            total_length = (total_length // block_size) * block_size
            result = {
                key: [values[index : index + block_size] for index in range(0, total_length, block_size)]
                for key, values in concatenated.items()
            }
            result["labels"] = [ids.copy() for ids in result["input_ids"]]
            return result

        lm_datasets = tokenized.map(group_texts, batched=True, desc=f"Grouping into {block_size}-token blocks")
    train_blocks = len(lm_datasets["train"])
    eval_blocks = len(lm_datasets["test"])
    if train_blocks == 0:
        raise ValueError("Training dataset produced zero token blocks")

    world_size = int(runtime_config.get("world_size", 1))
    epoch_estimated_steps = estimate_optimizer_steps(
        train_blocks=train_blocks,
        per_device_train_batch_size=int(training_config["per_device_train_batch_size"]),
        gradient_accumulation_steps=int(training_config.get("gradient_accumulation_steps", 1)),
        num_train_epochs=float(training_config["num_train_epochs"]),
        world_size=world_size,
    )
    configured_max_steps = training_config.get("max_steps")
    estimated_steps = int(configured_max_steps) if configured_max_steps is not None else epoch_estimated_steps
    if estimated_steps <= 0:
        raise ValueError("Configured max_steps must be positive")
    save_steps = int(training_config.get("save_steps") or interval_from_fractions(estimated_steps, list(training_config.get("checkpoint_fractions", [0.25]))))
    eval_steps = int(training_config.get("eval_steps") or save_steps)

    warmup_ratio = float(training_config.get("warmup_ratio", 0.0))
    warmup_steps = int(training_config.get("warmup_steps", round(estimated_steps * warmup_ratio)))

    args_kwargs: dict[str, Any] = {
        "output_dir": str(run_dir / "checkpoints"),
        "per_device_train_batch_size": int(training_config["per_device_train_batch_size"]),
        "per_device_eval_batch_size": int(training_config["per_device_eval_batch_size"]),
        "gradient_accumulation_steps": int(training_config.get("gradient_accumulation_steps", 1)),
        "num_train_epochs": float(training_config["num_train_epochs"]),
        "learning_rate": float(training_config["learning_rate"]),
        "weight_decay": float(training_config.get("weight_decay", 0.0)),
        "warmup_steps": warmup_steps,
        "lr_scheduler_type": str(training_config.get("lr_scheduler_type", "linear")),
        "logging_steps": int(training_config.get("logging_steps", 10)),
        "save_steps": save_steps,
        "eval_steps": eval_steps,
        "save_strategy": "steps",
        "report_to": [],
        "seed": seed,
        "data_seed": data_seed,
        "bf16": bool(training_config.get("bf16", False)),
        "fp16": bool(training_config.get("fp16", False)),
        "gradient_checkpointing": bool(training_config.get("gradient_checkpointing", False)),
        "max_grad_norm": float(training_config.get("max_grad_norm", 1.0)),
        "save_total_limit": int(training_config.get("save_total_limit", 8)),
        "logging_dir": str(run_dir / "logs"),
    }
    if configured_max_steps is not None:
        args_kwargs["max_steps"] = int(configured_max_steps)
    eval_arg = _training_args_eval_key(TrainingArguments)
    args_kwargs[eval_arg] = "steps"
    if "save_safetensors" in inspect.signature(TrainingArguments).parameters:
        args_kwargs["save_safetensors"] = True

    training_args = TrainingArguments(**_supported_training_args_kwargs(TrainingArguments, args_kwargs))
    collator = default_data_collator if loss_mode == "answer_only" else None
    if collator is None:
        from transformers import DataCollatorForLanguageModeling

        collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=lm_datasets["train"],
        eval_dataset=lm_datasets["test"],
        data_collator=collator,
    )

    train_output = trainer.train()
    final_model_dir = run_dir / "final_model"
    trainer.save_model(str(final_model_dir))
    tokenizer.save_pretrained(str(final_model_dir))
    train_metrics = train_output.metrics
    eval_metrics = trainer.evaluate()
    write_json(run_dir / "train_metrics.json", train_metrics)
    write_json(run_dir / "eval_metrics.json", eval_metrics)
    checkpoints = sorted(str(path) for path in (run_dir / "checkpoints").glob("checkpoint-*") if path.is_dir())
    return {
        "run_dir": str(run_dir),
        "final_model_dir": str(final_model_dir),
        "checkpoint_dirs": checkpoints,
        "train_blocks": train_blocks,
        "eval_blocks": eval_blocks,
        "estimated_optimizer_steps": estimated_steps,
        "save_steps": save_steps,
        "eval_steps": eval_steps,
        "warmup_steps": warmup_steps,
        "train_metrics": train_metrics,
        "eval_metrics": eval_metrics,
        "software": {
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "transformers": transformers.__version__,
            "datasets": datasets.__version__,
            "cuda_device_count": torch.cuda.device_count(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        },
    }


def _training_args_eval_key(training_args_class: type[Any]) -> str:
    parameters = inspect.signature(training_args_class).parameters
    return "eval_strategy" if "eval_strategy" in parameters else "evaluation_strategy"


def _supported_training_args_kwargs(training_args_class: type[Any], values: dict[str, Any]) -> dict[str, Any]:
    parameters = inspect.signature(training_args_class).parameters
    return {key: value for key, value in values.items() if key in parameters}


def _git_commit(repo_root: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return None


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_yaml_config(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ModuleNotFoundError:
        return _simple_yaml(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        key, _, value = raw_line.strip().partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if not value.strip():
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_yaml_scalar(value.strip())
    return root


def _parse_yaml_scalar(value: str) -> Any:
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "None"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_yaml_scalar(part.strip()) for part in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        if any(marker in value for marker in (".", "e", "E")):
            return float(value)
        return int(value)
    except ValueError:
        return value
