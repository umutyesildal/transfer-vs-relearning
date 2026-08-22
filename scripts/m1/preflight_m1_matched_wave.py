#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import yaml

from transfer_vs_relearning.training.clm import load_training_config
from transfer_vs_relearning.utils.io import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed preflight for the matched M1 family.")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--family-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--config", type=Path, action="append", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--minimum-free-bytes", type=int, default=60_000_000_000)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    family = args.family_root.resolve()
    if not str(family).startswith("/vol/tmp2/yesildau/") or family.exists():
        raise ValueError(f"fresh approved family root required: {family}")
    observed_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    if observed_commit != args.expected_commit:
        raise ValueError(f"commit mismatch: {observed_commit} != {args.expected_commit}")
    configs = []
    outputs = set()
    labels = ("olmo", "qwen", "smollm")
    for index, raw in enumerate(args.config):
        path = raw if raw.is_absolute() else repo / raw
        config = load_training_config(path.resolve())
        dataset = config["dataset"]
        dataset_manifest = repo / dataset["dataset_manifest"]
        if sha256_file(dataset_manifest) != "b37268d6f3afbb37f13ef746b80b99169c4d94ced3471aed2ae4aa09dc85b752":
            raise ValueError("Relation V2 manifest drift")
        manifest = json.loads(dataset_manifest.read_text())
        for key in ("train_file", "validation_file"):
            data_path = repo / dataset[key]
            relative = str(data_path.relative_to(repo / dataset["dataset_dir"]))
            if sha256_file(data_path) != manifest["files"][relative]:
                raise ValueError(f"dataset file drift: {relative}")
        model_manifest = Path(config["model"]["base_model_manifest"])
        if not model_manifest.is_file():
            raise FileNotFoundError(model_manifest)
        output = family / "training" / labels[index]
        if output.exists():
            raise ValueError(f"fresh family-owned output required: {output}")
        outputs.add(str(output))
        configs.append({"path": str(path.resolve()), "sha256": sha256_file(path), "model_manifest": str(model_manifest), "model_manifest_sha256": sha256_file(model_manifest), "output_root": str(output)})
    if len(configs) != 3 or len(outputs) != 3:
        raise ValueError("exactly three distinct M1 configs are required")
    free = shutil.disk_usage(family.parent).free
    if free < args.minimum_free_bytes:
        raise RuntimeError(f"scratch capacity gate failed: {free} < {args.minimum_free_bytes}")
    args.manifest.parent.mkdir(parents=True, exist_ok=False)
    write_json(args.manifest, {"schema_version": 1, "status": "passed", "git_commit": observed_commit, "family_root": str(family), "free_bytes": free, "minimum_free_bytes": args.minimum_free_bytes, "configs": configs})
    print(args.manifest)


if __name__ == "__main__":
    main()
