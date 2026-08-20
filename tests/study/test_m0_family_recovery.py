from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.study.m0_family_recovery import (
    finalize_family_recovery,
    finalize_recovered_model,
    initialize_family_recovery_namespace,
    load_family_recovery_plan,
    validate_family_recovery_source,
)
from transfer_vs_relearning.study.m0_parallel import build_m0_parallel_plan
from transfer_vs_relearning.utils.io import sha256_file, write_json


ROOT = Path(__file__).resolve().parents[2]
CONFIGS = {
    "olmo": ROOT / "configs/evaluation/m0_scientific/olmo_m0_eval_v1_scientific_v1.yaml",
    "qwen": ROOT / "configs/evaluation/m0_scientific/qwen_m0_eval_v1_scientific_v1.yaml",
    "smollm": ROOT / "configs/evaluation/m0_scientific/smollm_m0_eval_v1_scientific_v1.yaml",
}
TARGETS = {
    "olmo": ["english_capability", "turkish_capability", "turkish_perplexity"],
    "qwen": ["english_retention_pile_10k", "turkish_capability", "turkish_perplexity"],
    "smollm": ["english_capability"],
}


def _complete_lane(plan: dict, root: Path, lane: dict) -> None:
    lane_root = root / "lanes" / lane["id"]
    raw = lane_root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    artifact = raw / "fixture.json"
    artifact.write_text(json.dumps({"lane": lane["id"]}), encoding="utf-8")
    write_json(
        lane_root / "lane_result.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "lane_id": lane["id"],
            "adapter": lane["adapter"],
            "families": lane["families"],
            "task_ids": lane.get("task_ids", []),
            "run_classification": "scientific",
            "status": "complete",
            "returncode": 0,
            "duration_seconds": 1.0,
            "artifact_root": str(raw),
            "artifacts": [
                {"path": str(artifact), "bytes": artifact.stat().st_size, "sha256": sha256_file(artifact)}
            ],
        },
    )


def _failed_lane(plan: dict, root: Path, lane: dict) -> None:
    lane_root = root / "lanes" / lane["id"]
    lane_root.mkdir(parents=True, exist_ok=True)
    stderr = lane_root / "stderr.log"
    stderr.write_text("operational oom", encoding="utf-8")
    write_json(
        lane_root / "lane_result.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "lane_id": lane["id"],
            "adapter": lane["adapter"],
            "families": lane["families"],
            "task_ids": lane.get("task_ids", []),
            "run_classification": "scientific",
            "status": "failed_pre_scoring",
            "returncode": 1,
            "artifacts": [
                {"path": str(stderr), "bytes": stderr.stat().st_size, "sha256": sha256_file(stderr)}
            ],
        },
    )


def _fixture(tmp_path: Path) -> tuple[Path, dict[str, dict]]:
    source_family = tmp_path / "source-family"
    recovery_family = tmp_path / "recovery-family"
    model_rows: dict[str, dict] = {}
    plans: dict[str, dict] = {}
    for model_id, config in CONFIGS.items():
        plan = build_m0_parallel_plan(config, repo_root=ROOT)
        plans[model_id] = plan
        source = source_family / model_id
        source.mkdir(parents=True)
        (source / "preflight").mkdir()
        write_json(source / "parallel_plan.json", plan)
        write_json(
            source / "preflight/preflight_result.json",
            {"status": "complete", "offline_reload_passed": True},
        )
        statuses = {}
        source_lanes = {}
        for lane in plan["lanes"]:
            if lane["id"] in TARGETS[model_id]:
                _failed_lane(plan, source, lane)
                statuses[lane["id"]] = "partial_invalid"
                contract_status = "failed_pre_scoring"
            else:
                _complete_lane(plan, source, lane)
                statuses[lane["id"]] = "complete"
                contract_status = "complete"
            result = source / "lanes" / lane["id"] / "lane_result.json"
            source_lanes[lane["id"]] = {
                "status": contract_status,
                "lane_result_sha256": sha256_file(result),
            }
        write_json(
            source / "bundle_status.json",
            {
                "schema_version": 1,
                "plan_id": plan["plan_id"],
                "status": "partial_invalid",
                "lanes": statuses,
                "normalization_allowed": False,
            },
        )
        write_json(source / "scientific_bundle_result.json", {"status": "partial_invalid"})
        write_json(source / "final_inventory.json", {"fixture": model_id})
        targets = {}
        for lane_id in TARGETS[model_id]:
            targets[lane_id] = {
                "route_id": "a10080gb" if model_id == "qwen" and lane_id == "english_retention_pile_10k" else "v10032gb",
                "min_free_gpu_bytes": 64 if model_id == "qwen" and lane_id == "english_retention_pile_10k" else 28,
            }
        model_rows[model_id] = {
            "config": str(config),
            "config_sha256": sha256_file(config),
            "source_root": str(source),
            "recovery_root": str(recovery_family / model_id),
            "source_parallel_plan_sha256": sha256_file(source / "parallel_plan.json"),
            "source_preflight_sha256": sha256_file(source / "preflight/preflight_result.json"),
            "source_bundle_status_sha256": sha256_file(source / "bundle_status.json"),
            "source_scientific_bundle_result_sha256": sha256_file(source / "scientific_bundle_result.json"),
            "source_final_inventory_sha256": sha256_file(source / "final_inventory.json"),
            "source_lanes": source_lanes,
            "targets": targets,
        }
    write_json(source_family / "three_model_m0_raw_bundle.json", {"status": "partial_invalid"})
    config_payload = {
        "schema_version": 1,
        "name": "fixture-recovery",
        "status": "frozen",
        "execution_authorized": False,
        "source_family_root": str(source_family),
        "source_family_bundle_sha256": sha256_file(source_family / "three_model_m0_raw_bundle.json"),
        "source_lane_count": 24,
        "recovery_lane_count": 7,
        "model_order": ["olmo", "qwen", "smollm"],
        "recovery_family_root": str(recovery_family),
        "hu_home_gate": {"path": "/tmp", "limit_bytes": 1, "writes_authorized": False},
        "implementation": {"commit": "0" * 40, "files": {}},
        "models": model_rows,
    }
    config_path = tmp_path / "recovery.yaml"
    config_path.write_text(yaml.safe_dump(config_payload, sort_keys=False), encoding="utf-8")
    return config_path, plans


