#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.utils.io import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family-root", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for label in ("olmo", "qwen", "smollm"):
        path = args.family_root / "bindings" / label / "binding_result.json"
        rows.append({"model": label, "status": "complete" if path.is_file() else "missing", "path": str(path), "sha256": sha256_file(path) if path.is_file() else None})
    payload = {"schema_version": 1, "status": "complete" if all(row["status"] == "complete" for row in rows) else "incomplete", "models": rows}
    write_json(args.family_root / "control" / "training_family_result.json", payload)
    print(json.dumps(payload, sort_keys=True))
    if payload["status"] != "complete":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
