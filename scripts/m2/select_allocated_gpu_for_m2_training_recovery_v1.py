#!/usr/bin/env python3
"""Persist the complete allocated-GPU ledger and select one bounded-safe device."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import write_json


def choose_gpu(rows: list[dict[str, Any]], minimum_free_mib: int, maximum_used_mib: int) -> dict[str, Any] | None:
    candidates = [
        row for row in rows
        if row["memory_free_mib"] >= minimum_free_mib and row["memory_used_mib"] <= maximum_used_mib
    ]
    return sorted(candidates, key=lambda row: (-row["memory_free_mib"], row["uuid"]))[0] if candidates else None


def _query(token: str) -> dict[str, Any]:
    fields = "index,uuid,name,memory.total,memory.used,memory.free"
    raw = subprocess.check_output(
        ["nvidia-smi", f"--id={token}", f"--query-gpu={fields}", "--format=csv,noheader,nounits"],
        text=True,
    ).strip()
    values = [value.strip() for value in raw.split(",")]
    if len(values) != 6:
        raise ValueError(f"Unexpected nvidia-smi GPU row for {token!r}: {raw!r}")
    process = subprocess.run(
        [
            "nvidia-smi", f"--id={token}",
            "--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory",
            "--format=csv,noheader,nounits",
        ],
        text=True, capture_output=True, check=False,
    )
    process_rows = []
    for line in process.stdout.splitlines():
        parts = [value.strip() for value in line.split(",")]
        if len(parts) == 4 and parts[1].isdigit():
            process_rows.append(
                {"gpu_uuid": parts[0], "pid": int(parts[1]), "process_name": parts[2], "used_memory_mib": int(parts[3])}
            )
    return {
        "allocated_token": token,
        "index": int(values[0]),
        "uuid": values[1],
        "name": values[2],
        "memory_total_mib": int(values[3]),
        "memory_used_mib": int(values[4]),
        "memory_free_mib": int(values[5]),
        "compute_process_query_returncode": process.returncode,
        "compute_process_query_stderr": process.stderr.strip(),
        "compute_processes": process_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimum-free-mib", type=int, required=True)
    parser.add_argument("--maximum-used-mib", type=int, required=True)
    parser.add_argument("--expected-device-count", type=int, default=3)
    args = parser.parse_args()
    visible = os.environ.get("CUDA_VISIBLE_DEVICES") or os.environ.get("SLURM_JOB_GPUS") or ""
    tokens = [token.strip() for token in visible.split(",") if token.strip()]
    payload: dict[str, Any] = {
        "schema_version": 1,
        "status": "M2_GPU_SELECTION_BLOCKED",
        "allocated_tokens": tokens,
        "expected_device_count": args.expected_device_count,
        "minimum_free_mib": args.minimum_free_mib,
        "maximum_used_mib": args.maximum_used_mib,
        "deterministic_rule": "highest_free_mib_then_lexicographic_uuid",
        "zero_process_required": False,
        "gpus": [],
        "selected": None,
    }
    try:
        if len(tokens) != args.expected_device_count:
            raise ValueError(f"Expected {args.expected_device_count} allocated GPUs, observed {len(tokens)}")
        rows = [_query(token) for token in tokens]
        if len({row["uuid"] for row in rows}) != args.expected_device_count:
            raise ValueError("Allocated GPU UUIDs are not unique")
        payload["gpus"] = rows
        selected = choose_gpu(rows, args.minimum_free_mib, args.maximum_used_mib)
        if selected is None:
            raise ValueError("No allocated GPU satisfies the frozen free/used VRAM bounds")
        payload["status"] = "M2_GPU_SELECTION_PASS"
        payload["selected"] = {
            "allocated_token": selected["allocated_token"],
            "uuid": selected["uuid"],
            "index": selected["index"],
            "memory_free_mib": selected["memory_free_mib"],
            "memory_used_mib": selected["memory_used_mib"],
        }
        write_json(args.output, payload)
        print(selected["allocated_token"])
        return 0
    except Exception as exc:
        payload["failure_reason"] = str(exc)
        write_json(args.output, payload)
        print(str(exc), file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
