from __future__ import annotations

import json
from pathlib import Path

import yaml

import transfer_vs_relearning.experiments.m1_cross_family as cross_family
from scripts.m1_cross_family_preflight import _unexpected_target_jobs, home_usage_evidence
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


def test_provenance_registry_freezes_three_required_candidates() -> None:
    registry = load_registry(_repo_root() / "configs/experiments/m1_provenance_screen_v1.yaml")
    assert [candidate["label"] for candidate in registry["candidates"]] == ["olmo", "pythia", "falcon"]
    assert all(candidate["required"] for candidate in registry["candidates"])
    assert estimated_family_gib(registry) == 709


def test_provenance_v3_registry_is_model_native_and_endpoint_only() -> None:
    registry = load_registry(_repo_root() / "configs/experiments/m1_provenance_screen_v3.yaml")
    assert registry["storage_correction_sha256"] == "1b55a03484682e065c9eaec106f8803b9ffdecba9301e3a0261df9e6ecd154fa"
    assert registry["tokenizer_validation_mode"] == "model_native_roundtrip"
    assert registry["require_native_tokenizer"] is False
    assert registry["expected_checkpoints_per_candidate"] == 1
    assert estimated_family_gib(registry) == 149
    template = yaml.safe_load(
        (_repo_root() / "configs/training/m1_provenance_screen_v3_seed42_template.yaml").read_text(encoding="utf-8")
    )
    assert template["training"]["checkpoint_fractions"] == [1.0]
    assert template["training"]["gradient_accumulation_steps"] * template["training"]["per_device_train_batch_size"] == 500
    storage = home_usage_evidence(registry)
    assert storage["reference_bytes"] == 14_689_423_360
    assert storage["limit_bytes"] == 30 * 1024**3
    assert storage["below_limit"] is True
    assert storage["recursive_du_executed_for_this_stage"] is False
    assert storage["home_write_allowed"] is False


def test_pythia_repair_registry_freezes_official_tokenizer_and_fresh_root() -> None:
    registry = load_registry(
        _repo_root() / "configs/experiments/m1_provenance_screen_v3_pythia_repair_v1.yaml"
    )
    assert registry["scratch_root"].endswith("m1_provenance_screen_v3_pythia_repair_v1")
    assert [candidate["label"] for candidate in registry["candidates"]] == ["pythia"]
    assert registry["candidates"][0]["requested_revision"] == "0da31d8fb309463877ed8c40e54a8f911dced3ec"
    source = registry["official_tokenizer_source"]
    assert source["repository"] == "EleutherAI/pythia"
    assert source["commit"] == "1e2365516a3284f18a68c13dbd4ca19fcae59a4b"
    assert source["bytes"] == 2_467_981
    assert source["sha256"] == "56ac4821e129d2c520fdaba60abd920fa852ada51b45c0dd52bbb6bd8c985ade"
    assert source["expected_vocabulary_length"] == 50_277
    assert estimated_family_gib(registry) == 46
    storage = home_usage_evidence(registry)
    assert storage["recursive_du_executed_for_this_stage"] is False


def test_pythia_retry_registry_uses_new_root_and_same_frozen_source() -> None:
    initial = load_registry(
        _repo_root() / "configs/experiments/m1_provenance_screen_v3_pythia_repair_v1.yaml"
    )
    retry = load_registry(
        _repo_root() / "configs/experiments/m1_provenance_screen_v3_pythia_repair_retry_v1.yaml"
    )
    assert retry["scratch_root"].endswith("m1_provenance_screen_v3_pythia_repair_retry_v1")
    assert retry["scratch_root"] != initial["scratch_root"]
    assert retry["official_tokenizer_source"] == initial["official_tokenizer_source"]
    assert retry["candidates"] == initial["candidates"]
    repair_source = (_repo_root() / "scripts/repair_pythia_official_tokenizer.py").read_text(encoding="utf-8")
    assert "pad_token=None" in repair_source


