from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.study import m1_wave_executor as executor
from transfer_vs_relearning.utils.io import sha256_file, sha256_text


def _write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _patch_runtime(tmp_path, monkeypatch) -> dict[str, tuple[str, str]]:
    frozen = {}
    for label in executor.FROZEN_INPUTS:
        path = tmp_path / "frozen" / label
        _write(path, json.dumps({"frozen_input": label}) + "\n")
        frozen[label] = (str(path), sha256_file(path))
    monkeypatch.setattr(executor, "FROZEN_INPUTS", frozen)
    runtime_python = tmp_path / "runtime" / "python"
    _write(runtime_python, "#!/bin/sh\n")
    runtime_python.chmod(0o755)
    runtime_lock = tmp_path / "runtime" / "environment.lock.txt"
    _write(runtime_lock, "runtime-lock")
    content_manifest = tmp_path / "runtime" / "dataset_content_manifest.jsonl"
    _write(content_manifest, "{}\n")
    cache_root = tmp_path / "runtime" / "cache"
    cache_root.mkdir()
    monkeypatch.setattr(executor, "RUNTIME_PYTHON", runtime_python)
    monkeypatch.setattr(executor, "RUNTIME_LOCK", runtime_lock)
    monkeypatch.setattr(executor, "RUNTIME_LOCK_SHA256", sha256_file(runtime_lock))
    monkeypatch.setattr(executor, "DATASET_CONTENT_MANIFEST", content_manifest)
    monkeypatch.setattr(
        executor, "DATASET_CONTENT_MANIFEST_SHA256", sha256_file(content_manifest)
    )
    monkeypatch.setattr(executor, "DATASET_CACHE_ROOT", cache_root)
    return frozen


def _patch_m0_evidence(monkeypatch) -> dict[str, list[dict]]:
    rows_by_model = {
        label: [
            {
                "lane_id": f"{label}_lane_{index}",
                "metric": "value",
                "value": 0.5,
                "raw_artifact_path": f"/vol/tmp2/yesildau/m0/{label}/lanes/lane_{index}/summary.json",
                "raw_artifact_sha256": sha256_text(f"{label}:{index}"),
            }
            for index in range(executor.M0_CANONICAL_EVIDENCE["rows_per_model"])
        ]
        for label in executor.MODEL_LABELS.values()
    }
    monkeypatch.setattr(
        executor,
        "load_m0_canonical_evidence",
        lambda: {
            "final_inventory_sha256": "0" * 64,
            "summary_sha256": "0" * 64,
            "manifest_sha256": "0" * 64,
            "observation_row_count": 42,
            "rows_by_model": rows_by_model,
        },
    )
    return rows_by_model


def _build_configs(tmp_path, frozen):
    configs = []
    for model_id, label in executor.MODEL_LABELS.items():
        model_manifest = tmp_path / "models" / f"{label}.json"
        _write(model_manifest, json.dumps({"model_id": model_id, "local_path_absolute": str(tmp_path)}))
        training_manifest = tmp_path / "training" / label / "training_manifest.json"
        _write(training_manifest, json.dumps({"status": "complete"}))
        checkpoints = []
        for epoch, checkpoint_id in enumerate(executor.EXPECTED_CHECKPOINT_IDS):
            row = {
                "checkpoint_id": checkpoint_id,
                "state": "M0" if checkpoint_id == "parent" else "M1",
                "epoch": epoch,
                "update": epoch * 7,
                "model_manifest": str(model_manifest),
                "model_manifest_sha256": sha256_file(model_manifest),
                "checkpoint_sha256": sha256_file(model_manifest),
            }
            if checkpoint_id != "parent":
                snapshot_manifest = tmp_path / "snapshots" / label / f"{checkpoint_id}.json"
                _write(snapshot_manifest, json.dumps({"checkpoint_sha256": row["checkpoint_sha256"]}))
                row["snapshot_manifest"] = str(snapshot_manifest)
                row["snapshot_manifest_sha256"] = sha256_file(snapshot_manifest)
            checkpoints.append(row)
        checkpoint_manifest = tmp_path / "bindings" / label / "checkpoint_manifest.json"
        _write(checkpoint_manifest, json.dumps({"checkpoints": checkpoints}))
        config = {
            "status": "frozen",
            "execution_authorized": False,
            "experiment": {"model_id": model_id, "model_revision": "revision"},
            "evaluation": {"contract": "eval-v2", "full_epochs": [0, 18, 36]},
            "outputs": {"root": str(tmp_path / "new-output")},
            "inputs": {
                "m0_model_manifest": str(model_manifest),
                "m0_model_manifest_sha256": sha256_file(model_manifest),
                "m1_checkpoint_manifest": str(checkpoint_manifest),
                "m1_checkpoint_manifest_sha256": sha256_file(checkpoint_manifest),
                "m1_training_manifest": str(training_manifest),
                "m1_training_manifest_sha256": sha256_file(training_manifest),
            },
            "execution": {"adapter_registered": True, "adapter": "slurm_m1_matched_wave_v1"},
        }
        path = tmp_path / "configs" / f"{label}.yaml"
        _write(path, yaml.safe_dump(config))
        configs.append(path)
    return configs


