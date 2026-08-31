#!/usr/bin/env bash
#SBATCH --job-name=m2-fact-tr-repair-v1a
#SBATCH --account=yesildau
#SBATCH --partition=longrun
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_retry_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_retry_v1/logs/%x-%j.err
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
module load anaconda/3-2024.06
root=/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_retry_v1
mkdir -p "$root/control" "$root/logs" "$root/tmp"
export TMPDIR="$root/tmp"
PYTHONPATH="$PWD/src" conda run --no-capture-output --name xfer-relearn \
  python scripts/m2/repair_three_model_oscar_m2_fact_translations.py \
  --repo-root "$PWD" \
  --config configs/corpora/vngrs_m2_oscar_fact_translation_repair_v1a.yaml \
  --execution-enabled
