import hashlib
import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.corpora.vngrs import d0_preflight_v2
from transfer_vs_relearning.corpora.vngrs.d0_preflight_v2 import (
    EXPECTED_EVIDENCE,
    V1_FAILURE_EVIDENCE,
    line_inventory_sha256,
    validate_d0_v2_preflight,
    write_d0_v2_preflight_failure,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_three_model_d0_v2.yaml"
CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-three-model-d0-v2.md"
COMMIT = "a" * 40


def _observation() -> dict:
    return {
        "git_commit": COMMIT,
        "clean_task_overlap": True,
        "accepted_evidence": dict(EXPECTED_EVIDENCE),
        "source_registry_sha256": (
            "b1c80bf78ff40de5c02e14f08082a51cc17cc90a9853028eaf866cb63326e41f"
        ),
        "hu_home_exact_bytes": 14_689_423_360,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": 0,
        "v1_failure_evidence": dict(V1_FAILURE_EVIDENCE),
        "storage": {
            "resolved_parent": "/vol/tmp2/yesildau",
            "proposed_root_absent": True,
            "available_bytes": 122_943_170_412_544,
            "available_inodes": 2_284_282_885,
        },
    }


def test_v2_contract_is_a_frozen_unexecuted_scientific_inheritance_overlay() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert CONTRACT.is_file()
    assert config["status"] == "frozen_unexecuted"
    assert config["contract"] == str(CONTRACT.relative_to(ROOT))
    assert config["inheritance"]["inherited_scientific_fields_unchanged"] is True
    assert config["output"]["root"].endswith("vngrs_m2_three_model_d0_v2")
    assert config["authority"]["hu_ssh"] is False
    assert config["authority"]["network_retrieval"] is False
    assert config["authority"]["cleanup_or_deletion"] is False


def test_v2_line_inventory_matches_the_historical_relative_path_size_format() -> None:
    rows = [{"path": "b", "bytes": 2}, {"path": "a", "bytes": 1}]
    expected = hashlib.sha256(b"a 1\nb 2\n").hexdigest()
    assert line_inventory_sha256(rows) == expected
    assert EXPECTED_EVIDENCE["inventory_serialization"] == (
        "relative_path_space_size_lf_utf8"
    )


def test_v2_preflight_passes_only_with_preserved_v1_evidence() -> None:
    result = validate_d0_v2_preflight(_observation(), expected_commit=COMMIT)
    assert result["schema_version"] == 2
    assert result["status"] == "D0_PREFLIGHT_PASS"
    assert result["v1_failure_evidence"] == V1_FAILURE_EVIDENCE
    assert result["ready_to_train"] is False
    row = _observation()
    row["v1_failure_evidence"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="V1C"):
        validate_d0_v2_preflight(row, expected_commit=COMMIT)


def test_v2_preflight_rejects_canonical_json_inventory_semantics() -> None:
    row = _observation()
    row["accepted_evidence"]["inventory_sha256"] = (
        "268ebe818021efcbd7a96658e4371fc28a4594a8c6259d473369166bdda550dc"
    )
    with pytest.raises(ValueError, match="closure drift"):
        validate_d0_v2_preflight(row, expected_commit=COMMIT)


def test_v2_failure_is_atomic_and_does_not_authorize_retry(tmp_path, monkeypatch) -> None:
    root = tmp_path / "vngrs_m2_three_model_d0_v2"
    monkeypatch.setattr(d0_preflight_v2, "APPROVED_SCRATCH_PARENT", tmp_path)
    monkeypatch.setattr(d0_preflight_v2, "OUTPUT_ROOT", root)
    monkeypatch.setenv("SLURM_JOB_ID", "999")
    result = write_d0_v2_preflight_failure(
        expected_commit=COMMIT,
        error=ValueError("fixture stop"),
    )
    persisted = json.loads((root / "control/preflight_failure.json").read_text())
    assert persisted == result
    assert result["network_requests"] == result["source_objects_written"] == 0
    assert result["automatic_retry_authorized"] is False
    with pytest.raises(FileExistsError):
        write_d0_v2_preflight_failure(
            expected_commit=COMMIT,
            error=ValueError("second attempt"),
        )


def test_v2_launcher_and_slurm_are_isolated_from_v1_and_training() -> None:
    runner = (ROOT / "scripts/corpora/run_vngrs_m2_d0_v2.py").read_text()
    submitter = (
        ROOT / "scripts/corpora/submit_vngrs_m2_d0_v2_phase1.sh"
    ).read_text()
    slurm = (ROOT / "slurm/m2/materialize_vngrs_m2_d0_v2_phase1.slurm").read_text()
    assert "d0_preflight_v2" in runner
    assert "/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v2" in runner + submitter
    assert "vngrs-m2-d0-v2" in slurm
    assert "--test-only" in submitter
    assert "vngrs_m2_three_model_d0_v1/control/preflight_failure.json" in submitter
    assert V1_FAILURE_EVIDENCE["sha256"] in submitter
    assert "train_clm" not in runner + submitter + slurm
    assert "unlink(" not in runner and "rmtree" not in runner
    assert "--output=/dev/null --error=/dev/null" in submitter
