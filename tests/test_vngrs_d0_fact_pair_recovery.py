from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.corpora.vngrs.d0_audit import D0Document, SyntheticFactSurface
from transfer_vs_relearning.corpora.vngrs.d0_fact_pair_recovery import run_oscar_fact_pair_recovery


ROOT = Path(__file__).resolve().parents[1]


def _atom_audit() -> dict:
    return {
        "status": "BLOCKED",
        "synthetic_contamination": {
            "pattern_count": 600,
            "exact_hit_count": 439_906,
            "unicode_normalized_hit_count": 935_276,
        },
    }


def _documents(text_at_four: str) -> list[D0Document]:
    rows = []
    for index in range(10_020):
        corpus = "oscar" if index < 10_010 else "mc4"
        text = text_at_four if index == 4 else f"Yeterince uzun Türkçe belge {index}."
        rows.append(D0Document(f"{index:064x}", "data/train-00004-of-00284.parquet", corpus, text))
    return rows


def _loader(rows: list[D0Document]):
    def load(*_args, execution_enabled: bool = False, **_kwargs) -> list[D0Document]:
        assert execution_enabled
        return rows

    return load


FACTS = (
    SyntheticFactSurface("s1", "Çok Nadir Kişi", "f1", "profession", "Mühendis"),
    SyntheticFactSurface("s1", "Çok Nadir Kişi", "f2", "born_in", "Ankara"),
)


def test_object_only_occurrence_is_diagnostic_not_blocking(tmp_path: Path) -> None:
    output = tmp_path / "output"
    result = run_oscar_fact_pair_recovery(
        tmp_path / "source",
        output,
        [],
        synthetic_facts=FACTS,
        predecessor_atom_audit=_atom_audit(),
        predecessor_atom_audit_sha256="a" * 64,
        execution_enabled=True,
        document_loader=_loader(_documents("Ankara ve mühendislik hakkında sıradan bir yazı.")),
    )
    assert result["status"] == "OSCAR_FACT_PAIR_AUDIT_COMPLETE"
    report = json.loads((output / "reports/fact_pair_contamination_audit.json").read_text())
    assert report["predecessor_atom_audit"]["unicode_normalized_hit_count"] == 935_276
    assert report["paired_contamination"]["unicode_normalized_document_fact_pairs"] == 0
    assert report["gate_semantics"]["diagnostic_non_blocking"] == [
        "subject_only_hits",
        "object_only_atom_hits",
    ]


def test_subject_only_occurrence_is_diagnostic_not_blocking(tmp_path: Path) -> None:
    output = tmp_path / "output"
    result = run_oscar_fact_pair_recovery(
        tmp_path / "source",
        output,
        [],
        synthetic_facts=FACTS,
        predecessor_atom_audit=_atom_audit(),
        predecessor_atom_audit_sha256="b" * 64,
        execution_enabled=True,
        document_loader=_loader(_documents("Çok Nadir Kişi hakkında nesnesiz biyografi.")),
    )
    assert result["status"] == "OSCAR_FACT_PAIR_AUDIT_COMPLETE"
    report = json.loads((output / "reports/fact_pair_contamination_audit.json").read_text())
    assert report["subject_only_diagnostic"]["exact_unique_documents"] == 1
    assert report["paired_contamination"]["exact_document_fact_pairs"] == 0


def test_only_the_subjects_own_answer_blocks_and_preserves_relation(tmp_path: Path) -> None:
    output = tmp_path / "output"
    result = run_oscar_fact_pair_recovery(
        tmp_path / "source",
        output,
        [],
        synthetic_facts=FACTS,
        predecessor_atom_audit=_atom_audit(),
        predecessor_atom_audit_sha256="c" * 64,
        execution_enabled=True,
        document_loader=_loader(_documents("çok nadir kişi Ankara doğumludur.")),
    )
    assert result["status"] == "BLOCKED"
    report = json.loads((output / "reports/fact_pair_contamination_audit.json").read_text())
    paired = report["paired_contamination"]
    assert paired["exact_document_fact_pairs"] == 0
    assert paired["unicode_normalized_document_fact_pairs"] == 1
    assert paired["unicode_normalized_by_relation"]["born_in"] == 1
    assert paired["unicode_normalized_examples"][0]["fact_id"] == "f2"
    assert result["split_created"] is result["human_review_packet_created"] is False


def test_fact_pair_recovery_is_disabled_without_writes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="disabled"):
        run_oscar_fact_pair_recovery(
            tmp_path / "source",
            tmp_path / "output",
            [],
            synthetic_facts=FACTS,
            predecessor_atom_audit=_atom_audit(),
            predecessor_atom_audit_sha256="d" * 64,
        )
    assert not (tmp_path / "output").exists()


def test_fact_pair_contract_is_single_offline_cpu_pass() -> None:
    contract = ROOT / "documentation/contracts/corpora/vngrs-m2-oscar-fact-pair-contamination-audit-v1.md"
    config = yaml.safe_load(
        (ROOT / "configs/corpora/vngrs_m2_oscar_fact_pair_audit_v1.yaml").read_text()
    )
    runner = (ROOT / "scripts/corpora/run_vngrs_m2_oscar_fact_pair_audit_v1.py").read_text()
    submitter = (ROOT / "scripts/corpora/submit_vngrs_m2_oscar_fact_pair_audit_v1.sh").read_text()
    slurm = (ROOT / "slurm/m2/audit_vngrs_m2_oscar_fact_pair_v1.slurm").read_text()
    assert contract.is_file()
    assert config["status"] == "frozen_unexecuted"
    assert config["gate"]["diagnostic_non_blocking"] == [
        "subject_only_hits", "object_only_atom_hits"
    ]
    assert config["predecessor_atom_audit"]["access"] == "read_only"
    assert config["output"]["fresh_and_absent_required"] is True
    assert config["authority"]["training"] is False
    assert config["authority"]["split_or_review_packet"] is False
    assert "--test-only" in submitter
    assert "PYTHONDONTWRITEBYTECODE=1" in slurm
    assert "train_clm" not in runner + submitter + slurm
    assert "requests" not in runner and "http" not in runner.casefold()
