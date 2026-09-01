#!/usr/bin/env python3
"""Atomically create or update one recovery training-task audit."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from transfer_vs_relearning.utils.io import sha256_file, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--status", choices=("TRAINING_TASK_LAUNCH", "TRAINING_TASK_PASS", "TRAINING_TASK_FAIL"), required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--arm", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--training-output-root", required=True)
    parser.add_argument("--selector-audit", type=Path)
    parser.add_argument("--selected-gpu", default="")
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--array-job-id", required=True)
    parser.add_argument("--array-task-id", required=True)
    args = parser.parse_args()
    prior = {}
    if args.output.exists():
        import json
        prior = json.loads(args.output.read_text(encoding="utf-8"))
    payload = {
        **prior,
        "schema_version": 1,
        "status": args.status,
        "role": args.role,
        "arm": args.arm,
        "config": args.config,
        "training_output_root": args.training_output_root,
        "job_id": args.job_id,
        "array_job_id": args.array_job_id,
        "array_task_id": args.array_task_id,
        "selected_gpu": args.selected_gpu or None,
        "selector_audit": str(args.selector_audit) if args.selector_audit else None,
        "selector_audit_sha256": sha256_file(args.selector_audit) if args.selector_audit and args.selector_audit.is_file() else None,
        "exit_code": args.exit_code,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if "created_at_utc" not in payload:
        payload["created_at_utc"] = payload["updated_at_utc"]
    write_json(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
