#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact authorized implementation commit}"
preflight_json="/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1-preflight.json"
test ! -e /vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1
test ! -e "$preflight_json"
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},PREFLIGHT_JSON=${preflight_json}"
sbatch --test-only --export="$exports" slurm/m2/preflight_vngrs_m2_d0.slurm
sbatch --test-only --export="$exports" slurm/m2/materialize_vngrs_m2_d0_phase1.slurm
preflight_id="$(sbatch --parsable --export="$exports" slurm/m2/preflight_vngrs_m2_d0.slurm)"
phase1_id="$(sbatch --parsable --dependency="afterok:${preflight_id}" --export="$exports" slurm/m2/materialize_vngrs_m2_d0_phase1.slurm)"
printf 'preflight_id=%s\nphase1_id=%s\npreflight_json=%s\n' "$preflight_id" "$phase1_id" "$preflight_json"
