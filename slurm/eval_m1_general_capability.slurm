#!/usr/bin/env bash
#SBATCH --job-name=m1-general-cap
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
: "${EVAL_CONFIG:?EVAL_CONFIG is required}"
cd "${REPO_ROOT}"

echo "hostname=$(hostname)"
echo "user=$(whoami)"
echo "slurm_job_id=${SLURM_JOB_ID:-none}"
echo "config=${EVAL_CONFIG}"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
nvidia-smi --query-gpu=name --format=csv,noheader || true

module load anaconda/3-2024.06
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

echo "Resolved evaluator config:"
cat "${EVAL_CONFIG}"
conda run --name xfer-relearn python scripts/evaluate_general_capability.py --config "${EVAL_CONFIG}"

