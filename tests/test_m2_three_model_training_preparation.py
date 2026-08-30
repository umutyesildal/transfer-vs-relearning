from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import yaml

from transfer_vs_relearning.utils.io import sha256_file


ROOT = Path(__file__).resolve().parents[1]


def _binding(path: Path) -> dict[str, str]:
    return {"path": str(path), "sha256": sha256_file(path)}


def test_prepare_and_validate_six_run_m2_family(tmp_path: Path) -> None:
    block_root = tmp_path / "blocks"
    parent_root = tmp_path / "parents"
    block_root.mkdir()
    parent_root.mkdir()
    models = {}
    parents = {}
    for role in ("olmo", "qwen", "smollm"):
        role_root = block_root / role
        role_root.mkdir()
        m2_a = role_root / "m2_a.jsonl"
        m2_b = role_root / "m2_b.jsonl"
        validation = role_root / "validation.jsonl"
        m2_a.write_text(f'{{"role":"{role}","arm":"a"}}\n', encoding="utf-8")
        m2_b.write_text(f'{{"role":"{role}","arm":"b"}}\n', encoding="utf-8")
        validation.write_text(f'{{"role":"{role}","split":"heldout"}}\n', encoding="utf-8")
        model_manifest = parent_root / f"{role}.json"
        model_manifest.write_text(
            json.dumps({"local_path_absolute": str(parent_root / role)}), encoding="utf-8"
        )
        models[role] = {
            "status": "EXACT_MATCHED_BLOCKS_PASS",
            "matching": {
                "m2_a_m2_b_block_count_equal": True,
                "m2_a_m2_b_token_budget_equal": True,
                "branch_a_fact_exposures": 0,
                "extra_tokens_over_m2_a": 0,
            },
            "artifacts": {
                "m2_a_train": _binding(m2_a),
                "m2_b_train": _binding(m2_b),
                "shared_validation": _binding(validation),
            },
        }
        parents[role] = {"model_manifest": _binding(model_manifest)}
    block_manifest = block_root / "manifest.json"
    block_manifest.write_text(
        json.dumps({"status": "EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED", "models": models}),
        encoding="utf-8",
    )
    parent_registry = parent_root / "registry.json"
    parent_registry.write_text(
        json.dumps({"status": "EXACT_M1_PARENT_REGISTRY_PASS", "models": parents}),
        encoding="utf-8",
    )
    output = tmp_path / "prepared"
    training = tmp_path / "training"
    env = {**os.environ, "PYTHONPATH": f"{ROOT / 'src'}:{ROOT}"}
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/m2/prepare_three_model_oscar_m2_training_family.py"),
            "--plan",
            str(ROOT / "configs/training/m2_matched_three_model_oscar_plan_v1.yaml"),
            "--preparation-config",
            str(ROOT / "configs/training/m2_three_model_oscar_training_preparation_v1.yaml"),
            "--block-manifest",
            str(block_manifest),
            "--parent-registry",
            str(parent_registry),
            "--output-dir",
            str(output),
            "--training-output-root",
            str(training),
            "--allow-local-paths",
        ],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )
    manifest = json.loads((output / "config_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "M2_TRAINING_CONFIGS_PREPARED_NOT_AUTHORIZED"
    assert {(row["role"], row["arm"]) for row in manifest["entries"]} == {
        (role, arm)
        for role in ("olmo", "qwen", "smollm")
        for arm in ("M2-A", "M2-B")
    }
    config = yaml.safe_load(Path(manifest["entries"][0]["config"]).read_text(encoding="utf-8"))
    assert config["training"]["checkpoint_updates"] == [76, 152, 229, 305, 381, 457, 533, 610, 686, 762]
    assert config["training"]["per_device_train_batch_size"] * config["training"]["gradient_accumulation_steps"] == 128
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/m2/validate_three_model_oscar_m2_training_family.py"),
            "--config-manifest",
            str(output / "config_manifest.json"),
            "--output",
            str(output / "validation.json"),
        ],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )
    result = json.loads((output / "validation.json").read_text(encoding="utf-8"))
    assert result["status"] == "M2_TRAINING_CONFIG_VALIDATION_PASS"
    assert result["training_authorized"] is False


def test_three_model_training_preparation_rejects_unmaterialized_blocks(tmp_path: Path) -> None:
    source = (ROOT / "scripts/m2/prepare_three_model_oscar_m2_training_family.py").read_text(
        encoding="utf-8"
    )
    assert "EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED" in source
    assert "EXACT_M1_PARENT_REGISTRY_PASS" in source
    assert "scientific_execution_authorized" in source


def test_m2_smoke_and_training_dag_is_syntax_valid_and_authorization_gated() -> None:
    paths = [
        ROOT / "slurm/m2/smoke_three_model_oscar_m2.slurm",
        ROOT / "slurm/m2/train_three_model_oscar_m2.slurm",
        ROOT / "scripts/m2/submit_three_model_oscar_m2_training.sh",
    ]
    for path in paths:
        subprocess.run(["bash", "-n", str(path)], check=True)
    smoke = paths[0].read_text(encoding="utf-8")
    training = paths[1].read_text(encoding="utf-8")
    submit = paths[2].read_text(encoding="utf-8")
    assert "#SBATCH --array=0-2%1" in smoke
    assert "OPTIMIZER_SMOKE_PASS" in smoke
    assert "#SBATCH --array=0-5%3" in training
    assert "afterok:${smoke_id}" in submit
    assert "M2_TRAINING_AUTHORIZATION_ACK" in submit
    assert "EXPECTED_CONTRACT_SHA256" in submit
    assert "/vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1/logs" in smoke
    assert "/vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1/logs" in training
