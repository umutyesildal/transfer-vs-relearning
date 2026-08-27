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


def test_d0_contract_is_frozen_unexecuted_and_present() -> None:
    config = load_config()
    assert CONTRACT.is_file()
    assert config["status"] == "frozen_unexecuted"
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
    assert source["expected_selected_object_bytes"] == 9_502_315_428


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
    assert operator["expected_total_bytes"] == 9_502_315_428


def test_d0_storage_bounds_are_explicit_but_require_fresh_execution_preflight() -> None:
    output = load_config()["output"]
    assert output["calculated_peak_bytes"] == 30_029_406_455
    assert output["frozen_peak_bytes"] == 32 * 1024**3
    assert output["required_available_bytes"] == 40 * 1024**3
    assert output["required_available_inodes"] == 1_024
    assert output["storage_bounds_result"].endswith("storage_bounds_v1.json")
    assert output["fresh_execution_preflight_required"] is True


def test_d0_final_orchestration_is_local_only_and_not_a_production_launcher() -> None:
    operator = load_config()["final_orchestration"]
    assert operator["execution_enabled"] is False
    assert operator["transport_injected"] is True
    assert operator["tokenizer_adapters_injected"] is True
    assert operator["reviewed_sample_injected"] is True
    assert operator["typed_post_materialization_failure"] == "control/d0_failure.json"
    assert operator["terminal_ready_to_train"] is False
    assert operator["production_launcher_frozen"] is True
    assert operator["phase1_terminal_status"] == "AWAITING_HUMAN_REVIEW"
    assert operator["phase2_requires_separate_authorization"] is True
    assert operator["all_64_usable_required_for_pass"] is True


def test_d0_synthetic_surface_source_is_exact_and_does_not_invent_aliases() -> None:
    source = load_config()["synthetic_surface_registry"]
    assert source["source_sha256"] == "9b1fcae2565fbf0d9c624a2c229c8173a59ca00064db1a017b0f2a5c0c749289"
    assert source["subjects"] == 100
    assert source["fact_objects"] == 500
    assert source["aliases"] == 0


def test_d0_source_registry_operator_is_exact_and_execution_disabled() -> None:
    operator = load_config()["source_registry_operator"]
    assert operator["module"] == "transfer_vs_relearning.corpora.vngrs.source_registry"
    assert operator["function"] == "build_source_registry_from_metadata_ledger"
    assert operator["execution_enabled"] is False
    assert operator["expected_ledger_sha256"] == (
        "6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3"
    )
    assert operator["expected_objects"] == 32
    assert operator["expected_total_object_bytes"] == 9_502_315_428
    assert operator["expected_total_parquet_compressed_bytes"] == 9_468_474_036
    assert operator["lfs_oid_is_full_object_sha256"] is True
    assert operator["corpus_rows_read"] == 0
    assert operator["full_objects_downloaded"] == 0
    assert operator["registry_closed"] is True
    assert operator["result"].endswith("source_registry_byte_semantics_repair_v1.json")
    assert operator["result_sha256"] == "63acadb8955411e0ee42dba0c28f72220568efce6e01db4bfcf90a31c49724a9"
    assert operator["registry_sha256"] == "b1c80bf78ff40de5c02e14f08082a51cc17cc90a9853028eaf866cb63326e41f"


def test_d0_epoch036_parent_and_tokenizer_asset_evidence_is_closed() -> None:
    accounting = load_config()["tokenizer_accounting"]
    evidence = accounting["local_binding_evidence"]
    assert evidence["sha256"] == "41c2f2c6b722fc25ac48af278f1b318acc5e743b3c48d649fe26259848080462"
    assert evidence["tokenizer_asset_inventory_closed"] is True
    assert evidence["tokenizer_asset_inventory_result"].endswith("tokenizer_manifest_inventory_v1.json")
    for model in accounting["models"].values():
        assert model["m1_epoch036_path"].endswith("epoch_snapshots/epoch-036")
        assert len(model["snapshot_manifest_sha256"]) == 64
        assert len(model["training_manifest_sha256"]) == 64
        assert len(model["model_manifest_sha256"]) == 64
        assert len(model["tokenizer_asset_manifest_sha256"]) == 64
        assert model["tokenizer_asset_binding_status"] == "closed_from_preserved_epoch036_manifests"
