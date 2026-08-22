#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.study.m1_wave_controller import build_m1_wave_plan
from transfer_vs_relearning.utils.io import write_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan the fresh matched three-model M1 training/evaluation wave; fail-closed."
    )
    parser.add_argument("--config", type=Path, action="append", dest="configs", required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--project-state", type=Path, default=Path("documentation/current/PROJECT_STATE.yaml"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--execute", action="store_true", help="Reserved; never bypasses the M1 gate.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    configs = [path if path.is_absolute() else repo_root / path for path in args.configs]
    project_state = args.project_state if args.project_state.is_absolute() else repo_root / args.project_state
    plan = build_m1_wave_plan(configs, repo_root=repo_root, project_state_path=project_state.resolve())
    if args.output:
        output = args.output if args.output.is_absolute() else repo_root / args.output
        write_json(output.resolve(), plan)
    print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    if args.execute:
        raise SystemExit(
            "M1 execution is fail-closed: this command is planner-only and requires a later "
            "SHA-bound contract plus explicit execution authorization."
        )
    if plan["status"] != "ready_to_execute":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
