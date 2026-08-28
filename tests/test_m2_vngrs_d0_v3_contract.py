import hashlib
import json
from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.corpora.vngrs import d0_inputs_v3, d0_preflight_v3
from transfer_vs_relearning.corpora.vngrs.d0_inputs_v3 import load_source_objects_v3
from transfer_vs_relearning.corpora.vngrs.d0_preflight_v3 import (
    V2_FAILURE_CORE,
    V2_PARTIAL_EVIDENCE,
    validate_d0_v3_preflight,
    write_d0_v3_preflight_failure,
)
from transfer_vs_relearning.corpora.vngrs.metadata import (
    FROZEN_SELECTED_SHARD_PATHS,
    VNGRS_REVISION,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_three_model_d0_v3.yaml"
CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-three-model-d0-v3.md"
COMMIT = "a" * 40


def _observation() -> dict:
    return {
        "git_commit": COMMIT,
        "clean_task_overlap": True,
        "accepted_source_rows": 32,
        "accepted_source_root": str(d0_preflight_v3.SOURCE_ROOT),
        "hu_home_exact_bytes": 14_689_423_360,
        "hu_home_writes_allowed": False,
        "duplicate_active_jobs": 0,
        "v2_failure_core": dict(V2_FAILURE_CORE),
        "v2_partial_evidence": dict(V2_PARTIAL_EVIDENCE),
        "v2_root_writes_allowed": False,
        "v2_partial_reuse_allowed": False,
        "storage": {
            "resolved_parent": "/vol/tmp2/yesildau",
            "proposed_root_absent": True,
            "available_bytes": 122_943_170_412_544,
            "available_inodes": 2_284_282_885,
        },
    }


def test_v3_contract_freezes_identity_separation_and_no_reuse() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert CONTRACT.is_file()
    assert config["status"] == "frozen_unexecuted"
    assert config["identity_semantics"]["object_id_is_full_byte_sha256"] is False
    assert config["identity_semantics"]["full_byte_sha256_role"] == (
        "computed_output_from_downloaded_bytes"
    )
    assert config["v2_terminal_evidence"]["reuse_or_resume"] is False
    assert config["output"]["root"].endswith("vngrs_m2_three_model_d0_v3")
    assert config["authority"]["hu_ssh"] is False
    assert config["authority"]["training"] is False


def test_v3_preflight_requires_exact_preserved_v2_partial() -> None:
    result = validate_d0_v3_preflight(_observation(), expected_commit=COMMIT)
    assert result["schema_version"] == 3
    assert result["status"] == "D0_PREFLIGHT_PASS"
    assert result["v2_partial_reuse_allowed"] is False
    drift = _observation()
    drift["v2_partial_evidence"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="partial byte evidence"):
        validate_d0_v3_preflight(drift, expected_commit=COMMIT)


def test_v3_preflight_failure_is_atomic_and_authorizes_no_retry(tmp_path, monkeypatch) -> None:
    root = tmp_path / "vngrs_m2_three_model_d0_v3"
    monkeypatch.setattr(d0_preflight_v3, "APPROVED_SCRATCH_PARENT", tmp_path)
    monkeypatch.setattr(d0_preflight_v3, "OUTPUT_ROOT", root)
    result = write_d0_v3_preflight_failure(expected_commit=COMMIT, error=ValueError("stop"))
    assert json.loads((root / "control/preflight_failure.json").read_text()) == result
    assert result["network_requests"] == result["source_objects_written"] == 0
    assert result["automatic_retry_authorized"] is False


def test_v3_loader_preserves_ledger_unverified_byte_sha_semantics(tmp_path, monkeypatch) -> None:
    footer = b"data" + b"\x04\x00\x00\x00PAR1"
    trailer = footer[-8:]
    rows = []
    remaining = 9_502_315_428 - 31
    for index, path in enumerate(FROZEN_SELECTED_SHARD_PATHS):
        footer_name = f"evidence/footer/{index:05d}.bin"
        trailer_name = f"evidence/footer_trailer/{index:05d}.bin"
        footer_path = tmp_path / footer_name
        trailer_path = tmp_path / trailer_name
        footer_path.parent.mkdir(parents=True, exist_ok=True)
        trailer_path.parent.mkdir(parents=True, exist_ok=True)
        footer_path.write_bytes(footer)
        trailer_path.write_bytes(trailer)
        rows.append(
            {
                "path": path,
                "immutable_revision": VNGRS_REVISION,
                "object_sha256": None,
                "object_sha256_status": "unverified_footer_only",
                "object_id": "a" * 64,
                "object_id_kind": "lfs_oid",
                "object_size_bytes": remaining if index == 0 else 1,
                "footer_metadata_length": len(footer) - 8,
                "footer_evidence_artifact": footer_name,
                "footer_sha256": hashlib.sha256(footer).hexdigest(),
                "footer_trailer_evidence_artifact": trailer_name,
                "footer_trailer_sha256": hashlib.sha256(trailer).hexdigest(),
            }
        )
    ledger = tmp_path / "shard_metadata_ledger.jsonl"
    ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    monkeypatch.setattr(d0_inputs_v3, "LEDGER_SHA256", hashlib.sha256(ledger.read_bytes()).hexdigest())
    objects = load_source_objects_v3(tmp_path)
    assert len(objects) == 32
    assert objects[0].object_id == "a" * 64
    assert not hasattr(objects[0], "sha256")


def test_v3_route_is_phase1_only_and_contains_no_training_or_cleanup() -> None:
    runner = (ROOT / "scripts/corpora/run_vngrs_m2_d0_v3.py").read_text()
    submitter = (ROOT / "scripts/corpora/submit_vngrs_m2_d0_v3_phase1.sh").read_text()
    slurm = (ROOT / "slurm/m2/materialize_vngrs_m2_d0_v3_phase1.slurm").read_text()
    assert 'choices=("phase1",)' in runner
    assert "materialize_full_objects_v3" in runner
    assert "--test-only" in submitter
    assert V2_PARTIAL_EVIDENCE["sha256"] in submitter
    assert "vngrs-m2-d0-v3" in slurm
    assert "train_clm" not in runner + submitter + slurm
    assert "rmtree" not in runner and "unlink(" not in runner
