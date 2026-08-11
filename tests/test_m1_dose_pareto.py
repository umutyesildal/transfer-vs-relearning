from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from transfer_vs_relearning.experiments.m1_dose_pareto import (
    CHECKPOINT_STEPS,
    CONTRACT_SHA256,
    LABELS,
    VERSION,
    final_gate,
    load_registry,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_registry_and_templates_freeze_document_159() -> None:
    registry = load_registry(repo_root() / "configs/experiments/m1_provenance_screen_v4_dose_pareto_v1.yaml")
    assert registry["version"] == VERSION
    assert registry["contract_sha256"] == CONTRACT_SHA256
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
    olmo = (repo_root() / "slurm/train_m1_dose_pareto_olmo_v100.slurm").read_text(encoding="utf-8")
    assert "#SBATCH --gres=gpu:v10032gb:1" in olmo
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
        launcher = (repo_root() / f"slurm/train_m1_dose_pareto_{label}_{'v100' if label == 'olmo' else 'rtx3090'}.slurm").read_text(encoding="utf-8")
        assert "M1_V4_PREFLIGHT" in launcher


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
