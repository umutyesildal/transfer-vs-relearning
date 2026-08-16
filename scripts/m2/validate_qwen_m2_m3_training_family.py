#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file, write_json


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.resolve().read_text(encoding="utf-8"))


def _scratch(path: Path) -> bool:
    value = str(path.resolve())
    return value == "/vol/tmp" or value.startswith("/vol/tmp/") or value == "/vol/tmp2" or value.startswith("/vol/tmp2/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a prepared Qwen M2/M3 training family without launching work.")
    parser.add_argument("--config-manifest", type=Path, required=True)
    parser.add_argument("--expected-commit")
    parser.add_argument("--allow-local-paths", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest_path = args.config_manifest.resolve()
    manifest = _json(manifest_path)
    if manifest.get("status") != "prepared":
        raise ValueError("Config manifest must have status=prepared")
    entries = manifest.get("configs")
    if not isinstance(entries, list) or len(entries) != 4:
        raise ValueError("Config manifest must contain exactly four configs")
    identities = {(str(item["arm"]), int(item["seed"])) for item in entries}
    expected = {(arm, seed) for arm in ("m2_clean", "m3_fact") for seed in (42, 43)}
    if identities != expected:
        raise ValueError(f"Unexpected M2/M3 config identities: {sorted(identities)}")
    if len({str(item["validation_file"]) for item in entries}) != 1:
        raise ValueError("All M2/M3 configs must use the same validation file")
    checked_files = []
    for item in entries:
        for field in ("config", "base_model_manifest", "train_file", "validation_file"):
            path = Path(str(item[field])).resolve()
            if not path.is_file():
                raise FileNotFoundError(f"Missing {field} for {item['label']}: {path}")
            if not args.allow_local_paths and not _scratch(path):
                raise ValueError(f"{field} is not on scratch: {path}")
            checked_files.append({"field": field, "label": item["label"], "path": str(path), "sha256": sha256_file(path)})
        config_path = Path(str(item["config"])).resolve()
        if sha256_file(config_path) != str(item["config_sha256"]):
            raise ValueError(f"Config hash mismatch: {config_path}")
        output_root = Path(str(item["output_root"])).resolve()
        if not args.allow_local_paths and not _scratch(output_root):
            raise ValueError(f"Training output is not on scratch: {output_root}")

    commit = None
    if args.expected_commit:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        if commit != args.expected_commit:
            raise ValueError(f"Git commit mismatch: {commit} != {args.expected_commit}")
    result = {
        "status": "passed",
        "config_manifest": str(manifest_path),
        "config_manifest_sha256": sha256_file(manifest_path),
        "config_count": len(entries),
        "identities": sorted({f"{arm}_seed{seed}" for arm, seed in identities}),
        "checked_files": checked_files,
        "expected_commit": args.expected_commit,
        "git_commit": commit,
        "storage_policy": "scratch_only" if not args.allow_local_paths else "local_test_paths_allowed",
    }
    if args.output:
        write_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
