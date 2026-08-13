#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from transfer_vs_relearning.corpora.vngrs.sample_transport import (
    OUTPUT_ROOT,
    SOURCE_ROOT,
    build_projection,
    validate_source_root,
    write_projection,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Project vngrs sample transport from accepted footer evidence")
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args()
    commit = subprocess.run(
        ["git", "-C", str(args.repo_root.resolve()), "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if commit != args.expected_commit:
        raise ValueError("implementation commit drift")
    rows = validate_source_root(args.source_root)
    payload = build_projection(rows, implementation_commit=commit)
    output = write_projection(payload, args.output_root)
    print(json.dumps({"status": "PASS", "output": str(output), "sha256": __import__("hashlib").sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
