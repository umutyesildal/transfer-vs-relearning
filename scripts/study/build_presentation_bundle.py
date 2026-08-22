#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.pipeline.presentation import build_presentation_bundle


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build deterministic presentation views from canonical run tables."
    )
    parser.add_argument("--root", type=Path, required=True, help="Existing run artifact root")
    args = parser.parse_args()
    manifest = build_presentation_bundle(args.root)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
