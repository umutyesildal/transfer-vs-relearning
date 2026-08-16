from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.study.workflow import (
    assess_m0_readiness,
    build_study_plan,
    initialize_study_namespace,
    load_study_config,
    load_study_namespace,
    next_stage_status,
    render_luna_packets,
    run_with_registered_adapters,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/studies/m0_to_m2_eval_v1_template.yaml"
EXPECTED_STAGES = [
    "contract_preflight",
    "m0_evaluation",
    "m0_probing",
    "m0_normalization",
    "m1_training",
    "m1_evaluation",
    "m1_probing",
    "m1_checkpoint_selection",
    "m2_sibling_preflight",
    "m2a_training",
    "m2b_training",
    "m2a_evaluation_probing",
    "m2b_evaluation_probing",
    "branch_analysis",
    "presentation_bundle",
]


def _write_yaml(path: Path, payload: dict) -> Path:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_full_study_plan_has_complete_causal_order_and_sibling_parent() -> None:
    plan = build_study_plan(CONFIG, repo_root=ROOT)
    assert plan["status"] == "planned_not_authorized"
    assert plan["execution_authorized"] is False
    assert [stage["id"] for stage in plan["stages"]] == EXPECTED_STAGES
    assert plan["state_design"]["m2_siblings"] == {
        "parent": "M1",
        "arms": ["M2-A", "M2-B"],
        "matched_budget_required": True,
    }
    stages = {stage["id"]: stage for stage in plan["stages"]}
    assert stages["m2a_training"]["depends_on"] == ["m2_sibling_preflight"]
    assert stages["m2b_training"]["depends_on"] == ["m2_sibling_preflight"]
    assert set(stages["branch_analysis"]["depends_on"]) == {
        "m2a_evaluation_probing",
        "m2b_evaluation_probing",
    }


def test_study_rejects_missing_causal_edge_and_context_overflow(tmp_path: Path) -> None:
    payload = load_study_config(CONFIG)
    broken = copy.deepcopy(payload)
    by_id = {stage["id"]: stage for stage in broken["stages"]}
    by_id["m2b_training"]["depends_on"] = ["m1_checkpoint_selection"]
    with pytest.raises(ValueError, match="causal edge"):
        build_study_plan(_write_yaml(tmp_path / "broken.yaml", broken), repo_root=ROOT)
    crowded = copy.deepcopy(payload)
    crowded["stages"][0]["context_files"] = [f"file-{index}" for index in range(9)]
    with pytest.raises(ValueError, match="eight-file context budget"):
        build_study_plan(_write_yaml(tmp_path / "crowded.yaml", crowded), repo_root=ROOT)


def test_frozen_study_rejects_unresolved_bindings(tmp_path: Path) -> None:
    payload = load_study_config(CONFIG)
    payload["status"] = "frozen"
    with pytest.raises(ValueError, match="cannot contain placeholders"):
        build_study_plan(_write_yaml(tmp_path / "frozen.yaml", payload), repo_root=ROOT)


def test_namespace_is_fresh_and_next_stage_stops_before_external_work(tmp_path: Path) -> None:
    plan = build_study_plan(CONFIG, repo_root=ROOT)
    namespace = initialize_study_namespace(tmp_path / "study", plan)
    loaded_plan, state = load_study_namespace(namespace)
    assert next_stage_status(loaded_plan, state) == {
        "stage_id": "contract_preflight",
        "status": "ready_for_registered_adapter",
        "authority_class": "local_read_only",
    }
    state["stages"]["contract_preflight"]["status"] = "complete"
    assert next_stage_status(loaded_plan, state) == {
        "stage_id": "m0_evaluation",
        "status": "awaiting_authorization",
        "authority_class": "evaluation",
    }
    with pytest.raises(FileExistsError):
        initialize_study_namespace(namespace, plan)


def test_registered_adapter_runner_can_walk_every_stage_but_stops_without_scope() -> None:
    plan = build_study_plan(CONFIG, repo_root=ROOT)
    calls: list[str] = []

    def adapter(stage: dict) -> dict:
        calls.append(stage["id"])
        return {"status": "complete", "evidence": [f"{stage['id']}.json"]}

    adapters = {stage["adapter_id"]: adapter for stage in plan["stages"]}
    blocked = run_with_registered_adapters(
        plan,
        adapters,
        authorized_scopes={"local_read_only", "local_write"},
    )
    assert blocked["status"] == "awaiting_authorization"
    assert blocked["blocked_stage"] == "m0_evaluation"

    calls.clear()
    complete = run_with_registered_adapters(
        plan,
        adapters,
        authorized_scopes={"local_read_only", "local_write", "evaluation", "training"},
    )
    assert complete["status"] == "complete"
    assert calls == EXPECTED_STAGES


def test_luna_packets_are_micro_context_adapter_tasks(tmp_path: Path) -> None:
    plan = build_study_plan(CONFIG, repo_root=ROOT)
    packets = render_luna_packets(plan, tmp_path / "packets")
    assert len(packets) == 15
    for packet in packets:
        text = packet.read_text(encoding="utf-8")
        assert len(text.splitlines()) <= 160
        assert "Packet mode: `adapter_implementation_or_validation`" in text
        assert "Do not execute the" in text
        assert "__" not in text
    manifest = json.loads((tmp_path / "packets/manifest.json").read_text(encoding="utf-8"))
    assert manifest["packets"] == [packet.name for packet in packets]


def test_entrypoint_catalog_preserves_every_old_file_and_flat_roots_are_clean() -> None:
    catalog = json.loads((ROOT / "configs/entrypoints/catalog.json").read_text(encoding="utf-8"))
    entries = catalog["entries"]
    assert len(entries) == 264
    assert len({entry["old_path"] for entry in entries}) == 264
    assert len({entry["path"] for entry in entries}) == 264
    assert all((ROOT / entry["path"]).is_file() for entry in entries)
    assert not any((ROOT / entry["old_path"]).exists() for entry in entries)
    assert {path.name for path in (ROOT / "scripts").iterdir() if path.is_file()} == {"README.md"}
    assert {path.name for path in (ROOT / "slurm").iterdir() if path.is_file()} == {"README.md"}


def test_m0_preflight_reports_current_contract_and_adapter_blockers() -> None:
    payload = assess_m0_readiness(
        CONFIG,
        repo_root=ROOT,
        project_state_path=ROOT / "documentation/current/PROJECT_STATE.yaml",
    )
    assert payload["status"] == "blocked"
    assert payload["scientific_work_started"] is False
    assert set(payload["blockers"]) == {
        "study_contract_frozen",
        "study_bindings_resolved",
    }
    checks = {row["id"]: row for row in payload["checks"]}
    assert checks["m0_evaluation_adapter_present"]["status"] == "pass"
    assert checks["m0_probing_adapter_present"]["status"] == "pass"
    assert checks["lm_eval_environment_identity"]["status"] == "pass"
    assert "version=0.4.12" in checks["lm_eval_environment_identity"]["detail"]
    assert "6d642546f4688648fced259eb3302efd36ece5af" in checks[
        "lm_eval_environment_identity"
    ]["detail"]
