from __future__ import annotations

import inspect
import json
import math
import platform
import random
import re
import subprocess
import uuid
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.candidates import RELATION_TO_FAMILY, build_candidate_inventories, resolve_expected_answer
from transfer_vs_relearning.data.constants import DATASET_FILES, OPTIONAL_DATASET_FILES
from transfer_vs_relearning.evaluation.prompts import render_prompt_answer
from transfer_vs_relearning.evaluation.token_scoring import answer_token_indices_from_offsets, shifted_label_positions
from transfer_vs_relearning.training.clm import estimate_optimizer_steps, interval_from_fractions, load_training_config, resolve_path, safe_run_name
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl, sha256_file, sha256_text, write_json


@dataclass(frozen=True)
class RankingExample:
    fact_id: str
    relation: str
    prompt: str
    correct_answer: str
    negative_answers: tuple[str, ...]
    prompt_style: str

    @property
    def candidates(self) -> list[str]:
        return [self.correct_answer, *self.negative_answers]


def _git_commit(repo_root: Path | None = None) -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return None


def _answer_char_span(text: str, answer: str) -> tuple[int, int]:
    start = text.rfind(answer)
    if start < 0:
        raise ValueError(f"Answer text {answer!r} not found")
    return start, start + len(answer)


def _prompt_from_answer_row(text: str, answer: str) -> str:
    start, _ = _answer_char_span(text, answer)
    return text[:start].rstrip()


def _stable_negative_sample(
    *,
    fact_id: str,
    relation: str,
    correct_answer: str,
    candidates: list[str],
    negatives_per_example: int,
    seed: int,
) -> tuple[str, ...]:
    eligible = [candidate for candidate in candidates if candidate != correct_answer]
    if negatives_per_example > len(eligible):
        raise ValueError(f"Requested {negatives_per_example} negatives for {relation}, only {len(eligible)} available")
    rng = random.Random(f"{seed}:{fact_id}:{relation}")
    sampled = rng.sample(eligible, negatives_per_example)
    return tuple(sampled)


def build_ranking_examples(
    *,
    dataset_dir: Path,
    include_direct_probes: bool,
    include_qa_train: bool,
    negatives_per_example: int,
    seed: int,
) -> list[RankingExample]:
    canonical_rows = read_csv_rows(dataset_dir / DATASET_FILES["canonical_profiles"])
    inventories = build_candidate_inventories(canonical_rows)
    examples: list[RankingExample] = []

    if include_direct_probes:
        for row in read_csv_rows(dataset_dir / DATASET_FILES["probes_en"]):
            family = RELATION_TO_FAMILY[row["relation"]]
            correct = resolve_expected_answer(row["relation"], "en", row["expected_answer"], inventories)
            negative_answers = _stable_negative_sample(
                fact_id=row["fact_id"],
                relation=row["relation"],
                correct_answer=correct.object_en,
                candidates=[candidate.object_en for candidate in inventories[family]],
                negatives_per_example=negatives_per_example,
                seed=seed,
            )
            examples.append(
                RankingExample(
                    fact_id=row["fact_id"],
                    relation=row["relation"],
                    prompt=row["question"],
                    correct_answer=correct.object_en,
                    negative_answers=negative_answers,
                    prompt_style="direct_probe",
                )
            )

    if include_qa_train:
        qa_path = dataset_dir / OPTIONAL_DATASET_FILES["english_qa_train"]
        if not qa_path.exists():
            raise FileNotFoundError(f"QA training file missing: {qa_path}")
        for row in read_jsonl(qa_path):
            family = RELATION_TO_FAMILY[str(row["relation"])]
            correct_answer = str(row["answer"])
            negative_answers = _stable_negative_sample(
                fact_id=str(row["fact_id"]),
                relation=str(row["relation"]),
                correct_answer=correct_answer,
                candidates=[candidate.object_en for candidate in inventories[family]],
                negatives_per_example=negatives_per_example,
                seed=seed,
            )
            examples.append(
                RankingExample(
                    fact_id=str(row["fact_id"]),
                    relation=str(row["relation"]),
                    prompt=_prompt_from_answer_row(str(row["text"]), correct_answer),
                    correct_answer=correct_answer,
                    negative_answers=negative_answers,
                    prompt_style="qa_train",
                )
            )

    if not examples:
        raise ValueError("Ranking dataset builder produced zero examples")
    return examples


