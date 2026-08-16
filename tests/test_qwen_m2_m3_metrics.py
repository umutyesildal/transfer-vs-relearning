from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from transfer_vs_relearning.metrics.qwen_m2_m3 import (
    branch_interaction_rows,
    paired_state_contrast_rows,
    robust_paired_contrast_rows,
    robust_state_accuracy_rows,
    robust_unit_rows,
    state_accuracy_rows,
    validate_matched_state_rows,
)
from transfer_vs_relearning.utils.io import write_csv


def _rows_for_state(*, correct_branch_b: bool) -> list[dict[str, str]]:
    rows = []
    for subject_id, branch in (("S1", "A"), ("S2", "B")):
        for form_id in ("form_a", "form_b", "form_c", "form_d"):
            for scaffold_id in ("direct", "qa"):
                rows.append(
                    {
                        "probe_id": f"{subject_id}_profession_en_to_en_{form_id}_{scaffold_id}",
                        "subject_id": subject_id,
                        "fact_id": f"{subject_id}_profession",
                        "direction": "en_to_en",
                        "relation": "profession",
                        "form_id": form_id,
                        "scaffold_id": scaffold_id,
                        "branch_group": branch,
                        "frequency_bucket": "low",
                        "name_type": "neutral",
                        "name_rarity_bucket": "rare",
                        "popularity_bucket": "low",
                        "correct_rank_mean": "1" if branch == "B" and correct_branch_b else "2",
                    }
                )
    return rows


def _states() -> tuple[dict[str, list[dict[str, str]]], dict[str, dict[str, str]]]:
    rows_by_state = {}
    metadata = {}
    for seed in ("42", "43"):
        for arm in ("m1", "m2_clean", "m3_fact"):
            state_id = f"{arm}_seed{seed}"
            rows_by_state[state_id] = _rows_for_state(correct_branch_b=arm == "m3_fact")
            metadata[state_id] = {"seed": seed, "arm": arm}
    return rows_by_state, metadata


def test_matched_state_validation_rejects_probe_or_metadata_drift() -> None:
    rows_by_state, _ = _states()
    report = validate_matched_state_rows(rows_by_state)
    assert report["probe_count_per_state"] == 16
    changed = {key: list(rows) for key, rows in rows_by_state.items()}
    changed["m3_fact_seed42"] = changed["m3_fact_seed42"][:-1]
    with pytest.raises(ValueError, match="Probe registry mismatch"):
        validate_matched_state_rows(changed)


def test_subject_paired_contrasts_and_branch_interaction_are_precomputed() -> None:
    rows_by_state, metadata = _states()
    contrasts = paired_state_contrast_rows(rows_by_state, metadata, bootstrap_samples=100, seed=3)
    m3_m2 = next(
        row
        for row in contrasts
        if row["seed"] == "42" and row["dimension"] == "global" and row["comparison"] == "m3_minus_m2"
    )
    assert m3_m2["difference_first_minus_second"] == pytest.approx(0.5)
    interactions = branch_interaction_rows(rows_by_state, metadata, bootstrap_samples=100, seed=3)
    global_interaction = next(row for row in interactions if row["seed"] == "42" and row["dimension"] == "global")
    assert global_interaction["branch_a_change"] == pytest.approx(0.0)
    assert global_interaction["branch_b_change"] == pytest.approx(1.0)
    assert global_interaction["difference_b_minus_a"] == pytest.approx(1.0)


def test_state_and_robust_outputs_use_subject_bootstrap_units() -> None:
    rows_by_state, metadata = _states()
    accuracy = state_accuracy_rows(rows_by_state, bootstrap_samples=50, seed=4)
    global_row = next(row for row in accuracy if row["state_id"] == "m3_fact_seed42" and row["dimension"] == "global")
    assert global_row["n_subjects"] == 2
    assert global_row["subject_mean_accuracy"] == pytest.approx(0.5)
    assert global_row["bootstrap_unit"] == "subject"
    robust = robust_unit_rows(rows_by_state["m3_fact_seed42"])
    assert len(robust) == 2
    assert all(row["robust"] is (row["branch_group"] == "B") for row in robust)
    robust_summary = robust_state_accuracy_rows(rows_by_state, bootstrap_samples=50, seed=4)
    assert any(row["scope"] == "direction_global" for row in robust_summary)
    robust_contrasts = robust_paired_contrast_rows(rows_by_state, metadata, bootstrap_samples=50, seed=4)
    assert any(row["comparison"] == "m3_minus_m2" for row in robust_contrasts)


def test_robust_rows_require_all_eight_form_scaffold_cells() -> None:
    rows = _rows_for_state(correct_branch_b=True)[:-1]
    with pytest.raises(ValueError, match="Incomplete robust cell set"):
        robust_unit_rows(rows)


def test_analysis_cli_writes_complete_cpu_package(tmp_path: Path) -> None:
    rows_by_state, metadata = _states()
    manifest_states = []
    for state_id, rows in rows_by_state.items():
        path = tmp_path / f"{state_id}.csv"
        write_csv(path, rows)
        manifest_states.append(
            {
                "state_id": state_id,
                "arm": metadata[state_id]["arm"],
                "seed": metadata[state_id]["seed"],
                "path": str(path),
            }
        )
    manifest = tmp_path / "states.json"
    manifest.write_text(json.dumps({"states": manifest_states}), encoding="utf-8")
    output = tmp_path / "analysis"
    root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts/m2/analyze_qwen_m2_m3_results.py"),
            "--results-manifest",
            str(manifest),
            "--output-dir",
            str(output),
            "--bootstrap-samples",
            "25",
        ],
        check=True,
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        capture_output=True,
        text=True,
    )
    assert json.loads((output / "integrity_summary.json").read_text(encoding="utf-8"))["status"] == "passed"
    assert (output / "state_accuracy.csv").is_file()
    assert (output / "paired_state_contrasts.csv").is_file()
    assert (output / "branch_interactions.csv").is_file()
    assert (output / "robust_paired_contrasts.csv").is_file()
