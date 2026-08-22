from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.study.m0_metric_normalization import (
    ALL_LANES,
    METRIC_ALIASES,
    audit_normalization,
    normalize,
)
from transfer_vs_relearning.utils.io import sha256_file


ROOT = Path(__file__).resolve().parents[2]


def _fixture(tmp_path: Path, *, authorized: bool = False) -> Path:
    source_root = tmp_path / "sources"
    registry_rows: list[dict] = []
    for model_id in ("olmo", "qwen", "smollm"):
        for lane_id in ALL_LANES:
            lane_root = source_root / model_id / lane_id
            lane_root.mkdir(parents=True)
            metrics = {
                aliases[0]: float(index + 1)
                for index, aliases in enumerate(METRIC_ALIASES[lane_id].values())
            }
            summary = lane_root / "summary.json"
            summary.write_text(json.dumps({"metrics": metrics}), encoding="utf-8")
            lane_result = lane_root / "lane_result.json"
            lane_payload = {
                "lane_id": lane_id,
                "status": "complete",
                "artifacts": [
                    {
                        "path": str(summary),
                        "bytes": summary.stat().st_size,
                        "sha256": sha256_file(summary),
                    }
                ],
            }
            if lane_id != "exact_prefix":
                lane_payload["returncode"] = 0
            lane_result.write_text(json.dumps(lane_payload), encoding="utf-8")
            registry_rows.append(
                {
                    "model_id": model_id,
                    "lane_id": lane_id,
                    "source_path": str(lane_result),
                    "source_sha256": sha256_file(lane_result),
                }
            )
    registry = tmp_path / "source_registry.jsonl"
    registry.write_text("".join(json.dumps(row) + "\n" for row in registry_rows), encoding="utf-8")
    manifest = tmp_path / "projection_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "status": "projection_complete_pending_metric_normalization",
                "source_registry_sha256": sha256_file(registry),
            }
        ),
        encoding="utf-8",
    )
    config = {
        "schema_version": 1,
        "name": "fixture-normalization",
        "status": "prepared_operator_bound_unexecuted",
        "execution_authorized": authorized,
        "normalization_authorized": authorized,
        "rescore_authorized": False,
        "historical_sources_read_only": True,
        "eval_contract": "eval-v2",
        "identities": {
            "eval_contract": {
                "path": "documentation/contracts/evaluation/eval-v2.md",
                "sha256": sha256_file(ROOT / "documentation/contracts/evaluation/eval-v2.md"),
            },
            "eval_registry": {
                "path": "configs/evaluation/eval_v2_registry.yaml",
                "sha256": sha256_file(ROOT / "configs/evaluation/eval_v2_registry.yaml"),
            },
            "result_schema": {
                "path": "documentation/evaluation/RESULT_SCHEMA_V1.md",
                "sha256": sha256_file(ROOT / "documentation/evaluation/RESULT_SCHEMA_V1.md"),
            },
        },
        "input_projection": {
            "source_registry": str(registry),
            "source_registry_sha256": sha256_file(registry),
            "projection_manifest": str(manifest),
            "projection_manifest_sha256": sha256_file(manifest),
            "required_source_rows": 24,
        },
        "output_root": str(tmp_path / "normalized"),
    }
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path


def test_normalization_audit_requires_all_24_rows_and_aliases(tmp_path: Path) -> None:
    report = audit_normalization(_fixture(tmp_path), repo_root=ROOT)

    assert report["status"] == "audit_pass"
    assert report["source_row_count"] == 24
    assert report["metric_observation_candidate_count"] == 42
    assert report["expected_metric_observation_count"] == 42
    assert report["normalization_performed"] is False
    assert report["rescoring_performed"] is False


def test_normalization_refuses_unauthorized_config_without_output(tmp_path: Path) -> None:
    config = _fixture(tmp_path, authorized=False)

    with pytest.raises(PermissionError, match="not authorized"):
        normalize(config, repo_root=ROOT)
    assert not (tmp_path / "normalized").exists()


def test_normalization_audit_blocks_ambiguous_metric(tmp_path: Path) -> None:
    config = _fixture(tmp_path)
    raw = json.loads((tmp_path / "sources/olmo/english_grammar_blimp/summary.json").read_text())
    raw["metrics"]["accuracy"] = 0.5
    raw["metrics"]["macro_accuracy"] = 0.5
    summary = tmp_path / "sources/olmo/english_grammar_blimp/summary.json"
    summary.write_text(json.dumps(raw), encoding="utf-8")
    lane = tmp_path / "sources/olmo/english_grammar_blimp/lane_result.json"
    lane_payload = json.loads(lane.read_text())
    lane_payload["artifacts"][0]["bytes"] = summary.stat().st_size
    lane_payload["artifacts"][0]["sha256"] = sha256_file(summary)
    lane.write_text(json.dumps(lane_payload), encoding="utf-8")
    registry = tmp_path / "source_registry.jsonl"
    rows = [json.loads(line) for line in registry.read_text().splitlines()]
    for row in rows:
        if row["model_id"] == "olmo" and row["lane_id"] == "english_grammar_blimp":
            row["source_sha256"] = sha256_file(lane)
    registry.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    manifest = tmp_path / "projection_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "status": "projection_complete_pending_metric_normalization",
                "source_registry_sha256": sha256_file(registry),
            }
        ),
        encoding="utf-8",
    )
    payload = yaml.safe_load(config.read_text())
    payload["input_projection"]["source_registry_sha256"] = sha256_file(registry)
    payload["input_projection"]["projection_manifest_sha256"] = sha256_file(manifest)
    config.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    report = audit_normalization(config, repo_root=ROOT)
    assert report["status"] == "audit_blocked"
    assert any(item["lane_id"] == "english_grammar_blimp" for item in report["findings"])