def run_from_config(config_path: Path, repo_root: Path | None = None) -> Path:
    repo_root = (repo_root or Path.cwd()).resolve()
    config_path = config_path.resolve()
    config = load_training_config(config_path)
    for section in ("dataset", "model", "training", "runtime"):
        if section not in config:
            raise ValueError(f"Missing required training config section: {section}")
    config_hash = sha256_text(json.dumps(config, ensure_ascii=False, sort_keys=True))
    run_name = safe_run_name(str(config["training"].get("run_name", config_path.stem)))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_root = resolve_path(repo_root, config["training"]["output_root"])
    run_dir = output_root / f"{timestamp}_{run_name}_{config_hash[:8]}"
    if run_dir.exists():
        raise FileExistsError(f"Training run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    _write_initial_manifest(config, config_path, config_hash, repo_root, run_dir)
    train_result = _run_ranking_training(config, repo_root, run_dir)
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
    dataset_dir = resolve_path(repo_root, dataset["dataset_dir"])
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
            "dataset_dir": str(dataset_dir),
            "dataset_manifest": str(dataset_manifest),
            "dataset_manifest_sha256": sha256_file(dataset_manifest),
            "canonical_profiles": str(dataset_dir / DATASET_FILES["canonical_profiles"]),
            "probes_en": str(dataset_dir / DATASET_FILES["probes_en"]),
            "english_qa_train": str(dataset_dir / OPTIONAL_DATASET_FILES["english_qa_train"]),
        },
        "model": {
            "base_model_manifest": str(model_manifest),
            "base_model_manifest_sha256": sha256_file(model_manifest),
            "base_model_manifest_payload": json.loads(model_manifest.read_text(encoding="utf-8")),
        },
        "objective": {
            "type": "candidate_ranking",
            "score_mode": config["training"].get("score_mode", "mean_logprob"),
        },
    }
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
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
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


def _offsets_to_pairs(offsets: Any) -> list[tuple[int, int]]:
    values = offsets.tolist() if hasattr(offsets, "tolist") else offsets
    return [(int(start), int(end)) for start, end in values]


def _score_candidate_groups(
    *,
    tokenizer: Any,
    model: Any,
    device: str,
    prompts: list[str],
    candidate_groups: list[list[str]],
    separator: str,
    score_mode: str,
) -> Any:
    import torch

    rendered: list[str] = []
    spans: list[tuple[int, int]] = []
    group_sizes: list[int] = []
    for prompt, candidates in zip(prompts, candidate_groups, strict=True):
        group_sizes.append(len(candidates))
        for candidate in candidates:
            text, answer_start, answer_end = render_prompt_answer(prompt, candidate, separator)
            rendered.append(text)
            spans.append((answer_start, answer_end))

    encoded = tokenizer(
        rendered,
        return_offsets_mapping=True,
        return_tensors="pt",
        padding=True,
    )
    offsets_batch = encoded.pop("offset_mapping")
    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)

    logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
    log_probs = torch.log_softmax(logits.float(), dim=-1)

    flat_scores = []
    for row_index, span in enumerate(spans):
        offsets = _offsets_to_pairs(offsets_batch[row_index])
        answer_indices = answer_token_indices_from_offsets(offsets, span[0], span[1])
        label_positions = shifted_label_positions(answer_indices)
        token_scores = []
        for token_index, logit_index in zip(answer_indices, label_positions, strict=True):
            if attention_mask is not None and int(attention_mask[row_index, token_index].item()) == 0:
                continue
            token_id = input_ids[row_index, token_index]
            token_scores.append(log_probs[row_index, logit_index, token_id])
        if not token_scores:
            raise ValueError("No token scores collected for candidate")
        stacked = torch.stack(token_scores)
        if score_mode == "total_logprob":
            flat_scores.append(stacked.sum())
        else:
            flat_scores.append(stacked.mean())

    grouped_scores = []
    offset = 0
    for size in group_sizes:
        grouped_scores.append(torch.stack(flat_scores[offset : offset + size]))
        offset += size
    return torch.stack(grouped_scores)


def _autocast_context(*, device: str, bf16: bool, fp16: bool):
    import torch

    if device != "cuda":
        return nullcontext()
    if bf16:
        return torch.autocast(device_type="cuda", dtype=torch.bfloat16)
    if fp16:
        return torch.autocast(device_type="cuda", dtype=torch.float16)
    return nullcontext()


def _save_checkpoint(model: Any, tokenizer: Any, checkpoint_dir: Path) -> None:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(checkpoint_dir), safe_serialization=True)
    tokenizer.save_pretrained(str(checkpoint_dir))


