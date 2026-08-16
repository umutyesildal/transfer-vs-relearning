#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.utils.io import sha256_file


MODEL_ORDER = ("olmo", "qwen", "smollm")
FINAL_TASKS = (
    "wikitext",
    "pile_10k",
    "blimp",
    "hellaswag",
    "winogender_female",
    "winogender_male",
    "winogender_neutral",
    "turblimp_core",
)


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping: {path}")
    return payload


def _project_configs(
    model_id: str,
    model: dict[str, Any],
    *,
    repo_root: Path,
    family_root: Path,
    output_dir: Path,
) -> dict[str, dict[str, Any]]:
    model_root = family_root / model_id
    hu_repo = Path("/vol/tmp2/yesildau/transfer-vs-relearning-monorepo-v1")
    factual = {
        "schema_version": 1,
        "name": f"m0-{model_id}-scientific-factual-v1",
        "adapter_engine": "pre_m2_frozen",
        "run_classification": "scientific",
        "model_label": f"m0_{model_id}_scientific",
        "model_manifest": model["manifest_path"],
        "dataset_dir": str(hu_repo / "artifacts/datasets/relation_v2_gate_v1"),
        "probe_registry": str(
            hu_repo / "configs/evaluation/registries/eval_v1_factual_full_bilingual_12000.csv"
        ),
        "output_dir": str(model_root / "lanes/factual_access/raw/frozen_suite"),
        "input_sha256": {
            "dataset_manifest": "b37268d6f3afbb37f13ef746b80b99169c4d94ced3471aed2ae4aa09dc85b752",
            "probe_registry": "5125850a2db24c6b570971a58e9ba8a8586cabdec9084eb0e99bbd639691d93f",
        },
        "candidate_batch_size": 16,
        "checkpoint_interval": 100,
        "probe_limit": None,
        "device": "cuda",
        "bf16": False,
        "scientific_result": True,
    }
    generation = {
        "schema_version": 1,
        "name": f"m0-{model_id}-scientific-generation-v1",
        "adapter_engine": "general_capability",
        "run_classification": "scientific",
        "run_name": f"m0_{model_id}_scientific_generation",
        "output_root": str(model_root / "lanes/generation_integrity/raw/general_capability"),
        "model_manifest": model["manifest_path"],
        "data": {
            "corpus_file": "/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl",
            "prompts_file": str(hu_repo / "configs/general_capability/prompts_v1.jsonl"),
            "completions_file": str(hu_repo / "configs/general_capability/completions_v1.jsonl"),
            "synthetic_subjects_file": str(
                hu_repo / "artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv"
            ),
        },
        "input_sha256": {
            "corpus_file": "578a0879807f928e423f61631ee697a865af006df21e60e10e25a534c345097a",
            "prompts_file": "b21035ecf4819798dbf2807177e6bdd0b97a117f49fb77591e0e1602e67fb977",
            "completions_file": "9c14631b8de651a2d7f698456d767f2126e30173116f5fb21c442b6af7002580",
            "synthetic_subjects_file": "60dd741f8ef2815755beafa8bb5799f4112af3d94b1b8c4c171bfef28b07e6c1",
        },
        "scoring": {
            "block_size": 512,
            "batch_size": 4,
            "candidate_batch_size": 16,
            "bootstrap_samples": 10000,
        },
        "generation": {"max_new_tokens": 64},
        "runtime": {"device": "cuda", "bf16": False, "seed": 42},
        "scientific_result": True,
    }
    turkish_ppl = {
        "schema_version": 1,
        "name": f"m0-{model_id}-scientific-turkish-ppl-v1",
        "adapter_engine": "corpora_perplexity",
        "run_classification": "scientific",
        "model_label": f"m0_{model_id}_scientific",
        "model_manifest": model["manifest_path"],
        "corpora": {
            "trwiki_cross_domain": (
                "/vol/tmp2/yesildau/turkish_bridge_v1/corpus/"
                "trwiki_20260601_bridge_v1/splits/validation_documents.jsonl"
            )
        },
        "input_sha256": {
            "trwiki_cross_domain": "15480c1f543acf6df7aac1b2a2ee15fdcb3a544814f0063a181bd7a9cb0ca4f8"
        },
        "output_dir": str(model_root / "lanes/turkish_perplexity/raw/corpora"),
        "scoring": {"block_size": 512, "batch_size": 4, "bootstrap_samples": 10000},
        "runtime": {"device": "cuda", "bf16": False, "seed": 42},
        "primary_metric": "bits_per_byte",
        "scientific_result": True,
    }
    payloads = {"factual": factual, "generation": generation, "turkish_ppl": turkish_ppl}
    paths: dict[str, dict[str, Any]] = {}
    for kind, payload in payloads.items():
        path = output_dir / f"{model_id}_{kind}_v1.yaml"
        _write_yaml(path, payload)
        paths[kind] = {
            "path": str(path.relative_to(repo_root)),
            "sha256": sha256_file(path),
            "payload": payload,
        }
    return paths


