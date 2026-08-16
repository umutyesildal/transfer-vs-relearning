#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.acquisition_diagnostics import build_acquisition_diagnostics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ladder-dir", type=Path, default=Path("artifacts/datasets/acquisition_ladder_v1"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/datasets/acquisition_diagnostics_v1"),
    )
    args = parser.parse_args()
    manifest = build_acquisition_diagnostics(args.ladder_dir, args.output_dir)
    print(args.output_dir / "manifest.json")
    print(f"selection={manifest['selection']}")
    for level, summary in manifest["levels"].items():
        print(f"{level}: {summary['subjects']} subjects, {summary['facts']} facts, {summary['train_rows']} rows")


if __name__ == "__main__":
    main()
