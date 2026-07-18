from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from transfer_vs_relearning.data.m1_form_generalization import (
    FORM_IDS,
    VERSION,
    build_m1_form_generalization_datasets,
)
from transfer_vs_relearning.evaluation.pre_m2_followup import _all_cell_intersection_rows, _intersection_rows
from transfer_vs_relearning.training.clm import estimate_optimizer_steps, load_training_config
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl


def test_builder_enforces_matched_budget_and_four_form_holdouts(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output = build_m1_form_generalization_datasets(repo_root, output_dir=tmp_path / VERSION)
    manifest = json.loads((output / "dataset_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "passed"
    assert manifest["probe_contract"] == {
        "forms": list(FORM_IDS),
        "scaffolds": ["direct", "qa"],
        "probes": 4000,
        "form_c_d_training_rows": 0,
    }
    probes = read_csv_rows(output / "evaluations/four_form_probe_registry.csv")
    assert len(probes) == 4000
    assert Counter(row["form_id"] for row in probes) == Counter({form_id: 1000 for form_id in FORM_IDS})
    for condition in ("control", "balanced_ab"):
        train = read_jsonl(output / "datasets" / condition / "train.jsonl")
        validation = read_jsonl(output / "datasets" / condition / "validation.jsonl")
        assert len(train) == 3500
        assert len(validation) == 500
        assert Counter(row["scaffold_id"] for row in train) == Counter({"direct": 2000, "qa": 1500})
        assert set(Counter(row["fact_id"] for row in train).values()) == {7}
        assert not {row["training_form_id"] for row in train} & {"form_c", "form_d"}
    balanced = read_jsonl(output / "datasets/balanced_ab/train.jsonl")
    assert Counter(row["training_form_id"] for row in balanced) == Counter({"form_a": 1750, "form_b": 1750})
    per_fact = {}
    for row in balanced:
        per_fact.setdefault(row["fact_id"], []).append(row)
    assert len(per_fact) == 500
    for rows in per_fact.values():
        assert {row["training_form_id"] for row in rows} == {"form_a", "form_b"}
        assert {row["scaffold_id"] for row in rows} == {"direct", "qa"}


def test_seed42_configs_are_matched_except_identity_and_dataset_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    control = load_training_config(repo_root / "configs/training/m1_form_generalization_control_seed42.yaml")
    intervention = load_training_config(repo_root / "configs/training/m1_form_generalization_balanced_ab_seed42.yaml")
    for section in ("model", "runtime"):
        assert control[section] == intervention[section]
    assert control["training"].keys() == intervention["training"].keys()
    for key, value in control["training"].items():
        if key not in {"run_name", "output_root"}:
            assert intervention["training"][key] == value
    assert control["training"]["supervise_eos"] is False
    assert estimate_optimizer_steps(3500, 10, 50, 36.0) == 252


def test_four_form_intersections_include_all_eight_cells() -> None:
    rows = []
    for fact_id, ranks in {"f1": [1] * 8, "f2": [1] * 7 + [2]}.items():
        index = 0
        for form_id in FORM_IDS:
            for scaffold_id in ("direct", "qa"):
                rows.append({"fact_id": fact_id, "relation": "born_in", "form_id": form_id, "scaffold_id": scaffold_id, "correct_rank_mean": ranks[index]})
                index += 1
    per_scaffold = _intersection_rows(rows)
    assert {row["all_form_intersection"] for row in per_scaffold} == {1, 2}
    assert _all_cell_intersection_rows(rows) == [
        {"relation": "born_in", "n": 2, "required_cells": 8, "all_cell_intersection": 1}
    ]
