#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.models.download import download_model_snapshot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", default="openai-community/gpt2")
    parser.add_argument("--revision", default=None)
    parser.add_argument("--artifact-root", type=Path, default=Path("artifacts/models"))
    parser.add_argument("--local-files-only", action="store_true")
    args = parser.parse_args()
    manifest = download_model_snapshot(args.model_id, args.revision, args.artifact_root, args.local_files_only)
    print(f"Downloaded {manifest['model_id']} at {manifest['resolved_revision']}")
    print(args.artifact_root / args.model_id.replace("/", "__") / "model_manifest.json")


if __name__ == "__main__":
    main()