def test_build_task_matrix_excludes_parent_and_projects_three_states(tmp_path, monkeypatch):
    frozen = _patch_runtime(tmp_path, monkeypatch)
    _patch_m0_evidence(monkeypatch)
    configs = _build_configs(tmp_path, frozen)
    adapter_module = tmp_path / "src/adapter.py"
    adapter_entrypoint = tmp_path / "scripts/execute.py"
    _write(adapter_module, "adapter")
    _write(adapter_entrypoint, "entrypoint")
    contract_path = tmp_path / "contract.md"
    _write(contract_path, "contract")
    execution_config_path = tmp_path / "execution.yaml"
    execution_config = {
        "status": "frozen",
        "execution_ready": True,
        "contract": "contract.md",
        "adapter": {
            "id": "slurm_m1_matched_wave_v1",
            "module": str(adapter_module.relative_to(tmp_path)),
            "module_sha256": sha256_file(adapter_module),
            "entrypoint": str(adapter_entrypoint.relative_to(tmp_path)),
            "entrypoint_sha256": sha256_file(adapter_entrypoint),
        },
        "pipeline_configs": {
            label: {
                "path": str(path.relative_to(tmp_path)),
                "sha256": sha256_file(path),
            }
            for label, path in zip(("olmo", "qwen", "smollm"), configs)
        },
    }
    _write(execution_config_path, yaml.safe_dump(execution_config))
    matrix = executor.build_task_matrix(
        configs,
        repo_root=tmp_path,
        contract_path=contract_path,
        contract_sha256=sha256_file(contract_path),
        execution_config_path=execution_config_path,
        execution_config_sha256=sha256_file(execution_config_path),
    )
    assert matrix["status"] == "ready"
    assert len(matrix["tasks"]) == executor.GPU_TASK_COUNT == 108
    assert {task["model"] for task in matrix["tasks"]} == {"olmo", "qwen", "smollm"}
    assert all(task["checkpoint_id"] != "parent" for task in matrix["tasks"])
    assert sum(task["full"] for task in matrix["tasks"]) == 6
    assert matrix["total_scientific_states"] == 111
    assert [entry["model"] for entry in matrix["parent_projections"]] == ["olmo", "qwen", "smollm"]
    for entry in matrix["parent_projections"]:
        assert entry["state"] == "M0"
        assert entry["projection"]["mode"] == "projected_from_canonical_m0_evidence_without_rescoring"


def test_initialize_wave_requires_fresh_root(tmp_path):
    matrix = {"output_root": str(tmp_path / "output"), "tasks": [{}] * 111}
    executor.initialize_wave(matrix)
    try:
        executor.initialize_wave(matrix)
    except FileExistsError:
        pass
    else:
        raise AssertionError("existing evaluation root must fail closed")


def test_initialize_wave_recovers_only_never_submitted_roots(tmp_path):
    output_root = tmp_path / "output"
    control = output_root / "control"
    control.mkdir(parents=True)
    (output_root / "results").mkdir()
    matrix = {"output_root": str(output_root), "tasks": [{}] * 111}
    manifest = control / "submission_manifest.json"

    manifest.write_text(json.dumps({"status": "not_submitted_test_only_failed"}), encoding="utf-8")
    executor.initialize_wave(matrix)
    preflight = json.loads((output_root / "control/preflight.json").read_text(encoding="utf-8"))
    assert preflight["recovered_stale_root"] is True

    (output_root / "results/olmo/epoch-001").mkdir(parents=True)
    (output_root / "results/olmo/epoch-001/task_result.json").write_text("{}", encoding="utf-8")
    try:
        executor.initialize_wave(matrix)
    except FileExistsError:
        pass
    else:
        raise AssertionError("root containing task results must fail closed")

    for stray in (output_root / "results").rglob("*"):
        if stray.is_file():
            stray.unlink()
    manifest.write_text(json.dumps({"status": "submitted"}), encoding="utf-8")
    try:
        executor.initialize_wave(matrix)
    except FileExistsError:
        pass
    else:
        raise AssertionError("submitted root must fail closed")

    manifest.write_text("{broken", encoding="utf-8")
    try:
        executor.initialize_wave(matrix)
    except FileExistsError:
        pass
    else:
        raise AssertionError("unreadable submission manifest must fail closed")


