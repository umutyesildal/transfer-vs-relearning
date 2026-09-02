#!/usr/bin/env bash
#SBATCH --job-name=m2-oscar-finalizer-order-v1
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=/vol/tmp2/yesildau/vnd_m2_oscar_finalizer_numeric_order_repair_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/vnd_m2_oscar_finalizer_numeric_order_repair_v1/logs/%x-%j.err
set -euo pipefail
: "${EXPECTED_COMMIT:?}" "${EXECUTION_CONTRACT:?}" "${EXPECTED_CONTRACT_SHA256:?}" "${REPAIR_CONFIG:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
module load anaconda/3-2024.06
root=/vol/tmp2/yesildau/vnd_m2_oscar_finalizer_numeric_order_repair_v1
export PYTHONPATH="$PWD/src:$PWD" PYTHONDONTWRITEBYTECODE=1
export HF_HOME="$root/cache/huggingface" TRANSFORMERS_CACHE="$root/cache/huggingface"
export TMPDIR="$root/tmp" XDG_CACHE_HOME="$root/cache/xdg"
conda run --name xfer-relearn python scripts/m2/run_m2_oscar_finalizer_numeric_order_repair_v1.py \
  --repo-root "$PWD" \
  --config "$REPAIR_CONFIG" \
  --contract "$EXECUTION_CONTRACT" \
  --contract-sha256 "$EXPECTED_CONTRACT_SHA256" \
  --expected-commit "$EXPECTED_COMMIT"
