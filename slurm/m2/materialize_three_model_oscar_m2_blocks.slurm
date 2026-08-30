#!/usr/bin/env bash
#SBATCH --job-name=vngrs-m2-oscar-blocks-v1
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=06:00:00
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
module load anaconda/3-2024.06
conda run --name xfer-relearn python \
  scripts/m2/materialize_three_model_oscar_m2_blocks.py \
  --repo-root "$PWD" \
  --config configs/corpora/vngrs_m2_oscar_exact_blocks_v1.yaml \
  --execution-enabled
