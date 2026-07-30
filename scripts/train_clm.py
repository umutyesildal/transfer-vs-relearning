#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.training.clm import run_from_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--resume-run-dir",
        type=Path,
        help="Resume the latest complete optimizer checkpoint in this existing run directory",
    )
    args = parser.parse_args()
    run_dir = run_from_config(args.config, resume_run_dir=args.resume_run_dir)
    print(run_dir)


if __name__ == "__main__":
    main()
