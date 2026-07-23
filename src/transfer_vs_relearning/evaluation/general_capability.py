from __future__ import annotations

import json
import math
import platform
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from transfer_vs_relearning.evaluation.evaluator import (
    _manifest_local_path,
    _resolve_path,
    _resolve_tokenizer_path,
)
from transfer_vs_relearning.evaluation.scoring import score_candidate_batch
from transfer_vs_relearning.utils.io import (
    read_csv_rows,
    read_jsonl,
    sha256_file,
    sha256_text,
    write_csv,
    write_json,
)


def split_token_ids(token_ids: list[int], block_size: int, minimum_tokens: int = 2) -> list[list[int]]:
    if block_size < 2:
        raise ValueError("block_size must be at least 2")
    if minimum_tokens < 2 or minimum_tokens > block_size:
        raise ValueError("minimum_tokens must be in [2, block_size]")
    return [
        token_ids[start : start + block_size]
        for start in range(0, len(token_ids), block_size)
        if len(token_ids[start : start + block_size]) >= minimum_tokens
    ]


def repeated_ngram_fraction(token_ids: list[int], n: int) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    ngrams = [tuple(token_ids[index : index + n]) for index in range(len(token_ids) - n + 1)]
    if not ngrams:
        return 0.0
    counts = Counter(ngrams)
    repeated_occurrences = sum(count for count in counts.values() if count > 1)
    return repeated_occurrences / len(ngrams)


def distinct_ngram_ratio(token_ids: list[int], n: int) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    ngrams = [tuple(token_ids[index : index + n]) for index in range(len(token_ids) - n + 1)]
    return len(set(ngrams)) / len(ngrams) if ngrams else 0.0


def longest_repeated_token_run(token_ids: list[int]) -> int:
    longest = 0
    current = 0
    previous: int | None = None
    for token_id in token_ids:
        if token_id == previous:
            current += 1
        else:
            previous = token_id
            current = 1
        longest = max(longest, current)
    return longest


def has_lexical_content(text: str) -> bool:
    """Return whether decoded generation text contains a Unicode letter or number."""
    return any(character.isalnum() for character in text)


def generation_metrics(token_ids: list[int], text: str, synthetic_subjects: Iterable[str]) -> dict[str, Any]:
    normalized_text = text.casefold()
    intrusions = sorted(
        subject for subject in synthetic_subjects if subject and subject.casefold() in normalized_text
    )
    near_empty_by_token_length = len(token_ids) <= 2
    return {
        "generated_token_count": len(token_ids),
        # Preserve the historical length-only diagnostic for strict sensitivity reporting.
        "empty_or_near_empty": near_empty_by_token_length,
        "near_empty_by_token_length": near_empty_by_token_length,
        # Hard empty-generation decisions use decoded lexical content, not token count.
        "empty_generation": not has_lexical_content(text),
        "distinct_1": distinct_ngram_ratio(token_ids, 1),
        "distinct_2": distinct_ngram_ratio(token_ids, 2),
        "distinct_3": distinct_ngram_ratio(token_ids, 3),
        "repeated_3gram_fraction": repeated_ngram_fraction(token_ids, 3),
        "repeated_4gram_fraction": repeated_ngram_fraction(token_ids, 4),
        "longest_repeated_token_run": longest_repeated_token_run(token_ids),
        "synthetic_subject_intrusion_count": len(intrusions),
        "synthetic_subject_intrusions": intrusions,
    }


def bootstrap_weighted_nll_interval(
    rows: list[dict[str, Any]],
    *,
    samples: int = 2000,
    seed: int = 42,
    alpha: float = 0.05,
) -> tuple[float, float]:
    if not rows:
        raise ValueError("Cannot bootstrap an empty block list")
    nll_sums = np.asarray([float(row["nll_sum"]) for row in rows], dtype=np.float64)
    token_counts = np.asarray([int(row["token_count"]) for row in rows], dtype=np.int64)
    rng = np.random.default_rng(seed)
    estimates = np.empty(samples, dtype=np.float64)
    for index in range(samples):
        sampled = rng.integers(0, len(rows), size=len(rows))
        estimates[index] = nll_sums[sampled].sum() / token_counts[sampled].sum()
    lower, upper = np.quantile(estimates, [alpha / 2.0, 1.0 - alpha / 2.0])
    return float(lower), float(upper)


def classify_perplexity_ratio(ratio: float) -> str:
    if ratio <= 1.10:
        return "no_material_generic_loss_degradation_detected"
    if ratio <= 1.25:
        return "measurable_generic_loss_drift"
    return "material_generic_loss_degradation_flag"


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _dump_yaml(path: Path, payload: dict[str, Any]) -> None:
    import yaml

    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=True, allow_unicode=True)


