from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.corpora.vngrs.d0_audit import D0Document
from transfer_vs_relearning.corpora.vngrs.d0_oscar_recovery import run_oscar_audit_recovery


ROOT = Path(__file__).resolve().parents[1]


def documents(*, contamination: bool = False) -> list[D0Document]:
    rows = []
    for index in range(10_020):
        corpus = "OSCAR" if index < 10_010 else "mC4"
        text = f"Uzun ve temiz Türkçe deneme belgesi numarası {index}."
        if contamination and index == 4:
            text += " Gizli Yüzey"
        rows.append(D0Document(f"{index:064x}", "data/train-00004-of-00284.parquet", corpus, text))
    return rows


def loader(rows: list[D0Document]):
    def load(*_args, execution_enabled: bool = False, **_kwargs) -> list[D0Document]:
        assert execution_enabled
        return rows
    return load


def test_oscar_recovery_is_disabled_without_writes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="disabled"):
        run_oscar_audit_recovery(tmp_path / "source", tmp_path / "output", [], synthetic_surfaces={})
    assert not (tmp_path / "output").exists()


def test_oscar_recovery_preserves_labels_when_exact_candidate_is_too_small(tmp_path: Path) -> None:
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="absent or too small"):
        run_oscar_audit_recovery(
            tmp_path / "source", output, [],
            synthetic_surfaces={"absent": "Bu yüzey yoktur"},
            execution_enabled=True,
            document_loader=loader(documents()[:100]),
        )
    assert (output / "reports/corpus_label_inventory.json").is_file()
    assert json.loads((output / "control/d0_failure.json").read_text())["status"] == "BLOCKED"


def test_oscar_recovery_persists_exact_label_inventory_and_audit(tmp_path: Path) -> None:
    output = tmp_path / "output"
    result = run_oscar_audit_recovery(
        tmp_path / "source", output, [],
        synthetic_surfaces={"absent": "Bu yüzey yoktur"},
        execution_enabled=True,
        document_loader=loader(documents()),
    )
    assert result["status"] == "OSCAR_AUDIT_COMPLETE"
    assert result["selected_document_count"] == 10_010
    inventory = json.loads((output / "reports/corpus_label_inventory.json").read_text())
    assert inventory["exact_labels"] == [
        {"documents": 10_010, "label": "OSCAR", "utf8_bytes": 529_430},
        {"documents": 10, "label": "mC4", "utf8_bytes": 540},
    ]
    audit = json.loads((output / "reports/lightweight_audit.json").read_text())
    assert audit["status"] == "AUDIT_COMPLETE"
    assert json.loads((output / "control/recovery_state.json").read_text()) == result
    assert result["split_created"] is result["human_review_packet_created"] is False


def test_oscar_recovery_records_blocking_cause_without_opening_later_stages(tmp_path: Path) -> None:
    output = tmp_path / "output"
    result = run_oscar_audit_recovery(
        tmp_path / "source", output, [],
        synthetic_surfaces={"fact-1": "Gizli Yüzey"},
        execution_enabled=True,
        document_loader=loader(documents(contamination=True)),
    )
    assert result["status"] == "BLOCKED"
    report = json.loads((output / "reports/lightweight_audit.json").read_text())
    assert report["synthetic_contamination"]["exact_hit_count"] == 1
    assert report["synthetic_contamination"]["unicode_normalized_hit_count"] == 1
    assert json.loads((output / "control/recovery_state.json").read_text())["status"] == "BLOCKED"
    assert not (output / "control/phase1_state.json").exists()


def test_oscar_recovery_contract_is_single_diagnostic_cpu_pass() -> None:
    contract = ROOT / "documentation/contracts/corpora/vngrs-m2-oscar-audit-recovery-v1.md"
    config = yaml.safe_load(
        (ROOT / "configs/corpora/vngrs_m2_oscar_audit_recovery_v1.yaml").read_text()
    )
    runner = (ROOT / "scripts/corpora/run_vngrs_m2_oscar_audit_recovery_v1.py").read_text()
    submitter = (ROOT / "scripts/corpora/submit_vngrs_m2_oscar_audit_recovery_v1.sh").read_text()
    slurm = (ROOT / "slurm/m2/audit_vngrs_m2_oscar_d0_v1.slurm").read_text()
    assert contract.is_file()
    assert config["status"] == "frozen_unexecuted"
    assert config["selection"] == {
        "field": "corpus",
        "operator": "exact_string_equality",
        "candidate_value": "OSCAR",
        "minimum_documents": 10001,
        "fail_if_absent_or_too_small": True,
    }
    assert config["source"]["access"] == "read_only"
    assert config["authority"]["corpus_download_or_copy"] is False
    assert "--test-only" in submitter
    assert "PYTHONDONTWRITEBYTECODE=1" in slurm
    assert "train_clm" not in runner + submitter + slurm
    assert "requests" not in runner and "http" not in runner.casefold()
