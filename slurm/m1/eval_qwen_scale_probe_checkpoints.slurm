#!/usr/bin/env bash
#SBATCH --job-name=qwen-scale-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_scale_probe_v3/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_scale_probe_v3/logs/%x-%A_%a.err
set -euo pipefail
: "${SLURM_ARRAY_TASK_ID:?}" 
ROOT=/vol/tmp2/yesildau/qwen_scale_probe_v3
REPO_ROOT="${SLURM_SUBMIT_DIR}"
REGISTRY="${ROOT}/evaluation_v1/checkpoint_registry.csv"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
field(){ conda run --name xfer-relearn python scripts/m1/resolve_m1_retention_evaluation.py --registry "${REGISTRY}" --task-index "${SLURM_ARRAY_TASK_ID}" --field "$1" | tr -d '\r'; }
label=$(field label); model=$(field model_manifest); hard=$(field hard_output); exact=$(field exact_config); general=$(field general_config)
tmp="${ROOT}/tmp/evaluation/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,logs} "${tmp}"
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface" XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TMPDIR="${tmp}" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/m2/evaluate_pre_m2_frozen_suite.py --model-label "${label}" --model-manifest "${model}" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry "${ROOT}/datasets/evaluations/four_form_probe_registry.csv" --output-dir "${hard}" --candidate-batch-size 64 --checkpoint-interval 25
conda run --name xfer-relearn python scripts/evaluation/evaluate_facts.py --config "${exact}"
conda run --name xfer-relearn python scripts/evaluation/evaluate_general_capability.py --config "${general}"
