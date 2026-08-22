#!/usr/bin/env bash
#SBATCH --job-name=m1-match-train
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
set -euo pipefail
: "${SLURM_ARRAY_TASK_ID:?}" "${FAMILY_ROOT:?}" "${PREFLIGHT_MANIFEST:?}"
labels=(olmo qwen smollm); label="${labels[$SLURM_ARRAY_TASK_ID]}"
cd "${SLURM_SUBMIT_DIR:?}"
export PYTHONPATH="$PWD/src"
module load anaconda/3-2024.06
task_tmp="${FAMILY_ROOT}/tmp/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$task_tmp" "${FAMILY_ROOT}/logs"
export HF_HOME="${FAMILY_ROOT}/cache/huggingface" XDG_CACHE_HOME="${FAMILY_ROOT}/cache" TORCH_HOME="${FAMILY_ROOT}/cache/torch" TMPDIR="$task_tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/m1/run_m1_matched_training.py \
  --preflight-manifest "${PREFLIGHT_MANIFEST}" --model-index "${SLURM_ARRAY_TASK_ID}" \
  --family-root "${FAMILY_ROOT}" \
  --binding-root "${FAMILY_ROOT}/bindings/${label}"