def _gpu_result(matrix, output_root: Path, task_index: int, *, status: str) -> None:
    task = matrix["tasks"][task_index]
    state_root = output_root / "results" / task["model"] / task["checkpoint_id"]
    state_root.mkdir(parents=True, exist_ok=True)
    (state_root / "task_result.json").write_text(
        json.dumps({"status": status}), encoding="utf-8"
    )


def test_finalize_closes_only_at_111_of_111(tmp_path, monkeypatch):
    _patch_m0_evidence(monkeypatch)
    output_root = tmp_path / "output"
    output_root.mkdir()
    matrix = {
        "matrix_id": "testmatrix",
        "output_root": str(output_root),
        "tasks": [],
        "parent_projections": [
            {
                "model": label,
                "model_id": f"id-{label}",
                "model_revision": "revision",
                "checkpoint_id": "parent",
                "state": "M0",
                "epoch": 0,
                "update": 0,
                "m0_model_manifest": str(tmp_path / "missing.json"),
                "m0_model_manifest_sha256": "1" * 64,
                "projection": executor._parent_projection_binding(),
            }
            for label in ("olmo", "qwen", "smollm")
        ],
    }
    for index in range(108):
        label = ["olmo", "qwen", "smollm"][index // 36]
        matrix["tasks"].append(
            {
                "task_index": index,
                "model": label,
                "checkpoint_id": f"epoch-{index % 36 + 1:03d}",
            }
        )
    for index in range(107):
        _gpu_result(matrix, output_root, index, status="complete")

    incomplete = executor.finalize_wave(matrix)
    assert incomplete["status"] == "incomplete"
    assert incomplete["gpu_complete_count"] == 107
    assert incomplete["parent_complete_count"] == 3
    assert incomplete["complete_count"] == 110

    _gpu_result(matrix, output_root, 107, status="complete")
    complete = executor.finalize_wave(matrix)
    assert complete["status"] == "complete"
    assert complete["complete_count"] == 111
    for label in ("olmo", "qwen", "smollm"):
        parent_path = output_root / "results" / label / "parent" / "task_result.json"
        payload = json.loads(parent_path.read_text(encoding="utf-8"))
        assert payload["status"] == "complete"
        assert payload["mode"] == "projected_from_canonical_m0_evidence_without_rescoring"
        assert payload["projection"]["projected_row_count"] == 14


def test_run_task_gates_complete_on_validators_and_derives_cheap_for_full(
    tmp_path, monkeypatch
):
    frozen = _patch_runtime(tmp_path, monkeypatch)
    monkeypatch.setattr(
        executor,
        "assert_free_gpu_memory",
        lambda: {"gpu_index": "0", "free_bytes": 1, "gate_bytes": 1},
    )
    output_root = tmp_path / "output"
    model_manifest = tmp_path / "models" / "olmo.json"
    _write(model_manifest, json.dumps({"local_path_absolute": str(tmp_path / "weights")}))
    training_manifest = tmp_path / "training.json"
    _write(training_manifest, "{}")
    task = {
        "task_index": 0,
        "model": "olmo",
        "model_id": "allenai/OLMo-2-0425-1B",
        "model_revision": "revision",
        "checkpoint_id": "epoch-036",
        "epoch": 36,
        "update": 252,
        "full": True,
        "model_manifest": str(model_manifest),
        "model_manifest_sha256": sha256_file(model_manifest),
        "snapshot_manifest": None,
        "snapshot_manifest_sha256": None,
        "checkpoint_sha256": "2" * 64,
        "training_manifest": str(training_manifest),
        "training_manifest_sha256": sha256_file(training_manifest),
    }
    matrix = {"repo_root": str(tmp_path), "output_root": str(output_root), "tasks": [task]}

    calls: dict[str, object] = {"commands": [], "derive": None, "factual": []}
    monkeypatch.setattr(
        executor,
        "_run",
        lambda command, *, repo_root: calls["commands"].append(command),
    )

    def _fake_validate(root, expected):
        calls["factual"].append((Path(root), expected))
        return {"status": "complete"}

    monkeypatch.setattr(executor, "validate_harness_output", lambda root, ids: {"status": "complete"})
    monkeypatch.setattr(executor, "validate_factual_output", _fake_validate)

    def _fake_derive(*, full_root, cheap_root, cheap_registry, cheap_registry_sha256):
        calls["derive"] = {
            "full_root": Path(full_root),
            "cheap_root": Path(cheap_root),
            "registry": Path(cheap_registry),
        }
        return {"status": "complete"}

    monkeypatch.setattr(executor, "derive_cheap_factual_from_full", _fake_derive)
    monkeypatch.setattr(
        executor, "validate_exact_prefix_output", lambda root: {"status": "complete"}
    )
    monkeypatch.setattr(
        executor,
        "validate_turkish_perplexity_output",
        lambda root, **kwargs: {"status": "complete"},
    )
    monkeypatch.setattr(
        executor,
        "validate_generation_output",
        lambda root, **kwargs: {"status": "complete"},
    )

    result = executor.run_task(matrix, 0)
    assert result["status"] == "complete"
    assert calls["derive"] is not None
    assert calls["derive"]["full_root"] == output_root / "results/olmo/epoch-036/factual_full/raw"
    assert calls["derive"]["cheap_root"] == output_root / "results/olmo/epoch-036/factual_cheap"
    assert calls["derive"]["registry"] == Path(frozen["cheap_factual"][0])
    assert [expected for _, expected in calls["factual"]] == [executor.FULL_PROBE_COUNT]
    factual_commands = [
        command
        for command in calls["commands"]
        if any("evaluate_pre_m2_frozen_suite.py" in part for part in command)
    ]
    assert len(factual_commands) == 1
    assert any(frozen["full_factual"][0] == part for part in factual_commands[0])
    saved = json.loads(
        (output_root / "results/olmo/epoch-036/task_result.json").read_text(encoding="utf-8")
    )
    assert saved["status"] == "complete"

    def _boom(root, **kwargs):
        raise ValueError("denominator drift")

    monkeypatch.setattr(executor, "validate_generation_output", _boom)
    second_root = tmp_path / "output2"
    matrix2 = {**matrix, "output_root": str(second_root)}
    with pytest.raises(ValueError, match="denominator drift"):
        executor.run_task(matrix2, 0)
    failed = json.loads(
        (second_root / "results/olmo/epoch-036/task_result.json").read_text(encoding="utf-8")
    )
    assert failed["status"] == "failed"
    assert "denominator drift" in failed["error"]


def test_run_task_verifies_snapshot_before_scoring(tmp_path, monkeypatch):
    _patch_runtime(tmp_path, monkeypatch)
    monkeypatch.setattr(
        executor,
        "assert_free_gpu_memory",
        lambda: {"gpu_index": "0", "free_bytes": 1, "gate_bytes": 1},
    )
    output_root = tmp_path / "output"
    model_manifest = tmp_path / "models" / "olmo.json"
    _write(model_manifest, json.dumps({"local_path_absolute": str(tmp_path / "weights")}))
    training_manifest = tmp_path / "training.json"
    _write(training_manifest, "{}")
    task = {
        "task_index": 0,
        "model": "olmo",
        "model_id": "allenai/OLMo-2-0425-1B",
        "model_revision": "revision",
        "checkpoint_id": "epoch-001",
        "epoch": 1,
        "update": 7,
        "full": False,
        "model_manifest": str(model_manifest),
        "model_manifest_sha256": sha256_file(model_manifest),
        "snapshot_manifest": str(tmp_path / "snapshots/snapshot_manifest.json"),
        "snapshot_manifest_sha256": "3" * 64,
        "checkpoint_sha256": "4" * 64,
        "training_manifest": str(training_manifest),
        "training_manifest_sha256": sha256_file(training_manifest),
    }
    matrix = {"repo_root": str(tmp_path), "output_root": str(output_root), "tasks": [task]}
    observed: dict[str, object] = {}
    seen_order: list[str] = []

    def _fail_verify(**kwargs):
        observed.update(kwargs)
        seen_order.append("verify")
        raise ValueError("snapshot byte mismatch")

    monkeypatch.setattr(executor, "verify_snapshot", lambda **kwargs: _fail_verify(**kwargs))

    def _run_recorder(command, *, repo_root):
        seen_order.append("run")

    monkeypatch.setattr(executor, "_run", _run_recorder)
    with pytest.raises(ValueError, match="snapshot byte mismatch"):
        executor.run_task(matrix, 0)
    assert observed["checkpoint_sha256"] == "4" * 64
    assert seen_order == ["verify"]
    failed = json.loads(
        (output_root / "results/olmo/epoch-001/task_result.json").read_text(encoding="utf-8")
    )
    assert failed["status"] == "failed"


def test_gpu_free_memory_gate_fails_closed(tmp_path, monkeypatch):
    import types

    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "2,3")

    def _probe(stdout: str, returncode: int = 0):
        completed = types.SimpleNamespace()
        completed.returncode = returncode
        completed.stdout = stdout
        completed.stderr = ""
        return completed

    monkeypatch.setattr(executor.subprocess, "run", lambda command, **k: _probe("1024\n"))
    monkeypatch.setattr(executor.time, "sleep", lambda seconds: None)
    with pytest.raises(RuntimeError, match="exhausted 13 probes"):
        executor.gate_with_retries()

    outputs = iter(["1024\n", "409600\n"])
    monkeypatch.setattr(
        executor.subprocess,
        "run",
        lambda command, **k: _probe(next(outputs)),
    )
    payload = executor.gate_with_retries()
    assert payload["gpu_index"] == "2"
    assert payload["free_bytes"] == 409600 * 1024 * 1024
    assert payload["probe_attempts"] == 2

    monkeypatch.setattr(executor.subprocess, "run", lambda command, **k: _probe("", returncode=1))
    with pytest.raises(RuntimeError, match="probe failed|exhausted"):
        executor.gate_with_retries()

    monkeypatch.delenv("CUDA_VISIBLE_DEVICES")
    with pytest.raises(RuntimeError, match="CUDA_VISIBLE_DEVICES is missing"):
        executor.assert_free_gpu_memory()


