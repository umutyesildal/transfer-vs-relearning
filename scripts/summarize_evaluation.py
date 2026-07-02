#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    for name in ("summary_metrics.json", "relation_binding_metrics.json"):
        path = args.run_dir / name
        print(f"\n{name}")
        print(json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
