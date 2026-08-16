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


def _general_config(*, label: str, output_root: Path, model_manifest: Path, corpus: Path, repo_root: Path) -> dict[str, object]:
    return {
        "run_name": f"m1_qwen_checkpoint_pareto_{label}",
        "output_root": str(output_root),
        "model_manifest": str(model_manifest),
        "data": {
            "corpus_file": str(corpus),
            "prompts_file": str(repo_root / "configs/general_capability/prompts_v1.jsonl"),
            "completions_file": str(repo_root / "configs/general_capability/completions_v1.jsonl"),
            "synthetic_subjects_file": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv"),
        },
        "scoring": {"block_size": 512, "batch_size": 4, "candidate_batch_size": 16, "bootstrap_samples": 2000},
        "generation": {"max_new_tokens": 64},
        "runtime": {"device": "cuda", "bf16": True, "seed": 42},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze the Document 107 Qwen checkpoint Pareto wave.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--general-corpus", type=Path, required=True)
    parser.add_argument("--probe-registry", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--resume-preparation", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_dir = _scratch(args.run_dir, "training run")
    output_root = _scratch(args.output_root, "wave output root")
    corpus = _scratch(args.general_corpus, "general corpus")
    probe_registry = _scratch(args.probe_registry, "probe registry")
    source_manifest = _scratch(args.source_manifest, "source manifest")
    if output_root.exists():
        if not args.resume_preparation:
            raise FileExistsError(f"Wave namespace already exists: {output_root}")
        allowed = {"model_manifests", "exact_configs", "general_configs", "logs"}
        unexpected = sorted(path.name for path in output_root.iterdir() if path.name not in allowed)
        if unexpected:
            raise ValueError(f"Unsafe preparation resume; unexpected namespaces: {unexpected}")
    for path in (corpus, probe_registry, source_manifest):
        if not path.is_file():
            raise FileNotFoundError(path)
    training_manifest_path = run_dir / "training_manifest.json"
    training_manifest = json.loads(training_manifest_path.read_text(encoding="utf-8"))
    if training_manifest.get("status") != "complete":
        raise ValueError(f"Qwen training run is not complete: {training_manifest_path}")

    rows: list[dict[str, object]] = []
    for step in CHECKPOINTS:
        label = f"qwen_step{step}"
        checkpoint = run_dir / "checkpoints" / f"checkpoint-{step}"
        if not checkpoint.is_dir():
            raise FileNotFoundError(checkpoint)
        model_manifest = output_root / "model_manifests" / f"{label}.json"
        create_local_model_manifest(
            source_manifest_path=source_manifest,
            local_model_dir=checkpoint,
            output_manifest_path=model_manifest,
            model_id=f"m1_qwen_checkpoint_pareto_{label}",
            resolved_revision=f"m1-qwen-seed42-update{step}",
            training_checkpoint=f"checkpoint-{step}",
            training_run_dir=run_dir,
        )
        exact_config = output_root / "exact_configs" / f"{label}.json"
        general_config = output_root / "general_configs" / f"{label}.json"
        write_json(exact_config, {
            "dataset_version": "relation_v2_gate_v1_100_subjects_500_facts_direct",
            "dataset_dir": str(repo_root / "artifacts/datasets/relation_v2_gate_v1"),
            "pilot_subject_file": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json"),
            "probe_files": {"en": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv")},
            "model_manifest": str(model_manifest),
            "languages": ["en"],
            "relations": list(RELATIONS),
            "prompt": {"format": "direct", "template": "{question}", "answer_separator": " "},
            "scoring": {"primary": "mean_logprob", "secondary": "total_logprob", "tie_breaker": "canonical_object_id"},
            "runtime": {"bf16": True, "device": "cuda", "candidate_batch_size": 64, "checkpoint_interval": 25, "seed": 42},
            "output": {"run_root": str(output_root / "exact_prefix" / label)},
        })
        write_json(general_config, _general_config(
            label=label,
            output_root=output_root / "general_capability" / label,
            model_manifest=model_manifest,
            corpus=corpus,
            repo_root=repo_root,
        ))
        rows.append({
            "array_index": len(rows),
            "label": label,
            "checkpoint_step": step,
            "model_manifest": str(model_manifest),
            "model_manifest_sha256": sha256_file(model_manifest),
            "hard_output": str(output_root / "hard_suite" / label),
            "exact_config": str(exact_config),
            "general_config": str(general_config),
        })

    registry = output_root / "checkpoint_registry.csv"
    write_csv(registry, rows)
    write_json(output_root / "wave_manifest.json", {
        "status": "frozen_ready_to_submit",
        "document": 107,
        "exploratory_only": True,
        "checkpoint_steps": list(CHECKPOINTS),
        "tasks": len(rows),
        "registry": str(registry),
        "registry_sha256": sha256_file(registry),
        "source_manifest": str(source_manifest),
        "source_manifest_sha256": sha256_file(source_manifest),
        "training_run": str(run_dir),
        "training_manifest_sha256": sha256_file(training_manifest_path),
        "probe_registry": str(probe_registry),
        "probe_registry_sha256": sha256_file(probe_registry),
        "general_corpus": str(corpus),
        "general_corpus_sha256": sha256_file(corpus),
        "frozen_base_perplexity": BASE_PERPLEXITY,
        "frozen_base_token_hash": BASE_TOKEN_HASH,
        "selection_rule": "earliest checkpoint passing all frozen gates; exploratory diagnostic only",
        "resumed_partial_preparation": bool(args.resume_preparation),
    })
    print(registry)
    print(f"tasks={len(rows)}")


if __name__ == "__main__":
    main()
