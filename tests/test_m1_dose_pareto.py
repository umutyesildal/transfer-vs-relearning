from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.experiments.m1_dose_pareto import (
    CHECKPOINT_STEPS,
    CONTRACT_SHA256,
    AMENDMENT_SHA256,
    FALCON_COMPLETED_CHEAP_STEPS,
    FALCON_EVALUATION_RECOVERY_SHA256,
    FALCON_EVALUATION_RTXA6000_RELOCATION_SHA256,
    FALCON_EVALUATION_RTXA6000_EXCLUSIVE_SHA256,
    FALCON_EVALUATION_CLEAN_UUID_SHA256,
    FALCON_RECOVERY_STEPS,
    PRECISION_REPAIR_SHA256,
    LABELS,
    VERSION,
    final_gate,
    evaluation_runtime_identity,
    load_registry,
    validate_falcon_evaluation_recovery_state,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_registry_and_templates_freeze_document_159() -> None:
    registry = load_registry(repo_root() / "configs/experiments/m1_provenance_screen_v4_dose_pareto_v1.yaml")
    assert registry["version"] == VERSION
    assert registry["contract_sha256"] == CONTRACT_SHA256
    assert registry["operational_amendment_sha256"] == AMENDMENT_SHA256
    assert registry["precision_repair_sha256"] == PRECISION_REPAIR_SHA256
    assert tuple(registry["checkpoint_steps"]) == CHECKPOINT_STEPS
    assert tuple(item["label"] for item in registry["candidates"]) == LABELS
    assert registry["gates"]["generic_ppl_ratio_max"] == 1.25
    for item in registry["candidates"]:
        template = yaml.safe_load((repo_root() / item["training_template"]).read_text(encoding="utf-8"))
        training = template["training"]
        assert training["save_steps"] == 42
        assert training["eval_steps"] == 42
        assert training["save_total_limit"] >= 6
        assert training["learning_rate"] == 5e-5
        assert training["num_train_epochs"] == 36.0
        assert training["per_device_train_batch_size"] * training["gradient_accumulation_steps"] == 500
        if item["label"] in {"falcon", "pythia"}:
            assert training["model_load_dtype"] == "bfloat16"


def test_launchers_bind_gpu_classes_and_no_cleanup() -> None:
    olmo = (repo_root() / "slurm/train_m1_dose_pareto_olmo_rtx3090.slurm").read_text(encoding="utf-8")
    assert "#SBATCH --gres=gpu:rtx3090:1" in olmo
    assert "#SBATCH --exclude=guppi6" in olmo
    for label in ("falcon", "pythia"):
        train = (repo_root() / f"slurm/train_m1_dose_pareto_{label}_rtx3090.slurm").read_text(encoding="utf-8")
        evaluate = (repo_root() / f"slurm/eval_m1_dose_pareto_{label}_rtx3090.slurm").read_text(encoding="utf-8")
        assert "#SBATCH --gres=gpu:rtx3090:1" in train
        assert "#SBATCH --exclude=guppi6" in train
        assert "#SBATCH --exclude=guppi6" in evaluate
    sources = "\n".join(path.read_text(encoding="utf-8") for path in (repo_root() / "slurm").glob("*m1_dose_pareto*.slurm"))
    assert "rm " not in sources
    assert "--force" not in sources
    for label in ("olmo", "falcon"):
        launcher = (repo_root() / f"slurm/train_m1_dose_pareto_{label}_rtx3090.slurm").read_text(encoding="utf-8")
        assert "M1_V4_PREFLIGHT" in launcher


def test_olmo_relocation_fallback_preserves_effective_batch_and_bounds_eval_batches() -> None:
    template = yaml.safe_load(
        (repo_root() / "configs/training/m1_provenance_screen_v4_olmo_rtx3090_fp16_fallback_seed42.yaml").read_text(encoding="utf-8")
    )
    training = template["training"]
    assert training["per_device_train_batch_size"] == 2
    assert training["gradient_accumulation_steps"] == 250
    assert training["optimizer_foreach"] is False
    assert training["per_device_train_batch_size"] * training["gradient_accumulation_steps"] == 500
    evaluate = (repo_root() / "slurm/eval_m1_dose_pareto_olmo_rtx3090.slurm").read_text(encoding="utf-8")
    assert "--candidate-batch-size 32" in evaluate


def test_olmo_explicit_bf16_repair_binds_low_memory_parameter_state() -> None:
    template = yaml.safe_load(
        (repo_root() / "configs/training/m1_provenance_screen_v4_olmo_rtx3090_bf16_seed42.yaml").read_text(encoding="utf-8")
    )
    training = template["training"]
    assert training["model_load_dtype"] == "bfloat16"
    assert training["bf16"] is True and training["fp16"] is False
    assert training["optimizer_foreach"] is False
    assert training["per_device_train_batch_size"] == 5
    assert training["gradient_accumulation_steps"] == 100
    assert training["per_device_train_batch_size"] * training["gradient_accumulation_steps"] == 500


def test_falcon_recovery_state_requires_exact_15_of_18_inventory(tmp_path: Path) -> None:
    root = tmp_path / "m1_provenance_screen_v4_dose_pareto_v1"
    training = root / "training" / "falcon" / "only-run"
    training.mkdir(parents=True)
    (training / "training_manifest.json").write_text(
        json.dumps({"status": "complete"}), encoding="utf-8"
    )
    for step in CHECKPOINT_STEPS:
        (training / "checkpoints" / f"checkpoint-{step}").mkdir(parents=True)
    for label in LABELS:
        steps = FALCON_COMPLETED_CHEAP_STEPS if label == "falcon" else CHECKPOINT_STEPS
        for step in steps:
            checkpoint = root / "evaluations" / label / f"checkpoint-{step}"
            checkpoint.mkdir(parents=True)
            (checkpoint / "cheap_gate.json").write_text(
                json.dumps(
                    {
                        "status": "FAIL_HARD_STAGE_SKIPPED",
                        "label": label,
                        "step": step,
                        "hard_stage_open": False,
                    }
                ),
                encoding="utf-8",
            )
    state = validate_falcon_evaluation_recovery_state(
        {"scratch_root": str(root)},
        summary_root=root / "analysis" / "three_model_dose_pareto_summary_v1",
    )
    assert state["status"] == "PASS"
    assert state["contract_sha256"] == FALCON_EVALUATION_RECOVERY_SHA256
    assert state["available_checkpoint_count"] == 15
    assert state["required_checkpoint_count"] == 18
    assert state["recovery_array_indices"] == [2, 4, 5]
    assert state["recovery_steps"] == list(FALCON_RECOVERY_STEPS)

    forbidden = root / "evaluations" / "falcon" / "checkpoint-126"
    forbidden.mkdir(parents=True)
    with pytest.raises(FileExistsError, match="namespace is not absent"):
        validate_falcon_evaluation_recovery_state(
            {"scratch_root": str(root)},
            summary_root=root / "analysis" / "three_model_dose_pareto_summary_v1",
        )


def test_falcon_recovery_launchers_are_evaluation_only_and_dependency_closed() -> None:
    evaluation = (
        repo_root() / "slurm/eval_m1_dose_pareto_falcon_recovery_rtx3090.slurm"
    ).read_text(encoding="utf-8")
    summary = (
        repo_root() / "slurm/summarize_m1_dose_pareto_falcon_recovery.slurm"
    ).read_text(encoding="utf-8")
    submit = (
        repo_root() / "scripts/submit_m1_dose_pareto_falcon_recovery.sh"
    ).read_text(encoding="utf-8")
    assert "#SBATCH --array=2,4,5%1" in evaluation
    assert "#SBATCH --partition=wbimlgpu" in evaluation
    assert "#SBATCH --nodelist=guppi5" in evaluation
    assert "case \"${SLURM_ARRAY_TASK_ID:?}\" in 2) step=126 ;; 4) step=210 ;; 5) step=252" in evaluation
    assert "train_clm.py" not in evaluation
    assert "prepare_m1_dose_pareto_evaluation.py" in evaluation
    assert "summarize_m1_dose_pareto.py" in summary
    assert "--dependency=afterok:${evaluation_id}" in submit
    assert "rm " not in evaluation + summary + submit


def test_falcon_rtxa6000_relocation_is_exact_and_access_checked() -> None:
    registry = load_registry(
        repo_root() / "configs/experiments/m1_provenance_screen_v4_dose_pareto_v1.yaml"
    )
    default_runtime = evaluation_runtime_identity(registry, "falcon")
    relocated = evaluation_runtime_identity(
        registry,
        "falcon",
        falcon_relocation_sha256=FALCON_EVALUATION_RTXA6000_RELOCATION_SHA256,
    )
    assert default_runtime["expected_gpu_substring"] == "RTX 3090"
    assert relocated["expected_gpu_substring"] == "RTX A6000"
    assert relocated["expected_compute_capability"] == "8.6"
    assert relocated["expected_compiled_arch"] == "sm_86"
    assert relocated["min_free_memory_bytes"] == 40 * 1024**3
    with pytest.raises(ValueError, match="Document 165"):
        evaluation_runtime_identity(
            registry, "falcon", falcon_relocation_sha256="0" * 64
        )
    with pytest.raises(ValueError, match="Document 165"):
        evaluation_runtime_identity(
            registry,
            "olmo",
            falcon_relocation_sha256=FALCON_EVALUATION_RTXA6000_RELOCATION_SHA256,
        )

    evaluation = (
        repo_root() / "slurm/eval_m1_dose_pareto_falcon_recovery_rtxa6000.slurm"
    ).read_text(encoding="utf-8")
    summary = (
        repo_root() / "slurm/summarize_m1_dose_pareto_falcon_recovery_rtxa6000.slurm"
    ).read_text(encoding="utf-8")
    submit = (
        repo_root() / "scripts/submit_m1_dose_pareto_falcon_rtxa6000_recovery.sh"
    ).read_text(encoding="utf-8")
    preflight = (
        repo_root() / "scripts/preflight_m1_dose_pareto_falcon_rtxa6000_recovery.py"
    ).read_text(encoding="utf-8")
    assert "#SBATCH --partition=gpu" in evaluation
    assert "#SBATCH --nodelist=gruenau8" in evaluation
    assert "#SBATCH --gres=gpu:rtxa6000:1" in evaluation
    assert "#SBATCH --array=2,4,5%1" in evaluation
    assert "--falcon-evaluation-relocation-sha256" in evaluation
    assert "sbatch --test-only" in submit
    assert submit.index("sbatch --test-only") < submit.index('evaluation_id="$(sbatch --parsable')
    assert "--dependency=afterok:${evaluation_id}" in submit
    assert 'TARGET_PARTITION = "gpu"' in preflight
    assert 'TARGET_NODE = "gruenau8"' in preflight
    assert 'TARGET_GRES = "gpu:rtxa6000:1"' in preflight
    assert "40 * 1024**3" in preflight
    assert "train_clm.py" not in evaluation + summary + submit + preflight
    assert "rm " not in evaluation + summary + submit + preflight


def test_falcon_rtxa6000_exclusive_retry_requires_runtime_cleanliness() -> None:
    registry = load_registry(
        repo_root() / "configs/experiments/m1_provenance_screen_v4_dose_pareto_v1.yaml"
    )
    runtime = evaluation_runtime_identity(
        registry,
        "falcon",
        falcon_relocation_sha256=FALCON_EVALUATION_RTXA6000_EXCLUSIVE_SHA256,
    )
    assert runtime["expected_gpu_substring"] == "RTX A6000"
    assert runtime["min_free_memory_bytes"] == 40 * 1024**3

    evaluation = (
        repo_root() / "slurm/eval_m1_dose_pareto_falcon_recovery_rtxa6000_exclusive.slurm"
    ).read_text(encoding="utf-8")
    submit = (
        repo_root() / "scripts/submit_m1_dose_pareto_falcon_rtxa6000_exclusive_recovery.sh"
    ).read_text(encoding="utf-8")
    preflight = (
        repo_root() / "scripts/preflight_m1_dose_pareto_falcon_rtxa6000_exclusive_recovery.py"
    ).read_text(encoding="utf-8")
    runtime_validator = (
        repo_root() / "scripts/validate_m1_dose_pareto_runtime.py"
    ).read_text(encoding="utf-8")
    assert "#SBATCH --exclusive" in evaluation
    assert "#SBATCH --array=2,4,5%1" in evaluation
    assert "--require-empty-compute-apps" in evaluation
    assert "--maximum-used-vram-bytes 536870912" in evaluation
    assert evaluation.index("validate_m1_dose_pareto_runtime.py") < evaluation.index("mkdir -p")
    assert 'DEAD_SUMMARY_JOB_ID = "456415"' in preflight
    assert "scancel 456415" in submit
    assert submit.index("scancel 456415") < submit.index("sbatch --test-only")
    assert submit.count('evaluation_id="$(sbatch --parsable') == 1
    assert "--dependency=afterok:${evaluation_id}" in submit
    assert "--query-compute-apps=pid,process_name,used_memory" in runtime_validator
    assert "Allocated GPU has compute processes" in runtime_validator
    assert "train_clm.py" not in evaluation + submit + preflight
    assert "rm " not in evaluation + submit + preflight


def test_falcon_clean_uuid_retry_audits_before_torch_and_is_dependency_closed() -> None:
    registry = load_registry(
        repo_root() / "configs/experiments/m1_provenance_screen_v4_dose_pareto_v1.yaml"
    )
    runtime = evaluation_runtime_identity(
        registry, "falcon", falcon_relocation_sha256=FALCON_EVALUATION_CLEAN_UUID_SHA256
    )
    assert runtime["expected_gpu_substring"] == "RTX A6000"
    evaluation = (repo_root() / "slurm/eval_m1_dose_pareto_falcon_clean_uuid_recovery.slurm").read_text(encoding="utf-8")
    selector = (repo_root() / "scripts/select_clean_a6000_uuid.py").read_text(encoding="utf-8")
    submit = (repo_root() / "scripts/submit_m1_dose_pareto_falcon_clean_uuid_recovery.sh").read_text(encoding="utf-8")
    preflight = (repo_root() / "scripts/preflight_m1_dose_pareto_falcon_clean_uuid_recovery.py").read_text(encoding="utf-8")
    assert "#SBATCH --exclusive" in evaluation and "#SBATCH --array=2,4,5%1" in evaluation
    assert evaluation.index("select_clean_a6000_uuid.py") < evaluation.index("validate_m1_dose_pareto_runtime.py")
    assert 'export CUDA_VISIBLE_DEVICES="${selected_uuid}"' in evaluation
    assert "import torch" not in selector
    assert "lexicographically_smallest_clean_gpu_uuid" in selector
    assert 'DEAD_SUMMARY_JOB_ID = "456467"' in preflight
    assert "scancel 456467" in submit
    assert submit.index("scancel 456467") < submit.index("sbatch --test-only")
    assert submit.count('evaluation_id="$(sbatch --parsable') == 1
    assert "--dependency=afterok:${evaluation_id}" in submit
    assert "train_clm.py" not in evaluation + selector + submit + preflight
    assert "rm " not in evaluation + selector + submit + preflight


def test_final_gate_reproduces_eight_prompt_intersection(tmp_path: Path) -> None:
    registry = yaml.safe_load((repo_root() / "configs/experiments/m1_provenance_screen_v4_dose_pareto_v1.yaml").read_text(encoding="utf-8"))
    cheap = tmp_path / "cheap.json"
    cheap.write_text(json.dumps({"hard_stage_open": True, "exact_accuracy": 1.0, "ppl_ratio": 1.1}), encoding="utf-8")
    hard = tmp_path / "hard.csv"
    fieldnames = ["relation", "subject_id", "form_id", "scaffold_id", "failure_type"]
    with hard.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for relation in ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry"):
            for subject in range(100):
                for form in ("form_a", "form_b", "form_c", "form_d"):
                    for scaffold in ("direct", "qa"):
                        writer.writerow({"relation": relation, "subject_id": f"{relation}-{subject}", "form_id": form, "scaffold_id": scaffold, "failure_type": "none"})
    output = tmp_path / "final.json"
    result = final_gate(registry, "olmo", 42, cheap, hard, output)
    assert result["all_gates_pass"] is True
    assert result["global_robust_intersection"] == 1.0
    assert result["min_heldout_cd_accuracy"] == 1.0
    assert output.is_file()
