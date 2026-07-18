#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.m1_form_generalization import build_m1_form_generalization_datasets


def main() -> None:
    parser = argparse.ArgumentParser(description="Build matched M1 form-generalization datasets and four-form probes.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--dataset-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    print(build_m1_form_generalization_datasets(args.repo_root, dataset_dir=args.dataset_dir, output_dir=args.output_dir))


if __name__ == "__main__":
    main()
