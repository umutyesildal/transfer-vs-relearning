from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.study.adapters.m0_evaluation import build_lm_eval_command
from transfer_vs_relearning.study.adapters.m0_probing import build_project_probe_command
from transfer_vs_relearning.study.m0_parallel import (
    REQUIRED_FAMILIES,
    assess_m0_parallel_readiness,
    build_m0_parallel_plan,
    finalize_m0_bundle,
    initialize_m0_namespace,
    run_m0_data_preflight,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/evaluation/m0_olmo_eval_v1_qualification_v1.yaml"


def _write_yaml(path: Path, payload: dict) -> Path:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _runtime_plan(tmp_path: Path) -> tuple[dict, Path]:
    plan = build_m0_parallel_plan(CONFIG, repo_root=ROOT)
    model_dir = tmp_path / "model"
    tokenizer_dir = tmp_path / "tokenizer"
    model_dir.mkdir()
    tokenizer_dir.mkdir()
    (model_dir / "config.json").write_text("{}", encoding="utf-8")
    (tokenizer_dir / "tokenizer.json").write_text("{}", encoding="utf-8")
    manifest_path = tmp_path / "model_manifest.json"
    write_json(
        manifest_path,
        {
            "model_id": plan["model"]["repository"],
            "resolved_revision": plan["model"]["revision"],
            "local_path_absolute": str(model_dir),
            "tokenizer_source_path_absolute": str(tokenizer_dir),
        },
    )
    plan["model"]["manifest_path"] = str(manifest_path)
    plan["model"]["manifest_sha256"] = sha256_file(manifest_path)
    plan["runtime"] = {
        **plan["runtime"],
        "python": "/frozen/env/bin/python",
        "precision": "bfloat16",
        "batch_size": "auto:4",
        "max_batch_size": 16,
        "device": "cuda:0",
        "log_samples": True,
    }
    return plan, manifest_path


def test_parallel_plan_covers_every_required_family_and_harness_task_once() -> None:
    plan = build_m0_parallel_plan(CONFIG, repo_root=ROOT)
    assert plan["lane_count"] == 7
    assert plan["max_parallel_lanes"] == 3
    assert plan["run_classification"] == "test_only_non_scientific"
    assert [route["id"] for route in plan["slurm"]["gpu_routes"]] == [
        "v10032gb",
        "a10080gb",
        "rtx3090",
        "rtx6000",
        "rtxa6000",
    ]
    assert plan["slurm"]["gpu_routes"][2] == {
        "id": "rtx3090",
        "partition": "wbimlgpu",
        "gres": "gpu:rtx3090:1",
        "memory": "64G",
    }
    families = {family for lane in plan["lanes"] for family in lane["families"]}
    assert REQUIRED_FAMILIES.issubset(families)
    tasks = [task for lane in plan["lanes"] for task in lane.get("task_ids", [])]
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert sorted(tasks) == sorted(config["required_task_discovery"])
    assert len(tasks) == 8
    assert len(tasks) == len(set(tasks))


def test_parallel_plan_rejects_duplicate_tasks_and_scientific_limits(tmp_path: Path) -> None:
    payload = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    duplicate = copy.deepcopy(payload)
    duplicate["parallel_evaluation"]["lanes"][1]["task_ids"] = ["wikitext"]
    with pytest.raises(ValueError, match="multiple lanes"):
        build_m0_parallel_plan(_write_yaml(tmp_path / "duplicate.yaml", duplicate), repo_root=ROOT)

    scientific = copy.deepcopy(payload)
    scientific["classification"] = "scientific_evaluation"
    with pytest.raises(ValueError, match="cannot use --limit"):
        build_m0_parallel_plan(_write_yaml(tmp_path / "scientific.yaml", scientific), repo_root=ROOT)


def test_materializer_repair_preflight_remains_fail_closed_until_refrozen() -> None:
    payload = assess_m0_parallel_readiness(
        CONFIG,
        repo_root=ROOT,
        project_state_path=ROOT / "documentation/current/PROJECT_STATE.yaml",
    )
    assert payload["status"] == "blocked_pre_scoring"
    assert payload["scientific_work_started"] is False
    assert payload["lane_count"] == 7
    assert payload["blockers"] == [
        "qualification_contract_frozen",
        "qualification_execution_ready",
        "qualification_execution_authorized",
        "runtime_and_artifact_identity",
    ]
    assert "project_ready_to_measure" not in payload["blockers"]


def test_lm_eval_command_is_offline_base_model_and_limit_is_test_only(tmp_path: Path) -> None:
    plan, _ = _runtime_plan(tmp_path)
    lane = copy.deepcopy(plan["lanes"][0])
    lane["limit"] = 3
    command = build_lm_eval_command(
        plan,
        lane,
        repo_root=ROOT,
        output_path=tmp_path / "raw",
    )
    assert command[:4] == ["/frozen/env/bin/python", "-m", "lm_eval", "run"]
    assert "apply_chat_template" not in " ".join(command)
    assert "trust_remote_code=False" in command
    assert "local_files_only=True" in command
    assert "--include_path" not in command
    assert command[command.index("--tasks") + 1] == "wikitext"
    assert command[command.index("--seed") + 1] == "42,42,42,42"
    assert command[command.index("--limit") + 1] == "3"

    plan["run_classification"] = "scientific"
    with pytest.raises(ValueError, match="forbidden"):
        build_lm_eval_command(plan, lane, repo_root=ROOT, output_path=tmp_path / "other")


def test_project_probe_command_accepts_only_registered_entrypoint_and_exact_config(tmp_path: Path) -> None:
    plan, manifest_path = _runtime_plan(tmp_path)
    evaluator_config = tmp_path / "factual.yaml"
    output_dir = tmp_path / "factual-output"
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()
    dataset_manifest = dataset_dir / "manifest.json"
    dataset_manifest.write_text("{}", encoding="utf-8")
    probe_registry = tmp_path / "probes.csv"
    probe_registry.write_text("probe_id\nprobe-1\n", encoding="utf-8")
    _write_yaml(
        evaluator_config,
        {
            "adapter_engine": "pre_m2_frozen",
            "run_classification": plan["run_classification"],
            "model_label": "m0-test",
            "model_manifest": str(manifest_path),
            "dataset_dir": str(dataset_dir),
            "probe_registry": str(probe_registry),
            "output_dir": str(output_dir),
            "input_sha256": {
                "dataset_manifest": sha256_file(dataset_manifest),
                "probe_registry": sha256_file(probe_registry),
            },
            "candidate_batch_size": 16,
            "checkpoint_interval": 8,
            "probe_limit": 8,
            "device": "cuda",
            "bf16": False,
        },
    )
    lane = copy.deepcopy(plan["lanes"][5])
    lane["evaluator_config"] = str(evaluator_config)
    lane["evaluator_config_sha256"] = sha256_file(evaluator_config)
    lane["expected_output_root"] = str(output_dir)
    command = build_project_probe_command(plan, lane, repo_root=ROOT)
    assert command[1].endswith("scripts/m2/evaluate_pre_m2_frozen_suite.py")
    assert command[command.index("--probe-limit") + 1] == "8"
    assert command[command.index("--output-dir") + 1] == str(output_dir)
    assert command[-1] == "--no-bf16"
    lane["evaluator_config_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        build_project_probe_command(plan, lane, repo_root=ROOT)


def test_single_entrypoint_submits_one_parallel_array_and_afterany_finalizer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    entrypoint_path = ROOT / "scripts/study/run_m0_olmo_evaluation.py"
    spec = importlib.util.spec_from_file_location("m0_entrypoint", entrypoint_path)
    assert spec and spec.loader
    entrypoint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entrypoint)

    plan = build_m0_parallel_plan(CONFIG, repo_root=ROOT)
    plan["runtime"]["python"] = "/frozen/env/bin/python"
    plan["slurm"] = {
        "account": "yesildau",
        "control_partition": "std",
        "gpu_route_selection_policy": "earliest_test_only_start_then_declared_order",
        "gpu_routes": [
            {
                "id": "v10032gb",
                "partition": "gpu",
                "gres": "gpu:v10032gb:1",
                "memory": "64G",
            },
            {
                "id": "rtx3090",
                "partition": "wbimlgpu",
                "gres": "gpu:rtx3090:1",
                "memory": "64G",
            },
        ],
        "cpus_per_task": 8,
        "time_limit": "04:00:00",
    }
    output_root = tmp_path / "m0"
    (output_root / "logs").mkdir(parents=True)
    submissions: list[list[str]] = []

    def fake_submit(argv: list[str]) -> str:
        submissions.append(argv)
        return str(1000 + len(submissions))

    def fake_probe(_: dict, route: dict[str, str]) -> dict:
        starts = {"v10032gb": "2026-08-16T15:00:00", "rtx3090": "2026-08-16T12:00:00"}
        return {
            "route": route,
            "eligible": True,
            "returncode": 0,
            "estimated_start": starts[route["id"]],
            "probe_output": "test-only",
        }

    monkeypatch.setattr(entrypoint, "_submit", fake_submit)
    monkeypatch.setattr(entrypoint, "_probe_gpu_route", fake_probe)
    payload = entrypoint._submit_parallel_jobs(
        plan,
        config_path=CONFIG,
        repo_root=ROOT,
        output_root=output_root,
    )
    assert len(submissions) == 3
    assert any("run-preflight" in argument for argument in submissions[0])
    assert "--partition=std" in submissions[0]
    assert not any(argument.startswith("--gres=") for argument in submissions[0])
    assert "--dependency=afterok:1001" in submissions[1]
    assert "--partition=wbimlgpu" in submissions[1]
    assert "--array=0-6%3" in submissions[1]
    assert "--gres=gpu:rtx3090:1" in submissions[1]
    assert any("run-lane" in argument for argument in submissions[1])
    assert "--dependency=afterany:1002" in submissions[2]
    assert "--partition=std" in submissions[2]
    assert any("finalize" in argument for argument in submissions[2])
    assert payload["preflight_job_id"] == "1001"
    assert payload["array_job_id"] == "1002"
    assert payload["finalizer_job_id"] == "1003"
    assert payload["selected_gpu_route"]["id"] == "rtx3090"
    selection = json.loads((output_root / "gpu_route_selection.json").read_text(encoding="utf-8"))
    assert selection["selected_route"]["id"] == "rtx3090"
    assert json.loads((output_root / "submission_manifest.json").read_text(encoding="utf-8")) == payload


def test_submitter_persists_first_sbatch_rejection_without_claiming_a_job(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    entrypoint_path = ROOT / "scripts/study/run_m0_olmo_evaluation.py"
    spec = importlib.util.spec_from_file_location("m0_entrypoint_rejection", entrypoint_path)
    assert spec and spec.loader
    entrypoint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entrypoint)
    plan = build_m0_parallel_plan(CONFIG, repo_root=ROOT)
    output_root = tmp_path / "m0-rejected"
    (output_root / "logs").mkdir(parents=True)

    def reject(_: list[str]) -> str:
        raise RuntimeError("GPU partition is only for use with GPUs")

    def eligible_route(_: dict, route: dict[str, str]) -> dict:
        return {
            "route": route,
            "eligible": True,
            "returncode": 0,
            "estimated_start": "2026-08-16T12:00:00",
            "probe_output": "test-only",
        }

    monkeypatch.setattr(entrypoint, "_submit", reject)
    monkeypatch.setattr(entrypoint, "_probe_gpu_route", eligible_route)
    with pytest.raises(RuntimeError, match="only for use with GPUs"):
        entrypoint._submit_parallel_jobs(
            plan,
            config_path=CONFIG,
            repo_root=ROOT,
            output_root=output_root,
        )
    manifest = json.loads(
        (output_root / "submission_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["status"] == "no_job_submitted_preflight_sbatch_rejected"
    assert manifest["preflight_job_id"] is None
    assert manifest["array_job_id"] is None
    assert manifest["finalizer_job_id"] is None


def test_finalizer_requires_every_lane_and_never_zero_fills(tmp_path: Path) -> None:
    plan = build_m0_parallel_plan(CONFIG, repo_root=ROOT)
    incomplete_root = initialize_m0_namespace(tmp_path / "incomplete", plan)
    incomplete = finalize_m0_bundle(plan, output_root=incomplete_root)
    assert incomplete["status"] == "partial_invalid"
    assert incomplete["complete_lane_count"] == 0
    assert incomplete["normalization_allowed"] is False
    assert not (incomplete_root / "evaluation_manifest.json").exists()

    complete_root = initialize_m0_namespace(tmp_path / "complete", plan)
    for lane in plan["lanes"]:
        raw = complete_root / "lanes" / lane["id"] / "raw.json"
        raw.write_text("{}", encoding="utf-8")
        write_json(
            complete_root / "lanes" / lane["id"] / "lane_result.json",
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
                "artifacts": [
                    {
                        "path": str(raw),
                        "bytes": raw.stat().st_size,
                        "sha256": sha256_file(raw),
                    }
                ],
            },
        )
    complete = finalize_m0_bundle(plan, output_root=complete_root)
    assert complete["status"] == "complete"
    assert complete["complete_lane_count"] == plan["lane_count"]
    assert complete["normalization_allowed"] is True
    manifest = json.loads((complete_root / "evaluation_manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_classification"] == "test_only_non_scientific"


def test_data_preflight_records_exact_task_and_cache_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = build_m0_parallel_plan(CONFIG, repo_root=ROOT)
    plan["runtime"]["python"] = "/frozen/env/bin/python"
    output_root = tmp_path / "qualification"
    (output_root / "cache").mkdir(parents=True)
    cache_file = output_root / "cache" / "dataset.arrow"
    cache_file.write_bytes(b"frozen-data")
    task_ids = [task for lane in plan["lanes"] for task in lane.get("task_ids", [])]
    seen_commands: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> object:
        seen_commands.append(command)
        if "ls" in command:
            stdout = "\n".join(f"| {task} | task |" for task in task_ids)
        else:
            stdout = "validated"
        return type("Result", (), {"stdout": stdout, "stderr": "", "returncode": 0})()

    monkeypatch.setattr("transfer_vs_relearning.study.m0_parallel.subprocess.run", fake_run)
    monkeypatch.setattr(
        "transfer_vs_relearning.study.m0_parallel.build_project_probe_command",
        lambda *_args, **_kwargs: ["verified"],
    )
    payload = run_m0_data_preflight(plan, output_root=output_root)
    assert payload["status"] == "complete"
    assert payload["resolved_task_count"] == len(task_ids)
    materialize_commands = [command for command in seen_commands if "-c" in command]
    assert len(materialize_commands) == 2
    assert all("loaded_entry_count" in command[-1] for command in materialize_commands)
    assert all("sorted(d)" not in command[-1] for command in materialize_commands)
    task_rows = [
        json.loads(line)
        for line in (output_root / "task_resolution.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert {row["task_id"] for row in task_rows} == set(task_ids)
    content_rows = [
        json.loads(line)
        for line in (output_root / "dataset_content_manifest.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert content_rows == [
        {
            "bytes": len(b"frozen-data"),
            "path": str(cache_file),
            "sha256": sha256_file(cache_file),
        }
    ]


def test_data_preflight_rejects_successful_validation_with_an_empty_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = build_m0_parallel_plan(CONFIG, repo_root=ROOT)
    plan["runtime"]["python"] = "/frozen/env/bin/python"
    output_root = tmp_path / "empty-cache"
    (output_root / "cache").mkdir(parents=True)
    task_ids = [task for lane in plan["lanes"] for task in lane.get("task_ids", [])]

    def fake_run(command: list[str], **_: object) -> object:
        stdout = (
            "\n".join(f"| {task} | task |" for task in task_ids)
            if "ls" in command
            else "validated"
        )
        return type("Result", (), {"stdout": stdout, "stderr": "", "returncode": 0})()

    monkeypatch.setattr("transfer_vs_relearning.study.m0_parallel.subprocess.run", fake_run)
    monkeypatch.setattr(
        "transfer_vs_relearning.study.m0_parallel.build_project_probe_command",
        lambda *_args, **_kwargs: ["verified"],
    )
    with pytest.raises(RuntimeError, match="task-data preflight failed"):
        run_m0_data_preflight(plan, output_root=output_root)
    result = json.loads(
        (output_root / "preflight/preflight_result.json").read_text(encoding="utf-8")
    )
    assert result["status"] == "failed_pre_scoring"
    assert result["cache_materialized"] is False
    assert result["network_retrieval_used"] is False