def _evaluate_loss(
    *,
    model: Any,
    tokenizer: Any,
    eval_examples: list[RankingExample],
    batch_size: int,
    device: str,
    separator: str,
    score_mode: str,
    bf16: bool,
    fp16: bool,
) -> tuple[float, float]:
    import torch
    import torch.nn.functional as F

    if not eval_examples:
        return 0.0, 0.0
    model.eval()
    total_loss = 0.0
    total_items = 0
    correct_top1 = 0
    with torch.inference_mode():
        for start in range(0, len(eval_examples), batch_size):
            batch = eval_examples[start : start + batch_size]
            prompts = [example.prompt for example in batch]
            candidate_groups = [example.candidates for example in batch]
            with _autocast_context(device=device, bf16=bf16, fp16=fp16):
                scores = _score_candidate_groups(
                    tokenizer=tokenizer,
                    model=model,
                    device=device,
                    prompts=prompts,
                    candidate_groups=candidate_groups,
                    separator=separator,
                    score_mode=score_mode,
                )
                targets = torch.zeros(scores.shape[0], dtype=torch.long, device=device)
                loss = F.cross_entropy(scores, targets)
            total_loss += float(loss.item()) * len(batch)
            total_items += len(batch)
            correct_top1 += int((scores.argmax(dim=1) == 0).sum().item())
    model.train()
    return total_loss / total_items, correct_top1 / total_items


