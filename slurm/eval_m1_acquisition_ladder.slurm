#!/usr/bin/env bash
#SBATCH --job-name=m1-ladder-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=01:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
: "${EVAL_CONFIG_DIR:?EVAL_CONFIG_DIR is required}"
: "${CHECKPOINT:?CHECKPOINT is required}"
cd "${REPO_ROOT}"

echo "hostname=$(hostname)"
echo "user=$(whoami)"
echo "slurm_job_id=${SLURM_JOB_ID:-none}"
echo "checkpoint=${CHECKPOINT}"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
nvidia-smi --query-gpu=name --format=csv,noheader || true

module load anaconda/3-2024.06
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

mapfile -t configs < <(find "${EVAL_CONFIG_DIR}" -maxdepth 1 -type f -name "${CHECKPOINT}_*.yaml" | sort)
if [[ "${#configs[@]}" -ne 3 ]]; then
  echo "Expected exactly three evaluation configs for ${CHECKPOINT}, found ${#configs[@]}" >&2
  printf '%s\n' "${configs[@]}" >&2
  exit 1
fi

for config_path in "${configs[@]}"; do
  echo "__EVAL_CONFIG__=${config_path}"
  cat "${config_path}"
  conda run --name xfer-relearn python scripts/evaluate_facts.py --config "${config_path}"
done
