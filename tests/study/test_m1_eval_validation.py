from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from transfer_vs_relearning.study.m1_eval_validation import (
    FACTUAL_SUMMARY_COMPLETE_STATUSES,
    derive_cheap_factual_from_full,
    validate_factual_output,
)

FULL_COUNT = 12_000
CHEAP_COUNT = 1_500
IDENTITY_FIELDS = (
    "fact_id",
    "subject_id",
    "direction",
    "relation",
    "form_id",
    "scaffold_id",
    "rendered_prompt",
    "expected_answer",
)


def _source_row(index: int) -> dict[str, str]:
    return {
        "probe_id": f"f{index:05d}",
        "fact_id": f"fact{index % 500:03d}",
        "subject_id": f"subj{index % 100:03d}",
        "direction": "en2tr" if index % 2 else "tr2en",
        "relation": "born_in" if index % 3 else "capital_of",
        "form_id": f"form{index % 4}",
        "scaffold_id": f"scaf{index % 5}",
        "rendered_prompt": f"prompt {index}",
        "expected_answer": f"answer {index}",
        "correct_rank_mean": str(index % 7),
    }


def _write_factual_root(root: Path, status: str, count: int) -> None:
    root.mkdir(parents=True)
    rows = [_source_row(index) for index in range(count)]
    with (root / "hard_suite_per_fact.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {"status": status, "probes": count}
    (root / "summary.json").write_text(json.dumps(summary), encoding="utf-8")


def _write_cheap_registry(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["probe_id", *IDENTITY_FIELDS]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index in range(CHEAP_COUNT):
            row = _source_row(index)
            writer.writerow({"probe_id": f"cheap_{row['probe_id']}", **{f: row[f] for f in IDENTITY_FIELDS}})


@pytest.fixture()
def cheap_registry(tmp_path: Path) -> Path:
    path = tmp_path / "cheap_registry.csv"
    _write_cheap_registry(path)
    return path


def test_derive_cheap_from_full_passes_and_validates(tmp_path: Path, cheap_registry: Path) -> None:
    full_root = tmp_path / "full"
    _write_factual_root(full_root, "completed", FULL_COUNT)
    cheap_root = tmp_path / "cheap"
    result = derive_cheap_factual_from_full(
        full_root=full_root,
        cheap_root=cheap_root,
        cheap_registry=cheap_registry,
        cheap_registry_sha256=__import__("hashlib").sha256(cheap_registry.read_bytes()).hexdigest(),
    )
    assert result["status"] == "complete"
    assert result["probe_count"] == CHEAP_COUNT
    derived_summary = json.loads((cheap_root / "summary.json").read_text(encoding="utf-8"))
    assert derived_summary["status"] == "completed_derived_from_full_without_rescoring"
    assert derived_summary["probes"] == CHEAP_COUNT


def test_validate_accepts_both_frozen_complete_statuses(tmp_path: Path) -> None:
    for status in FACTUAL_SUMMARY_COMPLETE_STATUSES:
        root = tmp_path / status
        _write_factual_root(root, status, CHEAP_COUNT)
        assert validate_factual_output(root, CHEAP_COUNT)["status"] == "complete"


def test_validate_rejects_unknown_status(tmp_path: Path) -> None:
    root = tmp_path / "bad"
    _write_factual_root(root, "running", CHEAP_COUNT)
    with pytest.raises(ValueError, match="Factual output is incomplete"):
        validate_factual_output(root, CHEAP_COUNT)


def test_derive_rejects_identity_mismatch(tmp_path: Path, cheap_registry: Path) -> None:
    full_root = tmp_path / "full"
    _write_factual_root(full_root, "completed", FULL_COUNT)
    tampered = cheap_registry.read_text(encoding="utf-8").replace(
        "subj003", "subj999"
    )
    cheap_registry.write_text(tampered, encoding="utf-8")
    with pytest.raises(ValueError, match="identity mismatch"):
        derive_cheap_factual_from_full(
            full_root=full_root,
            cheap_root=tmp_path / "cheap",
            cheap_registry=cheap_registry,
            cheap_registry_sha256=__import__("hashlib").sha256(cheap_registry.read_bytes()).hexdigest(),
        )
