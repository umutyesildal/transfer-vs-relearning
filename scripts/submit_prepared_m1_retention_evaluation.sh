#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="${1:-$(pwd)}"
ROOT="/vol/tmp2/yesildau/m1_retention_v1"
WAVE="${ROOT}/evaluation_v1"
cd "${REPO_ROOT}"
test -s "${WAVE}/checkpoint_registry.csv"
test -s "${WAVE}/wave_manifest.json"
test ! -e "${WAVE}/hard_suite"
test ! -e "${WAVE}/exact_prefix"
test ! -e "${WAVE}/general_capability"

preflight_id=$(sbatch --parsable slurm/preflight_m1_retention_evaluation.slurm)
preflight_manifest="${ROOT}/preflight/evaluation_${preflight_id}.json"
evaluation_id=$(sbatch --parsable --dependency="afterok:${preflight_id}" --array="0-21%3" \
  --export="ALL,PREFLIGHT_MANIFEST=${preflight_manifest}" \
  slurm/eval_m1_retention_checkpoints.slurm)
summary_id=$(sbatch --parsable --dependency="afterok:${evaluation_id}" \
  slurm/summarize_m1_retention_evaluation.slurm)
audit_id=$(sbatch --parsable --dependency="afterany:${evaluation_id}" \
  slurm/audit_m1_retention_evaluation.slurm)
printf 'preflight_id=%s\nevaluation_id=%s\nsummary_id=%s\naudit_id=%s\npreflight_manifest=%s\n' \
  "${preflight_id}" "${evaluation_id}" "${summary_id}" "${audit_id}" "${preflight_manifest}"
squeue -j "${preflight_id},${evaluation_id},${summary_id},${audit_id}" \
  -o '%.18i %.12T %.10M %.24j %.20N %.30R'
