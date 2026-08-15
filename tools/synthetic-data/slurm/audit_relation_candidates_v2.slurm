#!/usr/bin/env bash
#SBATCH --job-name=relation-v2-audit
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=00:30:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

: "${MODEL_MANIFEST:?MODEL_MANIFEST is required}"
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
cd "${REPO_ROOT}"
mkdir -p logs

module load anaconda/3-2024.06
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

echo "hostname=$(hostname)"
echo "slurm_job_id=${SLURM_JOB_ID:-none}"
nvidia-smi --query-gpu=name --format=csv,noheader

conda run --name xfer-relearn python audit_relation_candidates_v2.py \
  --model-manifest "${MODEL_MANIFEST}" \
  --device cuda \
  --output-dir output/relation_candidates_v2_audit