def test_submit_wave_single_route_topology(tmp_path, monkeypatch):
    import types

    output_root = tmp_path / "output"
    (output_root / "control").mkdir(parents=True)
    matrix = {
        "status": "ready",
        "matrix_id": "single",
        "repo_root": str(tmp_path),
        "output_root": str(output_root),
        "tasks": [{"task_index": index} for index in range(108)],
        "parent_projections": [{}, {}, {}],
        "total_scientific_states": 111,
    }
    matrix_path = output_root / "control/task_matrix.json"
    matrix_path.write_text(json.dumps(matrix), encoding="utf-8")
    monkeypatch.setattr(executor, "slurm_environment", lambda root: {})

    calls: list[list[str]] = []
    counter = {"n": 0}

    def _fake_run(command, **kwargs):
        calls.append([str(part) for part in command])
        counter["n"] += 1
        completed = types.SimpleNamespace()
        completed.returncode = 0
        completed.stdout = f"9{counter['n']:02d}\n"
        completed.stderr = ""
        return completed

    monkeypatch.setattr(executor.subprocess, "run", _fake_run)

    result = executor.submit_wave(matrix_path, entrypoint=Path("/repo/scripts/study/execute_m1_eval_v2.py"))
    assert result["status"] == "submitted"
    assert result["route"]["gres"] == "gpu:a10080gb:1"
    assert result["route"]["array_spec"] == "0-107%6"

    parsable = [call for call in calls if "--parsable" in call]
    assert len(parsable) == 3  # preflight + one array + finalizer
    array_call = next(call for call in parsable if any("gpu:a10080gb:1" in part for part in call))
    finalizer_call = next(call for call in parsable if any("finalize" in part for part in call))
    preflight_id = result["preflight_job_id"]
    assert any("--array=0-107%6" in part for part in array_call)
    assert any(f"--dependency=afterok:{preflight_id}" in part for part in array_call)
    assert not any("--task-offset" in part for part in array_call)
    assert any(
        f"--dependency=afterany:{result['evaluation_array_job_id']}" in part
        for part in finalizer_call
    )

    saved = json.loads((output_root / "control/submission_manifest.json").read_text(encoding="utf-8"))
    assert saved["status"] == "submitted"
    assert saved["evaluation_array_job_id"] == result["evaluation_array_job_id"]


