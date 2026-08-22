#!/usr/bin/env bash
#SBATCH --job-name=m1-match-audit
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:15:00
set -euo pipefail
: "${FAMILY_ROOT:?}"
cd "${SLURM_SUBMIT_DIR:?}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1/audit_m1_matched_training.py --family-root "${FAMILY_ROOT}"
