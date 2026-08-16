from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.study.model_matrix import (
    MODEL_IDS,
    PHASES,
    build_model_matrix_plan,
    initialize_model_matrix_namespace,
    load_model_matrix_namespace,
    next_model_matrix_wave,
    render_model_matrix_packets,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/studies/three_model_m0_to_m2_matrix_v1.yaml"


def _config() -> dict:
    value = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _write_yaml(path: Path, value: dict) -> Path:
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    return path


def test_matrix_expands_three_models_into_nine_three_job_waves() -> None:
    plan = build_model_matrix_plan(CONFIG, repo_root=ROOT)
    assert plan["status"] == "planned_not_authorized"
    assert plan["execution_authorized"] is False
    assert plan["model_count"] == 3
    assert plan["node_count"] == 27
    assert plan["wave_count"] == 9
    assert plan["training_node_count"] == 9
    assert plan["state_evaluation_node_count"] == 12
    assert [wave["id"] for wave in plan["waves"]] == [phase["id"] for phase in PHASES]
    assert all(len(wave["nodes"]) == 3 for wave in plan["waves"])
    assert all(wave["max_concurrent_jobs"] == 3 for wave in plan["waves"])
    for wave in plan["waves"]:
        assert [node_id.split("__", 1)[0] for node_id in wave["nodes"]] == MODEL_IDS


def test_matrix_preserves_same_m1_parent_and_matched_sibling_design() -> None:
    plan = build_model_matrix_plan(CONFIG, repo_root=ROOT)
    assert plan["state_design"]["m2_siblings"] == {
        "parent": "M1",
        "arms": ["M2-A", "M2-B"],
        "matched_budget_required": True,
    }
    nodes = {node["id"]: node for node in plan["nodes"]}
    for model_id in MODEL_IDS:
        preflight = f"{model_id}__m2_sibling_preflight"
        assert nodes[f"{model_id}__m2a_training"]["causal_dependencies"] == [preflight]
        assert nodes[f"{model_id}__m2b_training"]["causal_dependencies"] == [preflight]
        assert nodes[f"{model_id}__branch_analysis"]["causal_dependencies"] == [
            f"{model_id}__m2a_evaluation",
            f"{model_id}__m2b_evaluation",
        ]


def test_matrix_has_explicit_blockers_instead_of_placeholder_execution() -> None:
    plan = build_model_matrix_plan(CONFIG, repo_root=ROOT)
    nodes = {node["id"]: node for node in plan["nodes"]}
    olmo_m0 = nodes["olmo__m0_evaluation"]
    assert olmo_m0["status"] == "blocked_not_authorized"
    assert "evaluation_contract_not_authorized" in olmo_m0["execution_blockers"]
    assert "evaluation_contract_not_frozen" not in olmo_m0["execution_blockers"]
    assert "m0_scientific_evaluation_not_authorized" in olmo_m0["execution_blockers"]
    assert "m0_scientific_evaluation_not_frozen" not in olmo_m0["execution_blockers"]
    assert "matrix_not_authorized" in olmo_m0["execution_blockers"]
    qwen_m1 = nodes["qwen__m1_training"]
    assert "m1_training_contract_not_frozen" in qwen_m1["execution_blockers"]
    assert "m1_recipe_config_missing" in qwen_m1["execution_blockers"]
    assert nodes["smollm__m2_sibling_preflight"]["execution_blockers"] == []
    assert not any(
        node["status"] == "pending"
        for node in plan["nodes"]
        if node["kind"] in {"evaluation", "training"}
    )


def test_matrix_rejects_premature_authorization_and_sibling_drift(tmp_path: Path) -> None:
    premature = _config()
    premature["execution_authorized"] = True
    with pytest.raises(ValueError, match="unresolved execution blockers"):
        build_model_matrix_plan(_write_yaml(tmp_path / "premature.yaml", premature), repo_root=ROOT)

    drift = _config()
    drift["state_design"]["m2_siblings"]["parent"] = "M0"
    with pytest.raises(ValueError, match="matched siblings"):
        build_model_matrix_plan(_write_yaml(tmp_path / "drift.yaml", drift), repo_root=ROOT)


def test_wave_barrier_requires_all_three_models_before_next_wave() -> None:
    plan = build_model_matrix_plan(CONFIG, repo_root=ROOT)
    nodes = {node["id"]: node for node in plan["nodes"]}
    first_wave = set(plan["waves"][0]["nodes"])
    for node_id in plan["waves"][1]["nodes"]:
        assert first_wave.issubset(nodes[node_id]["depends_on"])
        assert f"{nodes[node_id]['model_id']}__m0_evaluation" in nodes[node_id][
            "causal_dependencies"
        ]


def test_namespace_and_next_wave_remain_fail_closed(tmp_path: Path) -> None:
    plan = build_model_matrix_plan(CONFIG, repo_root=ROOT)
    namespace = initialize_model_matrix_namespace(tmp_path / "matrix", plan)
    loaded_plan, state = load_model_matrix_namespace(namespace)
    next_wave = next_model_matrix_wave(loaded_plan, state)
    assert next_wave["wave_id"] == "m0_evaluation"
    assert next_wave["status"] == "blocked_not_authorized"
    assert next_wave["dependency_blockers"] == []
    assert len(next_wave["nodes"]) == 3
    assert any("matrix_not_authorized" in blocker for blocker in next_wave["execution_blockers"])
    with pytest.raises(FileExistsError):
        initialize_model_matrix_namespace(namespace, plan)


def test_luna_packets_are_one_model_one_stage_micro_context(tmp_path: Path) -> None:
    plan = build_model_matrix_plan(CONFIG, repo_root=ROOT)
    packets = render_model_matrix_packets(plan, tmp_path / "packets")
    assert len(packets) == 27
    for packet in packets:
        text = packet.read_text(encoding="utf-8")
        assert len(text.splitlines()) <= 100
        assert "Do not rely on chat history" in text
        assert "Do not execute evaluation, scoring or training" in text
        assert sum(repository in text for repository in [
            "allenai/OLMo-2-0425-1B",
            "Qwen/Qwen2.5-1.5B",
            "HuggingFaceTB/SmolLM2-1.7B",
        ]) == 1
    manifest = json.loads((tmp_path / "packets/manifest.json").read_text(encoding="utf-8"))
    assert manifest["packets"] == [packet.name for packet in packets]
