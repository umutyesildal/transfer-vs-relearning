#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOKENIZER_FILES = (
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
    "merges.txt",
    "special_tokens_map.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def allocated_bytes(path: Path) -> int:
    output = subprocess.check_output(
        ["du", "-sx", "--block-size=1", str(path)], text=True
    )
    return int(output.split()[0])


def verify_declared_file(name: str, item: dict[str, Any]) -> Path:
    source = Path(item["path"]).resolve()
    if source.name != name or not source.is_file():
        raise ValueError(f"Invalid selected file declaration for {name}: {source}")
    if source.stat().st_size != int(item["size_bytes"]):
        raise ValueError(f"Selected file size mismatch: {source}")
    if sha256_file(source) != item["sha256"]:
        raise ValueError(f"Selected file hash mismatch: {source}")
    return source


def collect_sources(manifest_paths: list[Path]) -> tuple[list[dict[str, Any]], Path, dict[str, str]]:
    selections: list[dict[str, Any]] = []
    tokenizer_root: Path | None = None
    tokenizer_hashes: dict[str, str] = {}

    for manifest_path in manifest_paths:
        manifest_path = manifest_path.resolve()
        payload = load_json(manifest_path)
        if payload.get("status") != "frozen_selected_model_only":
            raise ValueError(f"Selected manifest is not frozen: {manifest_path}")
        seed = int(payload["seed"])
        step = int(payload["checkpoint_step"])
        label = f"seed{seed}_step{step}"
        files = {
            name: verify_declared_file(name, item)
            for name, item in payload["files"].items()
        }
        if "model.safetensors" not in files:
            raise ValueError(f"Selected model weights are absent: {manifest_path}")

        training_manifest = Path(payload["training_manifest"]).resolve()
        if sha256_file(training_manifest) != payload["training_manifest_sha256"]:
            raise ValueError(f"Training manifest hash mismatch: {training_manifest}")
        training = load_json(training_manifest)
        model = training["model"]
        current_tokenizer_root = Path(
            model["base_model_manifest_payload"]["local_path_absolute"]
        ).resolve()
        current_hashes = {
            name: sha256_file(current_tokenizer_root / name)
            for name in TOKENIZER_FILES
            if (current_tokenizer_root / name).is_file()
        }
        for required in ("tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt"):
            if required not in current_hashes:
                raise FileNotFoundError(current_tokenizer_root / required)
        if tokenizer_root is None:
            tokenizer_root = current_tokenizer_root
            tokenizer_hashes = current_hashes
        elif current_hashes != tokenizer_hashes:
            raise ValueError("Selected artifacts do not share the same pinned tokenizer")

        selections.append(
            {
                "label": label,
                "seed": seed,
                "step": step,
                "manifest_path": manifest_path,
                "manifest_sha256": sha256_file(manifest_path),
                "manifest_sidecar": manifest_path.with_name("selected_artifact_manifest.sha256"),
                "training_manifest": training_manifest,
                "base_model_manifest": Path(model["base_model_manifest"]).resolve(),
                "dataset_manifest": Path(training["dataset"]["dataset_manifest"]).resolve(),
                "checkpoint": Path(payload["checkpoint"]).resolve(),
                "files": files,
            }
        )

    if tokenizer_root is None or len({item["label"] for item in selections}) != len(selections):
        raise ValueError("Selected manifest list is empty or contains duplicate seed/step labels")
    return selections, tokenizer_root, tokenizer_hashes


