#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.study.m1_historical_inventory import (
    inspect_historical_families,
    load_inventory_plan,
    write_historical_inventory,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory retained historical M1 checkpoints")
    parser.add_argument("command", choices=("plan", "inspect", "write"))
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    plan = load_inventory_plan(args.config)
    if args.command == "plan":
        result = plan
    elif args.command == "inspect":
        result = inspect_historical_families(plan)
    else:
        result = write_historical_inventory(plan)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
