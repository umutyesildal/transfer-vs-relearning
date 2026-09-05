#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}" "${EXECUTION_CONTRACT:?}" "${EXPECTED_CONTRACT_SHA256:?}"
: "${M2_ANALYSIS_CORRECTION_AUTHORIZATION_ACK:?}"
test "$M2_ANALYSIS_CORRECTION_AUTHORIZATION_ACK" = exact_sha_bound_user_authorization_received
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test "$(sha256sum "$EXECUTION_CONTRACT" | cut -d' ' -f1)" = "$EXPECTED_CONTRACT_SHA256"

source_root=/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_recovery_v1a
root=/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_analysis_correction_v1
test ! -e "$root"
test -f "$source_root/control/evaluation_family_result.json"
test "$(sha256sum "$source_root/control/evaluation_family_result.json" | cut -d' ' -f1)" = c04eff5ba1301f5fcd4a318cc3a88d281e389cd05f542e6f6d569826809bcebf
test "$(squeue -h -u yesildau -n m2-analysis-correct-v1 | wc -l)" -eq 0

config=configs/evaluation/m2_oscar_eval_v2_analysis_correction_v1.yaml
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},EXECUTION_CONTRACT=${EXECUTION_CONTRACT},EXPECTED_CONTRACT_SHA256=${EXPECTED_CONTRACT_SHA256},CORRECTION_CONFIG=${config},M2_ANALYSIS_CORRECTION_AUTHORIZATION_ACK=${M2_ANALYSIS_CORRECTION_AUTHORIZATION_ACK}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/finalize_m2_oscar_eval_analysis_correction_v1.slurm
mkdir -p "$root/logs" "$root/control" "$root/tmp"
job_id="$(sbatch --parsable --export="$exports" slurm/m2/finalize_m2_oscar_eval_analysis_correction_v1.slurm)"
printf '{"analysis_correction_job_id":"%s","source_root":"%s","output_root":"%s"}\n' \
  "$job_id" "$source_root" "$root" > "$root/control/submission_result.json"
printf '%s\n' "$job_id"
