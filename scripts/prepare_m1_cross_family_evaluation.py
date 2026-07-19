#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.experiments.m1_cross_family import (
    approved_scratch,
    candidate_by_index,
    candidate_model_manifest,
    candidate_training_root,
    combined_weight_sha256,
    find_completed_final_model,
    load_registry,
    model_weight_hashes,
)
from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.utils.io import sha256_file, write_json


RELATIONS = ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")


def _general_config(*, run_name: str, output_root: Path, model_manifest: Path, corpus: Path, repo_root: Path) -> dict[str, object]:
    return {
        "run_name": run_name,
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
    parser = argparse.ArgumentParser(description="Freeze one Document 105 candidate evaluation contract.")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--candidate-index", type=int, required=True)
    parser.add_argument("--general-corpus", type=Path, required=True)
    parser.add_argument("--probe-registry", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    registry_path = args.registry.resolve()
    registry = load_registry(registry_path)
    candidate = candidate_by_index(registry, args.candidate_index)
    label = str(candidate["label"])
    scratch_root = approved_scratch(Path(str(registry["scratch_root"])))
    output_root = approved_scratch(scratch_root / "evaluations" / label)
    if output_root.exists():
        raise FileExistsError(f"Evaluation namespace already exists: {output_root}")
    corpus, probe_registry = args.general_corpus.resolve(), args.probe_registry.resolve()
    if not corpus.is_file() or not probe_registry.is_file():
        raise FileNotFoundError(f"Frozen evaluation input missing: corpus={corpus}, probes={probe_registry}")

    base_manifest = candidate_model_manifest(registry, candidate)
    final_model = find_completed_final_model(candidate_training_root(registry, candidate))
    training_manifest = final_model.parent / "training_manifest.json"
    if json.loads(training_manifest.read_text(encoding="utf-8")).get("status") != "complete":
        raise ValueError(f"Candidate training is not complete: {training_manifest}")
    trained_manifest = output_root / "model_manifests" / f"{label}_trained.json"
    create_local_model_manifest(
        source_manifest_path=base_manifest,
        local_model_dir=final_model,
        output_manifest_path=trained_manifest,
        model_id=f"m1_cross_family_{label}_seed42",
        resolved_revision=f"m1-cross-family-{label}-seed42-update252",
        training_checkpoint="final_model_update252",
        training_run_dir=final_model.parent,
    )

    exact_config = output_root / "configs/exact_trained.json"
    general_base_config = output_root / "configs/general_base.json"
    general_trained_config = output_root / "configs/general_trained.json"
    write_json(exact_config, {
        "dataset_version": "relation_v2_gate_v1_100_subjects_500_facts_direct",
        "dataset_dir": str(repo_root / "artifacts/datasets/relation_v2_gate_v1"),
        "pilot_subject_file": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json"),
        "probe_files": {"en": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv")},
        "model_manifest": str(trained_manifest),
        "languages": ["en"],
        "relations": list(RELATIONS),
        "prompt": {"format": "direct", "template": "{question}", "answer_separator": " "},
        "scoring": {"primary": "mean_logprob", "secondary": "total_logprob", "tie_breaker": "canonical_object_id"},
        "runtime": {"bf16": True, "device": "cuda", "candidate_batch_size": 64, "checkpoint_interval": 25, "seed": 42},
        "output": {"run_root": str(output_root / "exact_prefix")},
    })
    write_json(general_base_config, _general_config(
        run_name=f"m1_cross_family_{label}_base_general_capability",
        output_root=output_root / "general_capability/base",
        model_manifest=base_manifest,
        corpus=corpus,
        repo_root=repo_root,
    ))
    write_json(general_trained_config, _general_config(
        run_name=f"m1_cross_family_{label}_trained_general_capability",
        output_root=output_root / "general_capability/trained",
        model_manifest=trained_manifest,
        corpus=corpus,
        repo_root=repo_root,
    ))
    weight_hashes = model_weight_hashes(final_model)
    write_json(output_root / "evaluation_manifest.json", {
        "status": "frozen_ready_to_submit",
        "candidate_index": int(candidate["index"]),
        "label": label,
        "model_id": candidate["model_id"],
        "base_resolved_revision": json.loads(base_manifest.read_text(encoding="utf-8"))["resolved_revision"],
        "registry": str(registry_path),
        "registry_sha256": sha256_file(registry_path),
        "training_manifest": str(training_manifest),
        "training_manifest_sha256": sha256_file(training_manifest),
        "final_model": str(final_model),
        "final_weight_hashes": weight_hashes,
        "final_combined_weight_sha256": combined_weight_sha256(weight_hashes),
        "trained_model_manifest": str(trained_manifest),
        "trained_model_manifest_sha256": sha256_file(trained_manifest),
        "probe_registry": str(probe_registry),
        "probe_registry_sha256": sha256_file(probe_registry),
        "general_corpus": str(corpus),
        "general_corpus_sha256": sha256_file(corpus),
        "hard_output": str(output_root / "hard_suite"),
        "exact_config": str(exact_config),
        "general_base_config": str(general_base_config),
        "general_trained_config": str(general_trained_config),
    })
    print(output_root / "evaluation_manifest.json")


if __name__ == "__main__":
    main()
