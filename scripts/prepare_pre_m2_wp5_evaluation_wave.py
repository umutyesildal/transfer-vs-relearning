#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.utils.io import sha256_file, write_csv, write_json


CHECKPOINTS = (25, 50, 75, 100, 150, 200, 252)
RELATIONS = ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")


def _parse_run(value: str) -> tuple[str, Path]:
    label, separator, path = value.partition("=")
    if not separator or not label or not path:
        raise ValueError(f"Run must use LABEL=/absolute/path syntax: {value}")
    return label, Path(path).resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze the WP5 checkpoint evaluation registry.")
    parser.add_argument("--run", action="append", required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--general-corpus", type=Path, required=True)
    parser.add_argument("--checkpoint-step", type=int, action="append")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_root = args.output_root.resolve()
    general_corpus = args.general_corpus.resolve()
    source_manifest = args.source_manifest.resolve()
    checkpoint_steps = tuple(args.checkpoint_step or CHECKPOINTS)
    if not checkpoint_steps or any(step <= 0 for step in checkpoint_steps):
        raise ValueError("Checkpoint steps must be positive")
    if len(set(checkpoint_steps)) != len(checkpoint_steps):
        raise ValueError("Checkpoint steps must be unique")
    if not str(output_root).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")):
        raise ValueError(f"WP5 evaluation root is not approved scratch: {output_root}")
    if not str(general_corpus).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")):
        raise ValueError(f"General-capability corpus is not on approved scratch: {general_corpus}")
    if not general_corpus.is_file():
        raise FileNotFoundError(f"General-capability corpus does not exist: {general_corpus}")
    runs = [_parse_run(value) for value in args.run]
    if len({label for label, _ in runs}) != len(runs):
        raise ValueError("WP5 run labels must be unique")

    rows = []
    for lr_label, run_dir in runs:
        training_manifest_path = run_dir / "training_manifest.json"
        training_manifest = json.loads(training_manifest_path.read_text(encoding="utf-8"))
        if training_manifest.get("status") != "complete":
            raise ValueError(f"Incomplete training run: {run_dir}")
        for step in checkpoint_steps:
            checkpoint_dir = run_dir / "checkpoints" / f"checkpoint-{step}"
            label = f"{lr_label}_step{step}"
            manifest_path = output_root / "model_manifests" / f"{label}.json"
            create_local_model_manifest(
                source_manifest_path=source_manifest,
                local_model_dir=checkpoint_dir,
                output_manifest_path=manifest_path,
                model_id=f"pre_m2_wp5_{label}",
                resolved_revision=f"wp5-{label}",
                training_checkpoint=f"checkpoint-{step}",
                training_run_dir=run_dir,
            )
            print(f"frozen={label}", flush=True)
            general_output = output_root / "general_capability" / label
            general_config_path = output_root / "general_configs" / f"{label}.json"
            write_json(
                general_config_path,
                {
                    "run_name": f"wp5_{label}_general_capability",
                    "output_root": str(general_output),
                    "model_manifest": str(manifest_path),
                    "data": {
                        "corpus_file": str(general_corpus),
                        "prompts_file": str(repo_root / "configs/general_capability/prompts_v1.jsonl"),
                        "completions_file": str(repo_root / "configs/general_capability/completions_v1.jsonl"),
                        "synthetic_subjects_file": str(
                            repo_root / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv"
                        ),
                    },
                    "scoring": {
                        "block_size": 512,
                        "batch_size": 4,
                        "candidate_batch_size": 16,
                        "bootstrap_samples": 2000,
                    },
                    "generation": {"max_new_tokens": 64},
                    "runtime": {"device": "cuda", "bf16": True, "seed": 42},
                },
            )
            exact_output = output_root / "exact_prefix" / label
            exact_config_path = output_root / "exact_configs" / f"{label}.json"
            write_json(
                exact_config_path,
                {
                    "dataset_version": "relation_v2_gate_v1_100_subjects_500_facts_direct",
                    "dataset_dir": str(repo_root / "artifacts/datasets/relation_v2_gate_v1"),
                    "pilot_subject_file": str(
                        repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json"
                    ),
                    "probe_files": {
                        "en": str(
                            repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv"
                        )
                    },
                    "model_manifest": str(manifest_path),
                    "languages": ["en"],
                    "relations": list(RELATIONS),
                    "prompt": {"format": "direct", "template": "{question}", "answer_separator": " "},
                    "scoring": {
                        "primary": "mean_logprob",
                        "secondary": "total_logprob",
                        "tie_breaker": "canonical_object_id",
                    },
                    "runtime": {
                        "bf16": True,
                        "device": "cuda",
                        "candidate_batch_size": 64,
                        "checkpoint_interval": 25,
                        "seed": 42,
                    },
                    "output": {"run_root": str(exact_output)},
                },
            )
            rows.append(
                {
                    "array_index": len(rows),
                    "label": label,
                    "lr_label": lr_label,
                    "checkpoint_step": step,
                    "model_manifest": str(manifest_path),
                    "model_manifest_sha256": sha256_file(manifest_path),
                    "hard_output": str(output_root / "hard_suite" / label),
                    "exact_config": str(exact_config_path),
                    "general_config": str(general_config_path),
                }
            )

    registry_path = output_root / "checkpoint_registry.csv"
    write_csv(registry_path, rows)
    write_json(
        output_root / "wave_manifest.json",
        {
            "status": "frozen_ready_to_submit",
            "checkpoint_steps": list(checkpoint_steps),
            "conditions": [label for label, _ in runs],
            "tasks": len(rows),
            "registry": str(registry_path),
            "registry_sha256": sha256_file(registry_path),
            "source_manifest": str(source_manifest),
            "source_manifest_sha256": sha256_file(source_manifest),
            "training_runs": {
                label: {
                    "path": str(run_dir),
                    "training_manifest_sha256": sha256_file(run_dir / "training_manifest.json"),
                }
                for label, run_dir in runs
            },
        },
    )
    print(registry_path)
    print(f"tasks={len(rows)}")


if __name__ == "__main__":
    main()
