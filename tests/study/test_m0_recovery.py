from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from transfer_vs_relearning.study.m0_parallel import (
    build_m0_parallel_plan,
    initialize_m0_namespace,
)
from transfer_vs_relearning.study.m0_recovery import (
    finalize_recovery_bundle,
    initialize_recovery_namespace,
    run_gpu_memory_guard,
    validate_recovery_source,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/evaluation/m0_olmo_eval_v1_qualification_v1.yaml"


def _complete_lane(plan: dict, root: Path, lane: dict) -> None:
    raw_root = root / "lanes" / lane["id"] / "raw"
    raw_root.mkdir()
    artifact = raw_root / "results_fixture.json"
    artifact.write_text(json.dumps({"lane": lane["id"]}), encoding="utf-8")
    write_json(
        root / "lanes" / lane["id"] / "lane_result.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "lane_id": lane["id"],
            "run_classification": plan["run_classification"],
            "adapter": lane["adapter"],
            "families": lane["families"],
            "task_ids": lane.get("task_ids", []),
            "status": "complete",
            "returncode": 0,
            "duration_seconds": 1.25,
            "artifact_root": str(raw_root),
            "artifacts": [
                {
                    "path": str(artifact),
                    "bytes": artifact.stat().st_size,
                    "sha256": sha256_file(artifact),
                }
            ],
        },
    )


def _source_bundle(tmp_path: Path) -> tuple[dict, Path, str]:
    plan = build_m0_parallel_plan(CONFIG, repo_root=ROOT)
    target = "english_capability"
    source_root = initialize_m0_namespace(tmp_path / "source", plan)
    cache_file = source_root / "cache" / "dataset.arrow"
    cache_file.write_bytes(b"offline-cache")
    (source_root / "preflight").mkdir()
    write_json(
        source_root / "preflight" / "preflight_result.json",
        {"status": "complete", "offline_reload_passed": True},
    )
    for lane in plan["lanes"]:
        if lane["id"] != target:
            _complete_lane(plan, source_root, lane)
    write_json(
        source_root / "bundle_status.json",
        {
            "schema_version": 1,
            "plan_id": plan["plan_id"],
            "status": "partial_invalid",
            "lanes": {
                lane["id"]: "failed" if lane["id"] == target else "complete"
                for lane in plan["lanes"]
            },
        },
    )
    write_json(source_root / "final_inventory.json", {"source": "fixture"})
    return plan, source_root, target


def test_recovery_reuses_six_valid_lanes_and_assembles_seven_lane_bundle(
    tmp_path: Path,
) -> None:
    plan, source_root, target = _source_bundle(tmp_path)
    source = validate_recovery_source(plan, source_root, target)
    assert source["status"] == "ready"
    assert len(source["reusable_lane_ids"]) == 6

    recovery_root = tmp_path / "recovery"
    initialized = initialize_recovery_namespace(
        plan,
        source_root=source_root,
        recovery_root=recovery_root,
        lane_id=target,
    )
    assert initialized["status"] == "initialized_not_run"
    assert (recovery_root / "cache" / "dataset.arrow").read_bytes() == b"offline-cache"
    target_lane = next(lane for lane in plan["lanes"] if lane["id"] == target)
    _complete_lane(plan, recovery_root, target_lane)

    bundle = finalize_recovery_bundle(
        plan,
        source_root=source_root,
        recovery_root=recovery_root,
        lane_id=target,
    )
    assert bundle["status"] == "complete"
    assert bundle["complete_lane_count"] == 7
    assert bundle["normalization_allowed"] is True
    assert bundle["lane_sources"][target] == "recovery"
    assert set(bundle["lane_sources"].values()) == {"source", "recovery"}
    assert (recovery_root / "evaluation_manifest.json").is_file()
    detailed = json.loads((recovery_root / "evaluation_results.json").read_text(encoding="utf-8"))
    assert len(detailed["lanes"]) == 7
    assert sum(row["lane_source"] == "source" for row in detailed["lanes"]) == 6
    qualification = json.loads(
        (recovery_root / "qualification_result.json").read_text(encoding="utf-8")
    )
    assert qualification["bundle_complete"] is True
    assert qualification["blockers"] == [
        "wikitext_count_result_and_heading_parity",
        "turblimp_16_subtask_macro_parity",
    ]


def test_gpu_memory_guard_passes_or_blocks_before_model_load(tmp_path: Path) -> None:
    root = tmp_path / "recovery"
    (root / "lanes" / "english_capability").mkdir(parents=True)
    passed = run_gpu_memory_guard(
        root,
        "english_capability",
        min_free_bytes=16,
        observer=lambda: (32, 64),
    )
    assert passed["status"] == "pass"
    with pytest.raises(RuntimeError, match="free-memory gate failed"):
        run_gpu_memory_guard(
            root,
            "english_capability",
            min_free_bytes=16,
            observer=lambda: (8, 64),
        )
    blocked = json.loads(
        (root / "lanes" / "english_capability" / "gpu_memory_preflight.json").read_text(
            encoding="utf-8"
        )
    )
    assert blocked["status"] == "blocked"
    assert blocked["free_bytes"] == 8


def test_recovery_submitter_launches_one_lane_and_one_afterany_finalizer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    entrypoint_path = ROOT / "scripts/study/recover_m0_lane.py"
    spec = importlib.util.spec_from_file_location("m0_recovery_entrypoint", entrypoint_path)
    assert spec and spec.loader
    entrypoint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entrypoint)

    plan = build_m0_parallel_plan(CONFIG, repo_root=ROOT)
    plan["runtime"]["python"] = "/frozen/env/bin/python"
    recovery_root = tmp_path / "recovery"
    (recovery_root / "logs").mkdir(parents=True)
    submissions: list[list[str]] = []

    def fake_submit(argv: list[str]) -> str:
        submissions.append(argv)
        return str(7000 + len(submissions))

    def fake_probe(_: dict, route: dict) -> dict:
        return {
            "route": route,
            "eligible": True,
            "returncode": 0,
            "estimated_start": "2026-08-16T20:00:00",
            "probe_output": "test-only",
        }

    monkeypatch.setattr(entrypoint, "_submit", fake_submit)
    monkeypatch.setattr(entrypoint, "_probe_route", fake_probe)
    payload = entrypoint.submit_recovery(
        plan,
        config_path=CONFIG,
        repo_root=ROOT,
        source_root=tmp_path / "source",
        recovery_root=recovery_root,
        lane_id="english_capability",
        route_id="v10032gb",
        min_free_bytes=16 * 1024**3,
    )
    assert len(submissions) == 2
    assert "--gres=gpu:v10032gb:1" in submissions[0]
    assert not any(argument.startswith("--array=") for argument in submissions[0])
    assert any("run-lane" in argument for argument in submissions[0])
    assert "--dependency=afterany:7001" in submissions[1]
    assert any("finalize" in argument for argument in submissions[1])
    assert payload["lane_job_id"] == "7001"
    assert payload["finalizer_job_id"] == "7002"
    assert payload["min_free_gpu_bytes"] == 16 * 1024**3
