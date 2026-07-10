#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.acquisition_ladder import build_acquisition_ladder


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, default=Path("artifacts/datasets/synthetic_v1"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/datasets/acquisition_ladder_v1"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    manifest = build_acquisition_ladder(args.dataset_dir, args.output_dir, seed=args.seed)
    print(args.output_dir / "manifest.json")
    for level, summary in manifest["levels"].items():
        print(
            f"{level} subjects: {summary['facts']} facts, "
            f"{summary['train_rows']} train rows, {summary['validation_rows']} validation rows"
        )


if __name__ == "__main__":
    main()
