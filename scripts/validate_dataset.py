#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.validation import validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, required=True)
    args = parser.parse_args()
    summary = validate_dataset(args.dataset_dir)
    print(f"Validation {summary['validation_status']}: {args.dataset_dir}")
    print(f"Facts: {summary['normalized_fact_count']}; candidates: {summary['candidate_inventory_sizes']}")


if __name__ == "__main__":
    main()
