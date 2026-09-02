from __future__ import annotations

"""Hash-close one exact M2 run into update-addressable evaluation bindings."""

import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.utils.io import sha256_file, write_json


M2_CHECKPOINT_UPDATES = (76, 152, 229, 305, 381, 457, 533, 610, 686, 762)


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON mapping required: {path}")
    return payload


def finalize_m2_training_outputs(
    run_dir: Path,
    binding_root: Path,
    *,
    role: str,
    arm: str,
) -> dict[str, Any]:
    """Validate one completed M2 run and create immutable model-only checkpoint manifests."""

    if role not in {"olmo", "qwen", "smollm"} or arm not in {"M2-A", "M2-B"}:
        raise ValueError("M2 binding role/arm identity is invalid")
    run_dir = run_dir.resolve()
    binding_root = binding_root.resolve()
    if binding_root.exists():
        raise FileExistsError(f"M2 binding root already exists: {binding_root}")
    training_path = run_dir / "training_manifest.json"
    if not training_path.is_file() or training_path.is_symlink():
        raise FileNotFoundError(training_path)
    training = _json(training_path)
    result = training.get("result")
    config = training.get("config")
    if training.get("status") != "complete" or not isinstance(result, dict) or not isinstance(config, dict):
        raise ValueError("M2 training manifest is not complete")
    metadata = config.get("metadata", {})
    recipe = config.get("training", {})
    if (
        metadata.get("role") != role
        or metadata.get("arm") != arm
        or recipe.get("max_steps") != 762
        or tuple(recipe.get("checkpoint_updates", ())) != M2_CHECKPOINT_UPDATES
        or result.get("estimated_optimizer_steps") != 762
        or tuple(result.get("checkpoint_updates", ())) != M2_CHECKPOINT_UPDATES
    ):
        raise ValueError("M2 identity, endpoint or checkpoint schedule drift")
    base_manifest_path = Path(str(training.get("model", {}).get("base_model_manifest", ""))).resolve()
    if (
        not base_manifest_path.is_file()
        or base_manifest_path.is_symlink()
        or sha256_file(base_manifest_path)
        != training.get("model", {}).get("base_model_manifest_sha256")
    ):
        raise ValueError("M2 parent model manifest identity drift")
    checkpoint_dirs = [Path(str(value)).resolve() for value in result.get("checkpoint_dirs", [])]
    expected_dirs = [run_dir / "checkpoints" / f"checkpoint-{update}" for update in M2_CHECKPOINT_UPDATES]
    if (
        len(checkpoint_dirs) != len(expected_dirs)
        or set(checkpoint_dirs) != set(expected_dirs)
        or any(not path.is_dir() for path in checkpoint_dirs)
    ):
        raise ValueError("M2 run does not contain exactly the ten precommitted checkpoints")
    # train_clm records glob results in lexicographic path order, placing checkpoint-76
    # between checkpoint-686 and checkpoint-762.  The manifest is a closed membership set;
    # normalize only its order after exact path equality has passed.
    checkpoint_dirs = expected_dirs

    binding_root.mkdir(parents=True)
    model_root = binding_root / "model_manifests"
    model_root.mkdir()
    checkpoints: list[dict[str, Any]] = []
    for update, checkpoint_dir in zip(M2_CHECKPOINT_UPDATES, checkpoint_dirs, strict=True):
        manifest_path = model_root / f"update-{update:03d}.json"
        payload = create_local_model_manifest(
            source_manifest_path=base_manifest_path,
            local_model_dir=checkpoint_dir,
            output_manifest_path=manifest_path,
            model_id=f"{role}_{arm.lower().replace('-', '_')}_update_{update:03d}",
            resolved_revision=f"m2-oscar-{role}-{arm.lower()}-update-{update:03d}",
            training_checkpoint=f"checkpoint-{update}",
            training_run_dir=run_dir,
        )
        checkpoints.append(
            {
                "state": arm,
                "role": role,
                "arm": arm,
                "update": update,
                "full": update in {381, 762},
                "model_path": str(checkpoint_dir),
                "model_manifest": str(manifest_path),
                "model_manifest_sha256": sha256_file(manifest_path),
                "model_file_hashes": payload["file_hashes"],
            }
        )
    checkpoint_manifest = {
        "schema_version": 1,
        "status": "M2_CHECKPOINT_BINDING_PASS",
        "role": role,
        "arm": arm,
        "run_dir": str(run_dir),
        "training_manifest": str(training_path),
        "training_manifest_sha256": sha256_file(training_path),
        "parent_model_manifest": str(base_manifest_path),
        "parent_model_manifest_sha256": sha256_file(base_manifest_path),
        "checkpoint_count": len(checkpoints),
        "checkpoints": checkpoints,
        "ready_for_evaluation_contract": False,
    }
    manifest_path = binding_root / "checkpoint_manifest.json"
    write_json(manifest_path, checkpoint_manifest)
    final = {
        "schema_version": 1,
        "status": "M2_TRAINING_OUTPUT_BINDING_PASS",
        "role": role,
        "arm": arm,
        "checkpoint_manifest": str(manifest_path),
        "checkpoint_manifest_sha256": sha256_file(manifest_path),
        "training_authorized": False,
        "evaluation_authorized": False,
    }
    write_json(binding_root / "binding_result.json", final)
    return final
