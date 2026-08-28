#!/usr/bin/env bash
#SBATCH --job-name=vngrs-m2-d0-v2
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=12:00:00
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
cd "${SLURM_SUBMIT_DIR:?}"
export PYTHONPATH="$PWD/src"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/corpora/run_vngrs_m2_d0_v2.py phase1 \
  --repo-root "$PWD" --expected-commit "$EXPECTED_COMMIT" --collect-preflight
