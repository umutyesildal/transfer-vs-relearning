#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact authorized implementation commit}"
source_root=/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
output_root=/vol/tmp2/yesildau/vngrs_m2_oscar_audit_recovery_v1
test ! -e "$output_root"
test "$(sha256sum "$source_root/control/materialization_v3.json" | cut -d' ' -f1)" = bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10
test "$(sha256sum "$source_root/control/d0_failure.json" | cut -d' ' -f1)" = a341e4787e38720f27beeaf5815331ef0163084cb2974d91799ee5ffe426c52f
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test "$(squeue -h -n vngrs-m2-oscar-audit-v1 | wc -l)" -eq 0
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/audit_vngrs_m2_oscar_d0_v1.slurm
job_id="$(sbatch --parsable --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/audit_vngrs_m2_oscar_d0_v1.slurm)"
printf 'job_id=%s\nsource_root=%s\noutput_root=%s\n' "$job_id" "$source_root" "$output_root"
