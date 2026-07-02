#!/usr/bin/env bash
#SBATCH --job-name=m0-gpt2-pilot
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

echo "hostname=$(hostname)"
echo "user=$(whoami)"
echo "slurm_job_id=${SLURM_JOB_ID:-none}"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
nvidia-smi --query-gpu=name --format=csv,noheader || true

module load anaconda/3-2024.06

conda run --name xfer-relearn python --version
conda run --name xfer-relearn python - <<'PY'
import torch, transformers
print("torch", torch.__version__)
print("cuda", torch.version.cuda)
print("transformers", transformers.__version__)
PY

echo "Resolved evaluator config:"
cat configs/evaluation/m0_gpt2_pilot.yaml

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

conda run --name xfer-relearn python scripts/evaluate_facts.py \
  --config configs/evaluation/m0_gpt2_pilot.yaml
