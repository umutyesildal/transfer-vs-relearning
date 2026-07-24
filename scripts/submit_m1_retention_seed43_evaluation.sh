#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="${1:-$(pwd)}"; ROOT=/vol/tmp2/yesildau/m1_retention_seed43_v1; cd "${REPO_ROOT}"
test ! -e "${ROOT}/evaluation_v1"
prepare_id=$(sbatch --parsable slurm/prepare_m1_retention_seed43_evaluation.slurm)
preflight_id=$(sbatch --parsable --dependency="afterok:${prepare_id}" slurm/preflight_m1_retention_seed43_evaluation.slurm)
manifest="${ROOT}/preflight/evaluation_${preflight_id}.json"
evaluation_id=$(sbatch --parsable --dependency="afterok:${preflight_id}" --array="0-10%3" --export="ALL,PREFLIGHT_MANIFEST=${manifest}" slurm/eval_m1_retention_seed43_checkpoints.slurm)
summary_id=$(sbatch --parsable --dependency="afterok:${evaluation_id}" slurm/summarize_m1_retention_seed43_evaluation.slurm)
audit_id=$(sbatch --parsable --dependency="afterany:${evaluation_id}" slurm/audit_m1_retention_seed43_evaluation.slurm)
printf 'prepare_id=%s\npreflight_id=%s\nevaluation_id=%s\nsummary_id=%s\naudit_id=%s\npreflight_manifest=%s\n' "${prepare_id}" "${preflight_id}" "${evaluation_id}" "${summary_id}" "${audit_id}" "${manifest}"
squeue -j "${prepare_id},${preflight_id},${evaluation_id},${summary_id},${audit_id}" -o '%.18i %.12T %.10M %.24j %.20N %.30R'
