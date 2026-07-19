from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.training.clm import estimate_optimizer_steps
from transfer_vs_relearning.utils.io import sha256_file


APPROVED_SCRATCH_PREFIXES = ("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")
EXPECTED_LABELS = ("qwen", "stablelm", "gemma", "llama")


def approved_scratch(path: Path) -> Path:
    resolved = path.resolve()
    if not str(resolved).startswith(APPROVED_SCRATCH_PREFIXES):
        raise ValueError(f"Path must resolve under approved scratch: {resolved}")
    return resolved


def load_registry(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Cross-family registry must contain a mapping")
    validate_registry(payload)
    return payload


def validate_registry(payload: dict[str, Any]) -> None:
    if payload.get("version") != "m1_cross_family_screen_v1":
        raise ValueError("Unexpected cross-family registry version")
    approved_scratch(Path(str(payload["scratch_root"])))
    approved_scratch(Path(str(payload["dataset_root"])))
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 4:
        raise ValueError("Registry requires exactly four candidate entries")
    labels = tuple(str(candidate["label"]) for candidate in candidates)
    indices = tuple(int(candidate["index"]) for candidate in candidates)
    if labels != EXPECTED_LABELS or indices != tuple(range(4)):
        raise ValueError(f"Candidate order must be {EXPECTED_LABELS} at indices 0..3")
    if any(not candidate.get("model_id") or not candidate.get("requested_revision") for candidate in candidates):
        raise ValueError("Every candidate needs a model ID and requested revision")
    if not all(bool(candidate.get("required")) for candidate in candidates[:3]):
        raise ValueError("Qwen, StableLM, and Gemma must remain required")
    if bool(candidates[3].get("required")):
        raise ValueError("Llama must remain conditional")
    if int(payload.get("expected_train_rows", 0)) != 3500:
        raise ValueError("Cross-family training budget must remain 3,500 rows")
    if int(payload.get("expected_validation_rows", 0)) != 500:
        raise ValueError("Cross-family validation budget must remain 500 rows")
    if int(payload.get("expected_optimizer_updates", 0)) != 252:
        raise ValueError("Cross-family endpoint must remain update 252")


def candidate_by_index(registry: dict[str, Any], index: int) -> dict[str, Any]:
    candidates = [candidate for candidate in registry["candidates"] if int(candidate["index"]) == index]
    if len(candidates) != 1:
        raise ValueError(f"Unknown or duplicate candidate index: {index}")
    return dict(candidates[0])


def candidate_by_label(registry: dict[str, Any], label: str) -> dict[str, Any]:
    candidates = [candidate for candidate in registry["candidates"] if str(candidate["label"]) == label]
    if len(candidates) != 1:
        raise ValueError(f"Unknown or duplicate candidate label: {label}")
    return dict(candidates[0])


def safe_model_dir_name(model_id: str) -> str:
    return model_id.replace("/", "__")


def candidate_model_root(registry: dict[str, Any], candidate: dict[str, Any]) -> Path:
    return approved_scratch(Path(str(registry["scratch_root"])) / "models" / safe_model_dir_name(str(candidate["model_id"])))


def candidate_model_manifest(registry: dict[str, Any], candidate: dict[str, Any]) -> Path:
    return candidate_model_root(registry, candidate) / "model_manifest.json"


def candidate_training_root(registry: dict[str, Any], candidate: dict[str, Any]) -> Path:
    return approved_scratch(Path(str(registry["scratch_root"])) / "training" / str(candidate["label"]))


def estimated_family_gib(registry: dict[str, Any], candidates: list[dict[str, Any]] | None = None) -> int:
    selected = candidates or list(registry["candidates"])
    checkpoints = int(registry["expected_checkpoints_per_candidate"])
    candidate_total = sum(
        int(candidate["estimated_checkpoint_gib"]) * checkpoints + int(candidate["estimated_download_gib"])
        for candidate in selected
    )
    return candidate_total + int(registry.get("estimated_shared_overhead_gib", 0))


def materialize_training_config(
    *,
    registry: dict[str, Any],
    candidate: dict[str, Any],
    template: dict[str, Any],
    dataset_root: Path,
) -> dict[str, Any]:
    payload = json.loads(json.dumps(template))
    scratch_root = approved_scratch(Path(str(registry["scratch_root"])))
    dataset_root = approved_scratch(dataset_root)
    model_manifest = candidate_model_manifest(registry, candidate)
    if not model_manifest.is_file():
        raise FileNotFoundError(f"Candidate model manifest is missing: {model_manifest}")
    payload["dataset"].update(
        {
            "dataset_dir": str(dataset_root),
            "dataset_manifest": str(dataset_root / "dataset_manifest.json"),
            "train_file": str(dataset_root / "train.jsonl"),
            "validation_file": str(dataset_root / "validation.jsonl"),
        }
    )
    payload["model"]["base_model_manifest"] = str(model_manifest)
    payload["training"]["run_name"] = f"m1_cross_family_{candidate['label']}_seed42"
    payload["training"]["output_root"] = str(candidate_training_root(registry, candidate))
    steps = estimate_optimizer_steps(
        int(registry["expected_train_rows"]),
        int(payload["training"]["per_device_train_batch_size"]),
        int(payload["training"]["gradient_accumulation_steps"]),
        float(payload["training"]["num_train_epochs"]),
        int(payload["runtime"]["world_size"]),
    )
    if steps != int(registry["expected_optimizer_updates"]):
        raise ValueError(f"Materialized config has {steps} updates instead of 252")
    if payload["training"]["loss_mode"] != "answer_only" or bool(payload["training"]["supervise_eos"]):
        raise ValueError("Cross-family loss contract must remain answer-only and EOS-false")
    if scratch_root not in candidate_training_root(registry, candidate).parents:
        raise ValueError("Candidate training root escaped the family scratch root")
    return payload


def find_completed_final_model(training_root: Path) -> Path:
    training_root = approved_scratch(training_root)
    completed: list[Path] = []
    for manifest_path in sorted(training_root.glob("*/training_manifest.json")):
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        final_model = manifest_path.parent / "final_model"
        if payload.get("status") == "complete" and final_model.is_dir():
            completed.append(final_model)
    if len(completed) != 1:
        raise ValueError(f"Expected exactly one completed training run under {training_root}, found {len(completed)}")
    return completed[0]


def model_weight_hashes(model_dir: Path) -> dict[str, str]:
    weight_files = sorted(path for path in model_dir.glob("*.safetensors") if path.is_file())
    if not weight_files:
        raise ValueError(f"No safetensors weights found in {model_dir}")
    return {path.name: sha256_file(path) for path in weight_files}


def combined_weight_sha256(hashes: dict[str, str]) -> str:
    canonical = json.dumps(hashes, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
