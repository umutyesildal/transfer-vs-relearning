#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact authorized implementation commit}"
test ! -e /vol/tmp2/yesildau/vngrs_m2_three_model_d0_v2
v1_failure=/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1/control/preflight_failure.json
test "$(stat -c '%s' "$v1_failure")" = 351
test "$(sha256sum "$v1_failure" | cut -d' ' -f1)" = 54e3f59abd2df14cc00acb260dbe13c0f90dd5a18a22e8d0eb9089f31382a1ce
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/materialize_vngrs_m2_d0_v2_phase1.slurm
phase1_id="$(sbatch --parsable --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/materialize_vngrs_m2_d0_v2_phase1.slurm)"
printf 'phase1_id=%s\noutput_root=%s\n' "$phase1_id" /vol/tmp2/yesildau/vngrs_m2_three_model_d0_v2
