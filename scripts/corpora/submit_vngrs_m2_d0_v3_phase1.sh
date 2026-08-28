#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact authorized implementation commit}"
test ! -e /vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
v2_failure=/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v2/control/failure.json
v2_partial=/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v2/raw/.partial/data/train-00004-of-00284.parquet
test -f "$v2_failure"
test "$(stat -c '%s' "$v2_partial")" = 448718347
test "$(sha256sum "$v2_partial" | cut -d' ' -f1)" = d72ae76652c1a3880288ebbea9d0004e17c03730971f62666ed09c6c87de0943
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/materialize_vngrs_m2_d0_v3_phase1.slurm
phase1_id="$(sbatch --parsable --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/materialize_vngrs_m2_d0_v3_phase1.slurm)"
printf 'phase1_id=%s\noutput_root=%s\n' "$phase1_id" /vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
