#!/usr/bin/env bash
set -euo pipefail

ROOT="/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${REPO_ROOT}"
EXPECTED_COMMIT="$(git rev-parse HEAD)"
mkdir -p "${ROOT}/logs"
test ! -e "${ROOT}/summaries_final"
test ! -e "${ROOT}/ppl_final"

ci_id="$(sbatch --parsable \
  --job-name=qwen-pre-m2-final-ci \
  --export="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},BASELINE_ROOT=${ROOT}" \
  slurm/summarize_qwen_pre_m2_baseline_final.slurm)"
ppl_id="$(sbatch --parsable \
  --array=0-1%1 \
  --exclude=guppi5,guppi6,guppi7 \
  --job-name=qwen-pre-m2-ppl \
  --export="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},BASELINE_ROOT=${ROOT}" \
  slurm/evaluate_qwen_pre_m2_ppl_rtx3090.slurm)"

printf 'final_ci_job_id=%s\n' "${ci_id}"
printf 'ppl_array_id=%s\n' "${ppl_id}"
printf 'expected_commit=%s\n' "${EXPECTED_COMMIT}"
printf 'output_root=%s\n' "${ROOT}"
printf 'ppl_gpu_type=rtx3090\n'
printf 'ppl_excluded_nodes=guppi5,guppi6,guppi7\n'
squeue -j "${ci_id},${ppl_id}" -o '%.18i %.12P %.32j %.8T %.10M %.10l %.20N %.30R'
