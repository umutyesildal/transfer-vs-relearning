#!/usr/bin/env bash
#SBATCH --job-name=smollm-pconsistency-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --array=0-11
#SBATCH --output=/vol/tmp2/yesildau/smollm_prompt_consistency_v2/evaluation_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/smollm_prompt_consistency_v2/evaluation_v1/logs/%x-%A_%a.err
set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT=/vol/tmp2/yesildau/smollm_prompt_consistency_v2/evaluation_v1
RUN=/vol/tmp2/yesildau/smollm_prompt_consistency_v2/training/seed42/20260729T085627Z_smollm_prompt_consistency_seed42_b7938973
SOURCE_CONFIG="${REPO_ROOT}/configs/training/smollm_prompt_consistency_seed42.yaml"
items=(checkpoint-25 checkpoint-50 checkpoint-75 checkpoint-100 checkpoint-125 checkpoint-150 checkpoint-175 checkpoint-200 checkpoint-225 checkpoint-250 checkpoint-252 final_model)
item="${items[${SLURM_ARRAY_TASK_ID}]}"
if [[ "${item}" == final_model ]]; then
  FINAL_MODEL="${RUN}/final_model"
else
  FINAL_MODEL="${RUN}/checkpoints/${item}"
fi
LABEL="smollm_pconsistency_seed42_${item//-/_}"
WORK_ROOT="${ROOT}/${LABEL}"
OUTPUT_ROOT="${WORK_ROOT}/results"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_form_generalization_preflight.py \
  --verify-manifest "${ROOT}/preflight/manifest.json" \
  --repo-root "${REPO_ROOT}" \
  --source-config "${SOURCE_CONFIG}" \
  --launcher slurm/eval_smollm_prompt_consistency_array.slurm
mkdir -p "${WORK_ROOT}"/{cache/huggingface,cache/torch,logs,tmp}
export HF_HOME="${WORK_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${WORK_ROOT}/cache/huggingface" XDG_CACHE_HOME="${WORK_ROOT}/cache" TORCH_HOME="${WORK_ROOT}/cache/torch" TMPDIR="${WORK_ROOT}/tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/prepare_m1_canonical_form_diversity_evaluation.py --label "${LABEL}" --final-model "${FINAL_MODEL}" --source-manifest artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json --output-root "${OUTPUT_ROOT}" --general-corpus /vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl --repo-root "${REPO_ROOT}"
conda run --name xfer-relearn python scripts/evaluate_pre_m2_frozen_suite.py --model-label "${LABEL}" --model-manifest "${OUTPUT_ROOT}/model_manifests/${LABEL}.json" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry /vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv --output-dir "${OUTPUT_ROOT}/hard_suite/${LABEL}" --candidate-batch-size 64 --checkpoint-interval 25
conda run --name xfer-relearn python scripts/evaluate_facts.py --config "${OUTPUT_ROOT}/exact_config.json"
conda run --name xfer-relearn python scripts/evaluate_general_capability.py --config "${OUTPUT_ROOT}/general_config.json"
