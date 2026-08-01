#!/usr/bin/env bash
set -euo pipefail

ROOT=/vol/tmp2/yesildau/qwen_m2_m3_v1
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_MANIFEST="${CONFIG_MANIFEST:-${ROOT}/family/config_manifest.json}"
cd "${REPO_ROOT}"
EXPECTED_COMMIT="$(git rev-parse HEAD)"

test -s "${CONFIG_MANIFEST}"
test ! -e "${ROOT}/smoke"
mkdir -p "${ROOT}/logs"

preflight_id="$(sbatch --parsable \
  --export="ALL,CONFIG_MANIFEST=${CONFIG_MANIFEST},EXPECTED_COMMIT=${EXPECTED_COMMIT}" \
  slurm/preflight_qwen_m2_m3.slurm)"
smoke_id="$(sbatch --parsable --dependency="afterok:${preflight_id}" \
  --export="ALL,CONFIG_MANIFEST=${CONFIG_MANIFEST},EXPECTED_COMMIT=${EXPECTED_COMMIT},PREFLIGHT_MANIFEST=${ROOT}/preflight/manifest.json" \
  slurm/smoke_qwen_m2_m3.slurm)"
printf 'preflight_id=%s\nsmoke_array_id=%s\nconfig_manifest=%s\nexpected_commit=%s\n' \
  "${preflight_id}" "${smoke_id}" "${CONFIG_MANIFEST}" "${EXPECTED_COMMIT}"
squeue -j "${preflight_id},${smoke_id}" -o '%.18i %.12P %.32j %.8T %.10M %.10l %.12R'
