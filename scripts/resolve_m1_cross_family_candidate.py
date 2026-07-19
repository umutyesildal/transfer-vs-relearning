#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.experiments.m1_cross_family import (
    candidate_by_index,
    candidate_model_manifest,
    candidate_model_root,
    candidate_training_root,
    load_registry,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve one frozen Document 105 candidate field.")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--candidate-index", type=int, required=True)
    parser.add_argument(
        "--field",
        choices=("label", "model_id", "requested_revision", "required", "model_root", "model_manifest", "training_root"),
        required=True,
    )
    args = parser.parse_args()
    registry = load_registry(args.registry.resolve())
    candidate = candidate_by_index(registry, args.candidate_index)
    values = {
        "label": candidate["label"],
        "model_id": candidate["model_id"],
        "requested_revision": candidate["requested_revision"],
        "required": "true" if candidate["required"] else "false",
        "model_root": candidate_model_root(registry, candidate),
        "model_manifest": candidate_model_manifest(registry, candidate),
        "training_root": candidate_training_root(registry, candidate),
    }
    print(values[args.field])


if __name__ == "__main__":
    main()
