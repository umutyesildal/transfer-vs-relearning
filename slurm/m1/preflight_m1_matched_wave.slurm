#!/usr/bin/env bash
#SBATCH --job-name=m1-match-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00
set -euo pipefail
: "${EXPECTED_COMMIT:?}" "${FAMILY_ROOT:?}" "${PREFLIGHT_MANIFEST:?}"
cd "${SLURM_SUBMIT_DIR:?}"
export PYTHONPATH="$PWD/src"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1/preflight_m1_matched_wave.py \
  --repo-root "$PWD" --family-root "${FAMILY_ROOT}" --expected-commit "${EXPECTED_COMMIT}" \
  --manifest "${PREFLIGHT_MANIFEST}" \
  --config configs/training/m1_matched_epoch_dense_olmo_seed42_draft.yaml \
  --config configs/training/m1_matched_epoch_dense_qwen_seed42_draft.yaml \
  --config configs/training/m1_matched_epoch_dense_smollm_seed42_draft.yaml
