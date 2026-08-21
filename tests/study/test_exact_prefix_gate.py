from __future__ import annotations

import json
from pathlib import Path

import pytest

from transfer_vs_relearning.study.adapters.exact_prefix_gate import (
    SEMANTIC_CLASSIFICATION,
    validate_exact_prefix_manifest,
)
from transfer_vs_relearning.utils.io import sha256_file


def _manifest(tmp_path: Path, *, state: str = "M1") -> Path:
    result = tmp_path / "result.json"
    result.write_text('{"accuracy": 0.5}\n', encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "status": "complete",
                "state": state,
                "semantic_classification": SEMANTIC_CLASSIFICATION,
                "probe_registry_sha256": "a" * 64,
                "checkpoints": [
                    {
                        "checkpoint_id": "epoch-1",
                        "status": "complete",
                        "probe_count": 500,
                        "result_path": str(result),
                        "result_sha256": sha256_file(result),
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return manifest


def test_exact_prefix_gate_requires_complete_hash_valid_checkpoint_coverage(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    result = validate_exact_prefix_manifest(
        manifest,
        expected_state="M1",
        expected_checkpoint_ids=["epoch-1"],
        expected_probe_registry_sha256="a" * 64,
    )
    assert result["status"] == "complete"
    assert result["probe_count_per_checkpoint"] == 500


def test_exact_prefix_gate_fails_closed_on_missing_checkpoint_or_wrong_state(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    with pytest.raises(ValueError, match="coverage mismatch"):
        validate_exact_prefix_manifest(
            manifest,
            expected_state="M1",
            expected_checkpoint_ids=["epoch-1", "epoch-2"],
            expected_probe_registry_sha256="a" * 64,
        )
    with pytest.raises(ValueError, match="state identity"):
        validate_exact_prefix_manifest(
            manifest,
            expected_state="M2-A",
            expected_checkpoint_ids=["epoch-1"],
            expected_probe_registry_sha256="a" * 64,
        )
