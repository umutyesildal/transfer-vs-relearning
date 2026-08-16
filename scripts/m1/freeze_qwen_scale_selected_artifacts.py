#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.utils.io import sha256_file, write_json


KEEP = ("model.safetensors", "config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt", "special_tokens_map.json")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--step", type=int, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--training-manifest", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    checkpoint, output = args.checkpoint.resolve(), args.output_dir.resolve()
    if not str(output).startswith("/vol/tmp2/yesildau/") or output.exists():
        raise ValueError("Output must be a new /vol/tmp2/yesildau directory")
    files = {name: checkpoint / name for name in KEEP if (checkpoint / name).is_file()}
    if "model.safetensors" not in files:
        raise FileNotFoundError(checkpoint / "model.safetensors")
    output.mkdir(parents=True)
    payload = {"status": "frozen_selected_model_only", "model": "Qwen2.5-1.5B", "seed": args.seed, "checkpoint_step": args.step, "checkpoint": str(checkpoint), "training_manifest": str(args.training_manifest.resolve()), "training_manifest_sha256": sha256_file(args.training_manifest.resolve()), "evaluation_root": str(args.evaluation_root.resolve()), "files": {name: {"path": str(path), "sha256": sha256_file(path), "size_bytes": path.stat().st_size} for name, path in files.items()}}
    write_json(output / "selected_artifact_manifest.json", payload)
    (output / "selected_artifact_manifest.sha256").write_text(f"{sha256_file(output / 'selected_artifact_manifest.json')}  selected_artifact_manifest.json\n", encoding="utf-8")
    print(output / "selected_artifact_manifest.json")


if __name__ == "__main__":
    main()
