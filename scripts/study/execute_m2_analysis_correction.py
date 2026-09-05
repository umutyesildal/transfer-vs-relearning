#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.study.m2_analysis_correction import run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--contract-sha256", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--authorization-ack", required=True)
    args = parser.parse_args()
    print(
        run(
            repo_root=args.repo_root,
            config_path=args.config,
            contract_path=args.contract,
            contract_sha256=args.contract_sha256,
            expected_commit=args.expected_commit,
            authorization_ack=args.authorization_ack,
        )
    )


if __name__ == "__main__":
    main()
