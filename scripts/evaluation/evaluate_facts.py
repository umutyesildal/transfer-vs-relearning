#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.evaluation.evaluator import run_from_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--resume-run-dir", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--allow-errors", action="store_true")
    args = parser.parse_args()
    run_dir = run_from_config(
        args.config,
        resume_run_dir=args.resume_run_dir,
        force=args.force,
        allow_errors=args.allow_errors,
    )
    print(run_dir)


if __name__ == "__main__":
    main()
