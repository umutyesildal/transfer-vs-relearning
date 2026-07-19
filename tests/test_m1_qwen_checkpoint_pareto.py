from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_frozen_checkpoint_contract_and_token_hash() -> None:
    module = _load_script("prepare_m1_qwen_checkpoint_pareto.py")
    assert module.CHECKPOINTS == (25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252)
    assert module.BASE_PERPLEXITY == 14.6988390227992
    assert module.BASE_TOKEN_HASH == "be2effefc9f0655b0fc5bc3052ecfd18b51bdfa48bffa1ab2d4f0c217b81c78f"


def test_hard_metrics_preserve_scaffold_cell_minima(tmp_path: Path) -> None:
    module = _load_script("summarize_m1_qwen_checkpoint_pareto.py")
    hard = tmp_path / "hard"
    relation_form_rows = []
    for relation in ("profession", "born_in"):
        for form in ("form_a", "form_b", "form_c", "form_d"):
            for scaffold in ("direct", "qa"):
                accuracy = 0.95
                if relation == "born_in" and form == "form_c" and scaffold == "qa":
                    accuracy = 0.79
                relation_form_rows.append({"relation": relation, "form_id": form, "scaffold_id": scaffold, "top1_accuracy": accuracy})
    _write_csv(hard / "summary_by_relation_form.csv", relation_form_rows)
    _write_csv(hard / "form_intersections.csv", [
        {"relation": "profession", "scaffold_id": "direct", "n": 10, "all_form_intersection": 9},
        {"relation": "profession", "scaffold_id": "qa", "n": 10, "all_form_intersection": 7},
        {"relation": "born_in", "scaffold_id": "direct", "n": 10, "all_form_intersection": 8},
        {"relation": "born_in", "scaffold_id": "qa", "n": 10, "all_form_intersection": 6},
    ])
    (hard / "summary.json").write_text(json.dumps({"top1": 36, "probes": 40}), encoding="utf-8")
    assert module._hard_metrics(hard) == (0.9, 0.95, 0.79, 0.75, 0.7)


def test_slurm_wave_excludes_anomalous_node_and_is_bounded() -> None:
    launcher = (ROOT / "slurm/eval_m1_qwen_checkpoint_pareto.slurm").read_text(encoding="utf-8")
    assert "#SBATCH --exclude=gruenau10" in launcher
    submitter = (ROOT.parent / "ssh-client/scripts/submit_m1_qwen_checkpoint_pareto.sh")
    if submitter.exists():
        source = submitter.read_text(encoding="utf-8")
        assert '--array="0-10%3"' in source
