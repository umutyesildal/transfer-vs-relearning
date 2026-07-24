#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.utils.io import sha256_file, write_csv, write_json


CHECKPOINTS = (25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252)
RELATIONS = ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")
APPROVED_PREFIXES = ("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")
BASE_PERPLEXITY = 14.6988390227992
BASE_TOKEN_HASH = "be2effefc9f0655b0fc5bc3052ecfd18b51bdfa48bffa1ab2d4f0c217b81c78f"


def _scratch(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not str(resolved).startswith(APPROVED_PREFIXES):
        raise ValueError(f"{label} is not on approved scratch: {resolved}")
    return resolved


def _one_run(root: Path) -> Path:
    completed = [
        path.parent
        for path in root.glob("*/training_manifest.json")
        if json.loads(path.read_text()).get("status") == "complete"
    ]
    if len(completed) != 1:
        raise ValueError(f"Expected one completed run under {root}, found {len(completed)}")
    return completed[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training-root", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--general-corpus", type=Path, required=True)
    parser.add_argument("--probe-registry", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    training_root = _scratch(args.training_root, "training root")
    output_root = _scratch(args.output_root, "evaluation root")
    corpus = _scratch(args.general_corpus, "general corpus")
    probes = _scratch(args.probe_registry, "probe registry")
    source_manifest = _scratch(args.source_manifest, "source manifest")
    if output_root.exists():
        raise FileExistsError(output_root)
    for path in (corpus, probes, source_manifest):
        if not path.is_file():
            raise FileNotFoundError(path)

    run = _one_run(training_root)
    training_manifest = run / "training_manifest.json"
    rows: list[dict[str, object]] = []
    for step in CHECKPOINTS:
        checkpoint = run / "checkpoints" / f"checkpoint-{step}"
        if not checkpoint.is_dir():
            raise FileNotFoundError(checkpoint)
        label = f"replay_seed43_step{step}"
        model_manifest = output_root / "model_manifests" / f"{label}.json"
        create_local_model_manifest(
            source_manifest_path=source_manifest,
            local_model_dir=checkpoint,
            output_manifest_path=model_manifest,
            model_id=f"m1_retention_{label}",
            resolved_revision=f"m1-retention-replay-seed43-update{step}",
            training_checkpoint=f"checkpoint-{step}",
            training_run_dir=run,
        )
        exact_config = output_root / "exact_configs" / f"{label}.json"
        general_config = output_root / "general_configs" / f"{label}.json"
        write_json(exact_config, {
            "dataset_version": "relation_v2_gate_v1_100_subjects_500_facts_direct",
            "dataset_dir": str(repo / "artifacts/datasets/relation_v2_gate_v1"),
            "pilot_subject_file": str(repo / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json"),
            "probe_files": {"en": str(repo / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv")},
            "model_manifest": str(model_manifest), "languages": ["en"], "relations": list(RELATIONS),
            "prompt": {"format": "direct", "template": "{question}", "answer_separator": " "},
            "scoring": {"primary": "mean_logprob", "secondary": "total_logprob", "tie_breaker": "canonical_object_id"},
            "runtime": {"bf16": True, "device": "cuda", "candidate_batch_size": 64, "checkpoint_interval": 25, "seed": 43},
            "output": {"run_root": str(output_root / "exact_prefix" / label)},
        })
        write_json(general_config, {
            "run_name": f"m1_retention_{label}", "output_root": str(output_root / "general_capability" / label),
            "model_manifest": str(model_manifest),
            "data": {"corpus_file": str(corpus), "prompts_file": str(repo / "configs/general_capability/prompts_v1.jsonl"),
                     "completions_file": str(repo / "configs/general_capability/completions_v1.jsonl"),
                     "synthetic_subjects_file": str(repo / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv")},
            "scoring": {"block_size": 512, "batch_size": 4, "candidate_batch_size": 16, "bootstrap_samples": 2000},
            "generation": {"max_new_tokens": 64}, "runtime": {"device": "cuda", "bf16": True, "seed": 43},
        })
        rows.append({"array_index": len(rows), "condition": "replay_seed43", "checkpoint_step": step,
                     "label": label, "model_manifest": str(model_manifest),
                     "model_manifest_sha256": sha256_file(model_manifest),
                     "hard_output": str(output_root / "hard_suite" / label),
                     "exact_config": str(exact_config), "general_config": str(general_config)})

    registry = output_root / "checkpoint_registry.csv"
    write_csv(registry, rows)
    write_json(output_root / "wave_manifest.json", {
        "status": "frozen_ready_for_preflight", "document": 119, "condition": "replay_seed43",
        "seed": 43, "data_seed": 43, "checkpoint_steps": list(CHECKPOINTS), "tasks": len(rows),
        "training_run": str(run), "training_manifest_sha256": sha256_file(training_manifest),
        "registry_sha256": sha256_file(registry), "source_manifest_sha256": sha256_file(source_manifest),
        "probe_registry_sha256": sha256_file(probes), "general_corpus_sha256": sha256_file(corpus),
        "frozen_base_perplexity": BASE_PERPLEXITY, "frozen_base_token_hash": BASE_TOKEN_HASH,
        "selection_rule": "earliest seed43 checkpoint passing all corrected primary gates; preserve legacy short-output sensitivity",
    })
    print(registry)
    print(f"tasks={len(rows)}")


if __name__ == "__main__":
    main()
