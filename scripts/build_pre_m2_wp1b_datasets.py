#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.pre_m2_followup import build_wp1b_training_datasets


def main() -> None:
    parser = argparse.ArgumentParser(description="Build frozen WP1B counterbalanced and swap training datasets.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--dataset-dir", type=Path, default=None)
    parser.add_argument("--followup-dir", type=Path, default=None)
    args = parser.parse_args()
    print(
        build_wp1b_training_datasets(
            args.repo_root,
            dataset_dir=args.dataset_dir,
            followup_dir=args.followup_dir,
        )
    )


if __name__ == "__main__":
    main()
