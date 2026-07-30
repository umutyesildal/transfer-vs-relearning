#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.qwen_canonical_scale import build_qwen_canonical_scale_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--replay-train-source", type=Path, required=True)
    parser.add_argument("--replay-validation-source", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_qwen_canonical_scale_dataset(
        Path.cwd(),
        output_dir=args.output_dir,
        replay_train_source=args.replay_train_source,
        replay_validation_source=args.replay_validation_source,
    )
    print(manifest)


if __name__ == "__main__":
    main()
