from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retention_evaluation_freezes_two_conditions_and_eleven_checkpoints() -> None:
    module = _load("prepare_m1_retention_evaluation.py")
    assert module.CONDITIONS == ("control", "replay_w0_5")
    assert module.CHECKPOINTS == (25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252)
    assert module.BASE_PERPLEXITY == 14.6988390227992


def test_exact_metrics_enforces_relation_minimum(tmp_path: Path) -> None:
    module = _load("summarize_m1_retention_evaluation.py")
    summary = tmp_path / "summary_metrics.json"
    summary.write_text(json.dumps({"primary_mean_logprob": {"top1_accuracy": 0.95}}))
    with (tmp_path / "subgroup_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("group", "scoring", "top1_accuracy"))
        writer.writeheader()
        for accuracy in (0.99, 0.98, 0.97, 0.96, 0.89):
            writer.writerow({"group": "relation", "scoring": "primary_mean_logprob", "top1_accuracy": accuracy})
    assert module._exact_metrics(summary) == (0.95, 0.89)


def test_resolver_reads_one_frozen_task(tmp_path: Path) -> None:
    module = _load("resolve_m1_retention_evaluation.py")
    registry = tmp_path / "registry.csv"
    with registry.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("array_index", "condition", "label"))
        writer.writeheader()
        writer.writerow({"array_index": 0, "condition": "control", "label": "control_step25"})
    assert module.resolve(registry, 0, "condition") == "control"
    assert module.resolve(registry, 0, "label") == "control_step25"


def test_evaluation_uses_available_rtx3090_pool_and_avoids_busy_nodes() -> None:
    launcher = (ROOT / "slurm/eval_m1_retention_checkpoints.slurm").read_text(encoding="utf-8")
    assert "#SBATCH --gres=gpu:rtx3090:1" in launcher
    assert "#SBATCH --exclude=guppi6,guppi7" in launcher
    resume = (ROOT / "scripts/submit_prepared_m1_retention_evaluation.sh").read_text(encoding="utf-8")
    assert '--array="0-21%3"' in resume


def test_adjudication_preserves_short_diagnostic_but_accepts_lexical_answer(tmp_path: Path) -> None:
    module = _load("adjudicate_m1_retention_evaluation.py")
    run_dir = tmp_path / "general_capability" / "replay_step50" / "run"
    run_dir.mkdir(parents=True)
    (run_dir / "summary_metrics.json").write_text(
        json.dumps({"completion_status": "completed"}), encoding="utf-8"
    )
    generations = [
        {
            "prompt_id": "qa_02",
            "continuation": " navigation",
            "empty_or_near_empty": True,
        }
    ]
    (run_dir / "generations.jsonl").write_text(
        "\n".join(json.dumps(row) for row in generations) + "\n", encoding="utf-8"
    )
    original = {
        "label": "replay_step50",
        "condition": "replay_w0_5",
        "checkpoint_step": 50,
        "synthetic_subject_intrusion_count": 0,
        **{key: True for key in module.GATE_KEYS},
    }
    row = module.adjudicate_rows(tmp_path, [original])[0]
    assert row["legacy_near_empty_by_token_length_count"] == 1
    assert row["lexical_empty_generation_count"] == 0
    assert row["short_but_lexical_prompt_ids"] == ["qa_02"]
    assert row["all_corrected_gates_pass"]


def test_seed43_launcher_uses_dedicated_scratch_and_single_replication_job() -> None:
    launcher = (ROOT / "scripts/submit_m1_retention_seed43.sh").read_text(encoding="utf-8")
    assert 'SCRATCH_ROOT="/vol/tmp2/yesildau/m1_retention_seed43_v1"' in launcher
    assert "--array" not in launcher
    training = (ROOT / "slurm/train_m1_retention_seed43.slurm").read_text(encoding="utf-8")
    assert "#SBATCH --gres=gpu:a10080gb:1" in training
    assert "m1_qwen_retention_replay_w0_5_seed43.yaml" in training


def test_seed43_evaluation_freezes_eleven_checkpoints_and_three_way_throttle() -> None:
    module = _load("prepare_m1_retention_seed43_evaluation.py")
    assert module.CHECKPOINTS == (25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252)
    launcher = (ROOT / "scripts/submit_m1_retention_seed43_evaluation.sh").read_text(encoding="utf-8")
    assert '--array="0-10%3"' in launcher
    evaluator = (ROOT / "slurm/eval_m1_retention_seed43_checkpoints.slurm").read_text(encoding="utf-8")
    assert "#SBATCH --gres=gpu:rtx3090:1" in evaluator
    summarizer = (ROOT / "scripts/summarize_m1_retention_seed43_evaluation.py").read_text(encoding="utf-8")
    assert "legacy_strict_integrity_gate" in summarizer
    assert "corrected_generic_integrity_gate" in summarizer
