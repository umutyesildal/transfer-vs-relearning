#!/usr/bin/env bash
#SBATCH --job-name=m2-oscar-3model-finalize
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=/vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1/logs/%x-%j.err
set -euo pipefail
: "${CONFIG_MANIFEST:?}"
: "${EXPECTED_COMMIT:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
module load anaconda/3-2024.06
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
conda run --name xfer-relearn python scripts/m2/finalize_three_model_oscar_m2_training_family.py \
  --config-manifest "$CONFIG_MANIFEST" \
  --output-root /vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1/bindings
