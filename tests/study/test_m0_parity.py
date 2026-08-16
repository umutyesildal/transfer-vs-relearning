from __future__ import annotations

import importlib.util
import json
import math
import re
from pathlib import Path

import pytest

from transfer_vs_relearning.study.m0_parity import (
    HEADING_TASK,
    build_parity_plan,
    canonical_wikitext_target,
    markdown_headings,
    validate_heading_sensitivity,
    validate_turblimp_macro,
    validate_wikitext_canonical,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/evaluation/m0_olmo_eval_v1_parity_v1.yaml"
OVERLAY = (
    ROOT
    / "configs/evaluation/task_overlays/wikitext_heading_sensitivity_v1/preprocess_wikitext_heading.py"
)
SUBTASKS = [
    "turblimp_anaphor_agreement",
    "turblimp_argument_structure_ditransitive",
    "turblimp_argument_structure_transitive",
    "turblimp_binding",
    "turblimp_determiners",
    "turblimp_ellipsis",
    "turblimp_irregular_forms",
    "turblimp_island_effects",
    "turblimp_nominalization",
    "turblimp_npi_licensing",
    "turblimp_passives",
    "turblimp_quantifiers",
    "turblimp_relative_clauses",
    "turblimp_scrambling",
    "turblimp_subject_agreement",
    "turblimp_suspended_affixation",
]


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _wiki_fixture(tmp_path: Path, *, heading: bool = False) -> tuple[Path, Path, list[dict]]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    docs = [
        {"page": " = First heading = \nToken @-@ one . "},
        {"page": " == Second heading == \nAnother token , here . "},
    ]
    loglikelihoods = [-8.0, -11.0]
    rows = []
    for doc_id, (doc, loglikelihood) in enumerate(zip(docs, loglikelihoods)):
        canonical = canonical_wikitext_target(doc)
        target = markdown_headings(canonical) if heading else canonical
        denominator_text = target if heading else doc["page"]
        words = len(re.split(r"\s+", denominator_text))
        byte_count = len(denominator_text.encode("utf-8"))
        rows.append(
            {
                "doc_id": doc_id,
                "doc_hash": f"doc-{doc_id}",
                "doc": doc,
                "target": target,
                "word_perplexity": [loglikelihood, words],
                "byte_perplexity": [loglikelihood, byte_count],
                "bits_per_byte": [loglikelihood, byte_count],
            }
        )
    loglikelihood = sum(loglikelihoods)
    words = sum(row["word_perplexity"][1] for row in rows)
    byte_count = sum(row["byte_perplexity"][1] for row in rows)
    task = HEADING_TASK if heading else "wikitext"
    result = {
        "results": {
            task: {
                "sample_len": 2,
                "word_perplexity,none": math.exp(-loglikelihood / words),
                "byte_perplexity,none": math.exp(-loglikelihood / byte_count),
                "bits_per_byte,none": -loglikelihood / (byte_count * math.log(2)),
            }
        },
        "n-samples": {task: {"effective": 2, "original": 62}},
    }
    result_path = tmp_path / f"results_{task}_fixture.json"
    sample_path = tmp_path / f"samples_{task}_2026-fixture.jsonl"
    write_json(result_path, result)
    _write_jsonl(sample_path, rows)
    return result_path, sample_path, rows


def test_overlay_and_validator_share_exact_heading_transform() -> None:
    spec = importlib.util.spec_from_file_location("wikitext_heading_overlay", OVERLAY)
    assert spec and spec.loader
    overlay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(overlay)
    doc = {"page": " = One = \n == Two == \nordinary\n"}
    canonical = canonical_wikitext_target(doc)
    assert overlay.canonical_wikitext_target(doc) == canonical
    assert overlay.markdown_wikitext_target(doc) == markdown_headings(canonical)
    assert markdown_headings(canonical).splitlines()[:2] == ["# One", "## Two"]


def test_wikitext_recomputes_exact_counts_and_rolling_aggregates(tmp_path: Path) -> None:
    result_path, sample_path, _ = _wiki_fixture(tmp_path)
    validation = validate_wikitext_canonical(
        result_path,
        sample_path,
        tolerance=1.0e-12,
        expected_sample_count=2,
    )
    assert validation["status"] == "pass"
    assert validation["blockers"] == []
    assert validation["recomputed"]["word_count"] > 0
    assert validation["heading_counts"] == [1, 1]


def test_turblimp_recomputes_byte_normalized_16_subtask_macro(tmp_path: Path) -> None:
    sample_paths = []
    results: dict[str, dict] = {}
    for task in SUBTASKS:
        rows = [
            {
                "doc": {"sentence_good": "iyi cümle", "sentence_bad": "kötü cümle"},
                "filtered_resps": [["-1.0", "False"], ["-3.0", "False"]],
                "acc": 1.0,
                "acc_norm": 1.0,
            },
            {
                "doc": {"sentence_good": "iyi cümle", "sentence_bad": "kötü cümle"},
                "filtered_resps": [["-4.0", "False"], ["-1.0", "False"]],
                "acc": 0.0,
                "acc_norm": 0.0,
            },
        ]
        path = tmp_path / f"samples_{task}_2026-fixture.jsonl"
        _write_jsonl(path, rows)
        sample_paths.append(path)
        results[task] = {"sample_len": 2, "acc,none": 0.5, "acc_norm,none": 0.5}
    results["turblimp_core"] = {"sample_len": 32, "acc_norm,none": 0.5}
    result_path = tmp_path / "results_turblimp_fixture.json"
    write_json(
        result_path,
        {
            "group_subtasks": {"turblimp_core": SUBTASKS},
            "results": results,
        },
    )
    group_path = tmp_path / "turblimp_group.yaml"
    group_path.write_text(
        "group: turblimp_core\n"
        "aggregate_metric_list:\n  - metric: acc\n"
        "aggregate_metric_list:\n  - metric: acc_norm\n",
        encoding="utf-8",
    )
    validation = validate_turblimp_macro(
        result_path,
        sample_paths,
        subtask_ids=SUBTASKS,
        tolerance=1.0e-12,
        expected_samples_per_subtask=2,
        group_yaml_path=group_path,
    )
    assert validation["status"] == "pass"
    assert validation["recomputed_macro_acc_norm"] == 0.5
    assert validation["subtask_count"] == 16


def test_heading_sensitivity_requires_same_documents_but_no_numeric_delta_gate(
    tmp_path: Path,
) -> None:
    plan = build_parity_plan(CONFIG, repo_root=ROOT)
    canonical_result, canonical_samples, _ = _wiki_fixture(tmp_path / "canonical")
    heading_root = tmp_path / "parity" / "heading"
    heading_root.mkdir(parents=True)
    heading_result, heading_samples, _ = _wiki_fixture(heading_root, heading=True)
    artifacts = []
    for path in (heading_result, heading_samples):
        artifacts.append(
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        )
    write_json(
        heading_root / "heading_run_result.json",
        {"status": "complete", "returncode": 0, "artifacts": artifacts},
    )
    structural = {
        "wikitext": {
            "sample_path": str(canonical_samples),
            "recomputed": validate_wikitext_canonical(
                canonical_result,
                canonical_samples,
                tolerance=1.0e-12,
                expected_sample_count=2,
            )["recomputed"],
        }
    }
    validation = validate_heading_sensitivity(plan, tmp_path / "parity", structural)
    assert validation["status"] == "pass"
    assert validation["role"] == "descriptive_sensitivity_only_no_numeric_gate"
    assert set(validation["markdown_minus_canonical"]) == {
        "word_perplexity",
        "byte_perplexity",
        "bits_per_byte",
    }


def test_prepared_plan_freezes_exact_16_subtasks_and_test_only_scope() -> None:
    plan = build_parity_plan(CONFIG, repo_root=ROOT)
    assert plan["status"] == "prepared"
    assert plan["execution_authorized"] is False
    assert plan["turblimp"]["subtask_ids"] == SUBTASKS
    assert plan["run_classification"] == "test_only_non_scientific"


def test_submitter_launches_heading_and_afterany_finalizer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    entrypoint_path = ROOT / "scripts/study/run_m0_parity.py"
    spec = importlib.util.spec_from_file_location("m0_parity_entrypoint", entrypoint_path)
    assert spec and spec.loader
    entrypoint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entrypoint)
    plan = build_parity_plan(CONFIG, repo_root=ROOT)
    output_root = tmp_path / "parity"
    (output_root / "logs").mkdir(parents=True)
    submissions: list[list[str]] = []

    monkeypatch.setattr(
        entrypoint,
        "run_structural_parity",
        lambda _plan, _root: {"status": "pass"},
    )
    monkeypatch.setattr(
        entrypoint,
        "_probe_route",
        lambda _plan: {
            "route": plan["slurm"]["gpu_route"],
            "eligible": True,
            "returncode": 0,
            "estimated_start": "2026-08-16T20:00:00",
            "probe_output": "ok",
        },
    )

    def fake_submit(argv: list[str]) -> str:
        submissions.append(argv)
        return str(8000 + len(submissions))

    monkeypatch.setattr(entrypoint, "_submit", fake_submit)
    payload = entrypoint.submit_parity(
        plan,
        config_path=CONFIG,
        repo_root=ROOT,
        output_root=output_root,
    )
    assert payload["heading_job_id"] == "8001"
    assert payload["finalizer_job_id"] == "8002"
    assert any("--gres=gpu:v10032gb:1" == part for part in submissions[0])
    assert any("--dependency=afterany:8001" == part for part in submissions[1])
