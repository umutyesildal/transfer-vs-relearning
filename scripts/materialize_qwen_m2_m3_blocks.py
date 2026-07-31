#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Iterable

from transfer_vs_relearning.data.qwen_pre_m2 import (
    build_matched_m2_m3_blocks,
    materialize_generic_blocks,
)
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_json


def _jsonl_rows(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL") from exc


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize token-matched Qwen M2/M3 blocks.")
    parser.add_argument("--generic-train", type=Path, required=True)
    parser.add_argument("--generic-validation", type=Path, required=True)
    parser.add_argument("--fact-registry", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--train-blocks", type=int, default=2048)
    parser.add_argument("--validation-blocks", type=int, default=256)
    parser.add_argument("--fact-cycles", type=int, required=True)
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite matched M2/M3 blocks: {output_root}")

    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(args.tokenizer.resolve()), local_files_only=True)
    generic_train = materialize_generic_blocks(
        _jsonl_rows(args.generic_train.resolve()),
        tokenizer,
        block_size=args.block_size,
        total_blocks=args.train_blocks,
    )
    generic_validation = materialize_generic_blocks(
        _jsonl_rows(args.generic_validation.resolve()),
        tokenizer,
        block_size=args.block_size,
        total_blocks=args.validation_blocks,
    )
    fact_rows = read_csv_rows(args.fact_registry.resolve())
    m2_rows, m3_rows, audit = build_matched_m2_m3_blocks(
        generic_train,
        fact_rows,
        tokenizer,
        fact_cycles=args.fact_cycles,
    )
    validation_rows = [
        {
            "block_index": index,
            "arm": "shared_validation",
            "input_ids": block,
            "attention_mask": [1] * args.block_size,
        }
        for index, block in enumerate(generic_validation)
    ]
    output_root.mkdir(parents=True)
    paths = {
        "m2_train": output_root / "m2_clean_train_blocks.jsonl",
        "m3_train": output_root / "m3_fact_train_blocks.jsonl",
        "shared_validation": output_root / "shared_validation_blocks.jsonl",
        "matching_audit": output_root / "matching_audit.json",
    }
    _write_jsonl(paths["m2_train"], m2_rows)
    _write_jsonl(paths["m3_train"], m3_rows)
    _write_jsonl(paths["shared_validation"], validation_rows)
    write_json(paths["matching_audit"], audit)
    write_json(
        output_root / "manifest.json",
        {
            "status": "matched_m2_m3_blocks_ready",
            "tokenizer": str(args.tokenizer.resolve()),
            "inputs": {
                "generic_train": {
                    "path": str(args.generic_train.resolve()),
                    "sha256": sha256_file(args.generic_train.resolve()),
                },
                "generic_validation": {
                    "path": str(args.generic_validation.resolve()),
                    "sha256": sha256_file(args.generic_validation.resolve()),
                },
                "fact_registry": {
                    "path": str(args.fact_registry.resolve()),
                    "sha256": sha256_file(args.fact_registry.resolve()),
                },
            },
            "parameters": {
                "block_size": args.block_size,
                "train_blocks": args.train_blocks,
                "validation_blocks": args.validation_blocks,
                "fact_cycles": args.fact_cycles,
            },
            "audit": audit,
            "artifacts": {
                label: {"path": str(path), "sha256": sha256_file(path)}
                for label, path in paths.items()
            },
        },
    )
    print(output_root / "manifest.json")


if __name__ == "__main__":
    main()
