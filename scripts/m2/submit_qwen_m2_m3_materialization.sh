#!/usr/bin/env bash
set -euo pipefail

ROOT="/vol/tmp2/yesildau/qwen_m2_m3_v1"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONTRACT_PATH="${REPO_ROOT}/configs/experiments/qwen_m2_m3_contract_v1.json"
cd "${REPO_ROOT}"
EXPECTED_COMMIT="$(git rev-parse HEAD)"
mkdir -p "${ROOT}/logs"
test -s "${CONTRACT_PATH}"
test ! -e "${ROOT}/blocks"

job_id="$(sbatch --parsable \
  --job-name=qwen-m2-m3-blocks \
  --export="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},CONTRACT_PATH=${CONTRACT_PATH}" \
  slurm/m2/materialize_qwen_m2_m3_blocks.slurm)"
printf 'materialization_job_id=%s\n' "${job_id}"
printf 'contract_path=%s\n' "${CONTRACT_PATH}"
printf 'expected_commit=%s\n' "${EXPECTED_COMMIT}"
printf 'output_root=%s\n' "${ROOT}"
printf 'planned_fact_cycles=4\nplanned_train_blocks=2048\nplanned_update_steps=128\n'
squeue -j "${job_id}" -o '%.18i %.12P %.32j %.8T %.10M %.10l %.20N %.30R'
