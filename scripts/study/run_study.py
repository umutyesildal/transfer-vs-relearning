#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.study.workflow import (
    assess_m0_readiness,
    build_study_plan,
    initialize_study_namespace,
    load_study_namespace,
    next_stage_status,
    render_luna_packets,
)
from transfer_vs_relearning.utils.io import write_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan and inspect the fail-closed M0→M1→M2-A/M2-B study lifecycle."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("--config", type=Path, required=True)
    plan_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    plan_parser.add_argument("--output", type=Path)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--config", type=Path, required=True)
    init_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    init_parser.add_argument("--namespace", type=Path, required=True)

    for name in ("status", "next"):
        command_parser = subparsers.add_parser(name)
        command_parser.add_argument("--namespace", type=Path, required=True)

    packet_parser = subparsers.add_parser("packets")
    packet_parser.add_argument("--config", type=Path, required=True)
    packet_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    packet_parser.add_argument("--output-dir", type=Path, required=True)
    packet_parser.add_argument("--replace", action="store_true")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--config", type=Path, required=True)
    run_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    run_parser.add_argument("--dry-run", action="store_true")

    preflight_parser = subparsers.add_parser("preflight-m0")
    preflight_parser.add_argument("--config", type=Path, required=True)
    preflight_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    preflight_parser.add_argument(
        "--project-state",
        type=Path,
        default=Path("documentation/current/PROJECT_STATE.yaml"),
    )

    args = parser.parse_args()
    if args.command in {"plan", "init", "packets", "run"}:
        plan = build_study_plan(args.config, repo_root=args.repo_root)
    if args.command == "plan":
        if args.output:
            write_json(args.output.resolve(), plan)
        print(json.dumps(plan, indent=2, ensure_ascii=False, sort_keys=True))
    elif args.command == "init":
        namespace = initialize_study_namespace(args.namespace.resolve(), plan)
        print(namespace)
    elif args.command in {"status", "next"}:
        plan, state = load_study_namespace(args.namespace.resolve())
        payload = state if args.command == "status" else next_stage_status(plan, state)
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    elif args.command == "packets":
        paths = render_luna_packets(
            plan, args.output_dir.resolve(), replace_existing=args.replace
        )
        print(json.dumps({"packets": [str(path) for path in paths]}, indent=2))
    elif args.command == "run":
        if not args.dry_run:
            parser.error(
                "Scientific stage adapters are not registered and execution is not authorized; "
                "use --dry-run until eval-v1 and training contracts are frozen."
            )
        print(
            json.dumps(
                {
                    "status": "dry_run_only",
                    "execution_authorized": False,
                    "flow": [
                        {
                            "ordinal": stage["ordinal"],
                            "stage_id": stage["id"],
                            "state": stage["state"],
                            "authority_class": stage["authority_class"],
                            "adapter_id": stage["adapter_id"],
                        }
                        for stage in plan["stages"]
                    ],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    elif args.command == "preflight-m0":
        repo_root = args.repo_root.resolve()
        project_state = args.project_state
        if not project_state.is_absolute():
            project_state = repo_root / project_state
        payload = assess_m0_readiness(
            args.config,
            repo_root=repo_root,
            project_state_path=project_state,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        if payload["status"] != "ready":
            raise SystemExit(2)


if __name__ == "__main__":
    main()