def test_run_task_archives_failed_attempt_and_blocks_complete_states(
    tmp_path, monkeypatch
):
    _patch_runtime(tmp_path, monkeypatch)
    monkeypatch.setattr(
        executor,
        "assert_free_gpu_memory",
        lambda: {"gpu_index": "0", "free_bytes": 1, "gate_bytes": 1},
    )
    model_manifest = tmp_path / "models" / "olmo.json"
    _write(model_manifest, json.dumps({"local_path_absolute": str(tmp_path / "weights")}))
    training_manifest = tmp_path / "training.json"
    _write(training_manifest, "{}")
    task = {
        "task_index": 0,
        "model": "olmo",
        "model_id": "allenai/OLMo-2-0425-1B",
        "model_revision": "revision",
        "checkpoint_id": "epoch-002",
        "epoch": 2,
        "update": 14,
        "full": False,
        "model_manifest": str(model_manifest),
        "model_manifest_sha256": sha256_file(model_manifest),
        "snapshot_manifest": None,
        "snapshot_manifest_sha256": None,
        "checkpoint_sha256": "5" * 64,
        "training_manifest": str(training_manifest),
        "training_manifest_sha256": sha256_file(training_manifest),
    }
    matrix = {"repo_root": str(tmp_path), "output_root": str(tmp_path / "output"), "tasks": [task]}
    monkeypatch.setattr(executor, "_run", lambda command, *, repo_root: None)
    for name in (
        "validate_harness_output",
        "validate_factual_output",
        "validate_exact_prefix_output",
        "validate_turkish_perplexity_output",
        "validate_generation_output",
    ):
        monkeypatch.setattr(executor, name, lambda root, *a, **k: {"status": "complete"})
    monkeypatch.setattr(
        executor,
        "derive_cheap_factual_from_full",
        lambda **kwargs: {"status": "complete"},
    )

    failed_root = tmp_path / "output/results/olmo/epoch-002"
    failed_root.mkdir(parents=True)
    (failed_root / "task_result.json").write_text(
        json.dumps({"status": "failed", "error": "old"}), encoding="utf-8"
    )
    result = executor.run_task(matrix, 0)
    assert result["status"] == "complete"
    assert result["archived_failed_attempts"] == ["epoch-002__failed_0"]
    assert json.loads(
        (tmp_path / "output/results/olmo/epoch-002__failed_0/task_result.json").read_text(
            encoding="utf-8"
        )
    )["status"] == "failed"

    try:
        executor.run_task(matrix, 0)
    except FileExistsError:
        pass
    else:
        raise AssertionError("complete states must never be re-executed")


