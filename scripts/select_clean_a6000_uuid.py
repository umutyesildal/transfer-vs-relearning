#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from transfer_vs_relearning.utils.io import write_json


EXPECTED_GPU_COUNT = 4
EXPECTED_NAME = "NVIDIA RTX A6000"
MINIMUM_FREE_BYTES = 40 * 1024**3
MAXIMUM_USED_BYTES = 512 * 1024**2


def _run(command: list[str]) -> str:
    return subprocess.run(command, check=True, text=True, capture_output=True).stdout.strip()


def _parse_gpu_rows(payload: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in payload.splitlines():
        if not line.strip():
            continue
        values = [value.strip() for value in line.split(",")]
        if len(values) != 6:
            raise ValueError(f"Malformed nvidia-smi GPU row: {line}")
        rows.append(
            {
                "index": int(values[0]),
                "uuid": values[1],
                "name": values[2],
                "total_bytes": int(values[3]) * 1024**2,
                "free_bytes": int(values[4]) * 1024**2,
                "used_bytes": int(values[5]) * 1024**2,
            }
        )
    if len(rows) != EXPECTED_GPU_COUNT:
        raise ValueError(f"Expected exactly four visible GPUs, observed {len(rows)}")
    uuids = [str(row["uuid"]) for row in rows]
    if len(set(uuids)) != EXPECTED_GPU_COUNT or any(not uuid.startswith("GPU-") for uuid in uuids):
        raise ValueError("GPU UUID set is duplicate or non-canonical")
    if any(row["name"] != EXPECTED_NAME for row in rows):
        raise ValueError("Visible GPU set is not exactly four NVIDIA RTX A6000 devices")
    return rows


def choose_clean_uuid(
    gpu_rows: list[dict[str, object]], compute_apps: dict[str, list[str]]
) -> tuple[str, list[dict[str, object]]]:
    audited: list[dict[str, object]] = []
    for row in gpu_rows:
        uuid = str(row["uuid"])
        apps = list(compute_apps.get(uuid, []))
        candidate = (
            not apps
            and int(row["free_bytes"]) >= MINIMUM_FREE_BYTES
            and int(row["used_bytes"]) <= MAXIMUM_USED_BYTES
        )
        audited.append({**row, "compute_app_rows": apps, "clean_candidate": candidate})
    candidates = sorted(str(row["uuid"]) for row in audited if row["clean_candidate"])
    if not candidates:
        raise ValueError("No clean RTX A6000 candidate satisfies the frozen process/memory gates")
    return candidates[0], audited


def validate_visible_binding(selector: str | None, gpu_rows: list[dict[str, object]]) -> list[str]:
    tokens = [token.strip() for token in (selector or "").split(",") if token.strip()]
    if len(tokens) != EXPECTED_GPU_COUNT or len(set(tokens)) != EXPECTED_GPU_COUNT:
        raise ValueError("CUDA_VISIBLE_DEVICES is not an exact unique four-device set")
    indices = {str(row["index"]) for row in gpu_rows}
    uuids = {str(row["uuid"]) for row in gpu_rows}
    if frozenset(tokens) not in {frozenset(indices), frozenset(uuids)}:
        raise ValueError("CUDA_VISIBLE_DEVICES does not match the audited four-device index/UUID set")
    return tokens


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract-sha256", required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    rows = _parse_gpu_rows(
        _run(
            [
                "nvidia-smi",
                "--query-gpu=index,uuid,name,memory.total,memory.free,memory.used",
                "--format=csv,noheader,nounits",
            ]
        )
    )
    visible_before = validate_visible_binding(os.environ.get("CUDA_VISIBLE_DEVICES"), rows)
    apps: dict[str, list[str]] = {}
    for row in rows:
        uuid = str(row["uuid"])
        result = _run(
            [
                "nvidia-smi",
                f"--id={uuid}",
                "--query-compute-apps=pid,process_name,used_memory",
                "--format=csv,noheader,nounits",
            ]
        )
        apps[uuid] = [line.strip() for line in result.splitlines() if line.strip()]
    base_payload = {
        "contract_sha256": args.contract_sha256,
        "selection_rule": "lexicographically_smallest_clean_gpu_uuid",
        "expected_gpu_count": EXPECTED_GPU_COUNT,
        "minimum_free_bytes": MINIMUM_FREE_BYTES,
        "maximum_used_bytes": MAXIMUM_USED_BYTES,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID"),
        "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID"),
        "slurm_job_nodelist": os.environ.get("SLURM_JOB_NODELIST"),
        "cuda_visible_devices_before_selection": visible_before,
    }
    try:
        selected, audited = choose_clean_uuid(rows, apps)
    except ValueError as exc:
        audited = []
        for row in rows:
            uuid = str(row["uuid"])
            process_rows = list(apps.get(uuid, []))
            audited.append(
                {
                    **row,
                    "compute_app_rows": process_rows,
                    "clean_candidate": False,
                    "rejection_reasons": [
                        reason
                        for reason, rejected in (
                            ("compute_apps_present", bool(process_rows)),
                            ("free_bytes_below_minimum", int(row["free_bytes"]) < MINIMUM_FREE_BYTES),
                            ("used_bytes_above_maximum", int(row["used_bytes"]) > MAXIMUM_USED_BYTES),
                        )
                        if rejected
                    ],
                }
            )
        write_json(
            output,
            {
                **base_payload,
                "status": "BLOCKED_NO_CLEAN_CANDIDATE",
                "selected_uuid": None,
                "error": str(exc),
                "gpus": audited,
            },
        )
        raise
    write_json(
        output,
        {**base_payload, "status": "PASS", "selected_uuid": selected, "gpus": audited},
    )
    print(selected)


if __name__ == "__main__":
    main()
