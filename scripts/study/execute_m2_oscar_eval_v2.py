#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.study.m2_eval_executor import (
    build_matrix,
    finalize,
    initialize,
    load_matrix,
    preflight,
    run_task,
    submit,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute the frozen OSCAR M2 eval-v2 wave")
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("--repo-root", type=Path, default=Path.cwd())
    start.add_argument("--config", type=Path, required=True)
    start.add_argument("--contract", type=Path, required=True)
    start.add_argument("--contract-sha256", required=True)
    start.add_argument("--expected-commit", required=True)
    start.add_argument("--authorization-ack", required=True)
    for name in ("preflight", "finalize"):
        child = sub.add_parser(name)
        child.add_argument("--matrix", type=Path, required=True)
    task = sub.add_parser("run-task")
    task.add_argument("--matrix", type=Path, required=True)
    task.add_argument("--task-index", type=int, required=True)
    args = parser.parse_args()
    if args.command == "start":
        matrix = build_matrix(
            repo_root=args.repo_root,
            config_path=args.config,
            contract_path=args.contract,
            contract_sha256=args.contract_sha256,
            expected_commit=args.expected_commit,
            authorization_ack=args.authorization_ack,
        )
        matrix_path = initialize(matrix)
        result = submit(matrix_path, entrypoint=Path(__file__).resolve())
    else:
        matrix = load_matrix(args.matrix.resolve())
        if args.command == "preflight":
            result = preflight(matrix)
        elif args.command == "run-task":
            result = run_task(matrix, args.task_index)
        else:
            result = finalize(matrix)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
