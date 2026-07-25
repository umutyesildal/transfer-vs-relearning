#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.utils.io import sha256_file, write_csv, write_json

STEPS = (25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--general-corpus", type=Path, required=True)
    args = parser.parse_args()
    root, repo = args.root.resolve(), args.repo_root.resolve()
    wave = root / "evaluation_v1"
    if wave.exists():
        raise FileExistsError(wave)
    run_roots = list((root / "training/replay_w0_5_seed42").glob("*/training_manifest.json"))
    if len(run_roots) != 1:
        raise ValueError(f"Expected one training manifest, found {len(run_roots)}")
    run = run_roots[0].parent
    rows = []
    for step in STEPS:
        checkpoint = run / "checkpoints" / f"checkpoint-{step}"
        if not checkpoint.is_dir():
            raise FileNotFoundError(checkpoint)
        label = f"qwen_scale_step{step}"
        model_manifest = wave / "model_manifests" / f"{label}.json"
        create_local_model_manifest(source_manifest_path=args.source_manifest, local_model_dir=checkpoint,
            output_manifest_path=model_manifest, model_id=label, resolved_revision=f"qwen-scale-probe-seed42-update{step}",
            training_checkpoint=f"checkpoint-{step}", training_run_dir=run)
        exact = wave / "exact_configs" / f"{label}.json"
        general = wave / "general_configs" / f"{label}.json"
        write_json(exact, {"dataset_version": "relation_v2_gate_v1_500_subjects_2500_facts", "dataset_dir": str(repo / "artifacts/datasets/relation_v2_gate_v1"), "pilot_subject_file": str(repo / "artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/summary.json"), "probe_files": {"en": str(repo / "artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/exact_prefix_probes_en.csv")}, "model_manifest": str(model_manifest), "languages": ["en"], "relations": ["profession", "born_in", "lives_in", "field_of_study", "works_in_industry"], "prompt": {"format": "direct", "template": "{question}", "answer_separator": " "}, "scoring": {"primary": "mean_logprob", "secondary": "total_logprob", "tie_breaker": "canonical_object_id"}, "runtime": {"bf16": True, "device": "cuda", "candidate_batch_size": 64, "checkpoint_interval": 25, "seed": 42}, "output": {"run_root": str(wave / "exact_prefix" / label)}})
        write_json(general, {"run_name": label, "output_root": str(wave / "general_capability" / label), "model_manifest": str(model_manifest), "data": {"corpus_file": str(args.general_corpus), "prompts_file": str(repo / "configs/general_capability/prompts_v1.jsonl"), "completions_file": str(repo / "configs/general_capability/completions_v1.jsonl"), "synthetic_subjects_file": str(repo / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv")}, "scoring": {"block_size": 512, "batch_size": 4, "candidate_batch_size": 16, "bootstrap_samples": 2000}, "generation": {"max_new_tokens": 64}, "runtime": {"device": "cuda", "bf16": True, "seed": 42}})
        rows.append({"array_index": len(rows), "label": label, "checkpoint_step": step, "model_manifest": str(model_manifest), "model_manifest_sha256": sha256_file(model_manifest), "hard_output": str(wave / "hard_suite" / label), "exact_config": str(exact), "general_config": str(general)})
    write_csv(wave / "checkpoint_registry.csv", rows)
    write_json(wave / "wave_manifest.json", {"status": "frozen_ready_for_preflight", "tasks": len(rows), "steps": list(STEPS), "registry_sha256": sha256_file(wave / "checkpoint_registry.csv"), "training_manifest_sha256": sha256_file(run / "training_manifest.json")})


if __name__ == "__main__":
    main()
