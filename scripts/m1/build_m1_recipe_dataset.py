#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.training.recipe_data import (
    build_m1_r1_recipe_records,
    summarize_recipe_records,
)


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    parser.add_argument("--declarative-multiplier", type=int, default=2)
    parser.add_argument("--qa-multiplier", type=int, default=2)
    parser.add_argument("--split-name", default="english_training_m1_r1_qamix")
    args = parser.parse_args()

    input_records = read_jsonl(args.input)
    output_records = build_m1_r1_recipe_records(
        input_records,
        declarative_multiplier=args.declarative_multiplier,
        qa_multiplier=args.qa_multiplier,
        split_name=args.split_name,
    )
    summary = summarize_recipe_records(
        input_records,
        output_records,
        declarative_multiplier=args.declarative_multiplier,
        qa_multiplier=args.qa_multiplier,
        split_name=args.split_name,
    )

    write_jsonl(args.output, output_records)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(args.output)
    print(args.summary_output)


if __name__ == "__main__":
    main()
