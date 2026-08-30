#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact separately authorized implementation commit}"
contract_id=vngrs-m2-oscar-exact-block-materialization-adapter-repair-v1
failed_job=482007
failed_root=/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_recovery_v1
predecessor_root=/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_v1
source_root=/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
split_root=/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1
output_root=/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_adapter_repair_v1
job_name=vngrs-m2-oscar-blocks-adapter-repair-v1

test -z "$(squeue -h -j "$failed_job")"
test "$(find "$failed_root" -maxdepth 3 -type f | wc -l)" -eq 8
test "$(du -sb "$failed_root" | cut -f1)" -eq 123392
test "$(sha256sum "$failed_root/control/failure.json" | cut -d' ' -f1)" = 1ce489502583f900a039e1776e67d4d2992d945405d49cfac3bf385a93c799d7
test "$(sha256sum "$failed_root/control/progress.json" | cut -d' ' -f1)" = 2badd02ca329ea7ce4ef5808981746fbd3e85bc88d29a4f01f15b1b24d69af38
test "$(sha256sum "$failed_root/control/slurm_exit.json" | cut -d' ' -f1)" = e427d45ca3e911b5c11b5a77b703e8ffdfa2f4192095e63a180155a3b0bbf914
test "$(sha256sum "$failed_root/control/slurm-482007.stderr.log" | cut -d' ' -f1)" = 0e48d7e87d46078a5b8acc91e4e55a349dda2b1ecc0b1578a8d1df5e420de821
test ! -e "$failed_root/manifest.json"
test ! -e "$failed_root/blocks"
test ! -e "$output_root"
test "$(find "$predecessor_root" -type f | wc -l)" -eq 1
test "$(sha256sum "$predecessor_root/facts/branch_b_turkish_facts.jsonl" | cut -d' ' -f1)" = 784f78a5a182c329b4b995ee1a97c580da994059a18b1f9702ec657569ccbfec
test "$(sha256sum "$source_root/control/materialization_v3.json" | cut -d' ' -f1)" = bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10
test "$(sha256sum "$split_root/splits/train_document_ids.jsonl" | cut -d' ' -f1)" = 90b74fbcfe62107693c35161fc328a6e43b13a830fc9590cc9810d3e99955aac
test "$(sha256sum "$split_root/splits/heldout_document_ids.jsonl" | cut -d' ' -f1)" = dc30629fe76ca722745fcd0148021de6c042218ed2994281d52d13c06011dc91
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test -x /usr/bin/time
test "$(squeue -h -n "$job_name" | wc -l)" -eq 0
available_bytes="$(df -PB1 /vol/tmp2/yesildau | awk 'NR==2 {print $4}')"
available_inodes="$(df -Pi /vol/tmp2/yesildau | awk 'NR==2 {print $4}')"
test "$available_bytes" -ge 10737418240
test "$available_inodes" -ge 4096

exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},OUTPUT_ROOT=${output_root}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/materialize_three_model_oscar_m2_blocks_adapter_repair.slurm

mkdir -p "$output_root/control"
temporary="$output_root/control/submission_state.json.tmp"
printf '{"schema_version":1,"status":"SUBMISSION_PREPARED","contract_id":"%s","expected_commit":"%s","repaired_from_terminal_job":"%s","repaired_from_root":"%s","automatic_retry_authorized":false,"ready_to_train":false}\n' \
  "$contract_id" "$EXPECTED_COMMIT" "$failed_job" "$failed_root" > "$temporary"
mv "$temporary" "$output_root/control/submission_state.json"
job_id="$(sbatch --parsable \
  --output="$output_root/control/slurm-%j.stdout.log" \
  --error="$output_root/control/slurm-%j.stderr.log" \
  --export="$exports" \
  slurm/m2/materialize_three_model_oscar_m2_blocks_adapter_repair.slurm)"
temporary="$output_root/control/submission_result.json.tmp"
printf '{"schema_version":1,"status":"SUBMITTED","job_id":"%s","contract_id":"%s","automatic_retry_authorized":false}\n' \
  "$job_id" "$contract_id" > "$temporary"
mv "$temporary" "$output_root/control/submission_result.json"
printf 'job_id=%s\noutput_root=%s\n' "$job_id" "$output_root"
