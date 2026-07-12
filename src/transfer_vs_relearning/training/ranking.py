from __future__ import annotations

import hashlib
import inspect
import json
import math
import platform
import random
import re
import subprocess
import uuid
from collections import Counter
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


RELATION_CONDITIONED_PROMPTS = {
    "profession": (
        "Identify the profession associated with {subject}:",
        "What occupation is recorded for {subject}?",
        "For the person {subject}, select the correct profession:",
    ),
    "born_in": (
        "Identify the birthplace associated with {subject}:",
        "In which place was {subject} born?",
        "For the person {subject}, select the correct place of birth:",
    ),
    "lives_in": (
        "Identify the current residence associated with {subject}:",
        "In which place does {subject} currently reside?",
        "For the person {subject}, select the correct place of residence:",
    ),
    "field_of_study": (
        "Identify the field of study associated with {subject}:",
        "Which academic field is recorded for {subject}?",
        "For the person {subject}, select the correct field of study:",
    ),
    "works_in_industry": (
        "Identify the work industry associated with {subject}:",
        "In which industry does {subject} work?",
        "For the person {subject}, select the correct industry:",
    ),
}


def _git_commit(repo_root: Path | None = None) -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return None


def _tokenizer_path_from_manifest(
    manifest: dict[str, Any],
    *,
    repo_root: Path,
    model_path: Path,
) -> Path:
    absolute = manifest.get("tokenizer_source_path_absolute")
    if absolute:
        return Path(str(absolute)).resolve()
    project_relative = manifest.get("tokenizer_source_path")
    if project_relative:
        return resolve_path(repo_root, str(project_relative)).resolve()
    return model_path


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


def _balanced_cycle_negative_sample(
    *,
    fact_id: str,
    relation: str,
    prompt_index: int,
    correct_answer: str,
    candidates: list[str],
    negatives_per_example: int,
    seed: int,
) -> tuple[str, ...]:
    eligible = sorted(candidate for candidate in candidates if candidate != correct_answer)
    if negatives_per_example > len(eligible):
        raise ValueError(f"Requested {negatives_per_example} negatives for {relation}, only {len(eligible)} available")
    key = f"{seed}:{fact_id}:{relation}".encode("utf-8")
    base = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    start = (base + prompt_index * negatives_per_example) % len(eligible)
    return tuple(eligible[(start + offset) % len(eligible)] for offset in range(negatives_per_example))


def _negative_sample(
    *,
    strategy: str,
    fact_id: str,
    relation: str,
    prompt_index: int,
    correct_answer: str,
    candidates: list[str],
    negatives_per_example: int,
    seed: int,
) -> tuple[str, ...]:
    if strategy == "balanced_cycle":
        return _balanced_cycle_negative_sample(
            fact_id=fact_id,
            relation=relation,
            prompt_index=prompt_index,
            correct_answer=correct_answer,
            candidates=candidates,
            negatives_per_example=negatives_per_example,
            seed=seed,
        )
    if strategy == "random":
        return _stable_negative_sample(
            fact_id=fact_id,
            relation=relation,
            correct_answer=correct_answer,
            candidates=candidates,
            negatives_per_example=negatives_per_example,
            seed=seed,
        )
    raise ValueError(f"Unknown negative sampling strategy: {strategy}")


