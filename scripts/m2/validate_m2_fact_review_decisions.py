#!/usr/bin/env python3
"""Validate one registry-bound human verdict for every frozen M2 Branch-B fact."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file, write_json


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"Blank JSONL row at line {line_number}: {path}")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row is not an object at line {line_number}: {path}")
        rows.append(value)
    return rows


def validate(
    packet_path: Path,
    decisions_path: Path,
    *,
    expected_registry_sha256: str,
) -> dict[str, Any]:
    packet = _jsonl(packet_path)
    decisions = _jsonl(decisions_path)
    if len(packet) != 250:
        raise ValueError(f"Frozen fact-review packet must contain 250 rows, found {len(packet)}")
    packet_ids = [str(row.get("fact_id", "")) for row in packet]
    if any(not value for value in packet_ids) or len(set(packet_ids)) != 250:
        raise ValueError("Frozen fact-review packet has missing or duplicate fact IDs")
    if [int(row.get("index", -1)) for row in packet] != list(range(250)):
        raise ValueError("Frozen fact-review packet index order drift")
    if len(decisions) != 250:
        raise ValueError(f"Human decisions must contain 250 rows, found {len(decisions)}")

    by_id: dict[str, dict[str, Any]] = {}
    for row in decisions:
        fact_id = str(row.get("fact_id", ""))
        if not fact_id or fact_id in by_id:
            raise ValueError("Human decisions contain a missing or duplicate fact ID")
        if row.get("schema_version") != 1:
            raise ValueError(f"Decision schema drift for {fact_id}")
        if row.get("fact_registry_sha256") != expected_registry_sha256:
            raise ValueError(f"Fact-registry SHA-256 mismatch for {fact_id}")
        if row.get("verdict") not in {"usable", "issue"}:
            raise ValueError(f"Unresolved or invalid verdict for {fact_id}")
        if not str(row.get("reviewer", "")).strip():
            raise ValueError(f"Missing reviewer identity for {fact_id}")
        by_id[fact_id] = row
    if set(by_id) != set(packet_ids):
        raise ValueError("Human decisions do not exactly cover the frozen 250-fact packet")

    verdicts = Counter(str(by_id[fact_id]["verdict"]) for fact_id in packet_ids)
    status = "M2_FACT_REVIEW_PASS" if verdicts == {"usable": 250} else "M2_FACT_REVIEW_BLOCKED"
    result = {
        "schema_version": 1,
        "status": status,
        "packet": str(packet_path.resolve()),
        "packet_sha256": sha256_file(packet_path),
        "decisions": str(decisions_path.resolve()),
        "decisions_sha256": sha256_file(decisions_path),
        "fact_registry_sha256": expected_registry_sha256,
        "rows": 250,
        "unique_fact_ids": 250,
        "verdicts": dict(sorted(verdicts.items())),
        "human_review_complete": True,
        "optimizer_smoke_authorized": False,
        "ready_to_train": False,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--expected-registry-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(
        args.packet.resolve(),
        args.decisions.resolve(),
        expected_registry_sha256=args.expected_registry_sha256,
    )
    write_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "M2_FACT_REVIEW_PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
