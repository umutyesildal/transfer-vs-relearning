from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_d0_tokenizer_manifest_inventory_v1.yaml"
CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-d0-tokenizer-manifest-inventory-v1.md"
RESULT = ROOT / "artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1.json"


def test_inventory_contract_is_exact_six_file_read_only_and_unexecuted() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert CONTRACT.is_file()
    assert config["status"] == "frozen_unexecuted"
    assert config["execution_authorized"] is False
    assert config["hu_writes"] is False
    assert config["remote_file_count"] == 6
    assert config["max_single_file_bytes"] == 1_048_576
    assert config["max_total_payload_bytes"] == 6_291_456
    paths = []
    for role, model in config["models"].items():
        assert role in {"olmo", "qwen", "smollm"}
        assert model["snapshot_root"].endswith("epoch_snapshots/epoch-036")
        for kind in ("snapshot_manifest", "model_manifest"):
            paths.append(model[kind]["path"])
            assert len(model[kind]["sha256"]) == 64
    assert len(paths) == len(set(paths)) == 6
    assert all(config["authority"][key] is False for key in config["authority"])


def test_contract_forbids_weights_corpus_training_and_remote_writes() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    for phrase in (
        "HU writes are exactly zero",
        "no model/tokenizer asset open",
        "no vngrs/trwiki access",
        "no Git push/pull/fetch",
        "no cleanup, deletion",
        "do not authorize HU/SSH",
    ):
        assert phrase in text


def test_executed_result_closes_exact_three_tokenizer_registries_only() -> None:
    import json

    from transfer_vs_relearning.corpora.vngrs.metadata import canonical_json_sha256

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["status"] == "PASS"
    assert result["contract_sha256"] == "4f21ec7201734e1d7a2e950f31bad3246f0620523622e0c305e1f3eea252ab2e"
    assert result["execution"]["remote_manifest_files_read"] == 6
    assert result["execution"]["remote_manifest_payload_bytes"] == 5988
    assert result["execution"]["hu_writes"] == 0
    assert result["execution"]["model_weight_files_opened"] == 0
    assert result["execution"]["tokenizer_asset_files_opened"] == 0
    assert set(result["models"]) == {"olmo", "qwen", "smollm"}
    for model in result["models"].values():
        assert model["asset_count"] == 2
        assert model["tokenizer_asset_manifest_sha256"] == canonical_json_sha256(model["assets"])
    assert result["gate"]["tokenizer_asset_inventory"] == "PASS"
    assert result["gate"]["vngrs_d0_qualified"] is False
    assert result["gate"]["ready_to_train"] is False