def build_ranking_examples(
    *,
    dataset_dir: Path,
    include_direct_probes: bool,
    include_qa_train: bool,
    negatives_per_example: int,
    seed: int,
    training_jsonl: Path | None = None,
    negative_strategy: str = "random",
    relations: list[str] | tuple[str, ...] | None = None,
    include_relation_conditioned_prompts: bool = False,
    include_training_jsonl_prompts: bool = True,
) -> list[RankingExample]:
    canonical_rows = read_csv_rows(dataset_dir / DATASET_FILES["canonical_profiles"])
    canonical_by_subject = {row["subject_id"]: row for row in canonical_rows}
    inventories = build_candidate_inventories(canonical_rows)
    examples: list[RankingExample] = []
    selected_relations = set(relations) if relations else None

    if training_jsonl is not None and include_training_jsonl_prompts:
        prompt_counts: Counter[tuple[str, str]] = Counter()
        for row in read_jsonl(training_jsonl):
            fact_id = str(row["fact_id"])
            relation = str(row["relation"])
            if selected_relations is not None and relation not in selected_relations:
                continue
            correct_answer = str(row["answer"])
            prompt_index = prompt_counts[(fact_id, relation)]
            prompt_counts[(fact_id, relation)] += 1
            if negative_strategy == "paired_city":
                if negatives_per_example != 1:
                    raise ValueError("paired_city requires exactly one negative per example")
                if relation not in {"born_in", "lives_in"}:
                    raise ValueError(f"paired_city is only valid for city relations, found {relation}")
                profile = canonical_by_subject[str(row["subject_id"])]
                expected = profile["birthplace_en"] if relation == "born_in" else profile["residence_en"]
                negative = profile["residence_en"] if relation == "born_in" else profile["birthplace_en"]
                if correct_answer != expected:
                    raise ValueError(f"Unexpected answer for paired_city fact {fact_id}: {correct_answer!r}")
                if negative == correct_answer:
                    raise ValueError(f"paired_city requires distinct city surfaces for {fact_id}")
                negative_answers = (negative,)
            else:
                family = RELATION_TO_FAMILY[relation]
                negative_answers = _negative_sample(
                    strategy=negative_strategy,
                    fact_id=fact_id,
                    relation=relation,
                    prompt_index=prompt_index,
                    correct_answer=correct_answer,
                    candidates=[candidate.object_en for candidate in inventories[family]],
                    negatives_per_example=negatives_per_example,
                    seed=seed,
                )
            examples.append(
                RankingExample(
                    fact_id=fact_id,
                    relation=relation,
                    prompt=_prompt_from_answer_row(str(row["text"]), correct_answer),
                    correct_answer=correct_answer,
                    negative_answers=negative_answers,
                    prompt_style=str(row.get("template_id", "training_jsonl")),
                )
            )

    if include_direct_probes:
        for row in read_csv_rows(dataset_dir / DATASET_FILES["probes_en"]):
            if selected_relations is not None and row["relation"] not in selected_relations:
                continue
            family = RELATION_TO_FAMILY[row["relation"]]
            correct = resolve_expected_answer(row["relation"], "en", row["expected_answer"], inventories)
            negative_answers = _negative_sample(
                strategy=negative_strategy,
                fact_id=row["fact_id"],
                relation=row["relation"],
                prompt_index=0,
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
            if selected_relations is not None and str(row["relation"]) not in selected_relations:
                continue
            family = RELATION_TO_FAMILY[str(row["relation"])]
            correct_answer = str(row["answer"])
            negative_answers = _negative_sample(
                strategy=negative_strategy,
                fact_id=str(row["fact_id"]),
                relation=str(row["relation"]),
                prompt_index=0,
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

    if include_relation_conditioned_prompts:
        if training_jsonl is None:
            raise ValueError("Relation-conditioned prompts require training_jsonl")
        facts: dict[str, dict[str, str]] = {}
        for row in read_jsonl(training_jsonl):
            relation = str(row["relation"])
            if selected_relations is not None and relation not in selected_relations:
                continue
            facts.setdefault(
                str(row["fact_id"]),
                {
                    "fact_id": str(row["fact_id"]),
                    "subject_id": str(row["subject_id"]),
                    "subject": str(row["subject"]),
                    "relation": relation,
                    "answer": str(row["answer"]),
                },
            )
        for fact_id in sorted(facts):
            fact = facts[fact_id]
            relation = fact["relation"]
            templates = RELATION_CONDITIONED_PROMPTS.get(relation)
            if templates is None:
                raise ValueError(f"No relation-conditioned prompts for relation: {relation}")
            family = RELATION_TO_FAMILY[relation]
            inventory = [candidate.object_en for candidate in inventories[family]]
            for prompt_index, template in enumerate(templates):
                negative_answers = list(
                    _negative_sample(
                        strategy="balanced_cycle",
                        fact_id=fact_id,
                        relation=relation,
                        prompt_index=prompt_index,
                        correct_answer=fact["answer"],
                        candidates=inventory,
                        negatives_per_example=negatives_per_example,
                        seed=seed,
                    )
                )
                if relation in {"born_in", "lives_in"}:
                    profile = canonical_by_subject[fact["subject_id"]]
                    paired_city = profile["residence_en"] if relation == "born_in" else profile["birthplace_en"]
                    if paired_city != fact["answer"] and paired_city not in negative_answers:
                        negative_answers[-1] = paired_city
                examples.append(
                    RankingExample(
                        fact_id=fact_id,
                        relation=relation,
                        prompt=template.format(subject=fact["subject"]),
                        correct_answer=fact["answer"],
                        negative_answers=tuple(negative_answers),
                        prompt_style=f"relation_conditioned_{prompt_index + 1:02d}",
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
    if dataset.get("training_jsonl"):
        training_jsonl = resolve_path(repo_root, dataset["training_jsonl"])
        payload["dataset"]["training_jsonl"] = str(training_jsonl)
        payload["dataset"]["training_jsonl_sha256"] = sha256_file(training_jsonl)
        payload["objective"]["negative_strategy"] = dataset.get("negative_strategy", "random")
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
        training_jsonl=(
            resolve_path(repo_root, dataset_config["training_jsonl"])
            if dataset_config.get("training_jsonl")
            else None
        ),
        negative_strategy=str(dataset_config.get("negative_strategy", "random")),
        relations=dataset_config.get("relations"),
        include_relation_conditioned_prompts=bool(dataset_config.get("include_relation_conditioned_prompts", False)),
        include_training_jsonl_prompts=bool(dataset_config.get("include_training_jsonl_prompts", True)),
    )
    rng = random.Random(int(dataset_config.get("split_seed", seed)))
    indices = list(range(len(examples)))
    rng.shuffle(indices)
    validation_fraction = float(dataset_config.get("validation_fraction", 0.02))
    if not 0 <= validation_fraction < 1:
        raise ValueError("validation_fraction must be in [0, 1)")
    eval_count = round(len(indices) * validation_fraction)
    eval_indices = set(indices[:eval_count])
    train_examples = [example for index, example in enumerate(examples) if index not in eval_indices]
    eval_examples = [example for index, example in enumerate(examples) if index in eval_indices]

    model_manifest = json.loads(resolve_path(repo_root, model_config["base_model_manifest"]).read_text(encoding="utf-8"))
    model_path = Path(model_manifest["local_path_absolute"])
    tokenizer_path = _tokenizer_path_from_manifest(
        model_manifest,
        repo_root=repo_root,
        model_path=model_path,
    )
    local_files_only = bool(runtime_config.get("local_files_only", True))
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=local_files_only, use_fast=True)
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
        "negative_strategy": str(dataset_config.get("negative_strategy", "random")),
        "prompt_sources": {
            "training_jsonl": dataset_config.get("training_jsonl"),
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
