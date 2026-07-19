#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDS = {
    "label",
    "model_manifest",
    "model_manifest_sha256",
    "hard_output",
    "exact_config",
    "general_config",
}


def resolve(registry: Path, task_index: int, field: str) -> str:
    with registry.open(newline="", encoding="utf-8-sig") as handle:
        matches = [row for row in csv.DictReader(handle) if int(row["array_index"]) == task_index]
    if len(matches) != 1:
        raise ValueError(f"Expected one registry row for task {task_index}, found {len(matches)}")
    value = matches[0][field]
    if not value:
        raise ValueError(f"Registry field {field} is empty for task {task_index}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve one frozen Document 107 registry field.")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--task-index", type=int, required=True)
    parser.add_argument("--field", choices=sorted(FIELDS), required=True)
    args = parser.parse_args()
    print(resolve(args.registry.resolve(), args.task_index, args.field))


if __name__ == "__main__":
    main()
