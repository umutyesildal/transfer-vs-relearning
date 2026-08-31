from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.m2.validate_m2_fact_review_decisions import validate
from scripts.m2.repair_three_model_oscar_m2_fact_translations import (
    _validate_precreated_root,
    rewrite_m2_b,
)


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
    registry = tmp_path / "registry.jsonl"
    _write_jsonl(
        registry,
        [
            {"fact_id": row["fact_id"], "relation": row["relation"], "text": row["text"]}
            for row in packet_rows
        ],
    )
    import hashlib

    registry_sha = hashlib.sha256(registry.read_bytes()).hexdigest()
    for row in decision_rows:
        row["fact_registry_sha256"] = registry_sha
    _write_jsonl(decisions, decision_rows)
    result = validate(
        packet,
        decisions,
        expected_registry_sha256=registry_sha,
        registry_path=registry,
    )
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


def test_corrected_optimizer_smoke_is_manifest_bound_and_training_closed() -> None:
    runner = (ROOT / "scripts/m2/smoke_three_model_oscar_m2_optimizer.py").read_text()
    config = ROOT / "configs/training/m2_oscar_optimizer_smoke_corrected_v1.yaml"
    slurm = ROOT / "slurm/m2/smoke_three_model_oscar_m2_optimizer_corrected_v1.slurm"
    submitter = ROOT / "scripts/m2/submit_three_model_oscar_m2_optimizer_smoke_corrected_v1.sh"
    subprocess.run(["bash", "-n", str(slurm)], check=True)
    subprocess.run(["bash", "-n", str(submitter)], check=True)
    config_text = config.read_text()
    slurm_text = slurm.read_text()
    submitter_text = submitter.read_text()
    assert "--block-family-manifest" in runner
    assert "Corrected-family artifact drift" in runner
    assert "M2_FACT_TRANSLATION_REPAIR_PASS" in runner
    assert '"model_weights_accessed": True' in runner
    assert '"scientific_training": False' in runner
    assert '"checkpoint_written": False' in runner
    assert "96f9867c857b08bfd784660331d1a354be7d7c6bc39250091f427fdfaa3c6486" in config_text
    assert "#SBATCH --array=0-2%1" in slurm_text
    assert "#SBATCH --gres=gpu:a10080gb:1" in slurm_text
    assert "M2_CORRECTED_OPTIMIZER_SMOKE_AUTHORIZATION_ACK" in submitter_text
    assert "M2_FACT_TRANSLATION_REPAIR_PASS False" in submitter_text
    assert "train_three_model_oscar_m2" not in submitter_text
    assert "finalize_three_model_oscar_m2" not in submitter_text


def test_fact_translation_repair_rewrites_only_corrected_m2_b(tmp_path: Path) -> None:
    m2_a = tmp_path / "m2_a.jsonl"
    old_b = tmp_path / "old_b.jsonl"
    new_b = tmp_path / "new_b.jsonl"
    rows_a = [
        {"block_index": index, "arm": "M2-A", "input_ids": [index, 1, 2, 3], "attention_mask": [1] * 4}
        for index in range(8)
    ]
    rows_b = [{**row, "arm": "M2-B"} for row in rows_a]
    _write_jsonl(m2_a, rows_a)
    _write_jsonl(old_b, rows_b)
    result = rewrite_m2_b(
        m2_a_path=m2_a,
        prior_m2_b_path=old_b,
        destination=new_b,
        schedule={1: ([9, 8], ["fact-1"])},
        block_size=4,
        total_blocks=8,
    )
    repaired = [json.loads(line) for line in new_b.read_text().splitlines()]
    assert result["changed_blocks_vs_predecessor_m2_b"] == 1
    assert repaired[1]["input_ids"] == [9, 8, 2, 3]
    assert repaired[0]["input_ids"] == rows_a[0]["input_ids"]
    assert all(row["arm"] == "M2-B" for row in repaired)


def test_fact_translation_repair_launcher_is_cpu_only_and_training_closed() -> None:
    runner = (ROOT / "scripts/m2/repair_three_model_oscar_m2_fact_translations.py").read_text()
    slurm = ROOT / "slurm/corpora/vngrs_m2_oscar_fact_translation_repair_v1.slurm"
    submitter = ROOT / "scripts/m2/submit_three_model_oscar_m2_fact_translation_repair.sh"
    subprocess.run(["bash", "-n", str(slurm)], check=True)
    subprocess.run(["bash", "-n", str(submitter)], check=True)
    assert "load_verified_parquet_documents" not in runner
    assert "model_weights_accessed\": False" in runner
    assert "training_opened\": False" in runner
    assert "#SBATCH --partition=cpu" in slurm.read_text()
    assert "M2_FACT_TRANSLATION_REPAIR_AUTHORIZATION_ACK" in submitter.read_text()


def test_fact_translation_repair_v1a_changes_only_partition_and_fresh_root() -> None:
    config = ROOT / "configs/corpora/vngrs_m2_oscar_fact_translation_repair_v1a.yaml"
    slurm = ROOT / "slurm/corpora/vngrs_m2_oscar_fact_translation_repair_v1a.slurm"
    submitter = ROOT / "scripts/m2/submit_three_model_oscar_m2_fact_translation_repair_v1a.sh"
    subprocess.run(["bash", "-n", str(slurm)], check=True)
    subprocess.run(["bash", "-n", str(submitter)], check=True)
    config_text = config.read_text()
    slurm_text = slurm.read_text()
    submitter_text = submitter.read_text()
    assert "partition: longrun" in config_text
    assert "vngrs_m2_oscar_fact_translation_repair_retry_v1" in config_text
    assert "#SBATCH --partition=longrun" in slurm_text
    assert "#SBATCH --cpus-per-task=4" in slurm_text
    assert "#SBATCH --mem=32G" in slurm_text
    assert "vngrs_m2_oscar_fact_translation_repair_retry_v1" in slurm_text
    assert "M2_FACT_TRANSLATION_REPAIR_V1A_AUTHORIZATION_ACK" in submitter_text
    assert "c65c87e404e287c7925752e7ddd250f7795517c2d2f2d5aa22fdf7ee27d29556" in submitter_text
    assert "vngrs_m2_oscar_fact_translation_repair_v1/control/submission_state.json" in submitter_text
    assert "train_three_model_oscar_m2" not in submitter_text
    assert "smoke_three_model_oscar_m2_optimizer" not in submitter_text


def test_fact_translation_repair_allows_only_runtime_tmp_before_operator(tmp_path: Path) -> None:
    root = tmp_path / "repair"
    runtime_tmp = root / "tmp" / "conda-runtime-file"
    runtime_tmp.parent.mkdir(parents=True)
    runtime_tmp.write_text("runtime-only", encoding="utf-8")
    _validate_precreated_root(root)
    unexpected = root / "blocks" / "unexpected.jsonl"
    unexpected.parent.mkdir(parents=True)
    unexpected.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unexpected pre-run"):
        _validate_precreated_root(root)
