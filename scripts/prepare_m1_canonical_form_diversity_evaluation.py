#!/usr/bin/env python3
"""Freeze the single-treatment Document 103 evaluation contract on scratch."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.utils.io import sha256_file, write_json


RELATIONS = ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")
LABEL = "treatment_seed42"
REFERENCE_H = "/vol/tmp2/yesildau/pre_m2_followup_v1/training/wp5_eos_ablation/lr5e-5_eos_false/20260718T152506Z_pre_m2_wp5_lr5e-5_eos_false_eb750e35/final_model"
REFERENCE_Q = "/vol/tmp2/yesildau/m1_form_generalization_v1/training/balanced_ab_seed42/20260718T205413Z_m1_form_generalization_balanced_ab_seed42_d689ca68/final_model"


def approved_scratch(path: Path) -> None:
    if not str(path.resolve()).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")):
        raise ValueError(f"Path must resolve under approved scratch: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze final-model evaluation for Document 103 Treatment T.")
    parser.add_argument("--final-model", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--general-corpus", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    output_root, final_model, general_corpus = args.output_root.resolve(), args.final_model.resolve(), args.general_corpus.resolve()
    approved_scratch(output_root)
    approved_scratch(final_model)
    training_manifest = final_model.parent / "training_manifest.json"
    if json.loads(training_manifest.read_text(encoding="utf-8")).get("status") != "complete":
        raise ValueError(f"Treatment training is not complete: {training_manifest}")
    if not general_corpus.is_file():
        raise FileNotFoundError(general_corpus)

    model_manifest = output_root / "model_manifests" / f"{LABEL}.json"
    create_local_model_manifest(
        source_manifest_path=args.source_manifest.resolve(), local_model_dir=final_model,
        output_manifest_path=model_manifest, model_id="m1_canonical_form_diversity_treatment_seed42",
        resolved_revision="m1-canonical-form-diversity-treatment-seed42",
        training_checkpoint="final_model", training_run_dir=final_model.parent,
    )
    exact_config = output_root / "exact_config.json"
    general_config = output_root / "general_config.json"
    write_json(exact_config, {
        "dataset_version": "relation_v2_gate_v1_100_subjects_500_facts_direct",
        "dataset_dir": str(repo_root / "artifacts/datasets/relation_v2_gate_v1"),
        "pilot_subject_file": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json"),
        "probe_files": {"en": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv")},
        "model_manifest": str(model_manifest), "languages": ["en"], "relations": list(RELATIONS),
        "prompt": {"format": "direct", "template": "{question}", "answer_separator": " "},
        "scoring": {"primary": "mean_logprob", "secondary": "total_logprob", "tie_breaker": "canonical_object_id"},
        "runtime": {"bf16": True, "device": "cuda", "candidate_batch_size": 64, "checkpoint_interval": 25, "seed": 42},
        "output": {"run_root": str(output_root / "exact_prefix" / LABEL)},
    })
    write_json(general_config, {
        "run_name": "m1_canonical_form_diversity_treatment_seed42_general_capability",
        "output_root": str(output_root / "general_capability" / LABEL), "model_manifest": str(model_manifest),
        "data": {"corpus_file": str(general_corpus), "prompts_file": str(repo_root / "configs/general_capability/prompts_v1.jsonl"), "completions_file": str(repo_root / "configs/general_capability/completions_v1.jsonl"), "synthetic_subjects_file": str(repo_root / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv")},
        "scoring": {"block_size": 512, "batch_size": 4, "candidate_batch_size": 16, "bootstrap_samples": 2000},
        "generation": {"max_new_tokens": 64}, "runtime": {"device": "cuda", "bf16": True, "seed": 42},
    })
    probe_registry = Path("/vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv")
    if not probe_registry.is_file():
        raise FileNotFoundError(probe_registry)
    write_json(output_root / "evaluation_manifest.json", {
        "status": "frozen_ready_to_submit", "treatment_label": LABEL,
        "treatment_final_model": str(final_model), "treatment_final_model_sha256": sha256_file(final_model / "model.safetensors"),
        "treatment_model_manifest": str(model_manifest), "treatment_model_manifest_sha256": sha256_file(model_manifest),
        "four_form_probe_registry": str(probe_registry), "four_form_probe_registry_sha256": sha256_file(probe_registry),
        "exact_config": str(exact_config), "general_config": str(general_config),
        "references_not_rerun": {"historical_canonical_h": REFERENCE_H, "balanced_ab_q": REFERENCE_Q},
    })
    print(output_root / "evaluation_manifest.json")


if __name__ == "__main__":
    main()
