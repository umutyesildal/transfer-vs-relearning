from __future__ import annotations

from pathlib import Path
import json
import subprocess

from scripts.m2.prepare_three_model_oscar_m2_training_readiness import _parent, _review_html
from transfer_vs_relearning.utils.io import sha256_file

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/training/m2_oscar_training_readiness_evidence_v1.yaml"
PREPARATION = ROOT / "configs/training/m2_three_model_oscar_training_preparation_v2.yaml"
RUNNER = ROOT / "scripts/m2/prepare_three_model_oscar_m2_training_readiness.py"
SLURM = ROOT / "slurm/m2/prepare_three_model_oscar_m2_training_readiness.slurm"
SUBMIT = ROOT / "scripts/m2/submit_three_model_oscar_m2_training_readiness.sh"
REPAIR_CONFIG = ROOT / "configs/training/m2_oscar_training_readiness_evidence_v1a.yaml"
REPAIR_PREPARATION = ROOT / "configs/training/m2_three_model_oscar_training_preparation_v3.yaml"
REPAIR_SLURM = ROOT / "slurm/m2/prepare_three_model_oscar_m2_training_readiness_v1a.slurm"
REPAIR_SUBMIT = ROOT / "scripts/m2/submit_three_model_oscar_m2_training_readiness_v1a.sh"


def test_readiness_evidence_is_cpu_only_and_preserves_training_gate() -> None:
    config = CONFIG.read_text(encoding="utf-8")
    preparation = PREPARATION.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    assert "68dd7ca18d794c09ce3e1b1aa8b2b4b9f6ddb175195959b24b0103c7ea65dd63" in config
    assert "vngrs_m2_oscar_exact_blocks_adapter_repair_v1/manifest.json" in preparation
    assert "vngrs_m2_oscar_training_readiness_evidence_v1/parent_registry.json" in preparation
    assert "fact_rows: 250" in config
    assert "human_verdict_entry_in_wave: false" in config
    assert '"ready_to_train": False' in runner
    assert '"training": False' in runner
    assert "EXACT_M1_PARENT_REGISTRY_PASS" in runner
    assert "EVIDENCE_PREPARED_AWAITING_FACT_REVIEW_AND_GPU_SMOKE" in runner


def test_readiness_launcher_is_single_cpu_wave_with_fresh_roots() -> None:
    subprocess.run(["bash", "-n", str(SLURM)], check=True)
    subprocess.run(["bash", "-n", str(SUBMIT)], check=True)
    slurm = SLURM.read_text(encoding="utf-8")
    submit = SUBMIT.read_text(encoding="utf-8")
    assert "#SBATCH --cpus-per-task=4" in slurm
    assert "#SBATCH --mem=64G" in slurm
    assert "--gres=gpu" not in slurm
    assert 'test ! -e "$output_root"' in submit
    assert 'test ! -e "$training_root"' in submit
    assert submit.count('job_id="$(sbatch --parsable') == 1
    assert "scancel" not in submit and "scontrol" not in submit
    assert "automatic_retry_authorized" in submit


def test_fact_review_handoff_is_all_rows_and_registry_bound() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "len(fact_rows) != 250" in source
    assert "fact_registry_sha256" in source
    assert "m2_fact_review_" in source
    assert "usable" in source and "issue" in source


def test_parent_asset_hash_validation_and_review_html(tmp_path: Path) -> None:
    snapshot = tmp_path / "epoch-036"
    snapshot.mkdir()
    (snapshot / "config.json").write_text("{}\n", encoding="utf-8")
    (snapshot / "model.safetensors").write_bytes(b"weights")
    snapshot_manifest = snapshot / "snapshot_manifest.json"
    checkpoint_sha256 = "c" * 64
    snapshot_manifest.write_text(
        json.dumps(
            {
                "checkpoint_sha256": checkpoint_sha256,
                "files": [
                    {"path": "config.json", "bytes": (snapshot / "config.json").stat().st_size, "sha256": sha256_file(snapshot / "config.json")},
                    {"path": "model.safetensors", "bytes": (snapshot / "model.safetensors").stat().st_size, "sha256": sha256_file(snapshot / "model.safetensors")},
                ],
            }
        ),
        encoding="utf-8",
    )
    model_manifest = tmp_path / "model_manifest.json"
    model_manifest.write_text(
        json.dumps(
            {
                "local_path_absolute": str(snapshot),
                "checkpoint_sha256": checkpoint_sha256,
            }
        ),
        encoding="utf-8",
    )
    result, size = _parent(
        "olmo",
        {
            "snapshot_root": str(snapshot),
            "snapshot_manifest": str(snapshot_manifest),
            "snapshot_manifest_sha256": sha256_file(snapshot_manifest),
            "model_manifest": str(model_manifest),
            "model_manifest_sha256": sha256_file(model_manifest),
        },
    )
    assert result["status"] == "EXACT_M1_PARENT_ASSETS_PASS"
    assert size == len("{}\n".encode()) + len(b"weights")
    rendered = _review_html(
        [{"index": 0, "fact_id": "S1_profession", "relation": "profession", "text": "Ada bir doktordur."}],
        "a" * 64,
    )
    assert "Ada bir doktordur." in rendered
    assert "fact_registry_sha256" in rendered


def test_v1a_repair_is_fresh_root_single_cpu_wave_bound_to_terminal_failure() -> None:
    subprocess.run(["bash", "-n", str(REPAIR_SLURM)], check=True)
    subprocess.run(["bash", "-n", str(REPAIR_SUBMIT)], check=True)
    config = REPAIR_CONFIG.read_text(encoding="utf-8")
    preparation = REPAIR_PREPARATION.read_text(encoding="utf-8")
    submit = REPAIR_SUBMIT.read_text(encoding="utf-8")
    slurm = REPAIR_SLURM.read_text(encoding="utf-8")
    assert "job_id: 482035" in config
    assert "exact_files: 5" in config
    assert "vngrs_m2_oscar_training_readiness_evidence_retry_v1" in config
    assert "vngrs_m2_oscar_training_readiness_evidence_retry_v1/parent_registry.json" in preparation
    assert "e31ebce25931b74eda597610a6dfb65bf8879c78dff3e59713adfa49ec2cd118" in submit
    assert 'test ! -e "$output_root"' in submit
    assert submit.count('job_id="$(sbatch --parsable') == 1
    assert "scancel" not in submit and "scontrol" not in submit
    assert "#SBATCH --cpus-per-task=4" in slurm and "#SBATCH --mem=64G" in slurm
    assert "--gres=gpu" not in slurm
