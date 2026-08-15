#!/bin/bash

#SBATCH --job-name=xfer-gpu-smoke
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:10:00
#SBATCH --output=logs/gpu-smoke-%j.out
#SBATCH --error=logs/gpu-smoke-%j.err

set -euo pipefail

cd "$HOME/transfer-vs-relearning"

module purge
module load anaconda/3-2024.06

echo "Date: $(date)"
echo "Hostname: $(hostname)"
echo "User: $(whoami)"
echo "Job ID: ${SLURM_JOB_ID}"
echo "CUDA_VISIBLE_DEVICES: ${CUDA_VISIBLE_DEVICES:-unset}"

echo "=== Slurm allocation ==="
scontrol show job "$SLURM_JOB_ID"

echo "=== NVIDIA status ==="
nvidia-smi

echo "=== Python GPU test ==="
conda run --no-capture-output \
  --name xfer-relearn \
  python scripts/gpu_smoke_test.py
