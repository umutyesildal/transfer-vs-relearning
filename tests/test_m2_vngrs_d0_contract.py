from pathlib import Path

import yaml

from transfer_vs_relearning.corpora.vngrs.metadata import (
    FROZEN_SELECTED_SHARD_PATHS,
    VNGRS_REPOSITORY,
    VNGRS_REVISION,
    VNGRS_SCHEMA,
    build_selection_evidence,
    canonical_json_sha256,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_three_model_d0_v1.yaml"
CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-three-model-d0-v1.md"


def load_config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def test_d0_contract_is_execution_disabled_and_present() -> None:
    config = load_config()
    assert CONTRACT.is_file()
    assert config["status"] == "draft_execution_disabled"
    assert config["contract"] == str(CONTRACT.relative_to(ROOT))
    assert config["authority"] == {
        "local_preparation": True,
        "network_retrieval": False,
        "hu_ssh": False,
        "corpus_materialization": False,
        "model_weight_load": False,
        "inference_or_scoring": False,
        "slurm_or_gpu": False,
        "training": False,
        "publication": False,
        "cleanup_or_deletion": False,
    }


def test_d0_source_identity_matches_frozen_vngrs_selection() -> None:
    config = load_config()
    source = config["source"]
    assert source["repository"] == VNGRS_REPOSITORY
    assert source["revision"] == VNGRS_REVISION
    assert tuple(source["schema"]) == VNGRS_SCHEMA
    assert source["selected_shards"] == 32
    assert tuple(source["selected_paths"]) == FROZEN_SELECTED_SHARD_PATHS
    assert source["selection_payload_sha256"] == canonical_json_sha256(
        build_selection_evidence()
    )
    assert source["expected_selected_compressed_bytes"] == 9_468_474_036


def test_d0_keeps_light_audit_split_and_three_model_scope() -> None:
    config = load_config()
    assert config["light_audit"]["human_review_documents"] == 64
    assert config["light_audit"]["corpus_wide_learned_quality_classifier"] is False
    assert config["light_audit"]["broad_manual_labeling"] is False
    assert config["split"]["heldout_documents"] == 10_000
    assert config["split"]["document_disjoint_required"] is True
    assert config["split"]["trwiki_training_rows"] == 0
    assert set(config["tokenizer_accounting"]["models"]) == {"olmo", "qwen", "smollm"}
    assert config["tokenizer_accounting"]["shared_raw_document_ids"] is True
    assert (
        config["tokenizer_accounting"]["model_token_counts_are_cross_model_equality_gate"]
        is False
    )


def test_d0_materialization_operator_remains_explicit_and_execution_disabled() -> None:
    operator = load_config()["materialization_operator"]
    assert operator["module"] == "transfer_vs_relearning.corpora.vngrs.materialization"
    assert operator["transport_injected"] is True
    assert operator["implicit_network_client"] is False
    assert operator["execution_enabled"] is False
    assert operator["exact_registry_required_before_root_creation"] is True
    assert operator["full_object_sha256_required"] is True
    assert operator["lfs_oid_must_bind_sha256"] is True
    assert operator["partial_directory"] == "raw/.partial"
    assert operator["atomic_publish_after_verification"] is True
    assert operator["automatic_retry"] is False
    assert operator["automatic_resume"] is False
    assert operator["cleanup_on_failure"] is False


def test_d0_epoch036_parent_evidence_is_bound_without_fabricating_tokenizer_assets() -> None:
    accounting = load_config()["tokenizer_accounting"]
    evidence = accounting["local_binding_evidence"]
    assert evidence["sha256"] == "41c2f2c6b722fc25ac48af278f1b318acc5e743b3c48d649fe26259848080462"
    assert evidence["tokenizer_asset_inventory_closed"] is False
    for model in accounting["models"].values():
        assert model["m1_epoch036_path"].endswith("epoch_snapshots/epoch-036")
        assert len(model["snapshot_manifest_sha256"]) == 64
        assert len(model["training_manifest_sha256"]) == 64
        assert len(model["model_manifest_sha256"]) == 64
        assert model["tokenizer_asset_manifest_sha256"] is None
        assert model["tokenizer_asset_binding_status"] == "unresolved_requires_read_only_inventory"
