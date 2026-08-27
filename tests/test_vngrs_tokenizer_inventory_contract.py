from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/corpora/vngrs_m2_d0_tokenizer_manifest_inventory_v1.yaml"
CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-d0-tokenizer-manifest-inventory-v1.md"


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

