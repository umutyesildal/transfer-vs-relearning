#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.evaluation.eval_v1_registry import (
    build_eval_v1_factual_registries,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build frozen eval-v1 factual registries")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    payload = build_eval_v1_factual_registries(
        args.repo_root,
        output_dir=args.output_dir,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
