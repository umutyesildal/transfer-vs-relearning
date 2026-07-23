#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_retention_seed43_v1"
cd "${REPO_ROOT}"
mkdir -p "${SCRATCH_ROOT}"/{logs,preflight}

preflight_id=$(sbatch --parsable slurm/preflight_m1_retention_seed43.slurm)
preflight_manifest="${SCRATCH_ROOT}/preflight/family_${preflight_id}.json"
training_id=$(sbatch --parsable --dependency="afterok:${preflight_id}" \
  --export="ALL,PREFLIGHT_MANIFEST=${preflight_manifest}" \
  slurm/train_m1_retention_seed43.slurm)
audit_id=$(sbatch --parsable --dependency="afterany:${training_id}" \
  --export="ALL,TRAINING_JOB_ID=${training_id}" \
  slurm/audit_m1_retention_seed43.slurm)

printf 'preflight_id=%s\ntraining_id=%s\naudit_id=%s\npreflight_manifest=%s\n' \
  "${preflight_id}" "${training_id}" "${audit_id}" "${preflight_manifest}"
squeue -j "${preflight_id},${training_id},${audit_id}" \
  -o '%.18i %.12T %.10M %.24j %.20N %.30R'
