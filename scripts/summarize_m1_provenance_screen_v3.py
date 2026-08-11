#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.experiments.m1_cross_family import (
    approved_scratch,
    candidate_model_root,
    candidate_training_root,
    load_registry,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


def _read(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble terminal evidence for the Document 152a family.")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    registry_path = args.registry.resolve()
    registry = load_registry(registry_path)
    if registry["version"] != "m1_provenance_screen_v3":
        raise ValueError("The v3 family assembler only accepts m1_provenance_screen_v3")
    scratch_root = approved_scratch(Path(str(registry["scratch_root"])))
    candidates: list[dict[str, Any]] = []
    for candidate in registry["candidates"]:
        label = str(candidate["label"])
        access_path = scratch_root / "manifests/access" / f"{label}.json"
        smoke_path = scratch_root / "manifests/smoke" / f"{label}.json"
        evaluation_path = scratch_root / "evaluations" / label / "evaluation_manifest.json"
        training_manifests = sorted(candidate_training_root(registry, candidate).glob("*/training_manifest.json"))
        training_rows: list[dict[str, Any]] = []
        for path in training_manifests:
            manifest = _read(path)
            training_rows.append(
                {
                    "path": str(path),
                    "sha256": sha256_file(path),
                    "status": manifest.get("status") if manifest else None,
                }
            )
        access = _read(access_path)
        smoke = _read(smoke_path)
        evaluation = _read(evaluation_path)
        if evaluation is not None:
            terminal = "EVALUATION_PREPARED_OR_COMPLETED"
        elif any(row["status"] == "complete" for row in training_rows):
            terminal = "TRAINING_COMPLETE_EVALUATION_MISSING"
        elif smoke is not None:
            terminal = "SMOKE_COMPLETE_TRAINING_INCOMPLETE"
        elif access is not None:
            terminal = "ACCESS_TERMINAL_WITHOUT_SMOKE"
        else:
            terminal = "NO_CANDIDATE_EVIDENCE"
        candidates.append(
            {
                "index": int(candidate["index"]),
                "label": label,
                "model_id": candidate["model_id"],
                "requested_revision": candidate["requested_revision"],
                "terminal_evidence_state": terminal,
                "model_root": str(candidate_model_root(registry, candidate)),
                "access_record": str(access_path) if access_path.is_file() else None,
                "access_status": access.get("status") if access else None,
                "smoke_record": str(smoke_path) if smoke_path.is_file() else None,
                "smoke_status": smoke.get("status") if smoke else None,
                "training_manifests": training_rows,
                "evaluation_manifest": str(evaluation_path) if evaluation_path.is_file() else None,
                "evaluation_manifest_status": evaluation.get("status") if evaluation else None,
            }
        )

    payload = {
        "version": "m1_provenance_screen_v3_terminal_assembly",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "registry": str(registry_path),
        "registry_sha256": sha256_file(registry_path),
        "scratch_root": str(scratch_root),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "scientific_gate_status": "PENDING_METRIC_ASSEMBLY",
        "note": "Terminal assembly preserves partial/blocked candidates; it does not infer a scientific PASS.",
    }
    output = approved_scratch(args.output.resolve())
    write_json(output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
