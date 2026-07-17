#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.pre_m2_followup import build_pre_m2_followup_contract


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze the local pre-M2 follow-up contract and WP1 probe registry.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--dataset-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--assignment-seed", type=int, default=20260717)
    parser.add_argument("--base-model-manifest", type=Path, default=None)
    parser.add_argument("--seed42-model-manifest", type=Path, default=None)
    parser.add_argument("--seed43-model-manifest", type=Path, default=None)
    args = parser.parse_args()
    model_manifests = {
        label: path
        for label, path in {
            "base": args.base_model_manifest,
            "seed42_checkpoint200": args.seed42_model_manifest,
            "seed43_data43_checkpoint75": args.seed43_model_manifest,
        }.items()
        if path is not None
    }
    output_dir = build_pre_m2_followup_contract(
        args.repo_root,
        dataset_dir=args.dataset_dir,
        output_dir=args.output_dir,
        assignment_seed=args.assignment_seed,
        model_manifests=model_manifests,
    )
    print(output_dir)


if __name__ == "__main__":
    main()
