#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.corpora.pipeline import run_stage


STAGES = (
    "resolve",
    "download",
    "verify",
    "extract",
    "normalize",
    "audit",
    "filter",
    "deduplicate",
    "contamination-preflight",
    "scan-contamination",
    "split",
    "report",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the reproducible Turkish Wikipedia Phase 1 corpus.")
    parser.add_argument("stage", choices=STAGES)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--fetch-metadata", action="store_true", help="Allow network metadata resolution for the configured dump date.")
    args = parser.parse_args()
    result = run_stage(args.config, args.stage, force=args.force, fetch_metadata=args.fetch_metadata)
    print(result)


if __name__ == "__main__":
    main()
