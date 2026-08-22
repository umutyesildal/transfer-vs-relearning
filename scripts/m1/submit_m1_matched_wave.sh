#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact authorized implementation commit}"
root=/vol/tmp2/yesildau/m1_matched_three_model_v1
manifest="${root}/control/preflight.json"
test ! -e "$root"
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},FAMILY_ROOT=${root},PREFLIGHT_MANIFEST=${manifest}"
sbatch --test-only --export="$exports" slurm/m1/preflight_m1_matched_wave.slurm
sbatch --test-only --array=0-2%3 --export="$exports" slurm/m1/train_m1_matched_wave.slurm
preflight_id="$(sbatch --parsable --export="$exports" slurm/m1/preflight_m1_matched_wave.slurm)"
training_id="$(sbatch --parsable --dependency="afterok:${preflight_id}" --array=0-2%3 --export="$exports" slurm/m1/train_m1_matched_wave.slurm)"
audit_id="$(sbatch --parsable --dependency="afterany:${training_id}" --export="$exports" slurm/m1/audit_m1_matched_wave.slurm)"
printf 'preflight_id=%s\ntraining_id=%s\naudit_id=%s\nfamily_root=%s\n' "$preflight_id" "$training_id" "$audit_id" "$root"
