#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.pipeline.m1_training_outputs import finalize_m1_training_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Hash-close one completed tracked M1 training run.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--binding-root", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            finalize_m1_training_outputs(args.run_dir, args.binding_root),
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
