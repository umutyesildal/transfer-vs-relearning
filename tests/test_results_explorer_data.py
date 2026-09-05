"""Focused contract tests for the static M0/M1/M2 results-explorer data layer."""

from __future__ import annotations

import json
import math
from pathlib import Path

from scripts.evaluation import build_results_explorer_data as builder


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_manifest_has_frozen_shape_and_source_hash_closure() -> None:
    manifest = builder.build_manifest(REPO_ROOT)

    assert manifest["schema_version"] == "results-explorer-data-v1"
    assert manifest["contract"]["m2_arms_are_parallel_siblings"] is True
    assert manifest["overview"]["completion"] == {
        "m1_evaluation_states": {"observed": 111, "expected": 111},
        "m2_evaluation_states": {"observed": 63, "expected": 63},
        "m2_training_checkpoints": {"observed": 60, "expected": 60},
    }
    assert len(manifest["provenance"]["sources"]) == 9
    for source in manifest["provenance"]["sources"]:
        assert source["sha256"] == builder.EXPECTED_SOURCE_SHA256[source["id"]]
    assert manifest["input_manifest_sha256"] == "647aa45c4f1fb170c40a62d5ebee81ca3cd404738851d3dcab99f4374522be22"
    assert manifest["manifest_sha256"] == manifest["input_manifest_sha256"]
    assert manifest["provenance"]["input_manifest_sha256"] == manifest["input_manifest_sha256"]


def test_corrected_all_subject_estimands_are_golden_values() -> None:
    manifest = builder.build_manifest(REPO_ROOT)
    observed = {
        (row["model"], row["contrast"]): (row["estimate"], row["ci95_low"], row["ci95_high"])
        for row in manifest["estimands"]
    }
    assert observed == {
        ("olmo", "transfer"): (-0.141, -0.16075, -0.1205),
        ("olmo", "relearning"): (0.02, 0.015, 0.0255),
        ("qwen", "transfer"): (-0.307, -0.33675, -0.2775),
        ("qwen", "relearning"): (0.0435, 0.0295, 0.05775),
        ("smollm", "transfer"): (-0.16175, -0.18525, -0.1385),
        ("smollm", "relearning"): (0.0035, 0.0005, 0.0065),
    }
    assert all(math.isclose(row["endpoint_delta"], row["estimate"], abs_tol=1e-12) for row in manifest["estimands"])


def test_canonical_gate_matrix_and_missing_values() -> None:
    manifest = builder.build_manifest(REPO_ROOT)
    expected = {
        "olmo": [True, True, True, True, False],
        "qwen": [True, True, True, True, False],
        "smollm": [False, True, True, True, False],
    }
    by_model: dict[str, list[bool]] = {model: [] for model in expected}
    for row in manifest["gates"]:
        by_model[row["model"]].append(row["passed"])
    assert by_model == expected
    assert manifest["overview"]["primary_model_selected"] is False
    assert [row["all_primary_gates_pass"] for row in manifest["primary_gate_summary"]] == [False, False, False]
    qwen_pile = next(row for row in manifest["m0_metrics"] if row["model"] == "qwen" and row["metric"] == "pile_bpb")
    assert qwen_pile["value"] is None
    assert qwen_pile["status"] == "pending"


def test_row_counts_and_deterministic_build(tmp_path: Path) -> None:
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"
    builder.build(REPO_ROOT, first_path)
    builder.build(REPO_ROOT, second_path)
    assert first_path.read_bytes() == second_path.read_bytes()
    payload = json.loads(first_path.read_text(encoding="utf-8"))
    assert len(payload["trajectories"]["m1"]) == 111
    assert len(payload["trajectories"]["m2"]) == 60
    assert len(payload["state_endpoints"]) == 27
    assert len(payload["breakdowns"]) == 66
    assert len(payload["bootstrap"]) == 39
