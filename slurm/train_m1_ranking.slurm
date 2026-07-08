#!/usr/bin/env bash
#SBATCH --job-name=m1-ranking
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
CONFIG_PATH="${TRAIN_CONFIG:-configs/training/m1_smollm2_360m_english_fact_ranking_lr2e-5_ep3.yaml}"
cd "${REPO_ROOT}"

echo "hostname=$(hostname)"
echo "user=$(whoami)"
echo "slurm_job_id=${SLURM_JOB_ID:-none}"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
nvidia-smi --query-gpu=name --format=csv,noheader || true

module load anaconda/3-2024.06

conda run --name xfer-relearn python --version
conda run --name xfer-relearn python - <<'PY'
import torch, transformers, datasets
print("torch", torch.__version__)
print("cuda", torch.version.cuda)
print("transformers", transformers.__version__)
print("datasets", datasets.__version__)
print("cuda_device_count", torch.cuda.device_count())
if torch.cuda.device_count() != 1:
    raise SystemExit("Expected exactly one Slurm-assigned GPU")
PY

echo "Selected training config: ${CONFIG_PATH}"
cat "${CONFIG_PATH}"

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

conda run --name xfer-relearn python scripts/train_ranking.py \
  --config "${CONFIG_PATH}"