def _main_config(
    model_id: str,
    model: dict[str, Any],
    project: dict[str, dict[str, Any]],
    *,
    family_root: Path,
    implementation_commit: str,
) -> dict[str, Any]:
    model_root = family_root / model_id
    runtime_files = {
        "scripts/study/run_m0_olmo_evaluation.py": "5f376bc36a33004e459405a764bf78c8ef47fa0f512719ba6ab8ab1fd9769e90",
        "scripts/study/run_three_model_m0_evaluation.py": "12359d5f06af586bc6f7912d62aef7519f4860ada1d93d281f671d65b7fce2f3",
        "src/transfer_vs_relearning/study/m0_parallel.py": "003077ee9034a1ed29bf293d7bb5d6128861d2527ac0ff6086ea1fe905e3cbda",
        "src/transfer_vs_relearning/study/adapters/m0_evaluation.py": "953f1958b6051be33e96c2b94ecb86ae79c5b19ce9a9376cd00f16af7ecdcfa5",
        "src/transfer_vs_relearning/study/adapters/m0_probing.py": "8c331dd8a18948343af255c337228c1f98bd2c73e78ff84a70a94b752b350744",
        "scripts/evaluation/evaluate_corpora_perplexity.py": "08c8ec90c50fee4e40d5396b135fffa97d2f4bcc7d486f46ba197146d782dcd9",
        "scripts/evaluation/evaluate_general_capability.py": "b062911213840affe5d5c11ec8d579b27673f5b9d3aa5b8838fe01f9a4a0b9e0",
        "scripts/m2/evaluate_pre_m2_frozen_suite.py": "d69c2ff340d5d7fb642b87540e79cf5e5c6601171ff18fa81423a170c71b4015",
    }
    routes = [
        {"id": "v10032gb", "partition": "gpu", "gres": "gpu:v10032gb:1", "memory": "64G", "parallel_slots": 3},
        {"id": "a10080gb", "partition": "gpu", "gres": "gpu:a10080gb:1", "memory": "64G", "parallel_slots": 3},
        {"id": "rtx3090", "partition": "wbimlgpu", "gres": "gpu:rtx3090:1", "memory": "64G", "parallel_slots": 1},
        {"id": "rtx6000", "partition": "gpu", "gres": "gpu:rtx6000:1", "memory": "64G", "parallel_slots": 3},
        {"id": "rtxa6000", "partition": "gpu", "gres": "gpu:rtxa6000:1", "memory": "64G", "parallel_slots": 4},
    ]
    return {
        "schema_version": 1,
        "name": f"m0-{model_id}-eval-v1-scientific-v1",
        "status": "frozen",
        "as_of": "2026-08-16",
        "classification": "scientific_evaluation",
        "scientific_result": True,
        "execution_ready": True,
        "execution_authorized": False,
        "contract": "documentation/contracts/evaluation/eval-v1.md",
        "contract_sha256": "72403598d7f9c8ba35bdfcc3e4791d097d41c6ef8f4e79c55cf9a6f34a37479e",
        "evaluation_registry": "configs/evaluation/eval_v1_registry.yaml",
        "evaluation_registry_sha256": "71d6f76e91f7891f32f9a1fffbc7493e3f85373b4c0737c9a734de9ec2d67d37",
        "scientific_inputs": "configs/evaluation/eval_v1_scientific_inputs_v1.yaml",
        "scientific_inputs_sha256": "845cb891c9a74c98becb4c50e397124c8ab1f47aefdf91dfdd5548b4dcd3b62f",
        "model": {
            "repository": model["repository"],
            "revision": model["revision"],
            "backend": "hf",
            "apply_chat_template": False,
            "system_instruction": None,
            "historical_manifest_path": model["manifest_path"],
            "historical_manifest_sha256": model["manifest_sha256"],
        },
        "harness": {
            "package": "lm_eval",
            "release": "v0.4.12",
            "git_commit": "6d642546f4688648fced259eb3302efd36ece5af",
            "environment_lock_path": "/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/environment.lock.txt",
            "environment_lock_sha256": "f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942",
            "environment_identity_sha256": "9061cbc59d021676ca6b768f7688eb7da10e5460bf4919b963c9931eefcc7d71",
            "integrity_validation": "frozen_offline_cache_and_task_validation",
        },
        "seeds": {"python": 42, "numpy": 42, "torch": 42, "fewshot": 42},
        "required_task_discovery": list(FINAL_TASKS),
        "parallel_evaluation": {
            "topology": "gpu_route_selection_per_lane_then_preflight_then_independent_jobs_plus_afterany_finalizer",
            "one_model_instance_per_lane": True,
            "max_parallel_lanes": 8,
            "finalizer_policy": "complete only when all eight raw lanes and every identity gate pass",
            "runtime": {
                "python": "/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/bin/python",
                "implementation_commit": implementation_commit,
                "implementation_files": runtime_files,
                "environment_lock_path": "/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/environment.lock.txt",
                "environment_lock_sha256": "f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942",
                "device": "cuda:0",
                "precision": "float16",
                "batch_size": "auto:4",
                "max_batch_size": 16,
                "log_samples": True,
            },
            "environment_preparation": {
                "authorized": False,
                "root": "/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3",
                "reason": "reuse_exact_frozen_environment_no_mutation",
            },
            "data_preflight": {
                "mode": "frozen_offline_reuse",
                "network_retrieval_authorized": False,
                "source_cache_root": "/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v8/cache",
                "source_content_manifest": "/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v8/dataset_content_manifest.jsonl",
                "source_content_manifest_sha256": "0bd32f84bcf94b8208b35a32cdb9a0e311e7ba005392a7557f80c316d0dfd7fb",
                "source_cache_files": 404,
                "source_cache_bytes": 413883554,
                "partition": "std",
                "min_cache_files": 404,
                "max_cache_files": 404,
                "min_cache_bytes": 413883554,
                "max_cache_bytes": 413883554,
                "cpus_per_task": 8,
                "memory": "32G",
                "time_limit": "02:00:00",
            },
            "slurm": {
                "account": "yesildau",
                "control_partition": "std",
                "gpu_route_selection_policy": "earliest_start_window_then_declared_slots_per_lane",
                "max_route_start_skew_seconds": 900,
                "gpu_routes": routes,
                "cpus_per_task": 8,
                "time_limit": "1-00:00:00",
            },
            "lanes": [
                {"id": "english_retention_wikitext", "adapter": "lm_eval", "families": ["english_retention"], "task_ids": ["wikitext"], "fewshot": 0},
                {"id": "english_retention_pile_10k", "adapter": "lm_eval", "families": ["english_retention"], "task_ids": ["pile_10k"], "fewshot": 0},
                {"id": "english_grammar_blimp", "adapter": "lm_eval", "families": ["english_capability"], "task_ids": ["blimp"], "fewshot": 0},
                {"id": "english_capability", "adapter": "lm_eval", "families": ["english_capability"], "task_ids": ["hellaswag", "winogender_female", "winogender_male", "winogender_neutral"], "fewshot": 0},
                {"id": "turkish_capability", "adapter": "lm_eval", "families": ["turkish_capability"], "task_ids": ["turblimp_core"], "fewshot": 0},
                {"id": "turkish_perplexity", "adapter": "project_corpus_perplexity", "families": ["turkish_retention"], "evaluator_config": project["turkish_ppl"]["path"], "evaluator_config_sha256": project["turkish_ppl"]["sha256"], "expected_output_root": project["turkish_ppl"]["payload"]["output_dir"]},
                {"id": "factual_access", "adapter": "project_factual", "families": ["factual_access", "statistical_uncertainty"], "evaluator_config": project["factual"]["path"], "evaluator_config_sha256": project["factual"]["sha256"], "expected_output_root": project["factual"]["payload"]["output_dir"]},
                {"id": "generation_integrity", "adapter": "project_generation_integrity", "families": ["generation_integrity"], "evaluator_config": project["generation"]["path"], "evaluator_config_sha256": project["generation"]["sha256"], "expected_output_root": project["generation"]["payload"]["output_root"]},
            ],
        },
        "storage": {
            "proposed_root": str(model_root),
            "fresh_root_required": True,
            "hu_home_read_only": True,
            "previous_evidence_roots_read_only": True,
            "source_dataset_cache_read_only": True,
            "atomic_writes_required": True,
        },
        "required_outputs": [
            "evaluation_manifest.json",
            "environment_lock.json",
            "model_identity.json",
            "task_resolution.jsonl",
            "dataset_content_manifest.jsonl",
            "runtime_measurements.jsonl",
            "raw_artifact_manifest.jsonl",
            "evaluation_results.json",
            "scientific_bundle_result.json",
            "final_inventory.json",
        ],
        "prohibitions": [
            "network_retrieval",
            "training",
            "corpus_materialization",
            "source_cache_mutation",
            "qualification_result_reuse",
            "outcome_aware_rerun",
            "cleanup_or_deletion",
        ],
    }


