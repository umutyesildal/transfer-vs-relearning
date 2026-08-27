from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_d0_source_registry_storage_discovery_v1.yaml"
CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-d0-source-registry-storage-discovery-v1.md"
RESULT = ROOT / "artifacts/corpora/vngrs_m2_d0/source_registry_storage_discovery_v1.json"
RETRY_CONFIG = ROOT / "configs/corpora/vngrs_m2_d0_source_registry_storage_discovery_retry_v1.yaml"
RETRY_CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-d0-source-registry-storage-discovery-retry-v1.md"
RETRY_RESULT = ROOT / "artifacts/corpora/vngrs_m2_d0/source_registry_storage_discovery_retry_v1.json"
CAPTURE_CONFIG = ROOT / "configs/corpora/vngrs_m2_d0_source_registry_capture_retry_v1.yaml"
CAPTURE_CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-d0-source-registry-capture-retry-v1.md"
CAPTURE_RESULT = ROOT / "artifacts/corpora/vngrs_m2_d0/source_registry_storage_discovery_capture_retry_v1.json"
SEMANTICS_CONFIG = ROOT / "configs/corpora/vngrs_m2_d0_source_registry_byte_semantics_repair_v1.yaml"
SEMANTICS_CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-d0-source-registry-byte-semantics-repair-v1.md"


def load_config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def test_discovery_contract_is_one_file_read_only_and_unexecuted() -> None:
    config = load_config()
    assert CONTRACT.is_file()
    import hashlib

    assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest() == (
        "c17e178a4148a9482b0f37c2d96309897d618a08e65a84fa2bd7edb6c845c644"
    )
    assert config["status"] == "frozen_unexecuted"
    assert config["execution_authorized"] is False
    assert config["hu_writes"] is False
    assert config["remote_file_count"] == 1
    assert config["max_single_file_bytes"] == 4_194_304
    assert config["max_total_payload_bytes"] == 4_194_304
    assert config["automatic_retry"] is False
    assert all(config["authority"][key] is False for key in config["authority"])


def test_discovery_contract_binds_exact_ledger_and_zero_corpus_reads() -> None:
    config = load_config()
    ledger = config["metadata_ledger"]
    assert ledger["path"].endswith("/shard_metadata_ledger.jsonl")
    assert ledger["sha256"] == "6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3"
    assert ledger["selected_objects"] == 32
    assert ledger["expected_total_object_bytes"] == 9_468_474_036
    assert ledger["object_id_kind"] == "lfs_oid"
    assert ledger["lfs_oid_is_full_object_sha256"] is True
    assert config["local_derivation"]["corpus_rows_read"] == 0
    assert config["local_derivation"]["full_objects_downloaded"] == 0


def test_discovery_contract_limits_storage_observation_and_preserves_home() -> None:
    config = load_config()
    storage = config["filesystem_observations"]
    assert storage["required_mount_prefix"] == "/vol/tmp2"
    assert storage["proposed_root_must_be_absent"] is True
    assert storage["commands"] == ["readlink_parent", "root_absence_test", "df_bytes", "df_inodes"]
    assert storage["recursive_du"] is False
    assert storage["directory_inventory"] is False
    assert storage["fresh_materialization_preflight_still_required"] is True
    home = config["home_usage_reference"]
    assert home["exact_bytes"] == 14_689_423_360
    assert home["policy_limit_bytes"] == 30 * 1024**3
    assert home["new_home_du_authorized"] is False
    assert home["home_write_allowed"] is False


def test_contract_forbids_execution_and_qualification_expansion() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    for phrase in (
        "HU writes are exactly zero",
        "No `du` is run",
        "no corpus object/footer read",
        "no Git push/pull/fetch",
        "do not authorize HU/SSH",
        "no claim that D0 is qualified",
    ):
        assert phrase in text


def test_single_execution_failed_closed_before_payload_and_registry_derivation() -> None:
    import json

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["status"] == "BLOCKED_OPERATIONAL_NOT_RUN"
    assert result["failure_class"] == "blocked_by_filesystem_metadata_command_compatibility"
    assert result["failure"]["phase"] == "df_inodes"
    assert result["failure"]["automatic_retry_allowed"] is False
    assert result["failure"]["retry_executed"] is False
    assert result["execution"]["remote_passes"] == 1
    assert result["execution"]["hu_writes"] == 0
    assert result["execution"]["ledger_payload_returned"] is False
    assert result["ledger_prechecks"]["expected_sha256_matched"] is True
    assert result["filesystem_observations"]["proposed_root_absent"] is True
    assert result["filesystem_observations"]["inode_capacity"] is None
    assert result["source_registry"]["status"] == "NOT_DERIVED_LEDGER_PAYLOAD_NOT_RETURNED"
    assert all(result["gate"][key] is False for key in result["gate"])


