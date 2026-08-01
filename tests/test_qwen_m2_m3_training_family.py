from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from transfer_vs_relearning.training.clm import load_training_config


def _run_script(root: Path, script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / script), *args],
        check=True,
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        capture_output=True,
        text=True,
    )


def test_prepare_and_validate_qwen_m2_m3_family_contract(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    block_root = tmp_path / "blocks"
    block_root.mkdir()
    artifacts = {}
    for name in ("m2_train", "m3_train", "shared_validation"):
        path = block_root / f"{name}.jsonl"
        path.write_text('{"input_ids": [1], "attention_mask": [1]}\n', encoding="utf-8")
        artifacts[name] = {"path": str(path)}
    block_manifest = block_root / "manifest.json"
    block_manifest.write_text(json.dumps({"artifacts": artifacts}), encoding="utf-8")

    models = []
    for seed in (42, 43):
        model_path = tmp_path / f"model_{seed}.json"
        model_path.write_text(json.dumps({"seed": seed}), encoding="utf-8")
        models.append(
            {
                "seed": seed,
                "training_seed": seed + 100,
                "data_seed": seed + 200,
                "base_model_manifest": str(model_path),
            }
        )
    contract = tmp_path / "contract.json"
    contract.write_text(
        json.dumps(
            {
                "status": "frozen",
                "block_manifest": str(block_manifest),
                "training_output_root": str(tmp_path / "training"),
                "parameters": {
                    "block_size": 1,
                    "update_steps": 8,
                    "fact_cycles": 2,
                    "learning_rate": 1e-5,
                    "per_device_train_batch_size": 1,
                    "per_device_eval_batch_size": 1,
                    "gradient_accumulation_steps": 1,
                    "warmup_steps": 1,
                    "save_steps": 2,
                    "eval_steps": 2,
                },
                "models": models,
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "prepared"
    _run_script(
        root,
        "prepare_qwen_m2_m3_training_family.py",
        "--contract",
        str(contract),
        "--output-dir",
        str(output),
        "--allow-local-paths",
    )
    manifest = json.loads((output / "config_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "prepared"
    assert {(item["arm"], item["seed"]) for item in manifest["configs"]} == {
        ("m2_clean", 42),
        ("m2_clean", 43),
        ("m3_fact", 42),
        ("m3_fact", 43),
    }
    config = load_training_config(Path(manifest["configs"][0]["config"]))
    assert config["dataset"]["pretokenized"] is True
    assert config["training"]["loss_mode"] == "full_sequence"
    assert config["training"]["max_steps"] == 8

    validation = tmp_path / "validation.json"
    _run_script(
        root,
        "validate_qwen_m2_m3_training_family.py",
        "--config-manifest",
        str(output / "config_manifest.json"),
        "--allow-local-paths",
        "--output",
        str(validation),
    )
    assert json.loads(validation.read_text(encoding="utf-8"))["status"] == "passed"


def test_qwen_m2_m3_slurm_launchers_are_syntax_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    for filename in (
        "slurm/preflight_qwen_m2_m3.slurm",
        "slurm/train_qwen_m2_m3_array.slurm",
        "slurm/smoke_qwen_m2_m3.slurm",
        "scripts/submit_qwen_m2_m3.sh",
        "scripts/submit_qwen_m2_m3_smoke.sh",
    ):
        subprocess.run(["bash", "-n", str(root / filename)], check=True)
