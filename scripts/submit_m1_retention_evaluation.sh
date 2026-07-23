#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="${1:-$(pwd)}"
ROOT="/vol/tmp2/yesildau/m1_retention_v1"
cd "${REPO_ROOT}"
mkdir -p "${ROOT}"/{logs,preflight}

recovery_audit_id=$(sbatch --parsable --export="ALL,TRAINING_JOB_ID=411279" \
  slurm/audit_m1_retention_seed42.slurm)
prepare_id=$(sbatch --parsable slurm/prepare_m1_retention_evaluation.slurm)
preflight_id=$(sbatch --parsable --dependency="afterok:${prepare_id}" \
  slurm/preflight_m1_retention_evaluation.slurm)
preflight_manifest="${ROOT}/preflight/evaluation_${preflight_id}.json"
evaluation_id=$(sbatch --parsable --dependency="afterok:${preflight_id}" --array="0-21%3" \
  --export="ALL,PREFLIGHT_MANIFEST=${preflight_manifest}" \
  slurm/eval_m1_retention_checkpoints.slurm)
summary_id=$(sbatch --parsable --dependency="afterok:${evaluation_id}" \
  slurm/summarize_m1_retention_evaluation.slurm)
audit_id=$(sbatch --parsable --dependency="afterany:${evaluation_id}" \
  slurm/audit_m1_retention_evaluation.slurm)
printf 'recovery_audit_id=%s\nprepare_id=%s\npreflight_id=%s\nevaluation_id=%s\nsummary_id=%s\naudit_id=%s\npreflight_manifest=%s\n' \
  "${recovery_audit_id}" "${prepare_id}" "${preflight_id}" "${evaluation_id}" \
  "${summary_id}" "${audit_id}" "${preflight_manifest}"
squeue -j "${recovery_audit_id},${prepare_id},${preflight_id},${evaluation_id},${summary_id},${audit_id}" \
  -o '%.18i %.12T %.10M %.24j %.20N %.30R'
