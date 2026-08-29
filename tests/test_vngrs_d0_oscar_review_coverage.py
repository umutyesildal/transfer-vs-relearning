from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.corpora.vngrs.d0_audit import D0Document
from transfer_vs_relearning.corpora.vngrs.d0_oscar_review_coverage import (
    run_oscar_review_coverage_repair,
)
from transfer_vs_relearning.corpora.vngrs.d0_oscar_split_review import (
    run_oscar_split_review_handoff,
)
from transfer_vs_relearning.corpora.vngrs.metadata import (
    FROZEN_SELECTED_SHARD_PATHS,
    canonical_json_sha256,
)


ROOT = Path(__file__).resolve().parents[1]


def _documents() -> list[D0Document]:
    return [
        D0Document(
            f"doc-{index:04d}",
            FROZEN_SELECTED_SHARD_PATHS[index % 32],
            "oscar",
            f"İnsan incelemesi için belge {index}." + ("\u0085devam" if index == 3 else ""),
        )
        for index in range(128)
    ]


def _loader(rows: list[D0Document]):
    def load(*_args, execution_enabled: bool = False, **_kwargs) -> list[D0Document]:
        assert execution_enabled
        return rows

    return load


def _split_handoff(tmp_path: Path, rows: list[D0Document]) -> tuple[Path, dict]:
    state = {
        "status": "OSCAR_FACT_PAIR_AUDIT_COMPLETE",
        "selected_document_count": len(rows),
        "selected_document_ids_sha256": canonical_json_sha256(
            sorted(row.stable_document_id for row in rows)
        ),
    }
    audit = {
        "status": "AUDIT_COMPLETE",
        "invalid_encoding_documents": 0,
        "paired_contamination": {
            "exact_document_fact_pairs": 0,
            "unicode_normalized_document_fact_pairs": 0,
        },
    }
    root = tmp_path / "split"
    result = run_oscar_split_review_handoff(
        tmp_path / "source",
        root,
        [],
        predecessor_state=state,
        predecessor_audit=audit,
        predecessor_state_sha256="a" * 64,
        predecessor_audit_sha256="b" * 64,
        heldout_documents=16,
        review_documents=8,
        execution_enabled=True,
        document_loader=_loader(rows),
    )
    return root, result


def test_coverage_repair_validates_split_and_covers_all_nonempty_quartiles(tmp_path: Path) -> None:
    rows = _documents()
    prior, predecessor = _split_handoff(tmp_path, rows)
    output = tmp_path / "coverage"
    result = run_oscar_review_coverage_repair(
        tmp_path / "source",
        prior,
        output,
        [],
        predecessor_state=predecessor,
        predecessor_final=predecessor["final_audit"],
        predecessor_state_sha256="c" * 64,
        predecessor_final_sha256="d" * 64,
        review_documents=8,
        execution_enabled=True,
        document_loader=_loader(rows),
    )
    assert result["status"] == "AWAITING_HUMAN_REVIEW"
    assert result["split_rewritten"] is False
    assert set(result["new_sample_strata"]) == {"oscar|q0", "oscar|q1", "oscar|q2", "oscar|q3"}
    assert all(value >= 1 for value in result["new_sample_strata"].values())
    assert result["old_packet_status"].startswith("SUPERSEDED")
    packet_path = output / "reports/human_review_packet.jsonl"
    with packet_path.open(encoding="utf-8") as handle:
        packet = [json.loads(line) for line in handle]
    assert len(packet) == 8
    assert (output / "control/final_audit.json").is_file()
    assert not (output / "splits").exists()


def test_coverage_repair_is_disabled_without_writes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="disabled"):
        run_oscar_review_coverage_repair(
            tmp_path / "source",
            tmp_path / "prior",
            tmp_path / "output",
            [],
            predecessor_state={},
            predecessor_final={},
            predecessor_state_sha256="a" * 64,
            predecessor_final_sha256="b" * 64,
        )
    assert not (tmp_path / "output").exists()


def test_coverage_contract_is_one_offline_preverdict_cpu_pass() -> None:
    contract = ROOT / "documentation/contracts/corpora/vngrs-m2-oscar-review-coverage-repair-v1.md"
    config = yaml.safe_load(
        (ROOT / "configs/corpora/vngrs_m2_oscar_review_coverage_v1.yaml").read_text()
    )
    runner = (ROOT / "scripts/corpora/run_vngrs_m2_oscar_review_coverage_v1.py").read_text()
    submitter = (
        ROOT / "scripts/corpora/submit_vngrs_m2_oscar_review_coverage_v1.sh"
    ).read_text()
    slurm = (ROOT / "slurm/m2/review_coverage_vngrs_m2_oscar_v1.slurm").read_text()
    assert contract.is_file()
    assert config["status"] == "frozen_unexecuted"
    assert config["predecessor"]["access"] == "read_only"
    assert config["review"]["sample_documents"] == 64
    assert config["review"]["allocation"] == "one_per_nonempty_stratum_then_largest_remainder"
    assert config["output"]["split_rewritten"] is False
    assert config["output"]["maximum_success_bytes"] == 2 * 1024**2
    assert config["authority"]["human_verdict_entry"] is False
    assert config["authority"]["phase2"] is False
    assert config["authority"]["training"] is False
    assert "--test-only" in submitter
    assert "PYTHONDONTWRITEBYTECODE=1" in slurm
    assert "train_clm" not in runner + submitter + slurm
    assert "requests" not in runner and "http" not in runner.casefold()
