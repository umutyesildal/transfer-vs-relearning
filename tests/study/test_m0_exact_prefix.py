from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from transfer_vs_relearning.study.m0_exact_prefix import (
    MODEL_ORDER,
    audit_exact_prefix_inputs,
    finalize_exact_prefix_family,
    initialize_exact_prefix_namespace,
    load_exact_prefix_plan,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/evaluation/m0_exact_prefix_three_model_v1.yaml"
RECOVERY_CONFIG = ROOT / "configs/evaluation/m0_exact_prefix_three_model_a100_recovery_v1.yaml"


def test_frozen_plan_preserves_historical_exact_prefix_semantics() -> None:
    plan = load_exact_prefix_plan(CONFIG, repo_root=ROOT)
    assert plan["status"] == "frozen"
    assert plan["execution_authorized"] is True
    assert plan["execution_authorization"]["status"] == "authorized_single_wave"
    assert plan["semantic_classification"] == (
        "historical_exact_prefix_candidate_ranking_not_free_generation"
    )
    assert tuple(model["model_id"] for model in plan["models"]) == MODEL_ORDER
    assert plan["evaluation"]["prompt"] == {
        "format": "direct",
        "template": "{question}",
        "answer_separator": " ",
    }


def test_recovery_plan_preserves_semantics_and_uses_fresh_a100_root() -> None:
    plan = load_exact_prefix_plan(RECOVERY_CONFIG, repo_root=ROOT)
    assert plan["classification"] == "operational_recovery"
    assert plan["execution_authorized"] is False
    assert plan["authorization_scope"] == "m0_exact_prefix_recovery"
    assert plan["slurm"]["nodelist"] == "gruenau9"
    assert plan["slurm"]["gres"] == "gpu:a10080gb:1"
    assert plan["family_root"].endswith("_a100_recovery_v1")
    assert plan["evaluation"]["scoring"]["primary"] == "mean_logprob"


def test_exact_prefix_registry_has_same_facts_but_zero_prompt_overlap_with_robust() -> None:
    plan = load_exact_prefix_plan(CONFIG, repo_root=ROOT)
    audit = audit_exact_prefix_inputs(plan)
    assert audit["status"] == "pass"
    assert audit["probe_count"] == 500
    assert audit["fact_count"] == 500
    assert audit["subject_count"] == 100
    assert audit["fact_answer_identity_with_robust_registry"] is True
    assert audit["prompt_overlap_with_robust_registry"] == 0
    assert set(audit["relation_counts"].values()) == {100}


def test_namespace_is_fresh_and_never_reused(tmp_path: Path) -> None:
    plan = load_exact_prefix_plan(CONFIG, repo_root=ROOT)
    plan["family_root"] = str(tmp_path / "exact")
    root = initialize_exact_prefix_namespace(plan)
    manifest = json.loads((root / "family_manifest.json").read_text(encoding="utf-8"))
    assert manifest["plan_id"] == plan["plan_id"]
    with pytest.raises(FileExistsError):
        initialize_exact_prefix_namespace(plan)


def test_finalizer_requires_all_three_hash_valid_lanes(tmp_path: Path) -> None:
    plan = load_exact_prefix_plan(CONFIG, repo_root=ROOT)
    plan["family_root"] = str(tmp_path / "exact")
    initialize_exact_prefix_namespace(plan)
    for index, model in enumerate(plan["models"]):
        model_root = Path(plan["family_root"]) / model["model_id"]
        model_root.mkdir()
        artifact = model_root / "metric.json"
        write_json(artifact, {"accuracy": index / 10})
        write_json(
            model_root / "lane_result.json",
            {
                "status": "complete",
                "model_id": model["model_id"],
                "plan_id": plan["plan_id"],
                "primary_mean_logprob_top1_accuracy": index / 10,
                "artifacts": [
                    {
                        "path": str(artifact),
                        "bytes": artifact.stat().st_size,
                        "sha256": sha256_file(artifact),
                    }
                ],
            },
        )
    result = finalize_exact_prefix_family(plan)
    assert result["status"] == "complete"
    assert [row["top1_accuracy"] for row in result["models"]] == [0.0, 0.1, 0.2]
    assert (Path(plan["family_root"]) / "family_inventory.json").is_file()


def test_submitter_launches_one_parallel_array_and_afterany_finalizer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    entrypoint_path = ROOT / "scripts/study/run_three_model_m0_exact_prefix.py"
    spec = importlib.util.spec_from_file_location("m0_exact_prefix_entrypoint", entrypoint_path)
    assert spec and spec.loader
    entrypoint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entrypoint)
    plan = load_exact_prefix_plan(CONFIG, repo_root=ROOT)
    plan["family_root"] = str(tmp_path / "wave")
    submissions: list[list[str]] = []
    monkeypatch.setattr(
        entrypoint,
        "_route_probe",
        lambda _plan: {
            "eligible": True,
            "returncode": 0,
            "estimated_start": "2026-08-21T22:00:00",
            "output": "ok",
        },
    )

    def fake_submit(argv: list[str]) -> str:
        submissions.append(argv)
        return str(9200 + len(submissions))

    monkeypatch.setattr(entrypoint, "_submit", fake_submit)
    payload = entrypoint.submit_wave(plan, config_path=CONFIG, repo_root=ROOT)
    assert payload["array_job_id"] == "9201"
    assert payload["finalizer_job_id"] == "9202"
    assert payload["array_spec"] == "0-2%3"
    assert any("--array=0-2%3" in value for value in submissions[0])
    assert any("--dependency=afterany:9201" in value for value in submissions[1])


def test_route_block_writes_a_terminal_no_job_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    entrypoint_path = ROOT / "scripts/study/run_three_model_m0_exact_prefix.py"
    spec = importlib.util.spec_from_file_location("m0_exact_prefix_entrypoint_blocked", entrypoint_path)
    assert spec and spec.loader
    entrypoint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entrypoint)
    plan = load_exact_prefix_plan(CONFIG, repo_root=ROOT)
    plan["family_root"] = str(tmp_path / "wave")
    monkeypatch.setattr(entrypoint, "_route_probe", lambda _plan: {"eligible": False, "output": "blocked"})
    with pytest.raises(RuntimeError, match="did not pass"):
        entrypoint.submit_wave(plan, config_path=CONFIG, repo_root=ROOT)
    manifest = json.loads((Path(plan["family_root"]) / "submission_manifest.json").read_text())
    assert manifest["status"] == "no_job_submitted_route_blocked"
    assert manifest["array_job_id"] is None


def test_submitter_can_pin_the_gpu_array_to_one_node(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    entrypoint_path = ROOT / "scripts/study/run_three_model_m0_exact_prefix.py"
    spec = importlib.util.spec_from_file_location("m0_exact_prefix_entrypoint_node", entrypoint_path)
    assert spec and spec.loader
    entrypoint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entrypoint)
    plan = load_exact_prefix_plan(CONFIG, repo_root=ROOT)
    plan["family_root"] = str(tmp_path / "wave")
    plan["slurm"]["nodelist"] = "gruenau9"
    monkeypatch.setattr(
        entrypoint,
        "_route_probe",
        lambda _plan: {"eligible": True, "returncode": 0, "estimated_start": "now", "output": "ok"},
    )
    submissions: list[list[str]] = []
    monkeypatch.setattr(
        entrypoint,
        "_submit",
        lambda argv: submissions.append(argv) or str(9300 + len(submissions)),
    )
    entrypoint.submit_wave(plan, config_path=CONFIG, repo_root=ROOT)
    assert "--nodelist=gruenau9" in submissions[0]
