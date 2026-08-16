#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.pilot import select_pilot_subjects


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-version", default="synthetic_v1")
    parser.add_argument("--dataset-root", type=Path, default=Path("artifacts/datasets"))
    parser.add_argument("--subjects", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    payload = select_pilot_subjects(args.dataset_root / args.dataset_version, args.subjects, args.seed)
    print(f"Selected {len(payload['selected_subject_ids'])} subjects")
    print(args.dataset_root / args.dataset_version / f"pilot_{args.subjects}_subjects.json")


if __name__ == "__main__":
    main()
