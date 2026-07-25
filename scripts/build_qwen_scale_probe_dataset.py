#!/usr/bin/env python3
import argparse
from pathlib import Path

from transfer_vs_relearning.data.qwen_scale_probe import build_qwen_scale_probe_dataset

parser = argparse.ArgumentParser()
parser.add_argument("--repo-root", type=Path, default=Path.cwd())
parser.add_argument("--output-dir", type=Path, required=True)
args = parser.parse_args()
print(build_qwen_scale_probe_dataset(args.repo_root, output_dir=args.output_dir))
