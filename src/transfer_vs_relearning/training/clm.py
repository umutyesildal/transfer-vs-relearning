from __future__ import annotations

import inspect
import hashlib
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import count_lines, sha256_file, sha256_text, write_json
from transfer_vs_relearning.utils.io import read_csv_rows
from transfer_vs_relearning.data.constants import RELATION_MAP


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


def combine_retention_losses(factual_loss: Any, anchor_loss: Any, coefficient: float) -> Any:
    if coefficient <= 0:
        raise ValueError("Retention coefficient must be positive")
    return factual_loss + coefficient * anchor_loss


def combine_contrastive_losses(factual_loss: Any, ranking_loss: Any, coefficient: float) -> Any:
    """Keep canonical LM loss primary while adding the frozen binding objective."""
    if coefficient <= 0:
        raise ValueError("Contrastive coefficient must be positive")
    return factual_loss + coefficient * ranking_loss


def prompt_distribution_consistency_loss(scores: Any) -> Any:
    """KL agreement of same-fact, A/B-only candidate distributions."""
    import torch.nn.functional as F

    if scores.ndim != 3 or scores.shape[1] < 2:
        raise ValueError("Prompt-consistency scores must be [groups, prompts, candidates]")
    log_distributions = F.log_softmax(scores, dim=-1)
    mean_distribution = log_distributions.exp().mean(dim=1, keepdim=True).detach()
    return F.kl_div(
        log_distributions,
        mean_distribution.expand_as(log_distributions),
        reduction="batchmean",
    )


def combine_binding_losses(
    factual_loss: Any,
    ranking_loss: Any,
    ranking_coefficient: float,
    consistency_loss: Any,
    consistency_coefficient: float,
) -> Any:
    if ranking_coefficient <= 0 or consistency_coefficient <= 0:
        raise ValueError("Binding coefficients must be positive")
    return factual_loss + ranking_coefficient * ranking_loss + consistency_coefficient * consistency_loss


def _padded_full_sequence(
    input_ids: list[int],
    attention_mask: list[int],
    *,
    eos_token_id: int,
    pad_token_id: int,
    block_size: int,
) -> tuple[list[int], list[int], list[int]]:
    ids = list(input_ids) + [eos_token_id]
    mask = list(attention_mask) + [1]
    if len(ids) > block_size:
        raise ValueError("Full-sequence replay example exceeded configured block size")
    labels = ids.copy()
    pad_len = block_size - len(ids)
    return (
        ids + [pad_token_id] * pad_len,
        mask + [0] * pad_len,
        labels + [-100] * pad_len,
    )


def run_from_config(
    config_path: Path,
    repo_root: Path | None = None,
    *,
    resume_run_dir: Path | None = None,
) -> Path:
    repo_root = (repo_root or Path.cwd()).resolve()
    config_path = config_path.resolve()
    config = load_training_config(config_path)
    config_hash = sha256_text(json.dumps(config, ensure_ascii=False, sort_keys=True))
    training_config = config["training"]
    run_name = safe_run_name(str(training_config.get("run_name", config_path.stem)))
    output_root = resolve_path(repo_root, training_config["output_root"])
    resume_checkpoint: Path | None = None
    if resume_run_dir is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = output_root / f"{timestamp}_{run_name}_{config_hash[:8]}"
        if run_dir.exists():
            raise FileExistsError(f"Training run directory already exists: {run_dir}")
        run_dir.mkdir(parents=True)
        _write_initial_manifest(config, config_path, config_hash, repo_root, run_dir)
    else:
        run_dir = resume_run_dir.resolve()
        resume_checkpoint = validate_resume_run(
            config=config,
            config_hash=config_hash,
            repo_root=repo_root,
            output_root=output_root,
            run_dir=run_dir,
        )
        manifest_path = run_dir / "training_manifest.json"
        manifest = _read_json(manifest_path)
        manifest.setdefault("resume_events", []).append(
            {
                "resumed_at": datetime.now(timezone.utc).isoformat(),
                "checkpoint": str(resume_checkpoint),
                "git_commit": _git_commit(repo_root),
            }
        )
        write_json(manifest_path, manifest)

    train_result = _run_hf_training(
        config,
        repo_root,
        run_dir,
        resume_from_checkpoint=resume_checkpoint,
    )
    _write_final_manifest(config, config_path, config_hash, repo_root, run_dir, train_result)
    return run_dir