def _load_model(config: dict[str, Any]) -> tuple[Any, Any, str, dict[str, Any], Path, Path]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    manifest_path = _resolve_path(config["model_manifest"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    model_path = _manifest_local_path(manifest, manifest_path.parent)
    tokenizer_path = _resolve_tokenizer_path(manifest, manifest_path)
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    use_bf16 = (
        bool(config.get("runtime", {}).get("bf16"))
        and torch.cuda.is_available()
        and torch.cuda.is_bf16_supported()
    )
    dtype = torch.bfloat16 if use_bf16 else None
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        local_files_only=True,
        torch_dtype=dtype,
    )
    requested_device = config.get("runtime", {}).get("device", "cuda")
    device = "cuda" if requested_device == "cuda" and torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    return tokenizer, model, device, manifest, manifest_path, tokenizer_path


def _tokenize_corpus(tokenizer: Any, documents: list[str]) -> list[int]:
    eos_token_id = tokenizer.eos_token_id
    if eos_token_id is None:
        raise ValueError("Tokenizer must define eos_token_id")
    token_ids: list[int] = []
    for document in documents:
        encoded = tokenizer(document, add_special_tokens=False)["input_ids"]
        if encoded:
            token_ids.extend(int(token_id) for token_id in encoded)
            token_ids.append(int(eos_token_id))
    if len(token_ids) < 2:
        raise ValueError("Generic corpus produced fewer than two tokens")
    return token_ids


def _score_full_blocks(
    model: Any,
    device: str,
    blocks: list[list[int]],
    batch_size: int,
) -> list[dict[str, Any]]:
    import torch
    import torch.nn.functional as F

    rows: list[dict[str, Any]] = []
    full_length = len(blocks[0]) if blocks else 0
    full_blocks = [block for block in blocks if len(block) == full_length]
    tail_blocks = [block for block in blocks if len(block) != full_length]

    def score_batch(batch: list[list[int]], start_index: int) -> None:
        input_ids = torch.tensor(batch, dtype=torch.long, device=device)
        with torch.inference_mode():
            logits = model(input_ids=input_ids).logits.float()
        losses = F.cross_entropy(
            logits[:, :-1, :].transpose(1, 2),
            input_ids[:, 1:],
            reduction="none",
        )
        for row_index in range(losses.shape[0]):
            nll_sum = float(losses[row_index].sum().item())
            token_count = int(losses.shape[1])
            rows.append(
                {
                    "block_index": start_index + row_index,
                    "input_token_count": len(batch[row_index]),
                    "token_count": token_count,
                    "nll_sum": nll_sum,
                    "mean_nll": nll_sum / token_count,
                }
            )

    for start in range(0, len(full_blocks), batch_size):
        score_batch(full_blocks[start : start + batch_size], start)
    for tail in tail_blocks:
        score_batch([tail], len(rows))
    return rows


def _score_generic_completions(
    tokenizer: Any,
    model: Any,
    device: str,
    items: list[dict[str, Any]],
    candidate_batch_size: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        candidates = [str(candidate) for candidate in item["candidates"]]
        scores: list[dict[str, float | int]] = []
        for start in range(0, len(candidates), candidate_batch_size):
            scores.extend(
                score_candidate_batch(
                    tokenizer,
                    model,
                    device,
                    str(item["prompt"]),
                    candidates[start : start + candidate_batch_size],
                    str(item.get("answer_separator", " ")),
                )
            )
        scored = [dict(score, candidate=candidate) for candidate, score in zip(candidates, scores)]
        ordered = sorted(scored, key=lambda row: (-float(row["mean_logprob"]), str(row["candidate"])))
        correct = str(item["correct_answer"])
        correct_rank = next(index + 1 for index, row in enumerate(ordered) if row["candidate"] == correct)
        rows.append(
            {
                "item_id": item["id"],
                "category": item["category"],
                "prompt": item["prompt"],
                "correct_answer": correct,
                "predicted_answer": ordered[0]["candidate"],
                "correct_rank": correct_rank,
                "top1_correct": correct_rank == 1,
                "correct_mean_logprob": next(
                    float(row["mean_logprob"]) for row in ordered if row["candidate"] == correct
                ),
                "best_mean_logprob": float(ordered[0]["mean_logprob"]),
                "ordered_candidates_json": json.dumps(ordered, ensure_ascii=False, sort_keys=True),
            }
        )
    return rows


def _run_generations(
    tokenizer: Any,
    model: Any,
    device: str,
    prompts: list[dict[str, Any]],
    synthetic_subjects: list[str],
    max_new_tokens: int,
) -> list[dict[str, Any]]:
    import torch

    rows: list[dict[str, Any]] = []
    eos_token_id = tokenizer.eos_token_id
    pad_token_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else eos_token_id
    for item in prompts:
        prompt = str(item["prompt"])
        encoded = tokenizer(prompt, return_tensors="pt")
        input_ids = encoded["input_ids"].to(device)
        attention_mask = encoded.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(device)
        with torch.inference_mode():
            generated = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                do_sample=False,
                max_new_tokens=max_new_tokens,
                eos_token_id=eos_token_id,
                pad_token_id=pad_token_id,
            )
        continuation_ids = generated[0, input_ids.shape[1] :].tolist()
        continuation = tokenizer.decode(continuation_ids, skip_special_tokens=True)
        metrics = generation_metrics(continuation_ids, continuation, synthetic_subjects)
        rows.append(
            {
                "prompt_id": item["id"],
                "category": item["category"],
                "prompt": prompt,
                "continuation": continuation,
                "continuation_token_ids": continuation_ids,
                "ended_with_eos": bool(continuation_ids and continuation_ids[-1] == eos_token_id),
                **metrics,
            }
        )
    return rows


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def run_general_capability(config_path: Path) -> Path:
    import torch
    import transformers

    config_path = config_path.resolve()
    config = _load_yaml(config_path)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_root = _resolve_path(config["output_root"])
    run_dir = output_root / f"{timestamp}_{config['run_name']}"
    run_dir.mkdir(parents=True, exist_ok=False)
    _dump_yaml(run_dir / "resolved_config.yaml", config)
    started = datetime.now(timezone.utc).isoformat()

    corpus_path = _resolve_path(config["data"]["corpus_file"])
    prompts_path = _resolve_path(config["data"]["prompts_file"])
    completions_path = _resolve_path(config["data"]["completions_file"])
    subjects_path = _resolve_path(config["data"]["synthetic_subjects_file"])
    documents = [str(row["text"]) for row in read_jsonl(corpus_path) if str(row.get("text", "")).strip()]
    prompts = read_jsonl(prompts_path)
    completion_items = read_jsonl(completions_path)
    synthetic_subjects = [row["subject"] for row in read_csv_rows(subjects_path)]

    normalized_corpus = "\n".join(documents).casefold()
    corpus_intrusions = sorted(subject for subject in synthetic_subjects if subject.casefold() in normalized_corpus)
    if corpus_intrusions:
        raise ValueError(
            f"Generic corpus contains {len(corpus_intrusions)} synthetic full subject names; first={corpus_intrusions[0]!r}"
        )

    tokenizer, model, device, manifest, manifest_path, tokenizer_path = _load_model(config)
    token_ids = _tokenize_corpus(tokenizer, documents)
    block_size = int(config["scoring"].get("block_size", 512))
    blocks = split_token_ids(token_ids, block_size)
    token_hash = sha256_text(json.dumps(token_ids, separators=(",", ":")))
    loss_rows = _score_full_blocks(
        model,
        device,
        blocks,
        int(config["scoring"].get("batch_size", 4)),
    )
    write_csv(run_dir / "generic_loss_blocks.csv", loss_rows)

    total_nll = sum(float(row["nll_sum"]) for row in loss_rows)
    total_tokens = sum(int(row["token_count"]) for row in loss_rows)
    mean_nll = total_nll / total_tokens
    ci_low, ci_high = bootstrap_weighted_nll_interval(
        loss_rows,
        samples=int(config["scoring"].get("bootstrap_samples", 2000)),
        seed=int(config["runtime"].get("seed", 42)),
    )

    completion_rows = _score_generic_completions(
        tokenizer,
        model,
        device,
        completion_items,
        int(config["scoring"].get("candidate_batch_size", 16)),
    )
    write_csv(run_dir / "generic_completion_results.csv", completion_rows)

    generation_rows = _run_generations(
        tokenizer,
        model,
        device,
        prompts,
        synthetic_subjects,
        int(config["generation"].get("max_new_tokens", 64)),
    )
    _write_jsonl(run_dir / "generations.jsonl", generation_rows)

    completion_accuracy = sum(bool(row["top1_correct"]) for row in completion_rows) / len(completion_rows)
    summary = {
        "completion_status": "completed",
        "generic_loss": {
            "document_count": len(documents),
            "block_count": len(loss_rows),
            "input_token_count": len(token_ids),
            "scored_token_count": total_tokens,
            "mean_token_nll": mean_nll,
            "mean_token_nll_ci95": [ci_low, ci_high],
            "perplexity": math.exp(mean_nll),
            "perplexity_ci95_from_nll": [math.exp(ci_low), math.exp(ci_high)],
            "token_ids_sha256": token_hash,
        },
        "generic_completions": {
            "item_count": len(completion_rows),
            "top1_count": sum(bool(row["top1_correct"]) for row in completion_rows),
            "top1_accuracy": completion_accuracy,
            "mean_correct_rank": sum(int(row["correct_rank"]) for row in completion_rows) / len(completion_rows),
        },
        "generation": {
            "prompt_count": len(generation_rows),
            "empty_or_near_empty_count": sum(bool(row["empty_or_near_empty"]) for row in generation_rows),
            "near_empty_by_token_length_count": sum(
                bool(row["near_empty_by_token_length"]) for row in generation_rows
            ),
            "empty_generation_count": sum(bool(row["empty_generation"]) for row in generation_rows),
            "ended_with_eos_count": sum(bool(row["ended_with_eos"]) for row in generation_rows),
            "synthetic_subject_intrusion_count": sum(
                int(row["synthetic_subject_intrusion_count"]) for row in generation_rows
            ),
            "mean_repeated_3gram_fraction": sum(
                float(row["repeated_3gram_fraction"]) for row in generation_rows
            )
            / len(generation_rows),
            "mean_repeated_4gram_fraction": sum(
                float(row["repeated_4gram_fraction"]) for row in generation_rows
            )
            / len(generation_rows),
            "mean_distinct_2": sum(float(row["distinct_2"]) for row in generation_rows) / len(generation_rows),
            "max_repeated_token_run": max(int(row["longest_repeated_token_run"]) for row in generation_rows),
        },
    }
    write_json(run_dir / "summary_metrics.json", summary)
    write_json(run_dir / "errors.json", {"errors": []})
    ended = datetime.now(timezone.utc).isoformat()
    write_json(
        run_dir / "run_manifest.json",
        {
            "run_name": config["run_name"],
            "git_commit": _git_commit(),
            "model_manifest": str(manifest_path),
            "model_manifest_sha256": sha256_file(manifest_path),
            "model_id": manifest.get("model_id"),
            "model_revision": manifest.get("resolved_revision"),
            "local_model_snapshot": str(_manifest_local_path(manifest, manifest_path.parent)),
            "local_tokenizer_snapshot": str(tokenizer_path),
            "corpus_file": str(corpus_path),
            "corpus_sha256": sha256_file(corpus_path),
            "prompts_file": str(prompts_path),
            "prompts_sha256": sha256_file(prompts_path),
            "completions_file": str(completions_path),
            "completions_sha256": sha256_file(completions_path),
            "synthetic_subjects_file": str(subjects_path),
            "synthetic_subjects_sha256": sha256_file(subjects_path),
            "corpus_synthetic_full_name_matches": 0,
            "token_ids_sha256": token_hash,
            "dtype": str(next(model.parameters()).dtype),
            "device": device,
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cuda_version": torch.version.cuda,
            "pytorch_version": torch.__version__,
            "transformers_version": transformers.__version__,
            "python_version": platform.python_version(),
            "start_time": started,
            "end_time": ended,
            "completion_status": "completed",
        },
    )
    return run_dir


def compare_general_capability(
    base_summary_path: Path,
    seed42_summary_path: Path,
    seed43_summary_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    payloads = {
        "base": json.loads(base_summary_path.read_text(encoding="utf-8")),
        "seed42": json.loads(seed42_summary_path.read_text(encoding="utf-8")),
        "seed43": json.loads(seed43_summary_path.read_text(encoding="utf-8")),
    }
    base_ppl = float(payloads["base"]["generic_loss"]["perplexity"])
    comparisons: dict[str, Any] = {}
    for label in ("seed42", "seed43"):
        ppl = float(payloads[label]["generic_loss"]["perplexity"])
        ratio = ppl / base_ppl
        comparisons[label] = {
            "perplexity": ppl,
            "perplexity_ratio_vs_base": ratio,
            "generic_loss_interpretation": classify_perplexity_ratio(ratio),
            "generic_completion_accuracy": payloads[label]["generic_completions"]["top1_accuracy"],
            "generic_completion_accuracy_change_vs_base": float(
                payloads[label]["generic_completions"]["top1_accuracy"]
            )
            - float(payloads["base"]["generic_completions"]["top1_accuracy"]),
            "generation": payloads[label]["generation"],
        }
    output = {
        "base": {
            "perplexity": base_ppl,
            "generic_completion_accuracy": payloads["base"]["generic_completions"]["top1_accuracy"],
            "generation": payloads["base"]["generation"],
        },
        "comparisons": comparisons,
        "input_summaries": {
            "base": str(base_summary_path.resolve()),
            "seed42": str(seed42_summary_path.resolve()),
            "seed43": str(seed43_summary_path.resolve()),
        },
    }
    write_json(output_path, output)
    return output