def test_recovery_plan_binds_exactly_seventeen_plus_seven(tmp_path: Path) -> None:
    config_path, _ = _fixture(tmp_path)
    recovery = load_family_recovery_plan(config_path, repo_root=ROOT)
    assert recovery["retained_lane_count"] == 17
    assert recovery["target_lane_count"] == 7
    evidence = validate_family_recovery_source(recovery)
    assert evidence["status"] == "ready"
    assert evidence["retained_lane_count"] == 17
    retained = Path(recovery["models"][0]["source_root"]) / "lanes/english_retention_wikitext/lane_result.json"
    retained.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        validate_family_recovery_source(recovery)


def test_recovery_assembles_source_and_recovered_lanes_without_rescoring(tmp_path: Path) -> None:
    config_path, _ = _fixture(tmp_path)
    recovery = load_family_recovery_plan(config_path, repo_root=ROOT)
    initialize_family_recovery_namespace(recovery)
    for model in recovery["models"]:
        for lane in model["plan"]["lanes"]:
            if lane["id"] in model["targets"]:
                _complete_lane(model["plan"], Path(model["recovery_root"]), lane)
        bundle = finalize_recovered_model(model)
        assert bundle["status"] == "complete"
        assert bundle["complete_lane_count"] == 8
        assert bundle["recovered_lane_count"] == len(model["targets"])
    family = finalize_family_recovery(recovery)
    assert family["status"] == "complete_raw_pending_normalization"
    assert family["normalization_allowed"] is True
    assert family["retained_lane_count"] == 17
    assert family["recovered_lane_count"] == 7


def test_operator_submits_only_seven_lanes_and_four_finalizers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path, _ = _fixture(tmp_path)
    recovery = load_family_recovery_plan(config_path, repo_root=ROOT)
    entrypoint = ROOT / "scripts/study/recover_three_model_m0.py"
    spec = importlib.util.spec_from_file_location("recover_three_model_m0", entrypoint)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    submissions: list[list[str]] = []

    def fake_submit(argv: list[str]) -> str:
        submissions.append(argv)
        return str(8000 + len(submissions))

    monkeypatch.setattr(module, "_submit", fake_submit)
    monkeypatch.setattr(
        module,
        "_probe_route",
        lambda model, route: {
            "model_id": model["model_id"],
            "route": route,
            "eligible": True,
            "returncode": 0,
            "estimated_start": "2026-08-20T12:00:00",
            "probe_output": "eligible",
        },
    )
    payload = module.submit_family_recovery(recovery, config_path=config_path, repo_root=ROOT)
    assert len(submissions) == 11
    assert sum(any("run-lane" in value for value in argv) for argv in submissions) == 7
    assert sum(any("finalize-model" in value for value in argv) for argv in submissions) == 3
    assert sum(any("finalize-family" in value for value in argv) for argv in submissions) == 1
    pile = next(argv for argv in submissions if any("english_retention_pile_10k" in value for value in argv))
    assert "--gres=gpu:a10080gb:1" in pile
    assert payload["family_finalizer"] == "8011"
