#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
contract_id=vngrs-m2-oscar-training-readiness-evidence-v1
output_root=/vol/tmp2/yesildau/vngrs_m2_oscar_training_readiness_evidence_v1
training_root=/vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1
job_name=m2-oscar-readiness-evidence-v1
test ! -e "$output_root"
test ! -e "$training_root"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test "$(squeue -h -n "$job_name" | wc -l)" -eq 0
test "$(sha256sum /vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_adapter_repair_v1/manifest.json | cut -d' ' -f1)" = 68dd7ca18d794c09ce3e1b1aa8b2b4b9f6ddb175195959b24b0103c7ea65dd63
available_inodes="$(df -Pi /vol/tmp2/yesildau | awk 'NR==2 {print $4}')"
test "$available_inodes" -ge 8192
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},OUTPUT_ROOT=${output_root}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/prepare_three_model_oscar_m2_training_readiness.slurm
mkdir -p "$output_root/control" "$output_root/logs"
printf '{"schema_version":1,"status":"SUBMISSION_PREPARED","contract_id":"%s","expected_commit":"%s","automatic_retry_authorized":false,"ready_to_train":false}\n' "$contract_id" "$EXPECTED_COMMIT" > "$output_root/control/submission_state.json"
job_id="$(sbatch --parsable --output="$output_root/logs/slurm-%j.stdout.log" --error="$output_root/logs/slurm-%j.stderr.log" --export="$exports" slurm/m2/prepare_three_model_oscar_m2_training_readiness.slurm)"
printf '{"schema_version":1,"status":"SUBMITTED","job_id":"%s","contract_id":"%s","automatic_retry_authorized":false}\n' "$job_id" "$contract_id" > "$output_root/control/submission_result.json"
printf 'job_id=%s\noutput_root=%s\n' "$job_id" "$output_root"