def test_retry_contract_changes_only_inode_command_and_is_not_authorized() -> None:
    import hashlib

    config = yaml.safe_load(RETRY_CONFIG.read_text(encoding="utf-8"))
    assert hashlib.sha256(RETRY_CONTRACT.read_bytes()).hexdigest() == (
        "b2e6b23a96e36b87c1a7e68b2e5306d3be01bf45293e59c6bc635b08ceff67b5"
    )
    assert config["status"] == "frozen_unexecuted"
    assert config["execution_authorized"] is False
    assert config["hu_writes"] is False
    assert config["remote_file_count"] == 1
    assert config["sole_correction"] == {
        "failed_command": "df -i --output",
        "replacement_command": "df -Pi",
        "scientific_change": False,
    }
    assert config["metadata_ledger"] == load_config()["metadata_ledger"]
    assert config["filesystem_observations"]["inode_command"] == "df -Pi"
    assert config["filesystem_observations"]["recursive_du"] is False
    assert config["automatic_retry"] is False
    assert all(config["authority"][key] is False for key in config["authority"])


def test_retry_execution_closed_filesystem_observations_but_not_registry() -> None:
    import json

    result = json.loads(RETRY_RESULT.read_text(encoding="utf-8"))
    assert result["status"] == "BLOCKED_OPERATIONAL_NOT_RUN"
    assert result["failure_class"] == "blocked_by_local_transport_capture_limit"
    assert result["failure"]["remote_command_completed"] is True
    assert result["execution"]["remote_passes"] == 1
    assert result["execution"]["hu_writes"] == 0
    assert result["filesystem_observations"]["complete"] is True
    assert result["filesystem_observations"]["inode_capacity"]["available_inodes"] == 2_284_282_885
    assert result["source_registry"]["registry_sha256"] is None
    assert result["gate"]["source_registry_closed"] is False
    assert result["gate"]["ready_to_train"] is False


def test_capture_retry_is_direct_pipe_only_frozen_and_unexecuted() -> None:
    import hashlib

    config = yaml.safe_load(CAPTURE_CONFIG.read_text(encoding="utf-8"))
    assert hashlib.sha256(CAPTURE_CONTRACT.read_bytes()).hexdigest() == (
        "1d3836a18438a809329c889b5cda24c0e635666cda20f9d3c47fe60a1c92fcc5"
    )
    assert config["status"] == "frozen_unexecuted"
    assert config["execution_authorized"] is False
    assert config["hu_writes"] is False
    assert config["remote_file_count"] == 1
    assert config["sole_correction"]["layer"] == "local_transport"
    assert config["sole_correction"]["remote_command_change"] is False
    assert config["sole_correction"]["scientific_change"] is False
    assert config["local_transport"]["stdin_only"] is True
    assert config["local_transport"]["transcript_persisted"] is False
    assert config["local_transport"]["raw_ledger_persisted"] is False
    assert all(config["authority"][key] is False for key in config["authority"])


def test_capture_execution_exposes_object_vs_compressed_semantics_and_blocks() -> None:
    import json

    result = json.loads(CAPTURE_RESULT.read_text(encoding="utf-8"))
    assert result["status"] == "BLOCKED_EVIDENCE_SEMANTIC_MISMATCH"
    assert result["failure_class"] == "blocked_by_object_vs_parquet_compressed_byte_semantics"
    assert result["failure"]["observed_object_size_bytes"] == 9_502_315_428
    assert result["failure"]["accepted_parquet_compressed_bytes"] == 9_468_474_036
    assert result["failure"]["difference_bytes"] == 33_841_392
    assert result["execution"]["complete_ledger_payload_received_in_memory"] is True
    assert result["execution"]["raw_ledger_payload_persisted"] is False
    assert result["ledger_prechecks"][
        "frozen_path_order_revision_lfs_and_positive_size_rows_validated_before_aggregate_gate"
    ] == 32
    assert result["gate"]["source_registry_closed"] is False


def test_byte_semantics_repair_freezes_both_aggregates_without_source_change() -> None:
    import hashlib

    config = yaml.safe_load(SEMANTICS_CONFIG.read_text(encoding="utf-8"))
    assert hashlib.sha256(SEMANTICS_CONTRACT.read_bytes()).hexdigest() == (
        "3a6591c288c3a2e3c82c7fdc776e1205d6738e57d9042c94bf9b43fff0a09e1e"
    )
    assert config["status"] == "frozen_unexecuted"
    assert config["execution_authorized"] is False
    assert config["sole_repair"]["expected_total_object_bytes"] == 9_502_315_428
    assert config["sole_repair"]["expected_total_parquet_compressed_bytes"] == 9_468_474_036
    assert config["sole_repair"]["difference_bytes"] == 33_841_392
    assert config["sole_repair"]["source_row_change"] is False
    assert config["sole_repair"]["scientific_change"] is False
    assert config["local_transport"]["raw_ledger_persisted"] is False
    assert all(config["authority"][key] is False for key in config["authority"])
