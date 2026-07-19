from __future__ import annotations

import json
from pathlib import Path

import yaml

import transfer_vs_relearning.experiments.m1_cross_family as cross_family
from scripts.m1_cross_family_preflight import _unexpected_target_jobs
from transfer_vs_relearning.experiments.m1_cross_family import (
    candidate_by_index,
    combined_weight_sha256,
    estimated_family_gib,
    load_registry,
    materialize_training_config,
    model_weight_hashes,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_registry_freezes_required_and_conditional_candidates() -> None:
    registry = load_registry(_repo_root() / "configs/experiments/m1_cross_family_screen_v1.yaml")
    assert [candidate["label"] for candidate in registry["candidates"]] == ["qwen", "stablelm", "gemma", "llama"]
    assert [candidate["required"] for candidate in registry["candidates"]] == [True, True, True, False]
    assert estimated_family_gib(registry) == 1101


def test_materialized_config_preserves_frozen_budget(tmp_path: Path, monkeypatch) -> None:
    registry = load_registry(_repo_root() / "configs/experiments/m1_cross_family_screen_v1.yaml")
    registry["scratch_root"] = str(tmp_path / "m1_cross_family_screen_v1")
    candidate = candidate_by_index(registry, 0)
    manifest = tmp_path / "models/Qwen__Qwen2.5-1.5B/model_manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("{}\n", encoding="utf-8")
    training_root = tmp_path / "m1_cross_family_screen_v1/training/qwen"
    monkeypatch.setattr(cross_family, "approved_scratch", lambda path: path.resolve())
    monkeypatch.setattr(cross_family, "candidate_model_manifest", lambda _registry, _candidate: manifest)
    monkeypatch.setattr(cross_family, "candidate_training_root", lambda _registry, _candidate: training_root)
    template = yaml.safe_load((_repo_root() / "configs/training/m1_cross_family_seed42_template.yaml").read_text(encoding="utf-8"))
    payload = materialize_training_config(
        registry=registry,
        candidate=candidate,
        template=template,
        dataset_root=tmp_path / "datasets",
    )
    assert payload["training"]["run_name"] == "m1_cross_family_qwen_seed42"
    assert payload["training"]["supervise_eos"] is False
    assert payload["training"]["gradient_accumulation_steps"] * payload["training"]["per_device_train_batch_size"] == 500


def test_sharded_model_weight_digest(tmp_path: Path) -> None:
    (tmp_path / "model-00001-of-00002.safetensors").write_bytes(b"one")
    (tmp_path / "model-00002-of-00002.safetensors").write_bytes(b"two")
    hashes = model_weight_hashes(tmp_path)
    assert list(hashes) == ["model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors"]
    assert len(combined_weight_sha256(hashes)) == 64
    assert json.dumps(hashes, sort_keys=True)


def test_preflight_allows_its_own_afterok_target_but_rejects_other_duplicates() -> None:
    rows = [
        "m1-xfam-train|afterok:409100(unfulfilled)",
        "m1-xfam-train|(null)",
        "unrelated|afterok:409100(unfulfilled)",
    ]
    assert _unexpected_target_jobs("m1-xfam-train", rows, "409100") == ["m1-xfam-train|(null)"]
    assert _unexpected_target_jobs("m1-xfam-train", rows[:1], "999999") == rows[:1]


def test_array_launchers_reject_blank_labels_and_avoid_shared_training_config() -> None:
    launchers = [
        _repo_root() / "slurm/acquire_m1_cross_family_models.slurm",
        _repo_root() / "slurm/train_m1_cross_family.slurm",
        _repo_root() / "slurm/eval_m1_cross_family.slurm",
    ]
    for launcher in launchers:
        text = launcher.read_text(encoding="utf-8")
        assert "sed '/^[[:space:]]*$/d'" in text
        assert "Invalid resolved candidate label" in text
    training = launchers[1].read_text(encoding="utf-8")
    assert '${SLURM_ARRAY_TASK_ID}_${label}.yaml' in training
