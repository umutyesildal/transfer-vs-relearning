#!/usr/bin/env python3
"""Freeze model-only copies of the completed Qwen M2/M3 endpoint checkpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


MODEL_FILES = (
    "model.safetensors",
    "config.json",
    "generation_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "chat_template.jinja",
)
EXCLUDED_FILES = (
    "optimizer.pt",
    "scheduler.pt",
    "rng_state.pth",
    "trainer_state.json",
    "training_args.bin",
)
EXPECTED_STATES = {
    "m2_clean_seed42",
    "m2_clean_seed43",
    "m3_fact_seed42",
    "m3_fact_seed43",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_source(value: str) -> tuple[str, Path]:
    state, separator, path = value.partition("=")
    if not separator or not state or not path:
        raise argparse.ArgumentTypeError("source must be STATE=CHECKPOINT_PATH")
    return state, Path(path)


def parse_commit(value: str) -> str:
    return value or "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-commit", type=parse_commit, default="unknown")
    parser.add_argument(
        "--source",
        type=parse_source,
        action="append",
        required=True,
        help="Endpoint source in STATE=CHECKPOINT_PATH form; provide exactly four.",
    )
    args = parser.parse_args()

    sources = dict(args.source)
    if set(sources) != EXPECTED_STATES:
        missing = sorted(EXPECTED_STATES - set(sources))
        extra = sorted(set(sources) - EXPECTED_STATES)
        raise ValueError(f"source states mismatch; missing={missing}, extra={extra}")

    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output_dir}")

    source_records: dict[str, dict[str, object]] = {}
    for state in sorted(EXPECTED_STATES):
        source = sources[state].resolve()
        if not source.is_dir() or source.name != "checkpoint-128":
            raise FileNotFoundError(f"invalid checkpoint source for {state}: {source}")
        missing = [name for name in MODEL_FILES if not (source / name).is_file()]
        if missing:
            raise FileNotFoundError(f"missing model-only files for {state}: {missing}")
        training_manifest = source.parent.parent / "training_manifest.json"
        source_records[state] = {
            "source_checkpoint": str(source),
            "source_training_manifest": str(training_manifest),
            "source_training_manifest_sha256": (
                sha256_file(training_manifest) if training_manifest.is_file() else None
            ),
        }

    output_dir.mkdir(parents=True)
    files: dict[str, dict[str, object]] = {}
    for state in sorted(EXPECTED_STATES):
        source = Path(str(source_records[state]["source_checkpoint"]))
        destination = output_dir / state
        destination.mkdir()
        for name in MODEL_FILES:
            source_file = source / name
            retained_file = destination / name
            shutil.copy2(source_file, retained_file)
            source_hash = sha256_file(source_file)
            retained_hash = sha256_file(retained_file)
            if source_hash != retained_hash:
                raise RuntimeError(f"copy hash mismatch for {state}/{name}")
            files[f"{state}/{name}"] = {
                "source": str(source_file),
                "retained": str(retained_file),
                "size_bytes": retained_file.stat().st_size,
                "source_sha256": source_hash,
                "retained_sha256": retained_hash,
            }

    manifest = {
        "artifact": "qwen_m2_m3_checkpoint_128_model_only_retention_v1",
        "status": "completed",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "repository_commit": args.repo_commit,
        "output_dir": str(output_dir),
        "states": source_records,
        "included_files_per_state": list(MODEL_FILES),
        "excluded_checkpoint_files": list(EXCLUDED_FILES),
        "files": files,
        "scientific_boundary": "model_only_retention; no cleanup or gate change",
    }
    manifest_path = output_dir / "model_only_retention_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksum_lines = [
        f"{entry['retained_sha256']}  {relative}"
        for relative, entry in sorted(files.items())
    ]
    (output_dir / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), "manifest": str(manifest_path), "files": len(files)}, sort_keys=True))


if __name__ == "__main__":
    main()
