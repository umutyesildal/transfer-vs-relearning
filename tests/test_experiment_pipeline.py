from __future__ import annotations

import copy
import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from transfer_vs_relearning.pipeline.artifacts import (
    CHECKPOINT_FIELDS,
    METRIC_FIELDS,
    derive_retention_observation,
    initialize_artifact_scaffold,
)
from transfer_vs_relearning.pipeline.planner import (
    build_pipeline_plan,
    load_pipeline_config,
    validate_sibling_compatibility,
)
from transfer_vs_relearning.pipeline.training_trace import (
    TrainingTraceRecorder,
    create_transformers_trace_callback,
    make_epoch_trace_payload,
    summarize_tokenized_rows,
)


ROOT = Path(__file__).resolve().parents[1]
PIPELINE_CONFIG = ROOT / "configs/pipelines/eval_v1_olmo_epoch_trajectory_template.yaml"


def _write_yaml(path: Path, payload: dict) -> Path:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_prospective_olmo_plan_has_every_epoch_and_exact_batch_trace() -> None:
    plan = build_pipeline_plan(PIPELINE_CONFIG, repo_root=ROOT)
    assert plan["status"] == "planned_not_authorized"
    assert plan["execution_authorized"] is False
    assert plan["derived_training"] == {
        "epochs": 36,
        "updates_per_epoch": 7,
        "total_updates": 252,
        "effective_row_batch": 500,
        "expected_train_rows": 3500,
        "max_sequence_length": 128,
        "microbatch": 5,
        "gradient_accumulation": 100,
        "world_size": 1,
    }
    assert len(plan["checkpoints"]) == 37
    assert plan["checkpoints"][0]["checkpoint_id"] == "parent"
    assert plan["checkpoints"][1]["update"] == 7
    assert plan["checkpoints"][-1]["update"] == 252
    assert [row["epoch"] for row in plan["checkpoints"] if row["full"]] == [0, 18, 36]
    kinds = [task["kind"] for task in plan["tasks"]]
    assert kinds[:2] == ["preflight", "training"]
    assert kinds.count("dense_evaluation") == 37
    assert kinds.count("full_evaluation") == 3
    assert kinds[-2:] == ["normalization", "presentation"]


def test_historical_olmo_backfill_never_fabricates_missing_epochs(tmp_path: Path) -> None:
    payload = load_pipeline_config(PIPELINE_CONFIG)
    payload["training_plan"]["config"] = str(
        ROOT / "configs/training/m1_provenance_screen_v4_olmo_rtx3090_bf16_seed42.yaml"
    )
    payload["training_plan"]["trajectory_mode"] = "historical_backfill"
    payload["training_plan"]["available_updates"] = [0, 42, 84, 126, 168, 210, 252]
    payload["evaluation"]["full_updates"] = [0, 126, 252]
    plan = build_pipeline_plan(_write_yaml(tmp_path / "historical.yaml", payload), repo_root=ROOT)
    assert [row["epoch"] for row in plan["checkpoints"]] == [0, 6, 12, 18, 24, 30, 36]
    assert all(row["source"] == "historical_checkpoint" for row in plan["checkpoints"])


def test_pipeline_fails_when_epoch_update_mapping_is_not_exact(tmp_path: Path) -> None:
    payload = load_pipeline_config(PIPELINE_CONFIG)
    payload["training_plan"]["expected_train_rows"] = 3501
    with pytest.raises(ValueError, match="divisible"):
        build_pipeline_plan(_write_yaml(tmp_path / "invalid.yaml", payload), repo_root=ROOT)


def test_pipeline_and_training_tracking_cannot_drift(tmp_path: Path) -> None:
    payload = load_pipeline_config(PIPELINE_CONFIG)
    payload["training_plan"]["tracking"]["estimated_snapshot_bytes"] += 1
    with pytest.raises(ValueError, match="tracking mismatch: estimated_snapshot_bytes"):
        build_pipeline_plan(_write_yaml(tmp_path / "drift.yaml", payload), repo_root=ROOT)


def test_frozen_pipeline_rejects_every_remaining_placeholder(tmp_path: Path) -> None:
    payload = load_pipeline_config(PIPELINE_CONFIG)
    payload["status"] = "frozen"
    with pytest.raises(ValueError, match="Frozen pipelines cannot contain placeholders"):
        build_pipeline_plan(_write_yaml(tmp_path / "frozen.yaml", payload), repo_root=ROOT)


def test_m2_siblings_must_share_parent_budget_and_eval_bundle() -> None:
    left = load_pipeline_config(PIPELINE_CONFIG)
    right = copy.deepcopy(left)
    left["experiment"]["state"] = "M2-A"
    right["experiment"]["state"] = "M2-B"
    validate_sibling_compatibility(left, right)
    right["training_plan"]["expected_total_updates"] = 251
    right["evaluation"]["full_epochs"] = [0, 12, 36]
    with pytest.raises(ValueError, match="expected_total_updates.*full_epochs"):
        validate_sibling_compatibility(left, right)


def test_retention_uses_bpb_delta_and_ppl_ratio_not_a_bpb_ratio() -> None:
    row = derive_retention_observation(
        checkpoint_bpb=1.20,
        parent_bpb=1.00,
        checkpoint_perplexity=12.0,
        parent_perplexity=10.0,
    )
    assert row["bpb_absolute_delta"] == pytest.approx(0.20)
    assert row["perplexity_ratio_to_parent"] == pytest.approx(1.20)
    assert row["retention_score"] == pytest.approx(100 / 1.20)
    assert row["retention_score_role"] == "visualization_only"
    assert row["retention_score_scientific_gate"] is False
    assert "bpb_ratio_to_parent" not in row


