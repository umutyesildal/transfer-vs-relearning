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
