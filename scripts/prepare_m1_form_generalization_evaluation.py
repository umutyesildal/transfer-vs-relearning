#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.utils.io import sha256_file, write_csv, write_json


RELATIONS = ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")


def _parse_model(value: str) -> tuple[str, Path]:
    label, separator, path = value.partition("=")
    if not separator or not label or not path:
        raise ValueError("Model must use LABEL=/absolute/final_model/path syntax")
    return label, Path(path).resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze final-model evaluation registry for M1 form generalization.")
    parser.add_argument("--model", action="append", required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--general-corpus", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    output_root = args.output_root.resolve()
    source_manifest = args.source_manifest.resolve()
    general_corpus = args.general_corpus.resolve()
    if not str(output_root).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")):
        raise ValueError("Evaluation output root must be on approved scratch")
    if not general_corpus.is_file():
        raise FileNotFoundError(f"Generic-retention corpus missing: {general_corpus}")
    models = [_parse_model(value) for value in args.model]
    if {label for label, _ in models} != {"control_seed42", "balanced_ab_seed42"}:
        raise ValueError("Registry requires exactly control_seed42 and balanced_ab_seed42 final models")
    rows = []
    for label, model_dir in models:
        run_dir = model_dir.parent
        training_manifest = run_dir / "training_manifest.json"
        if json.loads(training_manifest.read_text(encoding="utf-8")).get("status") != "complete":
            raise ValueError(f"Training run incomplete: {run_dir}")
        manifest_path = output_root / "model_manifests" / f"{label}.json"
        create_local_model_manifest(
            source_manifest_path=source_manifest,
            local_model_dir=model_dir,
            output_manifest_path=manifest_path,
            model_id=f"m1_form_generalization_{label}",
            resolved_revision=f"m1-form-generalization-{label}",
            training_checkpoint="final_model",
            training_run_dir=run_dir,
        )
        exact_config = output_root / "exact_configs" / f"{label}.json"
        general_config = output_root / "general_configs" / f"{label}.json"
        write_json(exact_config, {
            "dataset_version": "relation_v2_gate_v1_100_subjects_500_facts_direct",
            "dataset_dir": str(repo_root / "artifacts/datasets/relation_v2_gate_v1"),
            "pilot_subject_file": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json"),
            "probe_files": {"en": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv")},
            "model_manifest": str(manifest_path), "languages": ["en"], "relations": list(RELATIONS),
            "prompt": {"format": "direct", "template": "{question}", "answer_separator": " "},
            "scoring": {"primary": "mean_logprob", "secondary": "total_logprob", "tie_breaker": "canonical_object_id"},
            "runtime": {"bf16": True, "device": "cuda", "candidate_batch_size": 64, "checkpoint_interval": 25, "seed": 42},
            "output": {"run_root": str(output_root / "exact_prefix" / label)},
        })
        write_json(general_config, {
            "run_name": f"m1_form_generalization_{label}_general_capability",
            "output_root": str(output_root / "general_capability" / label), "model_manifest": str(manifest_path),
            "data": {"corpus_file": str(general_corpus), "prompts_file": str(repo_root / "configs/general_capability/prompts_v1.jsonl"), "completions_file": str(repo_root / "configs/general_capability/completions_v1.jsonl"), "synthetic_subjects_file": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv")},
            "scoring": {"block_size": 512, "batch_size": 4, "candidate_batch_size": 16, "bootstrap_samples": 2000},
            "generation": {"max_new_tokens": 64}, "runtime": {"device": "cuda", "bf16": True, "seed": 42},
        })
        rows.append({"array_index": len(rows), "label": label, "model_manifest": str(manifest_path), "model_manifest_sha256": sha256_file(manifest_path), "hard_output": str(output_root / "hard_suite" / label), "exact_config": str(exact_config), "general_config": str(general_config)})
    registry = output_root / "evaluation_registry.csv"
    write_csv(registry, rows)
    write_json(output_root / "evaluation_manifest.json", {"status": "frozen_ready_to_submit", "tasks": len(rows), "registry": str(registry), "registry_sha256": sha256_file(registry), "four_form_probe_registry": "/vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv", "models": {label: str(path) for label, path in models}})
    print(registry)


if __name__ == "__main__":
    main()
