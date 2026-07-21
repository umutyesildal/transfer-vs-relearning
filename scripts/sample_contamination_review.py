#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.corpora.config import corpus_root, load_corpus_config
from transfer_vs_relearning.corpora.review import generate_contamination_review_sample


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic contamination review samples")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-size", type=int, default=20)
    args = parser.parse_args()
    config = load_corpus_config(args.config)
    result = generate_contamination_review_sample(corpus_root(config), seed=args.seed, sample_size=args.sample_size)
    print({
        "review_status": result["review_status"],
        "observed_bucket_counts": result["observed_bucket_counts"],
        "sample_counts": {key: len(value) for key, value in result["samples"].items()},
    })


if __name__ == "__main__":
    main()
