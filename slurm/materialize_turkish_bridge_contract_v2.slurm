#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-v2
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
OUTPUT_ROOT="${SCRATCH_ROOT}/contracts/v2"
TASK_TMP="${SCRATCH_ROOT}/tmp/contract_v2_${SLURM_JOB_ID}"

preserve_failed_contract() {
  if [[ -d "${OUTPUT_ROOT}" ]]; then
    failed_root="${SCRATCH_ROOT}/contracts/failed_v2_job_${SLURM_JOB_ID}"
    test ! -e "${failed_root}"
    mv "${OUTPUT_ROOT}" "${failed_root}"
    printf 'failed_contract_preserved=%s\n' "${failed_root}" >&2
  fi
}
trap preserve_failed_contract ERR

cd "${REPO_ROOT}"
test ! -e "${OUTPUT_ROOT}"
mkdir -p "${SCRATCH_ROOT}"/{logs,tmp,cache} "${TASK_TMP}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${SCRATCH_ROOT}/cache"
export TORCH_HOME="${SCRATCH_ROOT}/cache/torch"
export TMPDIR="${TASK_TMP}"

module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/prepare_turkish_bridge_contract_v2.py \
  --experiment-config configs/experiments/turkish_bridge_v1.yaml \
  --training-template configs/training/turkish_bridge_adaptation_template.yaml \
  --repo-root "${REPO_ROOT}"

conda run --name xfer-relearn python - "${OUTPUT_ROOT}/manifest.json" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text())
assert manifest["status"] == "frozen_ready_for_training_preflight"
assert manifest["subject_count"] == 100
assert manifest["fact_count"] == 500
assert manifest["probe_count"] == 1500
assert manifest["shared_eligible_count"] == 357
assert manifest["eligibility"]["qwen"]["summary"]["eligible"] == 497
assert manifest["eligibility"]["smollm2"]["summary"]["eligible"] == 359
assert all(value >= 2048 for value in manifest["dose"]["model_grouped_block_counts"].values())
assert all(value > 0 for value in manifest["dose"]["validation_tokenization"]["model_grouped_block_counts"].values())
assert manifest["dose"]["status"] == "passed_no_cycling"
assert manifest["storage"]["preflight_reserve_bytes"] > 0
PY

du -xsh "${HOME_ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
du -sh "${OUTPUT_ROOT}"
trap - ERR
printf 'status=contract_v2_ready\n'