def test_token_trace_records_padding_truncation_and_supervision() -> None:
    stats = summarize_tokenized_rows(
        [
            {
                "attention_mask": [1, 1, 1, 0],
                "labels": [-100, 2, 3, -100],
                "__trace_was_truncated": False,
            },
            {
                "attention_mask": [1, 1, 1, 1],
                "labels": [-100, -100, 4, -100],
                "__trace_was_truncated": True,
            },
        ],
        max_sequence_length=4,
    )
    assert stats.rows == 2
    assert stats.total_nonpad_tokens == 7
    assert stats.total_supervised_tokens == 3
    assert stats.padding_fraction == pytest.approx(1 / 8)
    assert stats.truncation_count == 1
    assert stats.truncation_rate == 0.5

    payload = make_epoch_trace_payload(
        epoch=2,
        global_step=14,
        epochs=36,
        train_rows=3500,
        fact_exposures_per_epoch=3500,
        tokenization=stats,
        latest_logs={"loss": 0.4, "learning_rate": 5e-5, "grad_norm": 1.2},
        snapshot_path=Path("epoch-002"),
        checkpoint_sha256="a" * 64,
    )
    assert payload["cumulative_examples"] == 7000
    assert payload["cumulative_fact_exposures"] == 7000
    assert payload["cumulative_supervised_tokens"] == 6
    assert payload["cumulative_total_tokens"] == 14


def test_trace_events_are_immutable_and_resume_identity_is_fail_closed(tmp_path: Path) -> None:
    manifest = {"identity_sha256": "identity-a", "status": "started"}
    recorder = TrainingTraceRecorder(tmp_path / "trace", manifest)
    event = recorder.record("train_begin", {"update": 0})
    recorder.complete()
    assert json.loads(event.read_text(encoding="utf-8"))["event"] == "train_begin"
    index = json.loads((tmp_path / "trace/trace_index.json").read_text(encoding="utf-8"))
    assert index["status"] == "complete"
    with pytest.raises(ValueError, match="identity changed"):
        TrainingTraceRecorder(
            tmp_path / "trace", {"identity_sha256": "identity-b", "status": "started"}
        )


def test_epoch_callback_writes_hashed_model_only_snapshot_and_trace(tmp_path: Path) -> None:
    stats = summarize_tokenized_rows(
        [{"attention_mask": [1, 1], "labels": [-100, 7]}],
        max_sequence_length=2,
    )
    recorder = TrainingTraceRecorder(
        tmp_path / "trace", {"identity_sha256": "identity", "status": "started"}
    )

    class CallbackBase:
        pass

    class Model:
        def save_pretrained(self, path: str, *, safe_serialization: bool) -> None:
            assert safe_serialization is True
            (Path(path) / "model.safetensors").write_bytes(b"weights")

    class Tokenizer:
        def save_pretrained(self, path: str) -> None:
            (Path(path) / "tokenizer.json").write_text("{}", encoding="utf-8")

    class State:
        is_world_process_zero = True
        epoch = 1.0
        global_step = 7

    callback = create_transformers_trace_callback(
        CallbackBase,
        recorder=recorder,
        tokenizer=Tokenizer(),
        snapshot_root=tmp_path / "snapshots",
        epochs=2,
        updates_per_epoch=7,
        train_rows=3500,
        fact_exposures_per_epoch=3500,
        tokenization=stats,
        estimated_snapshot_bytes=1,
        minimum_free_bytes=0,
    )
    callback.on_log(None, State(), None, {"loss": 0.5, "learning_rate": 5e-5})
    callback.on_epoch_end(None, State(), None, model=Model())
    snapshot_manifest = json.loads(
        (tmp_path / "snapshots/epoch-001/snapshot_manifest.json").read_text(encoding="utf-8")
    )
    assert snapshot_manifest["file_count"] == 2
    assert len(snapshot_manifest["checkpoint_sha256"]) == 64
    index = json.loads((tmp_path / "trace/trace_index.json").read_text(encoding="utf-8"))
    assert [item["event"] for item in index["events"]] == ["optimizer_log", "epoch_end"]


def test_artifact_scaffold_is_typed_explicitly_not_run_and_never_overwrites(tmp_path: Path) -> None:
    plan = build_pipeline_plan(PIPELINE_CONFIG, repo_root=ROOT)
    output = initialize_artifact_scaffold(tmp_path / "results", plan)
    manifest = json.loads((output / "evaluation_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "planned_not_run"
    assert manifest["result_rows"] == 0
    assert manifest["missing_reason"] == "evaluation_not_authorized_or_executed"
    assert list(pd.read_parquet(output / "checkpoint_registry.parquet").columns) == list(
        CHECKPOINT_FIELDS
    )
    assert list(pd.read_parquet(output / "metric_observations.parquet").columns) == list(
        METRIC_FIELDS
    )
    figures = json.loads(
        (output / "presentation/figure_manifest.json").read_text(encoding="utf-8")
    )
    assert {item["figure_id"] for item in figures["figures"]} == {
        "fact_access_vs_epoch",
        "retention_vs_epoch",
        "fact_retention_pareto",
        "m2a_m2b_branch_comparison",
    }
    with pytest.raises(FileExistsError):
        initialize_artifact_scaffold(output, plan)