def test_pythia_rtx3090_relocation_changes_only_runtime_identity() -> None:
    original = yaml.safe_load(
        (_repo_root() / "configs/experiments/m1_provenance_screen_v3_pythia_repair_retry_v1.yaml").read_text(
            encoding="utf-8"
        )
    )
    relocation = yaml.safe_load(
        (_repo_root() / "configs/experiments/m1_provenance_screen_v3_pythia_repair_rtx3090_v1.yaml").read_text(
            encoding="utf-8"
        )
    )
    ignored = {"contract_document", "contract_sha256", "status", "runtime"}
    assert {key: value for key, value in relocation.items() if key not in ignored} == {
        key: value for key, value in original.items() if key not in ignored
    }
    assert relocation["runtime"] == {
        "python": "/vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1/bin/python",
        "torch": "2.6.0+cu124",
        "expected_gpu": "NVIDIA GeForce RTX 3090",
        "expected_compute_capability": "8.6",
        "expected_compiled_arch": "sm_86",
    }
    for launcher_name, stage in (
        ("train_m1_pythia_repair_v100.slurm", "training"),
        ("eval_m1_pythia_repair_v100.slurm", "evaluation"),
    ):
        launcher = (_repo_root() / "slurm" / launcher_name).read_text(encoding="utf-8")
        assert "M1_PYTHIA_PREFLIGHT_MANIFEST" in launcher
        assert f"preflight/{stage}.json" in launcher


def test_pythia_rtx3090_bf16_repair_preserves_scientific_recipe() -> None:
    config_root = _repo_root() / "configs/training"
    fp16 = yaml.safe_load(
        (config_root / "m1_provenance_screen_v3_pythia_v100_fp16_seed42.yaml").read_text(encoding="utf-8")
    )
    bf16 = yaml.safe_load(
        (config_root / "m1_provenance_screen_v3_pythia_rtx3090_bf16_seed42.yaml").read_text(encoding="utf-8")
    )
    assert fp16["dataset"] == bf16["dataset"]
    assert fp16["model"] == bf16["model"]
    assert fp16["runtime"] == bf16["runtime"]
    precision = {"bf16", "fp16"}
    assert {key: value for key, value in fp16["training"].items() if key not in precision} == {
        key: value for key, value in bf16["training"].items() if key not in precision
    }
    assert (fp16["training"]["bf16"], fp16["training"]["fp16"]) == (False, True)
    assert (bf16["training"]["bf16"], bf16["training"]["fp16"]) == (True, False)

    registry = yaml.safe_load(
        (
            _repo_root()
            / "configs/experiments/m1_provenance_screen_v3_pythia_repair_rtx3090_bf16_v1.yaml"
        ).read_text(encoding="utf-8")
    )
    assert registry["candidates"][0]["training_overrides"] == {"model_load_dtype": "bfloat16"}
    assert registry["runtime"]["expected_amp_dtype"] == "bfloat16"
    assert registry["runtime"]["min_free_memory_bytes"] == 20 * 1024**3
    validator = (_repo_root() / "scripts/validate_m1_pythia_v100_runtime.py").read_text(encoding="utf-8")
    assert 'expected.get("expected_amp_dtype", "float16")' in validator
    assert "torch.cuda.is_bf16_supported()" in validator
    assert "torch.cuda.mem_get_info(0)" in validator
    for launcher_name in ("train_m1_pythia_repair_v100.slurm", "eval_m1_pythia_repair_v100.slurm"):
        launcher = (_repo_root() / "slurm" / launcher_name).read_text(encoding="utf-8")
        assert "M1_PYTHIA_REPAIR_TEMPLATE" in launcher

    train_launcher = (
        _repo_root() / "slurm/train_m1_pythia_repair_rtx3090_bf16.slurm"
    ).read_text(encoding="utf-8")
    eval_launcher = (
        _repo_root() / "slurm/eval_m1_pythia_repair_rtx3090_bf16.slurm"
    ).read_text(encoding="utf-8")
    for launcher in (train_launcher, eval_launcher):
        assert "#SBATCH --gres=gpu:rtx3090:1" in launcher
        assert "#SBATCH --exclude=guppi6" in launcher
        assert "m1_provenance_screen_v3_pythia_repair_retry_v1/logs" in launcher
        assert "m1_provenance_screen_v3_pythia_repair_rtx3090_bf16_v1.yaml" in launcher
        assert "m1_provenance_screen_v3_pythia_rtx3090_bf16_seed42.yaml" in launcher
        assert "M1_PYTHIA_REPAIR_ROOT" not in launcher
        assert "M1_PYTHIA_REPAIR_REGISTRY" not in launcher
        assert "M1_PYTHIA_REPAIR_TEMPLATE" not in launcher
    assert "training_rtx3090_bf16.json" in train_launcher
    assert "evaluation_rtx3090_bf16.json" in eval_launcher
    assert "--preserve-checkpoint" in train_launcher

    preflight = (_repo_root() / "scripts/m1_cross_family_preflight.py").read_text(encoding="utf-8")
    assert "registry_training_template_binding" in preflight
    smoke = (_repo_root() / "scripts/smoke_m1_cross_family_candidate.py").read_text(encoding="utf-8")
    assert "optimizer_state_dtypes" in smoke
    assert "BF16 AdamW state dtype gate failed" in smoke


