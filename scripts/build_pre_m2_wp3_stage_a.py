#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.pre_m2_wp3 import build_wp3_stage_a


def main() -> None:
    parser = argparse.ArgumentParser(description="Build WP3 four-relation fixture and Stage A dataset.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=20260718)
    args = parser.parse_args()
    print(build_wp3_stage_a(args.repo_root, output_root=args.output_root, seed=args.seed))


if __name__ == "__main__":
    main()
