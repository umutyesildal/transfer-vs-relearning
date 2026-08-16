from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.evaluation.evaluator import _manifest_local_path
from transfer_vs_relearning.training.clm import tokenizer_path_from_manifest
from transfer_vs_relearning.utils.io import sha256_file


def verify_m0_model_manifest(plan: dict[str, Any], *, repo_root: Path) -> tuple[dict[str, Any], Path, Path]:
    manifest_path = Path(plan["model"]["manifest_path"])
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path
    if not manifest_path.is_file():
        raise FileNotFoundError(f"M0 model manifest is missing: {manifest_path}")
    if sha256_file(manifest_path) != plan["model"]["manifest_sha256"]:
        raise ValueError("M0 model manifest SHA-256 mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("model_id") != plan["model"]["repository"]:
        raise ValueError("M0 model repository identity mismatch")
    resolved_revision = manifest.get("resolved_revision") or manifest.get("revision")
    if resolved_revision != plan["model"]["revision"]:
        raise ValueError("M0 model revision identity mismatch")
    model_path = _manifest_local_path(manifest, manifest_path.parent)
    if not model_path.is_dir():
        raise FileNotFoundError(f"M0 local model directory is missing: {model_path}")
    tokenizer_path = tokenizer_path_from_manifest(manifest, repo_root, model_path)
    if not tokenizer_path.is_dir():
        raise FileNotFoundError(f"M0 tokenizer directory is missing: {tokenizer_path}")
    return manifest, model_path, tokenizer_path


def build_lm_eval_command(
    plan: dict[str, Any],
    lane: dict[str, Any],
    *,
    repo_root: Path,
    output_path: Path,
) -> list[str]:
    if lane["adapter"] != "lm_eval":
        raise ValueError(f"Lane {lane['id']} is not an LM Evaluation Harness lane")
    _, model_path, tokenizer_path = verify_m0_model_manifest(plan, repo_root=repo_root)
    runtime = plan["runtime"]
    include_path = repo_root / str(plan["harness"]["include_path"])
    if not include_path.is_dir():
        raise FileNotFoundError(f"M0 Harness include path is missing: {include_path}")
    command = [
        runtime["python"],
        "-m",
        "lm_eval",
        "run",
        "--model",
        "hf",
        "--model_args",
        f"pretrained={model_path}",
        f"tokenizer={tokenizer_path}",
        f"dtype={runtime['precision']}",
        "trust_remote_code=False",
        "local_files_only=True",
        "--tasks",
        *lane["task_ids"],
        "--include_path",
        str(include_path),
        "--num_fewshot",
        str(lane["fewshot"]),
        "--batch_size",
        str(runtime["batch_size"]),
        "--max_batch_size",
        str(runtime["max_batch_size"]),
        "--device",
        runtime["device"],
        "--seed",
        ",".join(str(plan["seeds"][name]) for name in ("python", "numpy", "torch", "fewshot")),
        "--output_path",
        str(output_path),
        "--check_integrity",
        "--show_config",
    ]
    if runtime["log_samples"]:
        command.append("--log_samples")
    if lane.get("limit") is not None:
        if plan["run_classification"] != "test_only_non_scientific":
            raise ValueError("--limit is forbidden outside test_only_non_scientific runs")
        command.extend(["--limit", str(lane["limit"])])
    return command
