#!/usr/bin/env bash
#SBATCH --job-name=qwen-scale-s43-train
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1/logs/%x-%j.err
set -euo pipefail

: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1
SOURCE_ROOT=/vol/tmp2/yesildau/qwen_scale_probe_v3
test -s "${PREFLIGHT_MANIFEST}"
test -s "${SOURCE_ROOT}/datasets/dataset_manifest.json"
test -s "${SOURCE_ROOT}/anchor/manifest.json"
task_tmp="${ROOT}/tmp/training_${SLURM_JOB_ID}"
mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,logs} "${task_tmp}"
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TMPDIR="${task_tmp}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
nvidia-smi
conda run --name xfer-relearn python scripts/training/train_clm.py --config configs/training/qwen_scale_probe_replay_w0_5_seed43.yaml