def validate_resume_run(
    *,
    config: dict[str, Any],
    config_hash: str,
    repo_root: Path,
    output_root: Path,
    run_dir: Path,
) -> Path:
    if not run_dir.is_dir() or run_dir.parent.resolve() != output_root.resolve():
        raise ValueError("Resume run directory must be an existing direct child of the configured output root")
    manifest_path = run_dir / "training_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("Resume run is missing training_manifest.json")
    manifest = _read_json(manifest_path)
    if manifest.get("status") != "started":
        raise ValueError(f"Only an incomplete started run may resume, found {manifest.get('status')!r}")
    if manifest.get("config_sha256") != config_hash:
        raise ValueError("Resume config hash does not match the original run")

    dataset = config["dataset"]
    model = config["model"]
    current_inputs = {
        "dataset.train_file_sha256": sha256_file(resolve_path(repo_root, dataset["train_file"])),
        "dataset.dataset_manifest_sha256": sha256_file(resolve_path(repo_root, dataset["dataset_manifest"])),
        "model.base_model_manifest_sha256": sha256_file(resolve_path(repo_root, model["base_model_manifest"])),
    }
    if dataset.get("validation_file"):
        current_inputs["dataset.validation_file_sha256"] = sha256_file(
            resolve_path(repo_root, dataset["validation_file"])
        )
    retention = config.get("retention")
    if retention:
        current_inputs["retention.anchor_train_file_sha256"] = sha256_file(
            resolve_path(repo_root, retention["anchor_train_file"])
        )
        current_inputs["retention.anchor_validation_file_sha256"] = sha256_file(
            resolve_path(repo_root, retention["anchor_validation_file"])
        )
    for dotted_key, observed in current_inputs.items():
        section, key = dotted_key.split(".", 1)
        expected = manifest.get(section, {}).get(key)
        if expected != observed:
            raise ValueError(f"Resume input hash mismatch for {dotted_key}: {observed} != {expected}")

    candidates: list[tuple[int, Path]] = []
    for path in (run_dir / "checkpoints").glob("checkpoint-*"):
        if not path.is_dir():
            continue
        try:
            step = int(path.name.rsplit("-", 1)[1])
        except ValueError:
            continue
        required = ("trainer_state.json", "optimizer.pt", "scheduler.pt")
        if all((path / name).is_file() for name in required):
            candidates.append((step, path))
    if not candidates:
        raise ValueError("Resume run has no complete optimizer checkpoint")
    return max(candidates)[1]


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
    retention = config.get("retention")
    if retention:
        if retention.get("mechanism") != "replay":
            raise ValueError(f"Unsupported retention mechanism: {retention.get('mechanism')!r}")
        anchor_train_file = resolve_path(repo_root, retention["anchor_train_file"])
        anchor_validation_file = resolve_path(repo_root, retention["anchor_validation_file"])
        payload["retention"] = {
            "mechanism": "replay",
            "coefficient": float(retention["coefficient"]),
            "anchor_train_file": str(anchor_train_file),
            "anchor_train_file_sha256": sha256_file(anchor_train_file),
            "anchor_train_rows": count_lines(anchor_train_file),
            "anchor_validation_file": str(anchor_validation_file),
            "anchor_validation_file_sha256": sha256_file(anchor_validation_file),
            "anchor_validation_rows": count_lines(anchor_validation_file),
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


def _run_hf_training(
    config: dict[str, Any],
    repo_root: Path,
    run_dir: Path,
    *,
    resume_from_checkpoint: Path | None = None,
) -> dict[str, Any]:
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
    retention_config = config.get("retention")
    contrastive_config = config.get("contrastive")
    consistency_config = config.get("prompt_consistency")
    if retention_config and contrastive_config:
        raise ValueError("Replay and contrastive objectives cannot be combined in one frozen run")
    if consistency_config and not contrastive_config:
        raise ValueError("Prompt consistency requires the contrastive binding objective")
    if retention_config:
        if retention_config.get("mechanism") != "replay":
            raise ValueError(f"Unsupported retention mechanism: {retention_config.get('mechanism')!r}")
        if loss_mode != "answer_only":
            raise ValueError("Replay retention currently requires answer-only factual loss")
        retention_coefficient = float(retention_config["coefficient"])
        if retention_coefficient <= 0:
            raise ValueError("Replay retention coefficient must be positive")
    else:
        retention_coefficient = 0.0
    if contrastive_config:
        if loss_mode != "answer_only":
            raise ValueError("Contrastive binding requires answer-only factual loss")
        contrastive_coefficient = float(contrastive_config["coefficient"])
        negatives_per_example = int(contrastive_config["negatives_per_example"])
        if contrastive_coefficient <= 0 or negatives_per_example <= 0:
            raise ValueError("Contrastive coefficient and negative count must be positive")
        profiles = read_csv_rows(resolve_path(repo_root, contrastive_config["canonical_profiles_file"]))
        if not profiles:
            raise ValueError("Contrastive binding requires at least one canonical profile")
        available_columns = set(profiles[0])
        inventory = {
            relation: sorted({row[answer_column] for row in profiles})
            for relation, (answer_column, _, _) in RELATION_MAP.items()
            if answer_column in available_columns
        }
        profile_by_id = {row["subject_id"]: row for row in profiles}
        if consistency_config:
            consistency_coefficient = float(consistency_config["coefficient"])
            consistency_anchor = str(consistency_config["anchor_training_representation"])
            consistency_slots = tuple(str(value) for value in consistency_config["training_representations"])
            if consistency_coefficient <= 0 or len(consistency_slots) < 2:
                raise ValueError("Prompt-consistency coefficient must be positive and require at least two prompts")
            if consistency_anchor not in consistency_slots:
                raise ValueError("Prompt-consistency anchor must be one of the grouped representations")
        else:
            consistency_coefficient = 0.0
            consistency_anchor = ""
            consistency_slots = ()
    else:
        contrastive_coefficient = 0.0
        negatives_per_example = 0
        inventory = {}
        profile_by_id = {}
        consistency_coefficient = 0.0
        consistency_anchor = ""
        consistency_slots = ()

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

    anchor_column = "__retention_anchor_text"
    if retention_config:
        anchor_train_file = resolve_path(repo_root, retention_config["anchor_train_file"])
        anchor_validation_file = resolve_path(repo_root, retention_config["anchor_validation_file"])
        anchor_text_field = str(retention_config.get("text_field", "text"))
        anchor_split = load_dataset(
            "json",
            data_files={"train": str(anchor_train_file), "test": str(anchor_validation_file)},
        )
        for split_name in ("train", "test"):
            if anchor_text_field not in anchor_split[split_name].column_names:
                raise ValueError(
                    f"Anchor text field {anchor_text_field!r} not found in {split_name} dataset"
                )
            if len(anchor_split[split_name]) != len(raw_split[split_name]):
                raise ValueError(
                    f"Replay {split_name} rows must align one-to-one with factual rows: "
                    f"{len(anchor_split[split_name])} != {len(raw_split[split_name])}"
                )
            raw_split[split_name] = raw_split[split_name].add_column(
                anchor_column,
                [str(value) for value in anchor_split[split_name][anchor_text_field]],
            )

    pretokenized = bool(dataset_config.get("pretokenized", False))
    columns = raw_split["train"].column_names
    for split_name in ("train", "test"):
        if not pretokenized and text_field not in raw_split[split_name].column_names:
            raise ValueError(f"Text field {text_field!r} not found in {split_name} dataset")
        if raw_split[split_name].column_names != columns:
            raise ValueError("Training and validation datasets must have the same columns")

    consistency_rows_by_fact: dict[str, dict[str, dict[str, Any]]] = {}
    if consistency_config:
        for row in raw_split["train"]:
            representation = str(row.get("training_representation", ""))
            if representation in consistency_slots:
                fact_rows = consistency_rows_by_fact.setdefault(str(row["fact_id"]), {})
                if representation in fact_rows:
                    raise ValueError(f"Duplicate prompt-consistency row for {row['fact_id']} / {representation}")
                fact_rows[representation] = dict(row)
        incomplete = {
            fact_id: sorted(set(consistency_slots) - set(rows))
            for fact_id, rows in consistency_rows_by_fact.items()
            if set(rows) != set(consistency_slots)
        }
        expected_facts = len({str(row["fact_id"]) for row in raw_split["train"]})
        if len(consistency_rows_by_fact) != expected_facts or incomplete:
            raise ValueError(f"Prompt-consistency groups are incomplete: {list(incomplete.items())[:3]}")

    if pretokenized:
        if loss_mode != "full_sequence":
            raise ValueError("Pretokenized datasets currently require full_sequence loss")
        if retention_config or contrastive_config or consistency_config:
            raise ValueError("Pretokenized M2/M3 blocks cannot be combined with auxiliary objectives")

        def validate_pretokenized_batch(
            examples: dict[str, list[Any]],
        ) -> dict[str, list[list[int]]]:
            batch_input_ids: list[list[int]] = []
            batch_attention_mask: list[list[int]] = []
            batch_labels: list[list[int]] = []
            for input_ids, attention_mask in zip(
                examples["input_ids"], examples["attention_mask"], strict=True
            ):
                ids = [int(value) for value in input_ids]
                mask = [int(value) for value in attention_mask]
                if len(ids) != block_size or len(mask) != block_size:
                    raise ValueError("Pretokenized input_ids and attention_mask must equal block_size")
                if any(value != 1 for value in mask):
                    raise ValueError("Frozen M2/M3 pretokenized blocks must supervise every token")
                if any(value < 0 for value in ids):
                    raise ValueError("Pretokenized input IDs must be non-negative")
                batch_input_ids.append(ids)
                batch_attention_mask.append(mask)
                batch_labels.append(ids.copy())
            return {
                "input_ids": batch_input_ids,
                "attention_mask": batch_attention_mask,
                "labels": batch_labels,
            }

        for split_name in ("train", "test"):
            required_columns = {"input_ids", "attention_mask"}
            if not required_columns.issubset(raw_split[split_name].column_names):
                raise ValueError(
                    f"Pretokenized {split_name} split is missing {sorted(required_columns)}"
                )
        lm_datasets = raw_split.map(
            validate_pretokenized_batch,
            batched=True,
            remove_columns=columns,
            desc=f"Validating frozen {block_size}-token blocks",
        )
    elif loss_mode == "answer_only":
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
            batch_anchor_input_ids: list[list[int]] = []
            batch_anchor_attention_mask: list[list[int]] = []
            batch_anchor_labels: list[list[int]] = []
            batch_candidate_ids: list[list[list[int]]] = []
            batch_candidate_masks: list[list[list[int]]] = []
            batch_candidate_labels: list[list[list[int]]] = []
            batch_consistency_ids: list[list[list[list[int]]]] = []
            batch_consistency_masks: list[list[list[list[int]]]] = []
            batch_consistency_labels: list[list[list[list[int]]]] = []
            batch_consistency_active: list[bool] = []

            def candidate_rows_for_text(
                candidate_text_prefix: str,
                candidate_answer: str,
                candidate_values: list[str],
            ) -> list[tuple[list[int], list[int], list[int]]]:
                candidate_rows = []
                for candidate in candidate_values:
                    candidate_text = candidate_text_prefix[:_answer_char_span(candidate_text_prefix, candidate_answer)[0]] + candidate
                    encoded = tokenizer(candidate_text, add_special_tokens=False, truncation=True, max_length=block_size - 1, return_offsets_mapping=True)
                    ids, mask, offsets2 = list(encoded["input_ids"]), list(encoded["attention_mask"]), list(encoded["offset_mapping"])
                    start2, end2 = _answer_char_span(candidate_text, candidate)
                    labels2 = _answer_only_labels(ids, _token_label_mask_from_offsets(offsets2, answer_start=start2, answer_end=end2), eos_id, supervise_eos=False)
                    pad2 = block_size - (len(ids) + 1)
                    candidate_rows.append((ids + [eos_id] + [tokenizer.pad_token_id] * pad2, mask + [1] + [0] * pad2, labels2 + [-100] * pad2))
                return candidate_rows

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
                if contrastive_config:
                    relation = str(examples["relation"][len(batch_input_ids) - 1])
                    subject_id = str(examples["subject_id"][len(batch_input_ids) - 1])
                    exposure = str(examples.get("exposure_index", [0] * len(texts))[len(batch_input_ids) - 1])
                    candidates = [value for value in inventory[relation] if value != answer]
                    if len(candidates) < negatives_per_example:
                        raise ValueError(f"Insufficient relation candidates for {relation}")
                    start = int.from_bytes(hashlib.sha256(f"42:{relation}:{subject_id}:{exposure}".encode()).digest()[:8], "big") % len(candidates)
                    negatives = [candidates[(start + offset) % len(candidates)] for offset in range(negatives_per_example)]
                    if relation in {"born_in", "lives_in"}:
                        paired = profile_by_id[subject_id]["residence_en" if relation == "born_in" else "birthplace_en"]
                        if paired != answer and paired not in negatives:
                            negatives[-1] = paired
                    candidate_rows = []
                    for candidate in [answer, *negatives]:
                        candidate_text = text[:answer_start] + candidate
                        encoded = tokenizer(candidate_text, add_special_tokens=False, truncation=True, max_length=block_size - 1, return_offsets_mapping=True)
                        ids, mask, offsets2 = list(encoded["input_ids"]), list(encoded["attention_mask"]), list(encoded["offset_mapping"])
                        start2, end2 = _answer_char_span(candidate_text, candidate)
                        labels2 = _answer_only_labels(ids, _token_label_mask_from_offsets(offsets2, answer_start=start2, answer_end=end2), eos_id, supervise_eos=False)
                        pad2 = block_size - (len(ids) + 1)
                        candidate_rows.append((ids + [eos_id] + [tokenizer.pad_token_id] * pad2, mask + [1] + [0] * pad2, labels2 + [-100] * pad2))
                    batch_candidate_ids.append([item[0] for item in candidate_rows])
                    batch_candidate_masks.append([item[1] for item in candidate_rows])
                    batch_candidate_labels.append([item[2] for item in candidate_rows])
                    if consistency_config:
                        representation = str(examples.get("training_representation", [""] * len(texts))[len(batch_input_ids) - 1])
                        fact_id = str(examples["fact_id"][len(batch_input_ids) - 1])
                        is_anchor = representation == consistency_anchor
                        batch_consistency_active.append(is_anchor)
                        if is_anchor:
                            group_rows = consistency_rows_by_fact[fact_id]
                            group_relation = str(group_rows[consistency_slots[0]]["relation"])
                            group_answer = str(group_rows[consistency_slots[0]]["answer"])
                            if any(str(group_rows[slot]["relation"]) != group_relation or str(group_rows[slot]["answer"]) != group_answer for slot in consistency_slots):
                                raise ValueError(f"Prompt-consistency group disagrees on fact {fact_id}")
                            group_candidates = [value for value in inventory[group_relation] if value != group_answer]
                            group_start = int.from_bytes(hashlib.sha256(f"42:consistency:{fact_id}:{group_relation}".encode()).digest()[:8], "big") % len(group_candidates)
                            group_negatives = [group_candidates[(group_start + offset) % len(group_candidates)] for offset in range(negatives_per_example)]
                            if group_relation in {"born_in", "lives_in"}:
                                paired = profile_by_id[str(group_rows[consistency_slots[0]]["subject_id"])]["residence_en" if group_relation == "born_in" else "birthplace_en"]
                                if paired != group_answer and paired not in group_negatives:
                                    group_negatives[-1] = paired
                            group_values = [group_answer, *group_negatives]
                            grouped_candidates = [
                                candidate_rows_for_text(str(group_rows[slot]["text"]), group_answer, group_values)
                                for slot in consistency_slots
                            ]
                        else:
                            blank = ([tokenizer.pad_token_id] * block_size, [0] * block_size, [-100] * block_size)
                            grouped_candidates = [[blank for _ in range(negatives_per_example + 1)] for _ in consistency_slots]
                        batch_consistency_ids.append([[item[0] for item in group] for group in grouped_candidates])
                        batch_consistency_masks.append([[item[1] for item in group] for group in grouped_candidates])
                        batch_consistency_labels.append([[item[2] for item in group] for group in grouped_candidates])

            if retention_config:
                anchor_max_tokens = int(retention_config.get("max_tokens", block_size - 1))
                if anchor_max_tokens <= 0 or anchor_max_tokens >= block_size:
                    raise ValueError("Replay max_tokens must be positive and smaller than block_size")
                anchor_tokenized = tokenizer(
                    [str(value) for value in examples[anchor_column]],
                    add_special_tokens=False,
                    truncation=True,
                    max_length=anchor_max_tokens,
                )
                for anchor_ids, anchor_mask in zip(
                    anchor_tokenized["input_ids"],
                    anchor_tokenized["attention_mask"],
                    strict=True,
                ):
                    padded_ids, padded_mask, padded_labels = _padded_full_sequence(
                        list(anchor_ids),
                        list(anchor_mask),
                        eos_token_id=eos_id,
                        pad_token_id=tokenizer.pad_token_id,
                        block_size=block_size,
                    )
                    batch_anchor_input_ids.append(padded_ids)
                    batch_anchor_attention_mask.append(padded_mask)
                    batch_anchor_labels.append(padded_labels)

            result = {
                "input_ids": batch_input_ids,
                "attention_mask": batch_attention_mask,
                "labels": batch_labels,
            }
            if retention_config:
                result.update(
                    {
                        "anchor_input_ids": batch_anchor_input_ids,
                        "anchor_attention_mask": batch_anchor_attention_mask,
                        "anchor_labels": batch_anchor_labels,
                    }
                )
            if contrastive_config:
                result.update({"contrastive_input_ids": batch_candidate_ids, "contrastive_attention_mask": batch_candidate_masks, "contrastive_labels": batch_candidate_labels})
            if consistency_config:
                result.update({"consistency_input_ids": batch_consistency_ids, "consistency_attention_mask": batch_consistency_masks, "consistency_labels": batch_consistency_labels, "consistency_active": batch_consistency_active})
            return result

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
    if retention_config or contrastive_config:
        # The replay tensors are consumed by ReplayTrainer.compute_loss rather than model.forward.
        # Transformers would otherwise discard them as unused dataset columns.
        args_kwargs["remove_unused_columns"] = False
    eval_arg = _training_args_eval_key(TrainingArguments)
    args_kwargs[eval_arg] = "steps"
    if "save_safetensors" in inspect.signature(TrainingArguments).parameters:
        args_kwargs["save_safetensors"] = True

    training_args = TrainingArguments(**_supported_training_args_kwargs(TrainingArguments, args_kwargs))
    collator = default_data_collator if loss_mode == "answer_only" else None
    if collator is None:
        from transformers import DataCollatorForLanguageModeling

        collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    trainer_class = Trainer
    if retention_config:
        class ReplayTrainer(Trainer):
            def __init__(self, *args: Any, replay_coefficient: float, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self.replay_coefficient = replay_coefficient
                self.replay_train_batches = 0
                self.replay_fact_loss_sum = 0.0
                self.replay_anchor_loss_sum = 0.0

            def compute_loss(
                self,
                model: Any,
                inputs: dict[str, Any],
                return_outputs: bool = False,
                **kwargs: Any,
            ) -> Any:
                anchor_inputs = {
                    "input_ids": inputs.pop("anchor_input_ids"),
                    "attention_mask": inputs.pop("anchor_attention_mask"),
                    "labels": inputs.pop("anchor_labels"),
                }
                factual_outputs = model(**inputs)
                anchor_outputs = model(**anchor_inputs)
                factual_loss = factual_outputs.loss
                anchor_loss = anchor_outputs.loss
                loss = combine_retention_losses(
                    factual_loss,
                    anchor_loss,
                    self.replay_coefficient,
                )
                if model.training:
                    self.replay_train_batches += 1
                    self.replay_fact_loss_sum += float(factual_loss.detach().float().cpu())
                    self.replay_anchor_loss_sum += float(anchor_loss.detach().float().cpu())
                return (loss, factual_outputs) if return_outputs else loss

            def replay_metrics(self) -> dict[str, float | int]:
                count = self.replay_train_batches
                if count == 0:
                    return {"train_batches": 0}
                return {
                    "train_batches": count,
                    "mean_factual_loss": self.replay_fact_loss_sum / count,
                    "mean_anchor_loss": self.replay_anchor_loss_sum / count,
                    "coefficient": self.replay_coefficient,
                }

        trainer_class = ReplayTrainer
    elif contrastive_config:
        class ContrastiveTrainer(Trainer):
            def __init__(
                self,
                *args: Any,
                contrastive_coefficient: float,
                consistency_coefficient: float = 0.0,
                **kwargs: Any,
            ) -> None:
                super().__init__(*args, **kwargs)
                self.contrastive_coefficient = contrastive_coefficient
                self.consistency_coefficient = consistency_coefficient
                self.contrastive_train_batches = 0
                self.contrastive_factual_loss_sum = 0.0
                self.contrastive_ranking_loss_sum = 0.0
                self.consistency_loss_sum = 0.0
                self.consistency_group_count = 0
            def compute_loss(self, model: Any, inputs: dict[str, Any], return_outputs: bool = False, **kwargs: Any) -> Any:
                candidate_ids = inputs.pop("contrastive_input_ids")
                candidate_mask = inputs.pop("contrastive_attention_mask")
                candidate_labels = inputs.pop("contrastive_labels")
                consistency_ids = inputs.pop("consistency_input_ids", None)
                consistency_mask = inputs.pop("consistency_attention_mask", None)
                consistency_labels = inputs.pop("consistency_labels", None)
                consistency_active = inputs.pop("consistency_active", None)
                factual = model(**inputs)
                batch, choices, length = candidate_ids.shape
                outputs = model(input_ids=candidate_ids.reshape(batch * choices, length), attention_mask=candidate_mask.reshape(batch * choices, length))
                logits = outputs.logits[:, :-1, :]
                labels = candidate_labels.reshape(batch * choices, length)[:, 1:]
                mask = labels.ne(-100)
                token_logp = logits.log_softmax(-1).gather(-1, labels.masked_fill(~mask, 0).unsqueeze(-1)).squeeze(-1)
                scores = (token_logp * mask).sum(-1) / mask.sum(-1).clamp_min(1)
                ranking = torch.nn.functional.cross_entropy(scores.reshape(batch, choices), torch.zeros(batch, dtype=torch.long, device=scores.device))
                if self.consistency_coefficient > 0:
                    if consistency_ids is None or consistency_mask is None or consistency_labels is None or consistency_active is None:
                        raise ValueError("Prompt-consistency tensors are missing")
                    active = consistency_active.bool()
                    active_ids = consistency_ids[active]
                    active_mask = consistency_mask[active]
                    active_labels = consistency_labels[active]
                    groups, prompts, group_choices, group_length = active_ids.shape
                    if groups == 0:
                        consistency = scores.new_zeros(())
                    else:
                        group_outputs = model(
                            input_ids=active_ids.reshape(groups * prompts * group_choices, group_length),
                            attention_mask=active_mask.reshape(groups * prompts * group_choices, group_length),
                        )
                        group_logits = group_outputs.logits[:, :-1, :]
                        group_labels = active_labels.reshape(groups * prompts * group_choices, group_length)[:, 1:]
                        group_token_mask = group_labels.ne(-100)
                        group_token_logp = group_logits.log_softmax(-1).gather(-1, group_labels.masked_fill(~group_token_mask, 0).unsqueeze(-1)).squeeze(-1)
                        group_scores = ((group_token_logp * group_token_mask).sum(-1) / group_token_mask.sum(-1).clamp_min(1)).reshape(groups, prompts, group_choices)
                        consistency = prompt_distribution_consistency_loss(group_scores)
                    loss = combine_binding_losses(factual.loss, ranking, self.contrastive_coefficient, consistency, self.consistency_coefficient)
                else:
                    consistency = scores.new_zeros(())
                    groups = 0
                    loss = combine_contrastive_losses(factual.loss, ranking, self.contrastive_coefficient)
                if model.training:
                    self.contrastive_train_batches += 1
                    self.contrastive_factual_loss_sum += float(factual.loss.detach().float().cpu())
                    self.contrastive_ranking_loss_sum += float(ranking.detach().float().cpu())
                    self.consistency_loss_sum += float(consistency.detach().float().cpu())
                    self.consistency_group_count += int(groups)
                return (loss, factual) if return_outputs else loss

            def contrastive_metrics(self) -> dict[str, float | int]:
                count = self.contrastive_train_batches
                if count == 0:
                    return {"train_batches": 0}
                return {
                    "train_batches": count,
                    "mean_factual_lm_loss": self.contrastive_factual_loss_sum / count,
                    "mean_ranking_loss": self.contrastive_ranking_loss_sum / count,
                    "coefficient": self.contrastive_coefficient,
                    "mean_prompt_consistency_loss": self.consistency_loss_sum / count,
                    "prompt_consistency_coefficient": self.consistency_coefficient,
                    "prompt_consistency_groups": self.consistency_group_count,
                }
        trainer_class = ContrastiveTrainer

    trainer_kwargs: dict[str, Any] = {
        "model": model,
        "args": training_args,
        "train_dataset": lm_datasets["train"],
        "eval_dataset": lm_datasets["test"],
        "data_collator": collator,
    }
    if retention_config:
        trainer_kwargs["replay_coefficient"] = retention_coefficient
    if contrastive_config:
        trainer_kwargs["contrastive_coefficient"] = contrastive_coefficient
        trainer_kwargs["consistency_coefficient"] = consistency_coefficient
    trainer = trainer_class(
        **trainer_kwargs,
    )

    train_output = trainer.train(
        resume_from_checkpoint=str(resume_from_checkpoint) if resume_from_checkpoint else None
    )
    replay_metrics = trainer.replay_metrics() if retention_config else None
    contrastive_metrics = trainer.contrastive_metrics() if contrastive_config else None
    if replay_metrics is not None:
        replay_metrics["measurement_scope"] = (
            "post_resume_segment" if resume_from_checkpoint else "complete_run"
        )
        replay_metrics["resumed_from_checkpoint"] = (
            str(resume_from_checkpoint) if resume_from_checkpoint else None
        )
    if contrastive_metrics is not None:
        contrastive_metrics["measurement_scope"] = (
            "post_resume_segment" if resume_from_checkpoint else "complete_run"
        )
        contrastive_metrics["resumed_from_checkpoint"] = (
            str(resume_from_checkpoint) if resume_from_checkpoint else None
        )
    final_model_dir = run_dir / "final_model"
    trainer.save_model(str(final_model_dir))
    tokenizer.save_pretrained(str(final_model_dir))
    train_metrics = train_output.metrics
    eval_metrics = trainer.evaluate()
    write_json(run_dir / "train_metrics.json", train_metrics)
    write_json(run_dir / "eval_metrics.json", eval_metrics)
    if replay_metrics is not None:
        write_json(run_dir / "retention_loss_metrics.json", replay_metrics)
    if contrastive_metrics is not None:
        write_json(run_dir / "contrastive_loss_metrics.json", contrastive_metrics)
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
        "retention_loss_metrics": replay_metrics,
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
