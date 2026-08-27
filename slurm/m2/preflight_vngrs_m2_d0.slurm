#!/usr/bin/env bash
#SBATCH --job-name=vngrs-m2-d0-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00
set -euo pipefail
: "${EXPECTED_COMMIT:?}" "${PREFLIGHT_JSON:?}"
cd "${SLURM_SUBMIT_DIR:?}"
export PYTHONPATH="$PWD/src"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/corpora/preflight_vngrs_m2_d0.py \
  --repo-root "$PWD" --expected-commit "$EXPECTED_COMMIT" --output "$PREFLIGHT_JSON"
