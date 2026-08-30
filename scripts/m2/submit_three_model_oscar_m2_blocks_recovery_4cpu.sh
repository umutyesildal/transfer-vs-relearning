#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact separately authorized implementation commit}"
contract_id=vngrs-m2-oscar-exact-block-materialization-recovery-4cpu-relocation-v1
old_job=482007
old_root=/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_recovery_v1
predecessor_root=/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_v1
source_root=/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
split_root=/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1
output_root=/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_recovery_4cpu_v1
job_name=vngrs-m2-oscar-blocks-recovery-4cpu-v1

test "$(date +%H%M)" -ge 0300
test "$(squeue -h -j "$old_job" -o %T)" = PENDING
test "$(squeue -h -j "$old_job" -o %r)" = JobHeldUser
test "$(find "$old_root" -maxdepth 2 -type f | wc -l)" -eq 2
test "$(sha256sum "$old_root/control/submission_state.json" | cut -d' ' -f1)" = 2eb731f41f3fcce810b6c7153ed50ea6823e2cc1a311eb180f794a35756e792c
test "$(sha256sum "$old_root/control/submission_result.json" | cut -d' ' -f1)" = 2c099abba7d6da631228dee8721bb06bf8a0c7a30aee57ba5f8bf260deccf66b
test ! -e "$old_root/control/progress.json"
test ! -e "$old_root/manifest.json"
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
  slurm/m2/materialize_three_model_oscar_m2_blocks_recovery_4cpu.slurm

scancel "$old_job"
for _ in $(seq 1 30); do
  if test -z "$(squeue -h -j "$old_job")"; then break; fi
  sleep 1
done
test -z "$(squeue -h -j "$old_job")"

mkdir -p "$output_root/control"
temporary="$output_root/control/submission_state.json.tmp"
printf '{"schema_version":1,"status":"SUBMISSION_PREPARED","contract_id":"%s","expected_commit":"%s","relocated_from_cancelled_pending_job":"%s","relocated_from_root":"%s","automatic_retry_authorized":false,"ready_to_train":false}\n' \
  "$contract_id" "$EXPECTED_COMMIT" "$old_job" "$old_root" > "$temporary"
mv "$temporary" "$output_root/control/submission_state.json"
job_id="$(sbatch --parsable \
  --output="$output_root/control/slurm-%j.stdout.log" \
  --error="$output_root/control/slurm-%j.stderr.log" \
  --export="$exports" \
  slurm/m2/materialize_three_model_oscar_m2_blocks_recovery_4cpu.slurm)"
temporary="$output_root/control/submission_result.json.tmp"
printf '{"schema_version":1,"status":"SUBMITTED","job_id":"%s","contract_id":"%s","automatic_retry_authorized":false}\n' \
  "$job_id" "$contract_id" > "$temporary"
mv "$temporary" "$output_root/control/submission_result.json"
printf 'cancelled_job_id=%s\njob_id=%s\noutput_root=%s\n' "$old_job" "$job_id" "$output_root"
