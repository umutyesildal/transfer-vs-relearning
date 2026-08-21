from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file


SEMANTIC_CLASSIFICATION = "historical_exact_prefix_candidate_ranking_not_free_generation"
REQUIRED_STATES = ("M0", "M1", "M2-A", "M2-B")


def validate_exact_prefix_manifest(
    manifest_path: Path,
    *,
    expected_state: str,
    expected_checkpoint_ids: list[str],
    expected_probe_registry_sha256: str,
) -> dict[str, Any]:
    if expected_state not in REQUIRED_STATES:
        raise ValueError(f"Unsupported exact-prefix state: {expected_state}")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("status") != "complete":
        raise ValueError("Exact-prefix manifest must be complete")
    if payload.get("state") != expected_state:
        raise ValueError("Exact-prefix state identity mismatch")
    if payload.get("semantic_classification") != SEMANTIC_CLASSIFICATION:
        raise ValueError("Exact-prefix semantic identity mismatch")
    if payload.get("probe_registry_sha256") != expected_probe_registry_sha256:
        raise ValueError("Exact-prefix probe registry identity mismatch")
    checkpoints = payload.get("checkpoints")
    if not isinstance(checkpoints, list):
        raise ValueError("Exact-prefix checkpoints must be a list")
    observed_ids = [str(row.get("checkpoint_id")) for row in checkpoints]
    if observed_ids != expected_checkpoint_ids:
        raise ValueError("Exact-prefix checkpoint order or coverage mismatch")
    for row in checkpoints:
        if row.get("status") != "complete" or row.get("probe_count") != 500:
            raise ValueError("Every mandatory exact-prefix checkpoint must complete 500 probes")
        result_path = Path(str(row.get("result_path", "")))
        if not result_path.is_file() or sha256_file(result_path) != row.get("result_sha256"):
            raise ValueError("Exact-prefix checkpoint result identity mismatch")
    return {
        "schema_version": 1,
        "status": "complete",
        "state": expected_state,
        "checkpoint_count": len(checkpoints),
        "probe_count_per_checkpoint": 500,
        "semantic_classification": SEMANTIC_CLASSIFICATION,
        "manifest_path": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
    }
