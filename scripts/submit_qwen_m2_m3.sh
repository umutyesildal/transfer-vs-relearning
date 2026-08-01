#!/usr/bin/env bash
set -euo pipefail

: "${CONFIG_MANIFEST:?CONFIG_MANIFEST must point to a prepared four-config family}"
ROOT=/vol/tmp2/yesildau/qwen_m2_m3_v1
TRAIN_ARRAY="${TRAIN_ARRAY:-0-3%2}"
if [[ ${TRAIN_EXCLUDE+x} ]]; then
  TRAIN_EXCLUDE_ARGS=()
  [[ -n "${TRAIN_EXCLUDE}" ]] && TRAIN_EXCLUDE_ARGS=(--exclude="${TRAIN_EXCLUDE}")
else
  TRAIN_EXCLUDE_ARGS=(--exclude=gruenau10)
fi
TRAIN_NODE_ARGS=()
[[ -n "${TRAIN_NODELIST:-}" ]] && TRAIN_NODE_ARGS=(--nodelist="${TRAIN_NODELIST}")
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${REPO_ROOT}"
EXPECTED_COMMIT="$(git rev-parse HEAD)"
mkdir -p "${ROOT}/logs"
preflight_id="$(sbatch --parsable \
  --export="ALL,CONFIG_MANIFEST=${CONFIG_MANIFEST},EXPECTED_COMMIT=${EXPECTED_COMMIT}" \
  slurm/preflight_qwen_m2_m3.slurm)"
training_id="$(sbatch --parsable --dependency="afterok:${preflight_id}" \
  --array="${TRAIN_ARRAY}" \
  "${TRAIN_EXCLUDE_ARGS[@]}" "${TRAIN_NODE_ARGS[@]}" \
  --export="ALL,CONFIG_MANIFEST=${CONFIG_MANIFEST},EXPECTED_COMMIT=${EXPECTED_COMMIT},PREFLIGHT_MANIFEST=${ROOT}/preflight/manifest.json" \
  slurm/train_qwen_m2_m3_array.slurm)"
printf 'preflight_id=%s\ntraining_array_id=%s\nconfig_manifest=%s\nexpected_commit=%s\n' \
  "${preflight_id}" "${training_id}" "${CONFIG_MANIFEST}" "${EXPECTED_COMMIT}"
squeue -j "${preflight_id},${training_id}" -o '%.18i %.12P %.32j %.8T %.10M %.10l %.12R'
