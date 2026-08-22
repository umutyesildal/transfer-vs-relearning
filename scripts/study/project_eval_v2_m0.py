#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.study.m0_eval_v2_projection import (
    discover_projection_bindings,
    inspect_projection_sources,
    load_projection_plan,
    write_projection,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Hash-close retained M0 evidence into eval-v2")
    parser.add_argument("command", choices=("discover", "plan", "audit", "project"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    if args.command == "discover":
        payload = discover_projection_bindings(
            args.config, repo_root=args.repo_root.resolve()
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return

    plan = load_projection_plan(args.config, repo_root=args.repo_root.resolve())
    if args.command == "plan":
        payload = plan
    elif args.command == "audit":
        payload = inspect_projection_sources(plan)
    else:
        payload = write_projection(plan)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
