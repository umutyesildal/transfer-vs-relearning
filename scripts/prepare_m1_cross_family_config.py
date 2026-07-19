#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from transfer_vs_relearning.experiments.m1_cross_family import (
    candidate_by_index,
    load_registry,
    materialize_training_config,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize one frozen Document 105 training config.")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--candidate-index", type=int, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registry = load_registry(args.registry.resolve())
    candidate = candidate_by_index(registry, args.candidate_index)
    template = yaml.safe_load(args.template.read_text(encoding="utf-8"))
    payload = materialize_training_config(
        registry=registry,
        candidate=candidate,
        template=template,
        dataset_root=args.dataset_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