def build_configs(repo_root: Path, source_path: Path) -> Path:
    repo_root = repo_root.resolve()
    source = _load(source_path.resolve())
    if source.get("schema_version") != 1 or tuple(source.get("models", {})) != MODEL_ORDER:
        raise ValueError("Invalid three-model M0 config source")
    family_root = Path(source["family_root"])
    output_dir = repo_root / "configs/evaluation/m0_scientific"
    family_models: dict[str, Any] = {}
    for model_id in MODEL_ORDER:
        model = source["models"][model_id]
        project = _project_configs(
            model_id,
            model,
            repo_root=repo_root,
            family_root=family_root,
            output_dir=output_dir,
        )
        main = _main_config(
            model_id,
            model,
            project,
            family_root=family_root,
            implementation_commit=source["implementation_commit"],
        )
        main_path = output_dir / f"{model_id}_m0_eval_v1_scientific_v1.yaml"
        _write_yaml(main_path, main)
        family_models[model_id] = {
            "repository": model["repository"],
            "revision": model["revision"],
            "config": str(main_path.relative_to(repo_root)),
            "config_sha256": sha256_file(main_path),
        }
    family_manifest = {
        "schema_version": 1,
        "name": "m0-scientific-three-model-eval-v1",
        "status": "frozen",
        "as_of": "2026-08-16",
        "execution_ready": True,
        "execution_authorized": False,
        "family_root": str(family_root),
        "model_order": list(MODEL_ORDER),
        "models": family_models,
        "parallelism": {
            "models": 3,
            "lanes_per_model": 8,
            "total_lanes": 24,
            "submission": "all_model_preflights_then_three_independent_parallel_dags_then_one_family_finalizer",
        },
        "operator": "scripts/study/run_three_model_m0_evaluation.py",
        "implementation_commit": source["implementation_commit"],
        "execution_note": "frozen configuration is not execution authority",
    }
    manifest_path = repo_root / "configs/evaluation/m0_scientific_three_model_v1.yaml"
    _write_yaml(manifest_path, family_manifest)
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the frozen three-model scientific M0 configs")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("configs/evaluation/m0_scientific_model_matrix_v1.yaml"),
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    source = args.source if args.source.is_absolute() else repo_root / args.source
    print(build_configs(repo_root, source))


if __name__ == "__main__":
    main()
