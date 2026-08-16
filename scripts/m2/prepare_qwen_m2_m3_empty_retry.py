#!/usr/bin/env python3
"""Prepare a fail-closed retry manifest for explicitly empty endpoint slices."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file, write_json


def _json(path: Path) -> dict[str, Any] | list[dict[str, Any]]:
    return json.loads(path.resolve().read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation-manifest", type=Path, required=True)
    parser.add_argument("--slice-registry", type=Path, required=True)
    parser.add_argument("--task-ids", type=int, nargs="+", required=True)
    parser.add_argument("--required-state", default="m2_clean_seed42")
    parser.add_argument("--output-manifest", type=Path, required=True)
    args = parser.parse_args()

    evaluation_path = args.evaluation_manifest.resolve()
    registry_path = args.slice_registry.resolve()
    output_path = args.output_manifest.resolve()
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite retry manifest: {output_path}")
    evaluation = _json(evaluation_path)
    registry = _json(registry_path)
    if not isinstance(evaluation, dict) or not isinstance(registry, list):
        raise ValueError("Evaluation manifest and slice registry have invalid JSON shapes")
    states = evaluation.get("states")
    if not isinstance(states, list) or not states:
        raise ValueError("Evaluation manifest has no states")
    if len(registry) != int(evaluation.get("slice_count", len(registry))):
        raise ValueError("Evaluation manifest and slice registry disagree on slice count")

    task_ids = sorted(set(args.task_ids))
    expected_jobs = len(states) * len(registry)
    entries = []
    for task_id in task_ids:
        if task_id < 0 or task_id >= expected_jobs:
            raise ValueError(f"Task ID outside frozen evaluation family: {task_id}")
        state_index, slice_index = divmod(task_id, len(registry))
        state = states[state_index]
        item = registry[slice_index]
        state_id = str(state["state_id"])
        if state_id != args.required_state:
            raise ValueError(f"Retry task {task_id} maps to {state_id}, expected {args.required_state}")
        result_root = Path(str(state["results_root"])).resolve() / str(item["slice_id"])
        if result_root.exists():
            files = [path for path in result_root.rglob("*") if path.is_file()]
            if files:
                raise ValueError(
                    f"Refusing retry because result directory is non-empty: {result_root}; "
                    f"first_files={[str(path) for path in files[:5]]}"
                )
        entries.append(
            {
                "task_id": task_id,
                "state_id": state_id,
                "slice_id": str(item["slice_id"]),
                "result_root": str(result_root),
                "probe_count": int(item["probe_count"]),
            }
        )

    payload = {
        "status": "ready_for_fresh_preflight",
        "retry_family": "qwen_m2_m3_empty_slice_retry_v1",
        "evaluation_manifest": str(evaluation_path),
        "evaluation_manifest_sha256": sha256_file(evaluation_path),
        "slice_registry": str(registry_path),
        "slice_registry_sha256": sha256_file(registry_path),
        "task_ids": task_ids,
        "required_state": args.required_state,
        "expected_new_checkpoints": 0,
        "entries": entries,
        "retention_policy": "retain_valid_slice_evidence; no evaluation checkpoints",
    }
    write_json(output_path, payload)
    print(output_path)


if __name__ == "__main__":
    main()
