#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from transfer_vs_relearning.corpora.vngrs.clustered_sampling import (
    CLUSTERED_SAMPLE_CONTRACT_SHA256,
    build_clustered_schedule,
    validate_clustered_schedule,
)
from transfer_vs_relearning.corpora.vngrs.metadata import canonical_json_bytes
from transfer_vs_relearning.corpora.vngrs.sample_transport import SOURCE_ROOT, validate_source_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--contract-sha256", required=True)
    args = parser.parse_args()
    if args.contract_sha256 != CLUSTERED_SAMPLE_CONTRACT_SHA256:
        raise ValueError("Document 151bq SHA-256 drift")
    commit = subprocess.run(
        ["git", "-C", str(args.repo_root.resolve()), "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if commit != args.expected_commit:
        raise ValueError("implementation commit drift")
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    rows = validate_source_root(args.source_root)
    schedule = build_clustered_schedule(rows)
    validation = validate_clustered_schedule(schedule, rows)
    if not validation["complete"]:
        raise ValueError(f"clustered schedule validation failed: {validation['errors']}")
    payload = canonical_json_bytes({**schedule, "implementation_commit": commit})
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    if temporary.exists():
        raise FileExistsError(temporary)
    temporary.write_bytes(payload)
    os.replace(temporary, output)
    print(json.dumps({"status": "PASS", "output": str(output), **validation}, sort_keys=True))


if __name__ == "__main__":
    main()
