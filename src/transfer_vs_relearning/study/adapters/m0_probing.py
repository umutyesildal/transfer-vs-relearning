from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.utils.io import sha256_file


ENTRYPOINTS = {
    "project_factual": "scripts/m2/evaluate_pre_m2_frozen_suite.py",
    "project_generation_integrity": "scripts/evaluation/evaluate_general_capability.py",
}


def _verify_input(path_value: Any, expected_sha256: Any, label: str) -> Path:
    path = Path(str(path_value)).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Project evaluator input is missing ({label}): {path}")
    if sha256_file(path) != str(expected_sha256):
        raise ValueError(f"Project evaluator input SHA-256 mismatch ({label}): {path}")
    return path


def build_project_probe_command(
    plan: dict[str, Any], lane: dict[str, Any], *, repo_root: Path
) -> list[str]:
    try:
        entrypoint = repo_root / ENTRYPOINTS[lane["adapter"]]
    except KeyError as exc:
        raise ValueError(f"Lane {lane['id']} is not a registered project probe lane") from exc
    if not entrypoint.is_file():
        raise FileNotFoundError(f"Project evaluator entrypoint is missing: {entrypoint}")
    config_path = Path(lane["evaluator_config"])
    if not config_path.is_absolute():
        config_path = repo_root / config_path
    if not config_path.is_file():
        raise FileNotFoundError(f"Project evaluator config is missing: {config_path}")
    if sha256_file(config_path) != lane["evaluator_config_sha256"]:
        raise ValueError(f"Project evaluator config SHA-256 mismatch for lane {lane['id']}")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"Project evaluator config is not a mapping: {config_path}")
    if config.get("run_classification") != plan["run_classification"]:
        raise ValueError(f"Project evaluator classification mismatch for lane {lane['id']}")
    if Path(str(config.get("model_manifest", ""))).resolve() != Path(
        str(plan["model"]["manifest_path"])
    ).resolve():
        raise ValueError(f"Project evaluator model-manifest path mismatch for lane {lane['id']}")

    if lane["adapter"] == "project_generation_integrity":
        if config.get("adapter_engine") != "general_capability":
            raise ValueError("Generation lane requires adapter_engine=general_capability")
        output_root = Path(str(config.get("output_root", ""))).resolve()
        expected_root = Path(str(lane["expected_output_root"])).resolve()
        if output_root != expected_root:
            raise ValueError("Generation evaluator output root mismatch")
        input_sha256 = config.get("input_sha256")
        if not isinstance(input_sha256, dict):
            raise ValueError("Generation evaluator requires input_sha256")
        for key in ("corpus_file", "prompts_file", "completions_file", "synthetic_subjects_file"):
            _verify_input(config["data"][key], input_sha256.get(key), f"generation.{key}")
        return [plan["runtime"]["python"], str(entrypoint), "--config", str(config_path)]

    if config.get("adapter_engine") != "pre_m2_frozen":
        raise ValueError("Factual lane requires adapter_engine=pre_m2_frozen")
    output_root = Path(str(config.get("output_dir", ""))).resolve()
    expected_root = Path(str(lane["expected_output_root"])).resolve()
    if output_root != expected_root:
        raise ValueError("Factual evaluator output root mismatch")
    input_sha256 = config.get("input_sha256")
    if not isinstance(input_sha256, dict):
        raise ValueError("Factual evaluator requires input_sha256")
    _verify_input(
        Path(str(config["dataset_dir"])) / "manifest.json",
        input_sha256.get("dataset_manifest"),
        "factual.dataset_manifest",
    )
    _verify_input(
        config["probe_registry"],
        input_sha256.get("probe_registry"),
        "factual.probe_registry",
    )
    command = [
        plan["runtime"]["python"],
        str(entrypoint),
        "--model-label",
        str(config["model_label"]),
        "--model-manifest",
        str(config["model_manifest"]),
        "--dataset-dir",
        str(config["dataset_dir"]),
        "--probe-registry",
        str(config["probe_registry"]),
        "--output-dir",
        str(config["output_dir"]),
        "--candidate-batch-size",
        str(config["candidate_batch_size"]),
        "--checkpoint-interval",
        str(config["checkpoint_interval"]),
        "--device",
        str(config["device"]),
    ]
    probe_limit = config.get("probe_limit")
    if probe_limit is not None:
        command.extend(["--probe-limit", str(probe_limit)])
    if config.get("bf16") is False:
        command.append("--no-bf16")
    return command
