#!/usr/bin/env bash
#SBATCH --job-name=m1-ret43-eval-sum
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/summarize_m1_retention_seed43_evaluation.py --wave-root /vol/tmp2/yesildau/m1_retention_seed43_v1/evaluation_v1
