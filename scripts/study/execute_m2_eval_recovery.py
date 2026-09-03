#!/usr/bin/env python3
"""Exact-authorized M2 recovery entrypoint; never invoke the original all-task launcher."""
import argparse
from pathlib import Path
from transfer_vs_relearning.study import m2_eval_recovery as recovery
from transfer_vs_relearning.study.m2_eval_executor import load_matrix


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    start = sub.add_parser('start')
    for arg in ('config', 'contract', 'repo-root'):
        start.add_argument('--' + arg, type=Path, required=True)
    for arg in ('contract-sha256', 'expected-commit', 'authorization-ack'):
        start.add_argument('--' + arg, required=True)
    for name in ('preflight', 'run-task', 'finalize'):
        child = sub.add_parser(name)
        child.add_argument('--matrix', type=Path, required=True)
        if name == 'run-task':
            child.add_argument('--task-index', type=int, required=True)
    args = parser.parse_args()
    if args.command == 'start':
        print(recovery.start(args.repo_root, args.config, args.contract, args.contract_sha256,
                             args.expected_commit, args.authorization_ack))
    else:
        matrix = load_matrix(args.matrix)
        if args.command == 'run-task':
            print(recovery.run_task(matrix, args.task_index))
        else:
            print(getattr(recovery, args.command)(matrix))


if __name__ == '__main__':
    main()
