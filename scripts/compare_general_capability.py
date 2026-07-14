#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.evaluation.general_capability import compare_general_capability


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-summary", type=Path, required=True)
    parser.add_argument("--seed42-summary", type=Path, required=True)
    parser.add_argument("--seed43-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare_general_capability(
        args.base_summary,
        args.seed42_summary,
        args.seed43_summary,
        args.output,
    )
    print(args.output.resolve())
    print(result)


if __name__ == "__main__":
    main()

