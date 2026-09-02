#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}" "${EXECUTION_CONTRACT:?}" "${EXPECTED_CONTRACT_SHA256:?}" "${M2_FINALIZER_ORDER_REPAIR_AUTHORIZATION_ACK:?}"
test "$M2_FINALIZER_ORDER_REPAIR_AUTHORIZATION_ACK" = exact_sha_bound_user_authorization_received
test "$(sha256sum "$EXECUTION_CONTRACT" | cut -d' ' -f1)" = "$EXPECTED_CONTRACT_SHA256"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"

source_root=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_1gpu_relocation_v1
test -d "$source_root/training"
test "$(find "$source_root/training" -type d -name 'checkpoint-*' | wc -l)" -eq 60
test -d "$source_root/bindings"
test "$(find "$source_root/bindings" -mindepth 1 -maxdepth 1 | wc -l)" -eq 0
test ! -e "$source_root/evaluation"
test "$(squeue -h -j 482232,482233 | wc -l)" -eq 0

root=/vol/tmp2/yesildau/vnd_m2_oscar_finalizer_numeric_order_repair_v1
test ! -e "$root"
test "$(squeue -h -n m2-oscar-finalizer-order-v1 | wc -l)" -eq 0
repair_config=configs/training/m2_oscar_finalizer_numeric_order_repair_v1.yaml
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},EXECUTION_CONTRACT=${EXECUTION_CONTRACT},EXPECTED_CONTRACT_SHA256=${EXPECTED_CONTRACT_SHA256},REPAIR_CONFIG=${repair_config}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/finalize_m2_oscar_numeric_order_repair_v1.slurm
mkdir -p "$root/logs" "$root/control" "$root/tmp" "$root/cache"
job_id="$(sbatch --parsable --export="$exports" slurm/m2/finalize_m2_oscar_numeric_order_repair_v1.slurm)"
printf '{"finalizer_repair_job_id":"%s","source_root":"%s","output_root":"%s"}\n' "$job_id" "$source_root" "$root" | tee "$root/control/submission_result.json"
