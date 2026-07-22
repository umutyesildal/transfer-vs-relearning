#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
OUTPUT_ROOT="${SCRATCH_ROOT}/evaluation_v2_qwen"
cd "${REPO_ROOT}"
test ! -e "${OUTPUT_ROOT}"
mkdir -p "${SCRATCH_ROOT}"/{logs,preflight}

preflight_id=$(sbatch --parsable slurm/preflight_qwen_bridge_evaluation_recovery.slurm)
preflight_manifest="${SCRATCH_ROOT}/preflight/qwen_evaluation_recovery_${preflight_id}.json"
evaluation_id=$(sbatch --parsable --dependency="afterok:${preflight_id}" \
  --export="ALL,PREFLIGHT_MANIFEST=${preflight_manifest}" \
  slurm/evaluate_qwen_bridge_recovery.slurm)
audit_id=$(sbatch --parsable --dependency="afterany:${evaluation_id}" \
  slurm/audit_qwen_bridge_evaluation_recovery.slurm)
printf 'preflight_id=%s\nevaluation_id=%s\naudit_id=%s\npreflight_manifest=%s\n' \
  "${preflight_id}" "${evaluation_id}" "${audit_id}" "${preflight_manifest}"
squeue -j "${preflight_id},${evaluation_id},${audit_id}" \
  -o '%.18i %.12T %.10M %.24j %.20N %.30R'
