#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.study.m1_wave_executor import (
    build_task_matrix,
    finalize_wave,
    initialize_wave,
    load_matrix,
    preflight_matrix,
    run_task,
    submit_wave,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute the hash-bound M1 eval-v2 trajectory wave")
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("--config", type=Path, action="append", required=True)
    start.add_argument("--repo-root", type=Path, default=Path.cwd())
    start.add_argument("--contract", type=Path, required=True)
    start.add_argument("--contract-sha256", required=True)
    start.add_argument("--execution-config", type=Path, required=True)
    start.add_argument("--execution-config-sha256", required=True)
    for name in ("preflight", "finalize"):
        child = sub.add_parser(name)
        child.add_argument("--matrix", type=Path, required=True)
    task = sub.add_parser("run-task")
    task.add_argument("--matrix", type=Path, required=True)
    task.add_argument("--task-index", type=int, required=True)
    args = parser.parse_args()
    if args.command == "start":
        matrix = build_task_matrix(
            args.config,
            repo_root=args.repo_root,
            contract_path=args.contract,
            contract_sha256=args.contract_sha256,
            execution_config_path=args.execution_config,
            execution_config_sha256=args.execution_config_sha256,
        )
        matrix_path = initialize_wave(matrix)
        result = submit_wave(matrix_path, entrypoint=Path(__file__).resolve())
    else:
        matrix = load_matrix(args.matrix.resolve())
        if args.command == "preflight":
            result = preflight_matrix(matrix)
        elif args.command == "run-task":
            result = run_task(matrix, args.task_index)
        else:
            result = finalize_wave(matrix)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
