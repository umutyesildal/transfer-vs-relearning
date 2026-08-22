#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.study.m1_eval_controller import (
    build_m1_eval_matrix_plan,
    build_m1_eval_plan,
)
from transfer_vs_relearning.utils.io import write_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan the one-command M1 eval-v2 wave; execution is fail-closed."
    )
    parser.add_argument(
        "--config",
        type=Path,
        action="append",
        dest="configs",
        help="One config for a single model, or exactly three configs for the fixed M1 matrix.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--project-state",
        type=Path,
        default=Path("documentation/current/PROJECT_STATE.yaml"),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Reserved for a future hash-bound contract; never bypasses readiness gates.",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    configs = args.configs or [Path("configs/pipelines/eval_v1_olmo_epoch_trajectory_template.yaml")]
    configs = [path if path.is_absolute() else repo_root / path for path in configs]
    project_state = args.project_state if args.project_state.is_absolute() else repo_root / args.project_state
    plan = (
        build_m1_eval_plan(configs[0], repo_root=repo_root, project_state_path=project_state)
        if len(configs) == 1
        else build_m1_eval_matrix_plan(configs, repo_root=repo_root, project_state_path=project_state)
    )
    if args.output:
        output = args.output if args.output.is_absolute() else repo_root / args.output
        write_json(output.resolve(), plan)
    print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    if args.execute:
        raise SystemExit(
            "M1 execution is fail-closed: no registered scientific adapter or hash-bound M1 "
            "execution contract exists. Run without --execute to inspect the plan."
        )
    if plan["status"] != "ready_to_execute":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
