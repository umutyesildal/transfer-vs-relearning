#!/usr/bin/env bash
#SBATCH --job-name=m1-prov-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v1/logs/%x-%A.err
set -euo pipefail
: "${PREFLIGHT_STAGE:?PREFLIGHT_STAGE is required}"
: "${TARGET_LAUNCHER:?TARGET_LAUNCHER is required}"
: "${TARGET_JOB_NAME:?TARGET_JOB_NAME is required}"
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="${M1_PROVENANCE_SCREEN_ROOT:-/vol/tmp2/yesildau/m1_provenance_screen_v1}"
REGISTRY="${M1_PROVENANCE_REGISTRY:-${REPO_ROOT}/configs/experiments/m1_provenance_screen_v1.yaml}"
TEMPLATE="${M1_PROVENANCE_TEMPLATE:-${REPO_ROOT}/configs/training/m1_provenance_screen_seed42_template.yaml}"
MANIFEST="${PREFLIGHT_MANIFEST_PATH:-${SCRATCH_ROOT}/preflight/${PREFLIGHT_STAGE}.json}"
PREFLIGHT_TMP="${SCRATCH_ROOT}/tmp/preflight/${PREFLIGHT_STAGE}_${SLURM_JOB_ID}"
indices_value="${CANDIDATE_INDICES:-0:1:2}"
IFS=':' read -r -a indices <<< "${indices_value}"
candidate_args=()
for index in "${indices[@]}"; do candidate_args+=(--candidate-index "${index}"); done
mode_args=()
if [[ "${ALLOW_SUBSET_RETRY:-0}" == "1" ]]; then mode_args+=(--allow-subset-retry); fi
if [[ "${ALLOW_COMPLETED_SUBSET_EVALUATION:-0}" == "1" ]]; then mode_args+=(--allow-completed-subset-evaluation); fi
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/huggingface_datasets,cache/torch,cache/triton,cache/cuda,cache/matplotlib,cache/numba,cache/wandb} "${PREFLIGHT_TMP}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" HF_DATASETS_CACHE="${SCRATCH_ROOT}/cache/huggingface_datasets" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TRITON_CACHE_DIR="${SCRATCH_ROOT}/cache/triton" CUDA_CACHE_PATH="${SCRATCH_ROOT}/cache/cuda" MPLCONFIGDIR="${SCRATCH_ROOT}/cache/matplotlib" NUMBA_CACHE_DIR="${SCRATCH_ROOT}/cache/numba" WANDB_DIR="${SCRATCH_ROOT}/cache/wandb" WANDB_MODE=disabled TMPDIR="${PREFLIGHT_TMP}" PYTHONDONTWRITEBYTECODE=1
conda run --name xfer-relearn python scripts/m1/m1_cross_family_preflight.py \
  --stage "${PREFLIGHT_STAGE}" \
  --repo-root "${REPO_ROOT}" \
  --registry "${REGISTRY}" \
  --template "${TEMPLATE}" \
  --launcher "${TARGET_LAUNCHER}" \
  --target-job-name "${TARGET_JOB_NAME}" \
  --manifest "${MANIFEST}" \
  --expected-commit "$(git rev-parse HEAD)" \
  "${mode_args[@]}" \
  "${candidate_args[@]}"
