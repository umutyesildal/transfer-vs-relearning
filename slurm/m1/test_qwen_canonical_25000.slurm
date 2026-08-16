#!/usr/bin/env bash
#SBATCH --job-name=qwen25k-tests
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.err
set -euo pipefail
: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"

HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
PYTHON="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"
cd "${REPO_ROOT}"

observed_commit=$(git rev-parse HEAD)
test "${observed_commit}" = "${EXPECTED_COMMIT}"
export PYTHONDONTWRITEBYTECODE=1
"${PYTHON}" -m pytest -q
bash -n \
  slurm/m1/preflight_qwen_canonical_25000_prepare.slurm \
  slurm/m1/prepare_qwen_canonical_25000.slurm \
  slurm/m1/smoke_qwen_canonical_25000.slurm \
  slurm/m1/preflight_qwen_canonical_25000_training.slurm \
  slurm/m1/train_qwen_canonical_25000.slurm \
  slurm/m1/audit_qwen_canonical_25000.slurm
printf 'status=passed commit=%s\n' "${observed_commit}"
