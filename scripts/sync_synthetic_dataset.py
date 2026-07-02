#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.sync import sync_synthetic_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-repo", default="https://github.com/umutyesildal/synthetic-data-generation")
    parser.add_argument("--ref", default="main")
    parser.add_argument("--version", default="synthetic_v1")
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/datasets"))
    args = parser.parse_args()
    manifest = sync_synthetic_dataset(args.source_repo, args.ref, args.version, args.output_root)
    print(f"Synced {args.version} from {manifest['source_commit_sha']}")
    print(args.output_root / args.version / "manifest.json")


if __name__ == "__main__":
    main()
