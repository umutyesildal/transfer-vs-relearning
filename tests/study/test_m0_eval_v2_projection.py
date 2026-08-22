from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.study.m0_eval_v2_projection import (
    MODEL_IDS,
    REQUIRED_LANES,
    discover_projection_bindings,
    inspect_projection_sources,
    load_projection_plan,
    write_projection,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


ROOT = Path(__file__).resolve().parents[2]
MODEL_IDENTITIES = {
    "olmo": ("allenai/OLMo-2-0425-1B", "a" * 40),
    "qwen": ("Qwen/Qwen2.5-1.5B", "b" * 40),
    "smollm": ("HuggingFaceTB/SmolLM2-1.7B", "c" * 40),
}


def _lane_result(root: Path, *, model_id: str, lane_id: str) -> tuple[Path, str]:
    lane_root = root / "lanes" / lane_id
    lane_root.mkdir(parents=True)
    artifact = lane_root / "summary.json"
    write_json(artifact, {"model_id": model_id, "lane_id": lane_id})
    result = lane_root / "lane_result.json"
    write_json(
        result,
        {
            "schema_version": 1,
            "plan_id": f"plan-{model_id}",
            "model_id": model_id,
            "lane_id": lane_id,
            "run_classification": "scientific",
            "status": "complete",
            "returncode": 0,
            "artifacts": [
                {
                    "path": str(artifact),
                    "bytes": artifact.stat().st_size,
                    "sha256": sha256_file(artifact),
                }
            ],
        },
    )
    return result, sha256_file(result)


def _fixture(tmp_path: Path, *, authorized: bool = True) -> Path:
    models: dict[str, dict] = {}
    exact_rows = []
    for model_id in MODEL_IDS:
        repository, revision = MODEL_IDENTITIES[model_id]
        model_root = tmp_path / "m0" / model_id
        lanes = []
        for lane_id in REQUIRED_LANES:
            result, digest = _lane_result(model_root, model_id=model_id, lane_id=lane_id)
            lanes.append(
                {
                    "lane_id": lane_id,
                    "status": "complete",
                    "lane_result_path": str(result),
                    "lane_result_sha256": digest,
                }
            )
        lanes.append(
            {
                "lane_id": "english_retention_pile_10k",
                "status": "failed_pre_scoring",
                "lane_result_path": None,
                "lane_result_sha256": None,
            }
        )
        evaluation = model_root / "evaluation_results.json"
        write_json(
            evaluation,
            {
                "schema_version": 1,
                "status": "partial_invalid",
                "run_classification": "scientific",
                "model": {"repository": repository, "revision": revision},
                "lanes": lanes,
            },
        )
        models[model_id] = {
            "repository": repository,
            "revision": revision,
            "required_lane_ids": list(REQUIRED_LANES),
            "evaluation_results": {"path": str(evaluation), "sha256": sha256_file(evaluation)},
        }

        exact_result, exact_digest = _lane_result(
            tmp_path / "exact" / model_id, model_id=model_id, lane_id="exact_prefix"
        )
        exact_rows.append(
            {
                "model_id": model_id,
                "status": "complete",
                "lane_result": str(exact_result),
                "lane_result_sha256": exact_digest,
            }
        )

    exact_family = tmp_path / "exact" / "family_result.json"
    write_json(
        exact_family,
        {
            "schema_version": 1,
            "status": "complete",
            "semantic_classification": (
                "historical_exact_prefix_candidate_ranking_not_free_generation"
            ),
            "models": exact_rows,
        },
    )
    config = {
        "schema_version": 1,
        "name": "fixture-eval-v2-m0-projection",
        "status": "frozen",
        "execution_authorized": authorized,
        "eval_contract": "eval-v2",
        "rescore_authorized": False,
        "historical_sources_read_only": True,
        "identities": {
            "contract": {
                "path": "documentation/contracts/evaluation/eval-v2.md",
                "sha256": sha256_file(ROOT / "documentation/contracts/evaluation/eval-v2.md"),
            },
            "registry": {
                "path": "configs/evaluation/eval_v2_registry.yaml",
                "sha256": sha256_file(ROOT / "configs/evaluation/eval_v2_registry.yaml"),
            },
        },
        "models": models,
        "exact_prefix": {
            "semantic_classification": (
                "historical_exact_prefix_candidate_ranking_not_free_generation"
            ),
            "family_result": {"path": str(exact_family), "sha256": sha256_file(exact_family)},
        },
        "output_root": str(tmp_path / "projection"),
    }
    config_path = tmp_path / "projection.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return config_path


def test_projection_hash_closes_21_non_pile_lanes_and_three_exact_supplements(
    tmp_path: Path,
) -> None:
    plan = load_projection_plan(_fixture(tmp_path), repo_root=ROOT)
    inspection = inspect_projection_sources(plan)

    assert inspection["status"] == "source_identity_pass"
    assert inspection["canonical_lane_count"] == 21
    assert inspection["exact_prefix_supplement_count"] == 3
    assert len(inspection["source_rows"]) == 24
    assert not any("pile" in row["lane_id"] for row in inspection["source_rows"])
    assert inspection["rescoring_performed"] is False


def test_discovery_freezes_only_top_and_lane_result_bindings(tmp_path: Path) -> None:
    config_path = _fixture(tmp_path, authorized=False)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    for model in config["models"].values():
        model["evaluation_results"]["sha256"] = None
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    discovery = discover_projection_bindings(config_path, repo_root=ROOT)

    assert discovery["status"] == "source_binding_discovery_pass"
    assert discovery["top_manifest_count"] == 4
    assert discovery["lane_binding_count"] == 24
    assert discovery["historical_sources_mutated"] is False
    assert discovery["rescoring_performed"] is False
    assert discovery["artifact_payloads_rehashed"] is False


def test_projection_writes_only_a_fresh_reference_namespace(tmp_path: Path) -> None:
    plan = load_projection_plan(_fixture(tmp_path), repo_root=ROOT)
    manifest = write_projection(plan)
    output_root = Path(plan["output_root"])

    assert manifest["status"] == "projection_complete_pending_metric_normalization"
    assert manifest["metric_rows_written"] == 0
    assert manifest["historical_sources_mutated"] is False
    assert len((output_root / "source_registry.jsonl").read_text().splitlines()) == 24
    assert (output_root / "projection_manifest.json").is_file()
    assert (output_root / "final_inventory.json").is_file()
    with pytest.raises(FileExistsError):
        write_projection(plan)


def test_projection_refuses_execution_without_explicit_config_authority(tmp_path: Path) -> None:
    plan = load_projection_plan(_fixture(tmp_path, authorized=False), repo_root=ROOT)
    with pytest.raises(PermissionError, match="not authorized"):
        write_projection(plan)


def test_projection_fails_closed_on_source_hash_drift(tmp_path: Path) -> None:
    plan = load_projection_plan(_fixture(tmp_path), repo_root=ROOT)
    source = Path(plan["models"]["qwen"]["evaluation_results"]["path"])
    source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        inspect_projection_sources(plan)


def test_projection_fails_closed_when_a_required_lane_is_missing(tmp_path: Path) -> None:
    config_path = _fixture(tmp_path)
    plan = load_projection_plan(config_path, repo_root=ROOT)
    source = Path(plan["models"]["olmo"]["evaluation_results"]["path"])
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["lanes"] = [
        row for row in payload["lanes"] if row["lane_id"] != "generation_integrity"
    ]
    write_json(source, payload)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["models"]["olmo"]["evaluation_results"]["sha256"] = sha256_file(source)
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    plan = load_projection_plan(config_path, repo_root=ROOT)
    with pytest.raises(ValueError, match="generation_integrity"):
        inspect_projection_sources(plan)
