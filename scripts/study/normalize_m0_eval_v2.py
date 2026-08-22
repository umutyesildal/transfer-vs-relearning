#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.study.m0_metric_normalization import audit_normalization, normalize


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed M0 eval-v2 metric normalization")
    parser.add_argument("command", choices=("audit", "normalize"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    payload = audit_normalization(args.config, repo_root=args.repo_root.resolve()) if args.command == "audit" else normalize(args.config, repo_root=args.repo_root.resolve())
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
