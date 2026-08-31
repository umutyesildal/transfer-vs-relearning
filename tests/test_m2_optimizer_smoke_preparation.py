from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.m2.validate_m2_fact_review_decisions import validate


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SHA = "7" * 64


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_fact_review_validator_requires_exact_250_usable_rows(tmp_path: Path) -> None:
    packet = tmp_path / "packet.jsonl"
    decisions = tmp_path / "decisions.jsonl"
    packet_rows = [
        {"index": index, "fact_id": f"fact-{index:03d}", "relation": "profession", "text": "x"}
        for index in range(250)
    ]
    decision_rows = [
        {
            "schema_version": 1,
            "fact_id": row["fact_id"],
            "fact_registry_sha256": REGISTRY_SHA,
            "verdict": "usable",
            "reviewer": "human-reviewer",
            "notes": None,
        }
        for row in packet_rows
    ]
    _write_jsonl(packet, packet_rows)
    _write_jsonl(decisions, decision_rows)
    result = validate(packet, decisions, expected_registry_sha256=REGISTRY_SHA)
    assert result["status"] == "M2_FACT_REVIEW_PASS"
    assert result["verdicts"] == {"usable": 250}
    assert result["optimizer_smoke_authorized"] is False
    assert result["ready_to_train"] is False


def test_fact_review_validator_blocks_issue_and_rejects_missing(tmp_path: Path) -> None:
    packet = tmp_path / "packet.jsonl"
    decisions = tmp_path / "decisions.jsonl"
    packet_rows = [{"index": index, "fact_id": f"fact-{index:03d}"} for index in range(250)]
    decision_rows = [
        {
            "schema_version": 1,
            "fact_id": row["fact_id"],
            "fact_registry_sha256": REGISTRY_SHA,
            "verdict": "issue" if index == 0 else "usable",
            "reviewer": "human-reviewer",
        }
        for index, row in enumerate(packet_rows)
    ]
    _write_jsonl(packet, packet_rows)
    _write_jsonl(decisions, decision_rows)
    assert validate(packet, decisions, expected_registry_sha256=REGISTRY_SHA)["status"] == "M2_FACT_REVIEW_BLOCKED"
    _write_jsonl(decisions, decision_rows[:-1])
    with pytest.raises(ValueError, match="250 rows"):
        validate(packet, decisions, expected_registry_sha256=REGISTRY_SHA)


def test_optimizer_smoke_is_separate_bounded_and_non_scientific() -> None:
    runner = (ROOT / "scripts/m2/smoke_three_model_oscar_m2_optimizer.py").read_text()
    slurm = ROOT / "slurm/m2/smoke_three_model_oscar_m2_optimizer_only.slurm"
    submitter = ROOT / "scripts/m2/submit_three_model_oscar_m2_optimizer_smoke_only.sh"
    subprocess.run(["bash", "-n", str(slurm)], check=True)
    subprocess.run(["bash", "-n", str(submitter)], check=True)
    slurm_text = slurm.read_text()
    submitter_text = submitter.read_text()
    assert "#SBATCH --array=0-2%1" in slurm_text
    assert "#SBATCH --gres=gpu:a10080gb:1" in slurm_text
    assert "OPTIMIZER_SMOKE_PASS" in runner
    assert "scientific_training\": False" in runner
    assert "checkpoint_written\": False" in runner
    assert "_first_rows(train_path, batch_size * accumulation)" in runner
    assert "M2_FACT_REVIEW_PASS" in submitter_text
    assert "M2_OPTIMIZER_SMOKE_AUTHORIZATION_ACK" in submitter_text
    assert "train_three_model_oscar_m2" not in submitter_text
    assert "finalize_three_model_oscar_m2" not in submitter_text
