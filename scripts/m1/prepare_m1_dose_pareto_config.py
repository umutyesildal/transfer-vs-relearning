#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from transfer_vs_relearning.experiments.m1_dose_pareto import (
    load_registry,
    materialize_training_config,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--label", choices=("olmo", "falcon", "pythia"), required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registry = load_registry(args.registry.resolve())
    payload, _ = materialize_training_config(registry, args.label, args.repo_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
