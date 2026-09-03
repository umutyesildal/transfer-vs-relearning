from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from transfer_vs_relearning.corpora.vngrs.d0_audit import D0Document
from transfer_vs_relearning.study import m2_eval_executor as module
from transfer_vs_relearning.utils.io import sha256_file


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/evaluation/m2_oscar_eval_v2_execution_v1.yaml"
CONTRACT = ROOT / "documentation/contracts/evaluation/vngrs-m2-oscar-eval-v2-execution-v1.md"
REPAIR_CONFIG = ROOT / "configs/evaluation/m2_oscar_eval_v2_execution_v1a.yaml"
REPAIR_CONTRACT = ROOT / "documentation/contracts/evaluation/vngrs-m2-oscar-eval-v2-execution-v1a.md"


def test_execution_config_is_frozen_and_narrow() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert config["status"] == "frozen_unexecuted"
    assert config["execution_authorized"] is False
    assert config["matrix"]["gpu_tasks"] == 63
    assert config["matrix"]["m2_checkpoint_tasks"] == 60
    assert config["matrix"]["m1_parent_oscar_only_tasks"] == 3
    assert config["matrix"]["full_tasks"] == 12
    assert config["matrix"]["unique_scientific_states"] == 63
    assert config["oscar_source"]["heldout_documents"] == 10000
    assert config["evaluation"]["full_updates"] == [381, 762]
    assert config["evaluation"]["primary_cross_tokenizer_language_metric"] == "bits_per_byte"
    assert config["authority"]["evaluation_or_scoring"] is False
    assert config["authority"]["automatic_retry"] is False
    assert CONTRACT.is_file()
    assert sha256_file(CONTRACT) == "582b6b6d5f066f96c9fdbc38b6d34eb9e4d83aa15a45d29e5cf07f1ec22331bd"
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "54dedde78dda88f99d4cec80606c63b03657b04cb6545f816ff4979ed0b0567d" in contract
    assert "4bd68c27b486ea6b928a7ed21ef9171182fa01d1c9f6f9cb907cb8f254540ca9" in contract
    assert "141faf323ee85a4407525b51f6f757afdb749b3ac00b168cd6a8963fcfc5b215" in contract


def test_exact_heldout_selection_is_stable_and_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "OSCAR_HELDOUT_DOCUMENTS", 3)
    rows = [
        D0Document("c", "x", "oscar", "üç"),
        D0Document("a", "x", "oscar", "bir"),
        D0Document("b", "x", "oscar", "iki"),
        D0Document("z", "x", "mc4", "dışarı"),
    ]
    selected = module.select_heldout_documents(rows, {"a", "b", "c"})
    assert [row.stable_document_id for row in selected] == ["a", "b", "c"]
    with pytest.raises(ValueError, match="10,000-document"):
        module.select_heldout_documents(rows, {"a", "b", "missing"})


def test_executor_has_no_scientific_retry_or_training_path() -> None:
    text = (ROOT / "src/transfer_vs_relearning/study/m2_eval_executor.py").read_text(encoding="utf-8")
    assert '"--array=0-62%6"' in text
    assert '"automatic_retry": False' in text
    assert "TASK_RETRY" not in text
    assert "train_clm.py" not in text
    assert "optimizer" not in text.lower()
    assert "materialize_oscar_heldout" in text
    assert "exact_sha_bound_user_authorization_received" in text
    assert '"git", "status", "--porcelain=v1"' in text
    assert "wikitext2" in text and "oscar_heldout" in text and "trwiki_cross_domain" in text
    assert "paired_subject_bootstrap_accuracy_difference" in text
    assert "samples=10_000, seed=42" in text
    assert "M2-A minus M1" in text
    assert "M2-B minus M2-A" in text


def test_v1a_repair_separates_metadata_and_parquet_roots() -> None:
    config = yaml.safe_load(REPAIR_CONFIG.read_text(encoding="utf-8"))
    source = config["oscar_source"]
    assert source["root"].endswith("vngrs_m2_three_model_d0_v3")
    assert source["metadata_root"].endswith("luna_vngrs_metadata_footer_feasibility_v1")
    assert source["metadata_ledger_sha256"] == (
        "6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3"
    )
    assert source["root"] != source["metadata_root"]
    assert config["prior_attempt"]["dependency_dead_job_ids"] == [483720, 483721]
    assert config["prior_attempt"]["result_files"] == 0
    assert config["output"]["root"].endswith("m2_oscar_eval_v2_execution_v1a")
    assert config["authority"]["cancel_exact_dependency_dead_jobs"] is False
    assert REPAIR_CONTRACT.is_file()
    assert sha256_file(REPAIR_CONTRACT) == (
        "e152dab3ecfb3b54540716b0fd0d7046276c0d8d930797757e66f05616786541"
    )
    contract = REPAIR_CONTRACT.read_text(encoding="utf-8")
    assert "d209971308e422716262dff163adce171556d11b6522fe3f742d4aac31fdd801" in contract
    assert "af201694f6f120d061e4592d71d07854ba23350965705c1d39de8445104f0006" in contract
    text = (ROOT / "src/transfer_vs_relearning/study/m2_eval_executor.py").read_text(
        encoding="utf-8"
    )
    assert "load_source_objects_v3(metadata_root)" in text
