#!/usr/bin/env bash
#SBATCH --job-name=m1-ret43-train
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.err
set -euo pipefail
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_retention_seed43_v1"
CONFIG="configs/training/m1_qwen_retention_replay_w0_5_seed43.yaml"
LABEL="replay_w0_5_seed43"
test -s "${PREFLIGHT_MANIFEST}"
expected_commit=$("${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" -c \
  'import json,sys; print(json.load(open(sys.argv[1]))["git_commit"])' "${PREFLIGHT_MANIFEST}")
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${expected_commit}"

task_tmp="${SCRATCH_ROOT}/tmp/training/${LABEL}_${SLURM_JOB_ID}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs} "${task_tmp}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${SCRATCH_ROOT}/cache"
export TORCH_HOME="${SCRATCH_ROOT}/cache/torch"
export TMPDIR="${task_tmp}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

cd "${REPO_ROOT}"
module load anaconda/3-2024.06
printf 'condition=%s\nconfig=%s\noutput_root=%s\n' "${LABEL}" "${CONFIG}" \
  "${SCRATCH_ROOT}/training/${LABEL}"
nvidia-smi
conda run --name xfer-relearn python scripts/train_clm.py --config "${CONFIG}"
