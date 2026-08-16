#!/usr/bin/env bash
set -euo pipefail

ROOT=/vol/tmp2/yesildau/qwen_m2_m3_v1
EVAL_ROOT="${ROOT}/evaluation_v1"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${REPO_ROOT}"
EXPECTED_COMMIT="$(git rev-parse HEAD)"
test ! -e "${EVAL_ROOT}"
mkdir -p "${ROOT}/logs"

preflight_id="$(sbatch --parsable \
  --export="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT}" \
  slurm/m2/preflight_qwen_m2_m3_evaluation.slurm)"
evaluation_id="$(sbatch --parsable \
  --dependency="afterok:${preflight_id}" \
  --array=0-95%1 \
  --gres=gpu:rtx3090:1 \
  --nodelist=guppi8 \
  --exclude=guppi5,guppi6,guppi7 \
  --export="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},PREFLIGHT_MANIFEST=${EVAL_ROOT}/preflight/manifest.json,EVALUATION_MANIFEST=${EVAL_ROOT}/evaluation_manifest.json" \
  slurm/m2/eval_qwen_m2_m3_slice.slurm)"
printf 'preflight_id=%s\nevaluation_array_id=%s\nevaluation_manifest=%s\nexpected_commit=%s\ngpu_type=rtx3090\nnode=guppi8\narray=0-95%%1\n' \
  "${preflight_id}" "${evaluation_id}" "${EVAL_ROOT}/evaluation_manifest.json" "${EXPECTED_COMMIT}"
squeue -j "${preflight_id},${evaluation_id}" -o '%.18i %.12P %.32j %.8T %.10M %.10l %.20N %.30R'
