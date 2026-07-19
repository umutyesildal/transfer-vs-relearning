#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

from transfer_vs_relearning.training.clm import (
    _answer_char_span,
    _token_label_mask_from_offsets,
    load_training_config,
    resolve_path,
)
from transfer_vs_relearning.utils.io import read_jsonl, sha256_file, write_json


def _stats(values: list[int]) -> dict[str, float | int]:
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "min": min(ordered),
        "max": max(ordered),
        "mean": statistics.fmean(ordered),
        "median": statistics.median(ordered),
        "p95": ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit native-tokenizer exposure for one Document 105 candidate.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    from transformers import AutoTokenizer

    repo_root = args.repo_root.resolve()
    config = load_training_config(args.config.resolve())
    dataset = config["dataset"]
    training = config["training"]
    model_manifest_path = resolve_path(repo_root, config["model"]["base_model_manifest"]).resolve()
    model_manifest = json.loads(model_manifest_path.read_text(encoding="utf-8"))
    model_path = Path(model_manifest["local_path_absolute"])
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True, use_fast=True)
    if not tokenizer.is_fast:
        raise ValueError("Answer-only offset audit requires a fast tokenizer")
    if tokenizer.eos_token_id is None:
        raise ValueError("Tokenizer has no EOS token ID")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    block_size = int(training["block_size"])
    text_field, answer_field = str(dataset["text_field"]), str(dataset["answer_field"])
    split_paths = {
        "train": resolve_path(repo_root, dataset["train_file"]).resolve(),
        "validation": resolve_path(repo_root, dataset["validation_file"]).resolve(),
    }
    report: dict[str, Any] = {
        "status": "running",
        "config": str(args.config.resolve()),
        "config_sha256": sha256_file(args.config.resolve()),
        "model_id": model_manifest["model_id"],
        "resolved_revision": model_manifest["resolved_revision"],
        "model_manifest": str(model_manifest_path),
        "model_manifest_sha256": sha256_file(model_manifest_path),
        "tokenizer_class": tokenizer.__class__.__name__,
        "vocab_size": len(tokenizer),
        "block_size": block_size,
        "special_tokens": {
            "bos_token": tokenizer.bos_token,
            "bos_token_id": tokenizer.bos_token_id,
            "eos_token": tokenizer.eos_token,
            "eos_token_id": tokenizer.eos_token_id,
            "pad_token": tokenizer.pad_token,
            "pad_token_id": tokenizer.pad_token_id,
            "unk_token": tokenizer.unk_token,
            "unk_token_id": tokenizer.unk_token_id,
        },
        "splits": {},
    }

    for split, path in split_paths.items():
        rows = read_jsonl(path)
        total_lengths: list[int] = []
        prompt_lengths: list[int] = []
        answer_lengths: list[int] = []
        unknown_tokens = 0
        relation_counts: Counter[str] = Counter()
        representation_counts: Counter[str] = Counter()
        for row in rows:
            text, answer = str(row[text_field]), str(row[answer_field])
            encoded = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
            ids = list(encoded["input_ids"])
            offsets = list(encoded["offset_mapping"])
            answer_start, answer_end = _answer_char_span(text, answer)
            keep = _token_label_mask_from_offsets(offsets, answer_start=answer_start, answer_end=answer_end)
            answer_count = sum(keep)
            total_with_eos = len(ids) + 1
            if total_with_eos > block_size:
                raise ValueError(f"Tokenized row exceeds block size: {row.get('fact_id')} {total_with_eos}>{block_size}")
            total_lengths.append(total_with_eos)
            answer_lengths.append(answer_count)
            prompt_lengths.append(len(ids) - answer_count)
            if tokenizer.unk_token_id is not None:
                unknown_tokens += sum(token_id == tokenizer.unk_token_id for token_id in ids)
            relation_counts[str(row.get("relation", "unknown"))] += 1
            representation_counts[str(row.get("training_representation", "unknown"))] += 1
        report["splits"][split] = {
            "path": str(path),
            "sha256": sha256_file(path),
            "rows": len(rows),
            "total_tokens_with_eos": _stats(total_lengths),
            "prompt_tokens": _stats(prompt_lengths),
            "answer_tokens": _stats(answer_lengths),
            "multi_token_answers": sum(value > 1 for value in answer_lengths),
            "multi_token_answer_fraction": sum(value > 1 for value in answer_lengths) / len(answer_lengths),
            "unknown_token_occurrences": unknown_tokens,
            "truncated_rows": 0,
            "relation_counts": dict(sorted(relation_counts.items())),
            "representation_counts": dict(sorted(representation_counts.items())),
        }
    train_answer_tokens = int(sum(
        len(tokenizer(str(row[answer_field]), add_special_tokens=False)["input_ids"])
        for row in read_jsonl(split_paths["train"])
    ))
    report["train_answer_tokens_per_epoch_naive_answer_only"] = train_answer_tokens
    report["train_answer_tokens_over_36_epochs_naive_answer_only"] = train_answer_tokens * 36
    report["note"] = "Offset-aligned supervised-token counts in split statistics are authoritative; naive answer-only counts are an additional segmentation diagnostic. EOS is not supervised."
    report["status"] = "passed"
    write_json(args.output.resolve(), report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
