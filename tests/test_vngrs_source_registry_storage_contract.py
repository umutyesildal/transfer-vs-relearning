from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_d0_source_registry_storage_discovery_v1.yaml"
CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-d0-source-registry-storage-discovery-v1.md"


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