def test_pythia_v100_template_changes_only_mixed_precision() -> None:
    config_root = _repo_root() / "configs/training"
    frozen = yaml.safe_load((config_root / "m1_provenance_screen_v3_seed42_template.yaml").read_text(encoding="utf-8"))
    pythia = yaml.safe_load(
        (config_root / "m1_provenance_screen_v3_pythia_v100_fp16_seed42.yaml").read_text(encoding="utf-8")
    )
    frozen_training = dict(frozen["training"])
    pythia_training = dict(pythia["training"])
    assert frozen_training.pop("bf16") is True
    assert pythia_training.pop("bf16") is False
    assert frozen_training.pop("fp16") is False
    assert pythia_training.pop("fp16") is True
    assert pythia_training == frozen_training
    assert pythia["dataset"] == frozen["dataset"]
    assert pythia["model"] == frozen["model"]
    assert pythia["runtime"] == frozen["runtime"]


def test_olmo_3090_retry_changes_only_batch_decomposition() -> None:
    config_root = _repo_root() / "configs/training"
    frozen = yaml.safe_load((config_root / "m1_provenance_screen_v3_seed42_template.yaml").read_text(encoding="utf-8"))
    retry = yaml.safe_load(
        (config_root / "m1_provenance_screen_v3_olmo_3090_retry_seed42.yaml").read_text(encoding="utf-8")
    )
    frozen_training = dict(frozen["training"])
    retry_training = dict(retry["training"])
    assert frozen_training.pop("per_device_train_batch_size") == 10
    assert retry_training.pop("per_device_train_batch_size") == 5
    assert frozen_training.pop("gradient_accumulation_steps") == 50
    assert retry_training.pop("gradient_accumulation_steps") == 100
    assert retry_training == frozen_training
    assert retry["dataset"] == frozen["dataset"]
    assert retry["model"] == frozen["model"]
    assert retry["runtime"] == frozen["runtime"]
    assert 5 * 100 == 10 * 50 == 500


def test_olmo_3090_foreach_retry_changes_only_optimizer_kernel() -> None:
    config_root = _repo_root() / "configs/training"
    batch_retry = yaml.safe_load(
        (config_root / "m1_provenance_screen_v3_olmo_3090_retry_seed42.yaml").read_text(encoding="utf-8")
    )
    foreach_retry = yaml.safe_load(
        (config_root / "m1_provenance_screen_v3_olmo_3090_retry_foreach_false_seed42.yaml").read_text(encoding="utf-8")
    )
    foreach_training = dict(foreach_retry["training"])
    assert foreach_training.pop("optimizer_foreach") is False
    assert foreach_training == batch_retry["training"]
    assert foreach_retry["dataset"] == batch_retry["dataset"]
    assert foreach_retry["model"] == batch_retry["model"]
    assert foreach_retry["runtime"] == batch_retry["runtime"]


def test_olmo_v100_retry_changes_only_mixed_precision() -> None:
    config_root = _repo_root() / "configs/training"
    frozen = yaml.safe_load((config_root / "m1_provenance_screen_v3_seed42_template.yaml").read_text(encoding="utf-8"))
    v100 = yaml.safe_load(
        (config_root / "m1_provenance_screen_v3_olmo_v100_fp16_seed42.yaml").read_text(encoding="utf-8")
    )
    frozen_training = dict(frozen["training"])
    v100_training = dict(v100["training"])
    assert frozen_training.pop("bf16") is True
    assert v100_training.pop("bf16") is False
    assert frozen_training.pop("fp16") is False
    assert v100_training.pop("fp16") is True
    assert v100_training == frozen_training
    assert v100["dataset"] == frozen["dataset"]
    assert v100["model"] == frozen["model"]
    assert v100["runtime"] == frozen["runtime"]


def test_provenance_launchers_allow_isolated_scratch_python() -> None:
    for relative in ("slurm/train_m1_provenance_screen.slurm", "slurm/eval_m1_provenance_screen.slurm"):
        launcher = (_repo_root() / relative).read_text(encoding="utf-8")
        assert 'M1_PROVENANCE_PYTHON' in launcher
        assert 'test -x "${M1_PROVENANCE_PYTHON}"' in launcher
        assert 'run_python' in launcher


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


