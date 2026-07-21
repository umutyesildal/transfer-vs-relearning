#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.corpora.config import corpus_root, load_corpus_config
from transfer_vs_relearning.corpora.finalize import finalize_reviewed_corpus


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze a manually reviewed Turkish bridge corpus without overwriting candidate evidence")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-size", type=int, default=20)
    args = parser.parse_args()
    config = load_corpus_config(args.config)
    print(finalize_reviewed_corpus(corpus_root(config), seed=args.seed, sample_size=args.sample_size))


if __name__ == "__main__":
    main()
