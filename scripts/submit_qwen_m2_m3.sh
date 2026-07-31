#!/usr/bin/env bash
set -euo pipefail

: "${CONFIG_MANIFEST:?CONFIG_MANIFEST must point to a prepared four-config family}"
ROOT=/vol/tmp2/yesildau/qwen_m2_m3_v1
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${REPO_ROOT}"
EXPECTED_COMMIT="$(git rev-parse HEAD)"
mkdir -p "${ROOT}/logs"
preflight_id="$(sbatch --parsable \
  --export="ALL,CONFIG_MANIFEST=${CONFIG_MANIFEST},EXPECTED_COMMIT=${EXPECTED_COMMIT}" \
  slurm/preflight_qwen_m2_m3.slurm)"
training_id="$(sbatch --parsable --dependency="afterok:${preflight_id}" \
  --export="ALL,CONFIG_MANIFEST=${CONFIG_MANIFEST},EXPECTED_COMMIT=${EXPECTED_COMMIT},PREFLIGHT_MANIFEST=${ROOT}/preflight/manifest.json" \
  slurm/train_qwen_m2_m3_array.slurm)"
printf 'preflight_id=%s\ntraining_array_id=%s\nconfig_manifest=%s\nexpected_commit=%s\n' \
  "${preflight_id}" "${training_id}" "${CONFIG_MANIFEST}" "${EXPECTED_COMMIT}"
squeue -j "${preflight_id},${training_id}" -o '%.18i %.12P %.32j %.8T %.10M %.10l %.12R'
