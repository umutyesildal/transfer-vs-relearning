#!/usr/bin/env python3
"""Emit a compact, read-only snapshot of one completed M1 eval family.

This script is intentionally limited to JSON manifests and metric summaries.  It does not read
sample JSONL, parquet, CSV, model, checkpoint, or corpus payloads.  The output is newline-delimited
JSON so it can be transported through the HU SSH helper and consumed by a local result-dump
builder without copying the raw evaluation tree.
"""

import argparse
import hashlib
import json
import os
import sys
from glob import glob
from typing import Any, Dict, Iterable, Optional


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def artifact(path: Optional[str], include_data: bool = True) -> Optional[Dict[str, Any]]:
    if not path or not os.path.isfile(path):
        return None
    value: Dict[str, Any] = {
        "path": path,
        "bytes": os.path.getsize(path),
        "sha256": sha256_file(path),
    }
    if include_data:
        value["data"] = load_json(path)
    return value


def first_match(pattern: str) -> Optional[str]:
    matches = sorted(glob(pattern))
    return matches[0] if matches else None


def first_file(*paths: str) -> Optional[str]:
    for path in paths:
        if os.path.isfile(path):
            return path
    return None


def harness_artifact(state_root: str) -> Optional[Dict[str, Any]]:
    path = first_match(os.path.join(state_root, "harness", "raw", "*", "results_*.json"))
    if not path:
        return None
    raw = load_json(path)
    keep = {
        key: raw[key]
        for key in (
            "results",
            "groups",
            "versions",
            "lm_eval_version",
            "model_source",
            "git_hash",
            "upper_git_hash",
            "task_hashes",
        )
        if key in raw
    }
    value = artifact(path, include_data=False)
    assert value is not None
    value["data"] = keep
    return value


def state_record(root: str, model: str, checkpoint: str) -> Dict[str, Any]:
    state_root = os.path.join(root, "results", model, checkpoint)
    task_path = os.path.join(state_root, "task_result.json")
    record: Dict[str, Any] = {
        "state": "%s/%s" % (model, checkpoint),
        "model": model,
        "checkpoint": checkpoint,
        "task_result": artifact(task_path),
        "harness": harness_artifact(state_root),
        "exact_prefix": artifact(
            first_match(os.path.join(state_root, "exact_prefix", "raw", "*", "summary_metrics.json"))
        ),
        "factual_cheap": artifact(
            first_file(
                os.path.join(state_root, "factual_cheap", "summary.json"),
                os.path.join(state_root, "factual_cheap", "raw", "summary.json"),
            )
        ),
        "factual_cheap_derivation": artifact(
            os.path.join(state_root, "factual_cheap", "derivation_manifest.json")
        ),
        "factual_full": artifact(os.path.join(state_root, "factual_full", "raw", "summary.json")),
        "turkish": artifact(os.path.join(state_root, "turkish_perplexity", "raw", "summary.json")),
        "turkish_cross_domain": artifact(
            os.path.join(state_root, "turkish_perplexity", "raw", "trwiki_cross_domain", "summary.json")
        ),
        "generation": artifact(
            first_match(os.path.join(state_root, "generation_integrity", "raw", "*", "summary_metrics.json"))
        ),
    }
    return record


def iter_states(root: str) -> Iterable[Dict[str, Any]]:
    results_root = os.path.join(root, "results")
    for model in sorted(os.listdir(results_root)):
        model_root = os.path.join(results_root, model)
        if not os.path.isdir(model_root):
            continue
        for checkpoint in sorted(os.listdir(model_root)):
            if "__" in checkpoint:
                continue
            state_root = os.path.join(model_root, checkpoint)
            if os.path.isfile(os.path.join(state_root, "task_result.json")):
                yield state_record(root, model, checkpoint)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", help="completed M1 evaluation family output root")
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "results")):
        parser.error("missing results directory: %s" % os.path.join(root, "results"))

    print("__M1_COMPACT_BEGIN__")
    count = 0
    for record in iter_states(root):
        print(json.dumps(record, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        count += 1
    print("__M1_COMPACT_END__")
    print("__M1_COMPACT_COUNT__=%d" % count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
