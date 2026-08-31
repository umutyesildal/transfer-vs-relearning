#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
contract_id=vngrs-m2-oscar-training-readiness-evidence-v1a
failed_root=/vol/tmp2/yesildau/vngrs_m2_oscar_training_readiness_evidence_v1
output_root=/vol/tmp2/yesildau/vngrs_m2_oscar_training_readiness_evidence_retry_v1
training_root=/vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1
job_name=m2-oscar-readiness-evidence-v1a
test "$(find "$failed_root" -type f | wc -l)" -eq 5
test "$(du -sb "$failed_root" | cut -f1)" -eq 14971
test "$(sha256sum "$failed_root/logs/slurm-482035.stderr.log" | cut -d' ' -f1)" = e31ebce25931b74eda597610a6dfb65bf8879c78dff3e59713adfa49ec2cd118
test "$(sha256sum "$failed_root/control/slurm_exit.json" | cut -d' ' -f1)" = 29f49bf6beb885d0990dbdfe041d945b4f2eaad6149d85d2e978f6e772b6bdcd
test ! -e "$output_root"; test ! -e "$training_root"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"; test -z "$(git status --porcelain=v1)"
test "$(squeue -h -n "$job_name" | wc -l)" -eq 0
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},OUTPUT_ROOT=${output_root}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/prepare_three_model_oscar_m2_training_readiness_v1a.slurm
mkdir -p "$output_root/control" "$output_root/logs"
printf '{"schema_version":1,"status":"SUBMISSION_PREPARED","contract_id":"%s","expected_commit":"%s","failed_predecessor_job":"482035","automatic_retry_authorized":false,"ready_to_train":false}\n' "$contract_id" "$EXPECTED_COMMIT" > "$output_root/control/submission_state.json"
job_id="$(sbatch --parsable --output="$output_root/logs/slurm-%j.stdout.log" --error="$output_root/logs/slurm-%j.stderr.log" --export="$exports" slurm/m2/prepare_three_model_oscar_m2_training_readiness_v1a.slurm)"
printf '{"schema_version":1,"status":"SUBMITTED","job_id":"%s","contract_id":"%s","automatic_retry_authorized":false}\n' "$job_id" "$contract_id" > "$output_root/control/submission_result.json"
printf 'job_id=%s\noutput_root=%s\n' "$job_id" "$output_root"
