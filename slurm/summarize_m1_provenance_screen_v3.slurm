#!/usr/bin/env bash
#SBATCH --job-name=m1-pv3-summary
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:20:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v3/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v3/logs/%x-%j.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="${M1_PROVENANCE_SCREEN_ROOT:-/vol/tmp2/yesildau/m1_provenance_screen_v3}"
REGISTRY="${M1_PROVENANCE_REGISTRY:-${REPO_ROOT}/configs/experiments/m1_provenance_screen_v3.yaml}"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/summarize_m1_provenance_screen_v3.py \
  --registry "${REGISTRY}" \
  --output "${SCRATCH_ROOT}/manifests/family_terminal_assembly.json"
