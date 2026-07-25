#!/usr/bin/env python3
import argparse
from pathlib import Path
from transfer_vs_relearning.data.m1_canonical_form_diversity import build_m1_canonical_form_diversity_dataset

parser = argparse.ArgumentParser()
parser.add_argument("--repo-root", type=Path, default=Path.cwd())
parser.add_argument("--output-dir", type=Path, default=None)
parser.add_argument("--subject-count", type=int, choices=(100, 500), default=100)
args = parser.parse_args()
print(build_m1_canonical_form_diversity_dataset(args.repo_root, output_dir=args.output_dir, subject_count=args.subject_count))
