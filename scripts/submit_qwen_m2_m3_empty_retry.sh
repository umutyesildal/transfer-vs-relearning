#!/usr/bin/env bash
# Submit only the four m2_clean_seed42 endpoint slices whose result directories
# were verified empty. The CPU preflight is a hard dependency of the retry.
set -euo pipefail

ROOT=/vol/tmp2/yesildau/qwen_m2_m3_v1
EVAL_ROOT="${ROOT}/evaluation_v1"
RETRY_TASK_IDS="${RETRY_TASK_IDS:-2 11 14 15}"
RETRY_REQUIRED_STATE="${RETRY_REQUIRED_STATE:-m2_clean_seed42}"
RETRY_RUN_NAME="${RETRY_RUN_NAME:-retry_v1}"
read -r -a RETRY_TASK_ID_ARRAY <<< "${RETRY_TASK_IDS}"
ARRAY_SPEC="$(IFS=,; printf '%s' "${RETRY_TASK_ID_ARRAY[*]}")"
RETRY_ROOT="${ROOT}/${RETRY_RUN_NAME}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXPECTED_COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
cd "${REPO_ROOT}"

test -s "${EVAL_ROOT}/evaluation_manifest.json"
test -s "/vol/tmp2/yesildau/qwen_pre_m2_contract_v1/evaluation/slice_registry.json"
test ! -e "${RETRY_ROOT}/retry_manifest.json"
mkdir -p "${RETRY_ROOT}/logs"

echo "--- queue before retry preflight ---"
squeue -u yesildau -o '%.18i %.12P %.28j %.8T %.10M %.12R'

preflight_id="$(sbatch --parsable \
  --output="${RETRY_ROOT}/logs/qwen-m2-m3-retry-pre-%j.out" \
  --error="${RETRY_ROOT}/logs/qwen-m2-m3-retry-pre-%j.err" \
  --export="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},RETRY_TASK_IDS=${RETRY_TASK_IDS},RETRY_REQUIRED_STATE=${RETRY_REQUIRED_STATE},RETRY_RUN_NAME=${RETRY_RUN_NAME}" \
  slurm/preflight_qwen_m2_m3_empty_retry.slurm)"
retry_id="$(sbatch --parsable \
  --dependency="afterok:${preflight_id}" \
  --job-name=qwen-m2-m3-retry \
  --array="${ARRAY_SPEC}%3" \
  --gres=gpu:rtx6000:1 \
  --nodelist=gruenau2 \
  --export="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},PREFLIGHT_MANIFEST=${RETRY_ROOT}/preflight/manifest.json,EVALUATION_MANIFEST=${EVAL_ROOT}/evaluation_manifest.json,RETRY_MANIFEST=${RETRY_ROOT}/retry_manifest.json,RETRY_TASK_IDS=${RETRY_TASK_IDS},RETRY_REQUIRED_STATE=${RETRY_REQUIRED_STATE},RETRY_RUN_NAME=${RETRY_RUN_NAME},ALLOW_EXISTING_EMPTY_RESULT_ROOT=1" \
  slurm/eval_qwen_m2_m3_slice.slurm)"

echo "preflight_id=${preflight_id}"
echo "retry_array_id=${retry_id}"
echo "retry_task_ids=${RETRY_TASK_IDS}"
echo "retry_required_state=${RETRY_REQUIRED_STATE}"
echo "retry_run_name=${RETRY_RUN_NAME}"
echo "gpu_type=rtx6000"
echo "node=gruenau2"
echo "expected_runtime=20-60 minutes per batch; three cards maximum"
echo "--- queue after retry submission ---"
squeue -j "${preflight_id},${retry_id}" -o '%.18i %.12P %.28j %.8T %.10M %.12R'
