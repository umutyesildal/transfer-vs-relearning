#!/usr/bin/env bash
#SBATCH --job-name=m2-oscar-recovery-v1-finalize
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_v1/logs/%x-%j.err
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
module load anaconda/3-2024.06
root=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_v1
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src:$PWD"
conda run --no-capture-output --name xfer-relearn python \
  scripts/m2/finalize_three_model_oscar_m2_training_family.py \
  --config-manifest "$root/configs/config_manifest.json" --output-root "$root/bindings"
conda run --no-capture-output --name xfer-relearn python \
  scripts/m2/prepare_m2_oscar_eval_v2_matrix.py \
  --preparation-config configs/evaluation/m2_oscar_three_model_eval_v2_preparation_v1.yaml \
  --training-family-manifest "$root/bindings/family_manifest.json" \
  --repo-root "$PWD" --output "$root/evaluation/eval_v2_matrix.json"
