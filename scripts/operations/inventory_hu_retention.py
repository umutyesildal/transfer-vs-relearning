#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from transfer_vs_relearning.storage.retention_inventory import create_retention_inventory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a bounded, non-deleting HU retention inventory."
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("Config must contain a YAML mapping")
    summary = create_retention_inventory(config, args.output_root)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
