#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.study.model_matrix import (
    build_model_matrix_plan,
    initialize_model_matrix_namespace,
    load_model_matrix_namespace,
    next_model_matrix_wave,
    render_model_matrix_packets,
)
from transfer_vs_relearning.utils.io import write_json


DEFAULT_CONFIG = Path("configs/studies/three_model_m0_to_m2_matrix_v1.yaml")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan and inspect the fail-closed three-model M0→M2 study matrix."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "run"):
        command = subparsers.add_parser(name)
        command.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
        command.add_argument("--repo-root", type=Path, default=Path.cwd())
        command.add_argument("--output", type=Path)
        if name == "run":
            command.add_argument("--dry-run", action="store_true")

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    init_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    init_parser.add_argument("--namespace", type=Path, required=True)

    for name in ("status", "next"):
        command = subparsers.add_parser(name)
        command.add_argument("--namespace", type=Path, required=True)

    packet_parser = subparsers.add_parser("packets")
    packet_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    packet_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    packet_parser.add_argument("--output-dir", type=Path, required=True)
    packet_parser.add_argument("--replace", action="store_true")

    args = parser.parse_args()
    if args.command in {"plan", "run", "init", "packets"}:
        repo_root = args.repo_root.resolve()
        config_path = args.config if args.config.is_absolute() else repo_root / args.config
        plan = build_model_matrix_plan(config_path, repo_root=repo_root)
    if args.command == "plan":
        if args.output:
            write_json(args.output.resolve(), plan)
        print(json.dumps(plan, indent=2, ensure_ascii=False, sort_keys=True))
    elif args.command == "run":
        if not args.dry_run:
            parser.error(
                "Matrix execution is fail-closed. Use --dry-run until eval-v1, corpus and all "
                "model-specific M1/M2 recipe contracts are frozen and registered."
            )
        print(
            json.dumps(
                {
                    "matrix_id": plan["matrix_id"],
                    "plan_id": plan["plan_id"],
                    "status": plan["status"],
                    "model_count": plan["model_count"],
                    "node_count": plan["node_count"],
                    "training_node_count": plan["training_node_count"],
                    "state_evaluation_node_count": plan["state_evaluation_node_count"],
                    "waves": plan["waves"],
                    "execution_blockers": plan["execution_blockers"],
                },
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    elif args.command == "init":
        print(initialize_model_matrix_namespace(args.namespace.resolve(), plan))
    elif args.command in {"status", "next"}:
        plan, state = load_model_matrix_namespace(args.namespace.resolve())
        payload = state if args.command == "status" else next_model_matrix_wave(plan, state)
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    elif args.command == "packets":
        paths = render_model_matrix_packets(
            plan, args.output_dir.resolve(), replace_existing=args.replace
        )
        print(json.dumps({"packets": [str(path) for path in paths]}, indent=2))


if __name__ == "__main__":
    main()
