#!/usr/bin/env python3
"""Convert one bounded HU discovery transcript into a compact derived JSON result."""

from __future__ import annotations

import argparse
import json
import sys

from transfer_vs_relearning.corpora.vngrs.source_registry import parse_discovery_transport


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-ledger-sha256", required=True)
    args = parser.parse_args()
    result = parse_discovery_transport(
        sys.stdin.read(), expected_ledger_sha256=args.expected_ledger_sha256
    )
    json.dump(result, sys.stdout, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
