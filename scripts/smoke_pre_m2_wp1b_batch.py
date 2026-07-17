#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.training.clm import (
    _answer_char_span,
    _token_label_mask_from_offsets,
    load_training_config,
    resolve_path,
)
from transfer_vs_relearning.utils.io import read_jsonl, sha256_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one WP1B answer-only forward/backward batch without saving weights.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--batch-size", type=int, default=2)
    args = parser.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    repo_root = args.repo_root.resolve()
    config = load_training_config(args.config.resolve())
    dataset = config["dataset"]
    training = config["training"]
    train_path = resolve_path(repo_root, dataset["train_file"])
    rows = read_jsonl(train_path)[: args.batch_size]
    if len(rows) != args.batch_size:
        raise ValueError(f"Requested {args.batch_size} rows but found {len(rows)}")

    model_manifest_path = resolve_path(repo_root, config["model"]["base_model_manifest"])
    model_manifest = json.loads(model_manifest_path.read_text(encoding="utf-8"))
    model_path = Path(model_manifest["local_path_absolute"])
    weights_path = model_path / "model.safetensors"
    declared_hash = model_manifest.get("file_hashes", {}).get("model.safetensors")
    live_hash = sha256_file(weights_path)
    if declared_hash and declared_hash != live_hash:
        raise ValueError(f"Base weight hash mismatch: declared={declared_hash} live={live_hash}")

    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    block_size = int(training["block_size"])
    tokenized = tokenizer(
        [str(row[dataset["text_field"]]) for row in rows],
        add_special_tokens=False,
        truncation=True,
        max_length=block_size - 1,
        padding=False,
        return_offsets_mapping=True,
    )
    batch_input_ids: list[list[int]] = []
    batch_attention_mask: list[list[int]] = []
    batch_labels: list[list[int]] = []
    for row, input_ids, attention_mask, offsets in zip(
        rows,
        tokenized["input_ids"],
        tokenized["attention_mask"],
        tokenized["offset_mapping"],
        strict=True,
    ):
        text = str(row[dataset["text_field"]])
        answer = str(row[dataset["answer_field"]])
        answer_start, answer_end = _answer_char_span(text, answer)
        keep = _token_label_mask_from_offsets(list(offsets), answer_start=answer_start, answer_end=answer_end)
        ids = list(input_ids) + [tokenizer.eos_token_id]
        mask = list(attention_mask) + [1]
        labels = [-100 if not flag else token_id for token_id, flag in zip(ids[:-1], keep, strict=True)]
        labels.append(tokenizer.eos_token_id)
        padding = block_size - len(ids)
        batch_input_ids.append(ids + [tokenizer.pad_token_id] * padding)
        batch_attention_mask.append(mask + [0] * padding)
        batch_labels.append(labels + [-100] * padding)

    device = torch.device("cuda")
    model = AutoModelForCausalLM.from_pretrained(str(model_path), local_files_only=True)
    model.config.use_cache = False
    model.to(device)
    model.train()
    inputs: dict[str, Any] = {
        "input_ids": torch.tensor(batch_input_ids, device=device),
        "attention_mask": torch.tensor(batch_attention_mask, device=device),
        "labels": torch.tensor(batch_labels, device=device),
    }
    autocast_dtype = torch.bfloat16 if bool(training.get("bf16")) else torch.float16
    with torch.autocast(device_type="cuda", dtype=autocast_dtype, enabled=bool(training.get("bf16") or training.get("fp16"))):
        output = model(**inputs)
    if not torch.isfinite(output.loss):
        raise ValueError(f"Non-finite smoke loss: {output.loss.item()}")
    output.loss.backward()
    gradient_tensors = sum(1 for parameter in model.parameters() if parameter.grad is not None)
    if gradient_tensors == 0:
        raise ValueError("Smoke backward pass produced no gradients")
    print(
        json.dumps(
            {
                "status": "passed",
                "config": str(args.config.resolve()),
                "train_sha256": sha256_file(train_path),
                "model_weights_sha256": live_hash,
                "batch_size": args.batch_size,
                "block_size": block_size,
                "loss": float(output.loss.detach().cpu()),
                "gradient_tensors": gradient_tensors,
                "gpu": torch.cuda.get_device_name(0),
                "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
