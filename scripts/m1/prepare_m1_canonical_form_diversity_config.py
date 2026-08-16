#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize a scratch-rooted canonical-form-diversity config.")
    parser.add_argument("--source-config", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = yaml.safe_load(args.source_config.read_text(encoding="utf-8"))
    dataset_root = args.dataset_root.resolve()
    payload["dataset"].update({"dataset_dir": str(dataset_root), "dataset_manifest": str(dataset_root / "dataset_manifest.json"), "train_file": str(dataset_root / "train.jsonl"), "validation_file": str(dataset_root / "validation.jsonl")})
    payload["training"]["output_root"] = str(args.output_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


if __name__ == "__main__":
    main()