def _run_ranking_training(config: dict[str, Any], repo_root: Path, run_dir: Path) -> dict[str, Any]:
    import torch
    import torch.nn.functional as F
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, get_scheduler, set_seed

    dataset_config = config["dataset"]
    model_config = config["model"]
    training_config = config["training"]
    runtime_config = config["runtime"]

    seed = int(training_config.get("seed", 42))
    set_seed(seed)

    dataset_dir = resolve_path(repo_root, dataset_config["dataset_dir"])
    examples = build_ranking_examples(
        dataset_dir=dataset_dir,
        include_direct_probes=bool(dataset_config.get("include_direct_probes", True)),
        include_qa_train=bool(dataset_config.get("include_qa_train", True)),
        negatives_per_example=int(dataset_config.get("negatives_per_example", 7)),
        seed=seed,
    )
    rng = random.Random(int(dataset_config.get("split_seed", seed)))
    indices = list(range(len(examples)))
    rng.shuffle(indices)
    validation_fraction = float(dataset_config.get("validation_fraction", 0.02))
    eval_count = max(1, round(len(indices) * validation_fraction))
    eval_indices = set(indices[:eval_count])
    train_examples = [example for index, example in enumerate(examples) if index not in eval_indices]
    eval_examples = [example for index, example in enumerate(examples) if index in eval_indices]

    model_manifest = json.loads(resolve_path(repo_root, model_config["base_model_manifest"]).read_text(encoding="utf-8"))
    model_path = Path(model_manifest["local_path_absolute"])
    local_files_only = bool(runtime_config.get("local_files_only", True))
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=local_files_only, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(str(model_path), local_files_only=local_files_only)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    if bool(training_config.get("gradient_checkpointing", False)) and hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()

    per_device_train_batch_size = int(training_config["per_device_train_batch_size"])
    per_device_eval_batch_size = int(training_config["per_device_eval_batch_size"])
    gradient_accumulation_steps = int(training_config.get("gradient_accumulation_steps", 1))
    num_train_epochs = float(training_config["num_train_epochs"])
    world_size = int(runtime_config.get("world_size", 1))
    estimated_steps = estimate_optimizer_steps(
        train_blocks=len(train_examples),
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        num_train_epochs=num_train_epochs,
        world_size=world_size,
    )
    save_steps = int(training_config.get("save_steps") or interval_from_fractions(estimated_steps, list(training_config.get("checkpoint_fractions", [0.25]))))
    eval_steps = int(training_config.get("eval_steps") or save_steps)
    warmup_ratio = float(training_config.get("warmup_ratio", 0.0))
    warmup_steps = int(training_config.get("warmup_steps", round(estimated_steps * warmup_ratio)))

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(training_config["learning_rate"]),
        weight_decay=float(training_config.get("weight_decay", 0.0)),
    )
    scheduler = get_scheduler(
        str(training_config.get("lr_scheduler_type", "linear")),
        optimizer=optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=max(estimated_steps, 1),
    )

    bf16 = bool(training_config.get("bf16", False))
    fp16 = bool(training_config.get("fp16", False))
    separator = str(training_config.get("answer_separator", " "))
    score_mode = str(training_config.get("score_mode", "mean_logprob"))
    max_grad_norm = float(training_config.get("max_grad_norm", 1.0))
    logging_steps = int(training_config.get("logging_steps", 10))

    generator = torch.Generator()
    generator.manual_seed(seed)
    train_loader = torch.utils.data.DataLoader(
        train_examples,
        batch_size=per_device_train_batch_size,
        shuffle=True,
        collate_fn=list,
        generator=generator,
    )

    started_at = datetime.now(timezone.utc)
    global_step = 0
    optimizer_step = 0
    running_loss = 0.0
    log_history: list[dict[str, float | int]] = []
    saved_checkpoints: list[str] = []

    model.train()
    optimizer.zero_grad(set_to_none=True)
    for epoch_index in range(math.ceil(num_train_epochs)):
        for batch_index, batch in enumerate(train_loader):
            epoch_progress = epoch_index + ((batch_index + 1) / max(len(train_loader), 1))
            if epoch_progress > num_train_epochs + 1e-9:
                break
            prompts = [example.prompt for example in batch]
            candidate_groups = [example.candidates for example in batch]
            with _autocast_context(device=device, bf16=bf16, fp16=fp16):
                scores = _score_candidate_groups(
                    tokenizer=tokenizer,
                    model=model,
                    device=device,
                    prompts=prompts,
                    candidate_groups=candidate_groups,
                    separator=separator,
                    score_mode=score_mode,
                )
                targets = torch.zeros(scores.shape[0], dtype=torch.long, device=device)
                loss = F.cross_entropy(scores, targets) / gradient_accumulation_steps
            loss.backward()
            running_loss += float(loss.item()) * gradient_accumulation_steps
            global_step += 1
            if global_step % gradient_accumulation_steps == 0:
                if max_grad_norm > 0:
                    grad_norm = float(torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm).item())
                else:
                    grad_norm = 0.0
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                optimizer_step += 1

                if optimizer_step % logging_steps == 0:
                    logged_loss = running_loss / logging_steps
                    running_loss = 0.0
                    record = {
                        "loss": round(logged_loss, 3),
                        "grad_norm": round(grad_norm, 3),
                        "learning_rate": f"{scheduler.get_last_lr()[0]:.3e}",
                        "epoch": round(min(epoch_progress, num_train_epochs), 4),
                    }
                    log_history.append(record)
                    print(record)

                if optimizer_step % eval_steps == 0 or optimizer_step == estimated_steps:
                    eval_loss, eval_top1 = _evaluate_loss(
                        model=model,
                        tokenizer=tokenizer,
                        eval_examples=eval_examples,
                        batch_size=per_device_eval_batch_size,
                        device=device,
                        separator=separator,
                        score_mode=score_mode,
                        bf16=bf16,
                        fp16=fp16,
                    )
                    record = {
                        "eval_loss": round(eval_loss, 3),
                        "eval_top1": round(eval_top1, 4),
                        "epoch": round(min(epoch_progress, num_train_epochs), 4),
                    }
                    print(record)

                if optimizer_step % save_steps == 0 or optimizer_step == estimated_steps:
                    checkpoint_dir = run_dir / "checkpoints" / f"checkpoint-{optimizer_step}"
                    _save_checkpoint(model, tokenizer, checkpoint_dir)
                    saved_checkpoints.append(str(checkpoint_dir))

            if optimizer_step >= estimated_steps:
                break
        if optimizer_step >= estimated_steps:
            break

    final_model_dir = run_dir / "final_model"
    _save_checkpoint(model, tokenizer, final_model_dir)
    eval_loss, eval_top1 = _evaluate_loss(
        model=model,
        tokenizer=tokenizer,
        eval_examples=eval_examples,
        batch_size=per_device_eval_batch_size,
        device=device,
        separator=separator,
        score_mode=score_mode,
        bf16=bf16,
        fp16=fp16,
    )
    ended_at = datetime.now(timezone.utc)
    runtime_seconds = (ended_at - started_at).total_seconds()
    train_metrics = {
        "epoch": num_train_epochs,
        "train_runtime": runtime_seconds,
        "train_steps_per_second": optimizer_step / runtime_seconds if runtime_seconds else 0.0,
        "train_loss": sum(float(item["loss"]) for item in log_history) / len(log_history) if log_history else 0.0,
        "optimizer_steps": optimizer_step,
    }
    eval_metrics = {
        "epoch": num_train_epochs,
        "eval_loss": eval_loss,
        "eval_top1": eval_top1,
    }
    write_json(run_dir / "train_metrics.json", train_metrics)
    write_json(run_dir / "eval_metrics.json", eval_metrics)
    write_json(run_dir / "log_history.json", log_history)
    return {
        "run_dir": str(run_dir),
        "final_model_dir": str(final_model_dir),
        "checkpoint_dirs": saved_checkpoints,
        "estimated_optimizer_steps": estimated_steps,
        "train_example_count": len(train_examples),
        "eval_example_count": len(eval_examples),
        "objective": "candidate_ranking",
        "score_mode": score_mode,
        "negatives_per_example": int(dataset_config.get("negatives_per_example", 7)),
        "prompt_sources": {
            "include_direct_probes": bool(dataset_config.get("include_direct_probes", True)),
            "include_qa_train": bool(dataset_config.get("include_qa_train", True)),
        },
        "train_metrics": train_metrics,
        "eval_metrics": eval_metrics,
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "cuda_version": torch.version.cuda,
        "pytorch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "python_version": platform.python_version(),
        "training_uuid": str(uuid.uuid4()),
    }
