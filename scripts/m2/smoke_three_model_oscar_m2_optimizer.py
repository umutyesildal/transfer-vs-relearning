#!/usr/bin/env python3
"""Run one non-scientific, full-effective-batch M2 optimizer step and persist evidence."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from transfer_vs_relearning.training.clm import load_training_config
from transfer_vs_relearning.utils.io import sha256_file, write_json


def _first_rows(path: Path, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise ValueError(f"Blank pretokenized JSONL row at line {line_number}")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Pretokenized row is not an object at line {line_number}")
            rows.append(value)
            if len(rows) == limit:
                break
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import torch
    from transformers import AutoModelForCausalLM

    config_path = args.config.resolve()
    config = load_training_config(config_path)
    dataset, training, metadata = config["dataset"], config["training"], config["metadata"]
    role, arm = str(metadata["role"]), str(metadata["arm"])
    batch_size = int(training["per_device_train_batch_size"])
    accumulation = int(training["gradient_accumulation_steps"])
    block_size = int(training["block_size"])
    if arm != "M2-A" or role not in {"olmo", "qwen", "smollm"}:
        raise ValueError("Optimizer smoke must use exactly one M2-A config for a frozen model role")
    if (
        dataset.get("pretokenized") is not True
        or training.get("loss_mode") != "full_sequence"
        or block_size != 512
        or batch_size * accumulation != 128
        or training.get("model_load_dtype") != "bfloat16"
        or training.get("bf16") is not True
        or training.get("fp16") is not False
        or int(training.get("max_steps", -1)) != 762
    ):
        raise ValueError("Frozen M2 optimizer-smoke recipe drift")

    train_path = Path(str(dataset["train_file"])).resolve()
    rows = _first_rows(train_path, batch_size * accumulation)
    if len(rows) != 128:
        raise ValueError("Optimizer smoke requires the first exact 128 frozen blocks")
    for row in rows:
        ids, mask = row.get("input_ids"), row.get("attention_mask")
        if not isinstance(ids, list) or not isinstance(mask, list):
            raise ValueError("Pretokenized smoke row lacks input_ids/attention_mask")
        if len(ids) != block_size or len(mask) != block_size or any(int(value) != 1 for value in mask):
            raise ValueError("Pretokenized smoke block invariant failed")

    manifest_path = Path(str(config["model"]["base_model_manifest"])).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    model_path = Path(str(manifest["local_path_absolute"])).resolve()
    device = torch.device("cuda")
    torch.cuda.reset_peak_memory_stats()
    free_before, total_bytes = torch.cuda.mem_get_info()
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        local_files_only=True,
        low_cpu_mem_usage=True,
        torch_dtype=torch.bfloat16,
        trust_remote_code=bool(manifest.get("allow_pinned_remote_code", False)),
    )
    model.config.use_cache = False
    if training.get("gradient_checkpointing"):
        model.gradient_checkpointing_enable()
    model.to(device)
    model.train()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(training["learning_rate"]),
        betas=(float(training["adam_beta1"]), float(training["adam_beta2"])),
        eps=float(training["adam_epsilon"]),
        weight_decay=float(training["weight_decay"]),
        foreach=bool(training.get("optimizer_foreach", False)),
    )
    optimizer.zero_grad(set_to_none=True)
    losses: list[float] = []
    for offset in range(0, 128, batch_size):
        chunk = rows[offset : offset + batch_size]
        input_ids = torch.tensor([row["input_ids"] for row in chunk], dtype=torch.long, device=device)
        attention_mask = torch.tensor(
            [row["attention_mask"] for row in chunk], dtype=torch.long, device=device
        )
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            output = model(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)
            loss = output.loss / accumulation
        if not torch.isfinite(output.loss):
            raise ValueError("Non-finite M2 optimizer-smoke loss")
        losses.append(float(output.loss.detach().cpu()))
        loss.backward()
    gradient_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), float(training["max_grad_norm"]))
    if not torch.isfinite(gradient_norm):
        raise ValueError("Non-finite M2 optimizer-smoke gradient norm")
    optimizer.step()
    if any(not torch.isfinite(p).all() for p in model.parameters() if p.requires_grad):
        raise ValueError("Non-finite parameter after M2 optimizer-smoke step")

    parameter_dtypes = sorted({str(p.dtype) for p in model.parameters() if p.requires_grad})
    gradient_dtypes = sorted({str(p.grad.dtype) for p in model.parameters() if p.grad is not None})
    optimizer_state_dtypes: defaultdict[str, set[str]] = defaultdict(set)
    for state in optimizer.state.values():
        for key, value in state.items():
            if torch.is_tensor(value):
                optimizer_state_dtypes[str(key)].add(str(value.dtype))
    if parameter_dtypes != ["torch.bfloat16"] or gradient_dtypes != ["torch.bfloat16"]:
        raise ValueError("M2 BF16 parameter/gradient dtype gate failed")
    for key in ("exp_avg", "exp_avg_sq"):
        if optimizer_state_dtypes.get(key) != {"torch.bfloat16"}:
            raise ValueError(f"M2 BF16 AdamW state dtype gate failed: {key}")
    free_after, _ = torch.cuda.mem_get_info()
    result = {
        "schema_version": 1,
        "status": "OPTIMIZER_SMOKE_PASS",
        "scientific_training": False,
        "role": role,
        "arm": arm,
        "config": str(config_path),
        "config_sha256": sha256_file(config_path),
        "model_manifest": str(manifest_path),
        "model_manifest_sha256": sha256_file(manifest_path),
        "train_file": str(train_path),
        "train_sha256": sha256_file(train_path),
        "optimizer_steps": 1,
        "blocks_consumed": 128,
        "tokens_consumed": 65536,
        "batch_size": batch_size,
        "gradient_accumulation_steps": accumulation,
        "loss_min": min(losses),
        "loss_max": max(losses),
        "gradient_norm": float(gradient_norm.detach().cpu()),
        "parameter_dtypes": parameter_dtypes,
        "gradient_dtypes": gradient_dtypes,
        "optimizer_state_dtypes": {
            key: sorted(values) for key, values in sorted(optimizer_state_dtypes.items())
        },
        "gpu": torch.cuda.get_device_name(0),
        "gpu_total_bytes": total_bytes,
        "gpu_free_before_bytes": free_before,
        "gpu_free_after_bytes": free_after,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "checkpoint_written": False,
        "ready_to_train": False,
    }
    write_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