def copy_verified(source: Path, destination: Path, expected_sha256: str | None = None) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    observed = sha256_file(destination)
    expected = expected_sha256 or sha256_file(source)
    if observed != expected:
        raise ValueError(f"Copied file hash mismatch: {destination}")
    return {
        "path": str(destination.relative_to(destination.parents[1])),
        "sha256": observed,
        "size_bytes": destination.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a verified model-only home backup of frozen selected Qwen artifacts."
    )
    parser.add_argument("--selected-manifest", type=Path, action="append", required=True)
    parser.add_argument("--home-root", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--max-home-gb", type=int, default=30)
    args = parser.parse_args()

    home_root = args.home_root.resolve()
    destination = args.destination.resolve()
    if destination == home_root or home_root not in destination.parents:
        raise ValueError("Destination must be a child of the declared HU home root")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite home archive: {destination}")

    selections, tokenizer_root, tokenizer_hashes = collect_sources(args.selected_manifest)
    unique_sources = {
        source
        for item in selections
        for source in (
            *item["files"].values(),
            item["manifest_path"],
            item["training_manifest"],
            item["base_model_manifest"],
            item["dataset_manifest"],
        )
        if source.is_file()
    }
    unique_sources.update(tokenizer_root / name for name in tokenizer_hashes)
    source_bytes = sum(path.stat().st_size for path in unique_sources)
    home_bytes_before = allocated_bytes(home_root)
    max_home_bytes = args.max_home_gb * 1_000_000_000
    if home_bytes_before + source_bytes >= max_home_bytes:
        raise ValueError(
            f"Projected home use exceeds {args.max_home_gb} GB: "
            f"{home_bytes_before + source_bytes} bytes"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = Path(tempfile.mkdtemp(prefix=f".{destination.name}.partial-", dir=destination.parent))
    try:
        archive: dict[str, Any] = {
            "status": "frozen_home_backup_verified",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "policy": {
                "administrator": "Ralf Moritz",
                "approved_home_limit_gb": args.max_home_gb,
                "scope": "two frozen selected Qwen M1 model-only artifacts",
            },
            "home_root": str(home_root),
            "destination": str(destination),
            "home_bytes_before": home_bytes_before,
            "copied_source_bytes": source_bytes,
            "projected_home_bytes": home_bytes_before + source_bytes,
            "tokenizer": {"source_root": str(tokenizer_root), "files": {}},
            "models": {},
        }
        for name, expected_hash in tokenizer_hashes.items():
            archive["tokenizer"]["files"][name] = copy_verified(
                tokenizer_root / name, partial / "tokenizer" / name, expected_hash
            )

        for item in selections:
            label = item["label"]
            model_dir = partial / label
            copied_files = {
                name: copy_verified(source, model_dir / name)
                for name, source in item["files"].items()
            }
            metadata_files = {
                "source_selected_artifact_manifest.json": item["manifest_path"],
                "source_training_manifest.json": item["training_manifest"],
                "source_base_model_manifest.json": item["base_model_manifest"],
                "source_dataset_manifest.json": item["dataset_manifest"],
            }
            if item["manifest_sidecar"].is_file():
                metadata_files["source_selected_artifact_manifest.sha256"] = item["manifest_sidecar"]
            copied_metadata = {
                name: copy_verified(source, model_dir / name)
                for name, source in metadata_files.items()
            }
            archive["models"][label] = {
                "seed": item["seed"],
                "checkpoint_step": item["step"],
                "source_checkpoint": str(item["checkpoint"]),
                "source_selected_manifest": str(item["manifest_path"]),
                "source_selected_manifest_sha256": item["manifest_sha256"],
                "files": copied_files,
                "metadata": copied_metadata,
            }

        manifest_path = partial / "archive_manifest.json"
        manifest_path.write_text(
            json.dumps(archive, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        manifest_hash = sha256_file(manifest_path)
        (partial / "archive_manifest.sha256").write_text(
            f"{manifest_hash}  archive_manifest.json\n", encoding="utf-8"
        )
        os.replace(partial, destination)
    except BaseException:
        shutil.rmtree(partial, ignore_errors=True)
        raise

    print(
        json.dumps(
            {
                "status": "passed",
                "destination": str(destination),
                "models": [item["label"] for item in selections],
                "source_bytes": source_bytes,
                "archive_manifest_sha256": manifest_hash,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