def test_frozen_master_config_binds_adapter_and_pipeline_hashes():
    repo_root = Path(__file__).resolve().parents[2]
    master = yaml.safe_load(
        (repo_root / "configs/evaluation/m1_eval_v2_matched_three_model_v3.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert master["execution_authorized"] is False
    family = master["family"]
    assert family["task_count"] == 111
    assert family["states_per_model"] == 37
    assert family["gpu_task_count"] == 108
    assert family["parent_projection_count"] == 3
    assert family["output_root"].endswith("m1_eval_v2_matched_three_model_v3")
    slurm = master["slurm"]
    assert (slurm["evaluation_gres"], slurm["array_task_count"], slurm["array_throttle"]) == (
        "gpu:a10080gb:1",
        108,
        6,
    )
    assert slurm["job_count"] == 3
    runtime = master["runtime"]
    assert runtime["min_free_gpu_memory_bytes"] == executor.MIN_FREE_GPU_MEMORY_BYTES
    assert runtime["gate_probe_attempts"] == executor.GATE_PROBE_ATTEMPTS
    assert runtime["gate_retry_wait_seconds"] == executor.GATE_RETRY_WAIT_SECONDS
    for row in master["pipeline_configs"].values():
        assert sha256_file(repo_root / row["path"]) == row["sha256"]
    adapter = master["adapter"]
    assert sha256_file(repo_root / adapter["module"]) == adapter["module_sha256"]
    assert sha256_file(repo_root / adapter["entrypoint"]) == adapter["entrypoint_sha256"]
