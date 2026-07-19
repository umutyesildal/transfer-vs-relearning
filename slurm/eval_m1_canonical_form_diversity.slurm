#!/usr/bin/env bash
#SBATCH --job-name=m1-canonical-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/logs/%x-%A.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_canonical_form_diversity_v1"
FINAL_MODEL="${SCRATCH_ROOT}/training/seed42/20260719T064019Z_m1_canonical_form_diversity_seed42_453625c6/final_model"
EVALUATION_ROOT="${SCRATCH_ROOT}/evaluations"
PREFLIGHT_MANIFEST="${PREFLIGHT_MANIFEST:-${SCRATCH_ROOT}/evaluation_preflight/manifest.json}"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_form_generalization_preflight.py --verify-manifest "${PREFLIGHT_MANIFEST}" --repo-root "${REPO_ROOT}" --source-config configs/training/m1_canonical_form_diversity_seed42.yaml --launcher slurm/eval_m1_canonical_form_diversity.slurm
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs,tmp,evaluations}
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TMPDIR="${SCRATCH_ROOT}/tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/prepare_m1_canonical_form_diversity_evaluation.py --final-model "${FINAL_MODEL}" --source-manifest artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json --output-root "${EVALUATION_ROOT}" --general-corpus /vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl --repo-root "${REPO_ROOT}"
conda run --name xfer-relearn python scripts/evaluate_pre_m2_frozen_suite.py --model-label treatment_seed42 --model-manifest "${EVALUATION_ROOT}/model_manifests/treatment_seed42.json" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry /vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv --output-dir "${EVALUATION_ROOT}/hard_suite/treatment_seed42" --candidate-batch-size 64 --checkpoint-interval 25
conda run --name xfer-relearn python scripts/evaluate_facts.py --config "${EVALUATION_ROOT}/exact_config.json"
conda run --name xfer-relearn python scripts/evaluate_general_capability.py --config "${EVALUATION_ROOT}/general_config.json"
