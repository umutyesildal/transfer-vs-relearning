#!/usr/bin/env bash
#SBATCH --job-name=m1-form-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=/vol/tmp2/yesildau/m1_form_generalization_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/m1_form_generalization_v1/logs/%x-%A.err

set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_form_generalization_v1"
MANIFEST="${SCRATCH_ROOT}/preflight/manifest.json"
cd "${REPO_ROOT}"
EXPECTED_COMMIT="$(git rev-parse HEAD)"
mkdir -p "${SCRATCH_ROOT}"/{cache,logs,preflight,tmp}
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_form_generalization_preflight.py \
  --repo-root "${REPO_ROOT}" \
  --scratch-root "${SCRATCH_ROOT}" \
  --manifest "${MANIFEST}" \
  --source-config configs/training/m1_form_generalization_control_seed42.yaml \
  --source-config configs/training/m1_form_generalization_balanced_ab_seed42.yaml \
  --launcher slurm/train_m1_form_generalization.slurm \
  --output-namespace "${SCRATCH_ROOT}/training/control_seed42" \
  --output-namespace "${SCRATCH_ROOT}/training/balanced_ab_seed42" \
  --expected-commit "${EXPECTED_COMMIT}"
