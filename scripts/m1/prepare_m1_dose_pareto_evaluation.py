#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.experiments.m1_dose_pareto import (
    load_registry,
    prepare_checkpoint_evaluation,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--label", choices=("olmo", "falcon", "pythia"), required=True)
    parser.add_argument("--step", type=int, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    outputs = prepare_checkpoint_evaluation(load_registry(args.registry.resolve()), args.label, args.step, args.repo_root.resolve())
    for key, value in outputs.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
