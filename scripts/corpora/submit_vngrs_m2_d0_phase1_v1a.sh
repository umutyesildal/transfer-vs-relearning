#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact authorized implementation commit}"
test ! -e /vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/materialize_vngrs_m2_d0_phase1_v1a.slurm
phase1_id="$(sbatch --parsable --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/materialize_vngrs_m2_d0_phase1_v1a.slurm)"
printf 'phase1_id=%s\noutput_root=%s\n' "$phase1_id" /vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1
