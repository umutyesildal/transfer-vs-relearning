#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--local-model-dir", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--resolved-revision", default="local-checkpoint")
    parser.add_argument("--training-checkpoint", default=None)
    parser.add_argument("--training-run-dir", type=Path, default=None)
    args = parser.parse_args()

    payload = create_local_model_manifest(
        source_manifest_path=args.source_manifest,
        local_model_dir=args.local_model_dir,
        output_manifest_path=args.output_manifest,
        model_id=args.model_id,
        resolved_revision=args.resolved_revision,
        training_checkpoint=args.training_checkpoint,
        training_run_dir=args.training_run_dir,
    )
    print(args.output_manifest)
    print(payload["local_path_project_relative"])


if __name__ == "__main__":
    main()
