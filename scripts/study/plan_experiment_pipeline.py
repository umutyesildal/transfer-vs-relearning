#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.pipeline.artifacts import initialize_artifact_scaffold
from transfer_vs_relearning.pipeline.planner import build_pipeline_plan
from transfer_vs_relearning.utils.io import write_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and render a non-executable train/eval/analysis pipeline plan."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--initialize-artifact-scaffold",
        type=Path,
        help="Create a fresh planned_not_run result namespace; never runs evaluation.",
    )
    args = parser.parse_args()

    plan = build_pipeline_plan(args.config, repo_root=args.repo_root)
    if args.output:
        write_json(args.output.resolve(), plan)
    if args.initialize_artifact_scaffold:
        initialize_artifact_scaffold(args.initialize_artifact_scaffold.resolve(), plan)
    print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
