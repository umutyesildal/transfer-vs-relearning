#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gc
import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from transfer_vs_relearning.experiments.m1_cross_family import approved_scratch
from transfer_vs_relearning.training.clm import (
    _answer_char_span,
    _answer_only_labels,
    _token_label_mask_from_offsets,
    load_training_config,
    resolve_path,
)
from transfer_vs_relearning.utils.io import read_jsonl, sha256_file, write_json


def _verify_base_weights(model_path: Path, manifest: dict[str, Any]) -> dict[str, str]:
    declared = {
        name: digest
        for name, digest in manifest.get("file_hashes", {}).items()
        if name.endswith(".safetensors")
    }
    if not declared:
        raise ValueError("Base manifest contains no safetensors hashes")
    for relative, expected in declared.items():
        path = model_path / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise ValueError(f"Base weight hash mismatch: {relative}")
    return declared


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Document 105 masking, CUDA, and checkpoint round-trip smoke gates.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--batch-size", type=int, default=2)
    args = parser.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    repo_root = args.repo_root.resolve()
    config = load_training_config(args.config.resolve())
    dataset, training = config["dataset"], config["training"]
    train_path = resolve_path(repo_root, dataset["train_file"]).resolve()
    rows = read_jsonl(train_path)
    model_manifest_path = resolve_path(repo_root, config["model"]["base_model_manifest"]).resolve()
    model_manifest = json.loads(model_manifest_path.read_text(encoding="utf-8"))
    model_path = Path(model_manifest["local_path_absolute"])
    declared_weight_hashes = _verify_base_weights(model_path, model_manifest)

    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True, use_fast=True)
    if not tokenizer.is_fast or tokenizer.eos_token_id is None:
        raise ValueError("Candidate requires a fast tokenizer with EOS for answer-only masking")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    block_size = int(training["block_size"])
    text_field, answer_field = str(dataset["text_field"]), str(dataset["answer_field"])

    coverage: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row["relation"]), str(row["training_representation"]))
        coverage.setdefault(key, row)
    expected_relations = {"profession", "born_in", "lives_in", "field_of_study", "works_in_industry"}
    expected_representations = {"decl_01", "decl_02", "decl_03", "form_a_qa", "form_a_direct", "form_b_qa", "form_b_direct"}
    if set(relation for relation, _ in coverage) != expected_relations or set(representation for _, representation in coverage) != expected_representations or len(coverage) != 35:
        raise ValueError("Masking smoke coverage is not the frozen 5 relations x 7 representations")

    supervised_by_relation: defaultdict[str, int] = defaultdict(int)
    supervised_by_representation: defaultdict[str, int] = defaultdict(int)
    for (relation, representation), row in coverage.items():
        text, answer = str(row[text_field]), str(row[answer_field])
        encoded = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
        answer_start, answer_end = _answer_char_span(text, answer)
        keep = _token_label_mask_from_offsets(list(encoded["offset_mapping"]), answer_start=answer_start, answer_end=answer_end)
        if len(encoded["input_ids"]) + 1 > block_size:
            raise ValueError(f"Masking smoke row exceeds block size: {relation}/{representation}")
        supervised_by_relation[relation] += sum(keep)
        supervised_by_representation[representation] += sum(keep)

    batch_rows = list(coverage.values())[: args.batch_size]
    encoded_batch = tokenizer(
        [str(row[text_field]) for row in batch_rows],
        add_special_tokens=False,
        return_offsets_mapping=True,
    )
    batch_input_ids: list[list[int]] = []
    batch_attention_mask: list[list[int]] = []
    batch_labels: list[list[int]] = []
    for row, ids, attention, offsets in zip(batch_rows, encoded_batch["input_ids"], encoded_batch["attention_mask"], encoded_batch["offset_mapping"], strict=True):
        text, answer = str(row[text_field]), str(row[answer_field])
        answer_start, answer_end = _answer_char_span(text, answer)
        keep = _token_label_mask_from_offsets(list(offsets), answer_start=answer_start, answer_end=answer_end)
        ids_with_eos = list(ids) + [tokenizer.eos_token_id]
        labels = _answer_only_labels(list(ids), keep, tokenizer.eos_token_id, supervise_eos=False)
        padding = block_size - len(ids_with_eos)
        batch_input_ids.append(ids_with_eos + [tokenizer.pad_token_id] * padding)
        batch_attention_mask.append(list(attention) + [1] + [0] * padding)
        batch_labels.append(labels + [-100] * padding)

    device = torch.device("cuda")
    model = AutoModelForCausalLM.from_pretrained(str(model_path), local_files_only=True, low_cpu_mem_usage=True)
    model.config.use_cache = False
    model.to(device)
    model.train()
    inputs = {
        "input_ids": torch.tensor(batch_input_ids, device=device),
        "attention_mask": torch.tensor(batch_attention_mask, device=device),
        "labels": torch.tensor(batch_labels, device=device),
    }
    with torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=bool(training.get("bf16"))):
        output = model(**inputs)
    if not torch.isfinite(output.loss):
        raise ValueError(f"Non-finite smoke loss: {output.loss.item()}")
    output.loss.backward()
    smoke_loss = float(output.loss.detach().cpu())
    gradient_tensors = sum(1 for parameter in model.parameters() if parameter.grad is not None)
    if gradient_tensors == 0:
        raise ValueError("Smoke backward pass produced no gradients")
    peak_allocated_bytes = torch.cuda.max_memory_allocated()

    checkpoint_dir = approved_scratch(args.checkpoint_dir.resolve())
    if checkpoint_dir.exists():
        raise FileExistsError(f"Smoke checkpoint already exists: {checkpoint_dir}")
    model.save_pretrained(checkpoint_dir, safe_serialization=True)
    tokenizer.save_pretrained(checkpoint_dir)
    checkpoint_files = sorted(path for path in checkpoint_dir.iterdir() if path.is_file())
    checkpoint_bytes = sum(path.stat().st_size for path in checkpoint_files)
    checkpoint_hashes = {path.name: sha256_file(path) for path in checkpoint_files if path.suffix == ".safetensors"}
    del output, inputs, model
    gc.collect()
    torch.cuda.empty_cache()
    reloaded = AutoModelForCausalLM.from_pretrained(str(checkpoint_dir), local_files_only=True, low_cpu_mem_usage=True, torch_dtype="auto")
    reload_class = reloaded.__class__.__name__
    reload_parameters = sum(parameter.numel() for parameter in reloaded.parameters())
    del reloaded
    gc.collect()

    report = {
        "status": "passed",
        "config": str(args.config.resolve()),
        "config_sha256": sha256_file(args.config.resolve()),
        "model_id": model_manifest["model_id"],
        "resolved_revision": model_manifest["resolved_revision"],
        "base_weight_files_verified": len(declared_weight_hashes),
        "masking_coverage_cells": len(coverage),
        "supervised_tokens_by_relation": dict(sorted(supervised_by_relation.items())),
        "supervised_tokens_by_representation": dict(sorted(supervised_by_representation.items())),
        "batch_size": args.batch_size,
        "loss": smoke_loss,
        "gradient_tensors": gradient_tensors,
        "gpu": torch.cuda.get_device_name(0),
        "peak_allocated_bytes": peak_allocated_bytes,
        "checkpoint_files": len(checkpoint_files),
        "checkpoint_bytes": checkpoint_bytes,
        "checkpoint_weight_hashes": checkpoint_hashes,
        "reload_class": reload_class,
        "reload_parameters": reload_parameters,
        "checkpoint_cleanup": "completed_after_successful_reload",
    }
    # The checkpoint is a reproducible smoke artifact, never a selected scientific model.
    shutil.rmtree(checkpoint_dir)
    write_json(args.output.resolve(), report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
