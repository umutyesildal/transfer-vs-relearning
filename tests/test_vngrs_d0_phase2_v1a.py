from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from transfer_vs_relearning.corpora.vngrs.metadata import canonical_json_sha256


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1.json"
CORRECTED = ROOT / "artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1a.json"
CONFIG = ROOT / "configs/corpora/vngrs_m2_oscar_phase2_evidence_v1a.yaml"
CONTRACT = ROOT / "documentation/contracts/corpora/vngrs-m2-oscar-phase2-evidence-v1a.md"
RUNNER = ROOT / "scripts/corpora/run_vngrs_m2_oscar_phase2_v1a.py"
SUBMITTER = ROOT / "scripts/corpora/submit_vngrs_m2_oscar_phase2_v1a.sh"
SLURM = ROOT / "slurm/m2/phase2_vngrs_m2_oscar_v1a.slurm"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v1a_inventory_preserves_v1_and_corrects_only_olmo_hash() -> None:
    assert _sha256(ORIGINAL) == "fd3901408e7dfa6f299b3c260229926ba5733bfd3a88f2af80e3ea522b143cb5"
    assert _sha256(CORRECTED) == "72e1c51538a0a801a0fc766faea8af771fb126e190faefd19a0705af3a8886f9"
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    corrected = json.loads(CORRECTED.read_text(encoding="utf-8"))
    assert corrected["preserves_original_inventory"] is True
    assert corrected["trigger_job_id"] == "481910"
    assert corrected["trigger_failure_sha256"] == "a7c566f61427d67921091ac49ffb1debfc9632c7d401bfa99145755fab783c3f"
    old_assets = original["models"]["olmo"]["assets"]
    new_assets = corrected["models"]["olmo"]["assets"]
    assert old_assets[0]["sha256"].startswith("b460")
    assert new_assets[0]["sha256"].startswith("c460")
    assert old_assets[0]["sha256"][1:] == new_assets[0]["sha256"][1:]
    assert old_assets[0]["bytes"] == new_assets[0]["bytes"] == 7_137_656
    assert corrected["models"]["qwen"] == original["models"]["qwen"]
    assert corrected["models"]["smollm"] == original["models"]["smollm"]
    for model in corrected["models"].values():
        assert model["tokenizer_asset_manifest_sha256"] == canonical_json_sha256(model["assets"])


def test_v1a_config_is_fresh_cpu_only_and_unexecuted() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert config["contract_id"] == "vngrs-m2-oscar-phase2-evidence-v1a"
    assert config["status"] == "frozen_unexecuted"
    assert config["prior_wave"]["job_id"] == "481910"
    assert config["prior_wave"]["failure_sha256"] == "a7c566f61427d67921091ac49ffb1debfc9632c7d401bfa99145755fab783c3f"
    assert config["tokenizers"]["snapshot_manifest_cross_check"] is True
    assert config["output"]["root"] == "/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_retry_v1"
    assert config["execution"]["automatic_retry"] is False
    assert config["authority"]["local_preparation"] is True
    assert all(value is False for key, value in config["authority"].items() if key != "local_preparation")


def test_v1a_launcher_binds_failure_cross_check_and_no_gpu_or_training() -> None:
    runner = RUNNER.read_text(encoding="utf-8")
    submitter = SUBMITTER.read_text(encoding="utf-8")
    slurm = SLURM.read_text(encoding="utf-8")
    combined = "\n".join((runner, submitter, slurm)).lower()
    assert "verify_snapshot_manifest=true" in combined
    assert "a7c566f61427d67921091ac49ffb1debfc9632c7d401bfa99145755fab783c3f" in combined
    assert "/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_retry_v1" in combined
    assert "automodel" not in combined and "train_clm" not in combined
    assert "http://" not in combined and "https://" not in combined
    assert "#SBATCH --gres" not in slurm
    assert "TRANSFORMERS_OFFLINE=1" in slurm
    assert "--test-only" in submitter


def test_v1a_contract_hash_binds_implementation() -> None:
    contract = CONTRACT.read_text(encoding="utf-8")
    bindings = (CONFIG, CORRECTED, ROOT / "src/transfer_vs_relearning/corpora/vngrs/d0_phase2.py", ROOT / "src/transfer_vs_relearning/corpora/vngrs/d0_bundle.py", ROOT / "src/transfer_vs_relearning/corpora/vngrs/d0_runtime.py", RUNNER, SUBMITTER, SLURM)
    for path in bindings:
        assert _sha256(path) in contract
