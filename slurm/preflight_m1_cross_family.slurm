#!/usr/bin/env bash
#SBATCH --job-name=m1-xfam-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_cross_family_screen_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/m1_cross_family_screen_v1/logs/%x-%A.err
set -euo pipefail
: "${PREFLIGHT_STAGE:?PREFLIGHT_STAGE is required}"
: "${TARGET_LAUNCHER:?TARGET_LAUNCHER is required}"
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_cross_family_screen_v1"
REGISTRY="${REPO_ROOT}/configs/experiments/m1_cross_family_screen_v1.yaml"
TEMPLATE="${REPO_ROOT}/configs/training/m1_cross_family_seed42_template.yaml"
MANIFEST="${SCRATCH_ROOT}/preflight/${PREFLIGHT_STAGE}.json"
indices_value="${CANDIDATE_INDICES:-0:1:2:3}"
IFS=':' read -r -a indices <<< "${indices_value}"
candidate_args=()
for index in "${indices[@]}"; do candidate_args+=(--candidate-index "${index}"); done
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_cross_family_preflight.py \
  --stage "${PREFLIGHT_STAGE}" \
  --repo-root "${REPO_ROOT}" \
  --registry "${REGISTRY}" \
  --template "${TEMPLATE}" \
  --launcher "${TARGET_LAUNCHER}" \
  --manifest "${MANIFEST}" \
  --expected-commit "$(git rev-parse HEAD)" \
  "${candidate_args[@]}"