def test_provenance_materialized_config_has_bounded_namespace(tmp_path: Path, monkeypatch) -> None:
    registry = load_registry(_repo_root() / "configs/experiments/m1_provenance_screen_v1.yaml")
    registry["scratch_root"] = str(tmp_path / "m1_provenance_screen_v1")
    candidate = candidate_by_index(registry, 0)
    manifest = tmp_path / "models/allenai__OLMo-2-0425-1B/model_manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("{}\n", encoding="utf-8")
    training_root = tmp_path / "m1_provenance_screen_v1/training/olmo"
    monkeypatch.setattr(cross_family, "approved_scratch", lambda path: path.resolve())
    monkeypatch.setattr(cross_family, "candidate_model_manifest", lambda _registry, _candidate: manifest)
    monkeypatch.setattr(cross_family, "candidate_training_root", lambda _registry, _candidate: training_root)
    template = yaml.safe_load((_repo_root() / "configs/training/m1_provenance_screen_seed42_template.yaml").read_text(encoding="utf-8"))
    payload = materialize_training_config(
        registry=registry,
        candidate=candidate,
        template=template,
        dataset_root=tmp_path / "datasets",
    )
    assert payload["training"]["run_name"] == "m1_provenance_screen_olmo_seed42"
    assert payload["training"]["supervise_eos"] is False


def test_stablelm_remediation_only_overrides_model_load_dtype(tmp_path: Path, monkeypatch) -> None:
    registry = load_registry(_repo_root() / "configs/experiments/m1_cross_family_screen_v1.yaml")
    scratch_root = tmp_path / "m1_cross_family_screen_v1"
    registry["scratch_root"] = str(scratch_root)
    candidate = candidate_by_index(registry, 1)
    manifest = tmp_path / "models/stabilityai__stablelm-2-1_6b/model_manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(cross_family, "approved_scratch", lambda path: path.resolve())
    monkeypatch.setattr(cross_family, "candidate_model_manifest", lambda _registry, _candidate: manifest)
    monkeypatch.setattr(cross_family, "candidate_training_root", lambda _registry, _candidate: scratch_root / "training/stablelm")
    template = yaml.safe_load((_repo_root() / "configs/training/m1_cross_family_seed42_template.yaml").read_text(encoding="utf-8"))
    payload = materialize_training_config(registry=registry, candidate=candidate, template=template, dataset_root=tmp_path / "datasets")
    changed = {key: value for key, value in payload["training"].items() if template["training"].get(key) != value}
    assert changed == {
        "model_load_dtype": "bfloat16",
        "output_root": str(scratch_root / "training/stablelm"),
        "run_name": "m1_cross_family_stablelm_seed42",
    }


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


def test_completed_subset_evaluation_allows_only_disjoint_running_tasks() -> None:
    rows = [
        "410109_2|m1-xfam-eval|(null)",
        "410110_1|m1-xfam-eval|(null)",
        "410111_[1,3]|m1-xfam-eval|afterok:410105(unfulfilled)",
    ]
    assert _unexpected_target_jobs("m1-xfam-eval", rows, "410105", {1, 3}) == [
        "410110_1|m1-xfam-eval|(null)"
    ]


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


def test_subset_retry_requires_explicit_preflight_mode() -> None:
    preflight = (_repo_root() / "scripts/m1_cross_family_preflight.py").read_text(encoding="utf-8")
    launcher = (_repo_root() / "slurm/preflight_m1_cross_family.slurm").read_text(encoding="utf-8")
    assert 'parser.add_argument("--allow-subset-retry", action="store_true")' in preflight
    assert 'args.stage == "training"' in preflight
    assert 'bool(args.candidate_index)' in preflight
    assert 'ALLOW_SUBSET_RETRY' in launcher


def test_completed_subset_evaluation_requires_explicit_preflight_mode() -> None:
    preflight = (_repo_root() / "scripts/m1_cross_family_preflight.py").read_text(encoding="utf-8")
    launcher = (_repo_root() / "slurm/preflight_m1_cross_family.slurm").read_text(encoding="utf-8")
    assert 'parser.add_argument("--allow-completed-subset-evaluation", action="store_true")' in preflight
    assert 'args.stage == "evaluation"' in preflight
    assert 'completed_training_endpoints' in preflight
    assert 'ALLOW_COMPLETED_SUBSET_EVALUATION' in launcher
