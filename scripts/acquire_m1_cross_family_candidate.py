#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from transfer_vs_relearning.experiments.m1_cross_family import (
    approved_scratch,
    candidate_by_index,
    load_registry,
)
from transfer_vs_relearning.models.download import download_model_snapshot
from transfer_vs_relearning.utils.io import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve, download, and manifest one Document 105 base model.")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--candidate-index", type=int, required=True)
    args = parser.parse_args()
    registry_path = args.registry.resolve()
    registry = load_registry(registry_path)
    candidate = candidate_by_index(registry, args.candidate_index)
    scratch_root = approved_scratch(Path(str(registry["scratch_root"])))
    artifact_root = approved_scratch(scratch_root / "models")
    model_root = approved_scratch(artifact_root / str(candidate["model_id"]).replace("/", "__"))
    access_record = approved_scratch(scratch_root / "manifests" / "access" / f"{candidate['label']}.json")
    base_record = {
        "candidate_index": int(candidate["index"]),
        "label": candidate["label"],
        "model_id": candidate["model_id"],
        "requested_revision": candidate["requested_revision"],
        "required": bool(candidate["required"]),
        "gated": bool(candidate.get("gated", False)),
        "registry": str(registry_path),
        "registry_sha256": sha256_file(registry_path),
        "attempted_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        manifest = download_model_snapshot(
            model_id=str(candidate["model_id"]),
            revision=str(candidate["requested_revision"]),
            artifact_root=artifact_root,
        )
        record = {
            **base_record,
            "status": "passed",
            "resolved_revision": manifest["resolved_revision"],
            "model_manifest": str(artifact_root / str(candidate["model_id"]).replace("/", "__") / "model_manifest.json"),
            "parameter_count": manifest["parameter_count"],
            "tokenizer_class": manifest["tokenizer_class"],
        }
        write_json(access_record, record)
        print(json.dumps(record, indent=2, sort_keys=True))
    except Exception as exc:
        partial_cleanup = False
        if model_root.exists() and not (model_root / "model_manifest.json").is_file():
            shutil.rmtree(model_root)
            partial_cleanup = True
        record = {
            **base_record,
            "status": "failed_required_access_or_compatibility" if candidate["required"] else "not_run_access_gate",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "partial_model_root_cleanup": partial_cleanup,
        }
        write_json(access_record, record)
        print(json.dumps(record, indent=2, sort_keys=True))
        if candidate["required"]:
            raise


if __name__ == "__main__":
    main()
