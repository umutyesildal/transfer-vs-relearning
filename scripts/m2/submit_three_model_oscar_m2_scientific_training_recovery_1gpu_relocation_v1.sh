#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}" "${EXECUTION_CONTRACT:?}" "${EXPECTED_CONTRACT_SHA256:?}" "${M2_1GPU_RELOCATION_AUTHORIZATION_ACK:?}"
test "$M2_1GPU_RELOCATION_AUTHORIZATION_ACK" = exact_sha_bound_user_authorization_received
test "$(sha256sum "$EXECUTION_CONTRACT" | cut -d' ' -f1)" = "$EXPECTED_CONTRACT_SHA256"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
old_root=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_v1
test "$(( $(find "$old_root/training" -type f 2>/dev/null | wc -l) ))" -eq 0
test "$(squeue -h -j 482225,482226 | wc -l)" -eq 0
root=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_1gpu_relocation_v1
test ! -e "$root"
test "$(squeue -h -n m2-oscar-1gpu-v1-preflight,m2-oscar-scientific-1gpu-v1,m2-oscar-1gpu-v1-finalize | wc -l)" -eq 0
training_config=configs/training/m2_oscar_scientific_training_recovery_1gpu_relocation_v1.yaml
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},EXECUTION_CONTRACT=${EXECUTION_CONTRACT},EXPECTED_CONTRACT_SHA256=${EXPECTED_CONTRACT_SHA256},TRAINING_CONFIG=${training_config}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/preflight_three_model_oscar_m2_training_recovery_1gpu_relocation_v1.slurm
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/train_three_model_oscar_m2_recovery_1gpu_relocation_v1.slurm
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/finalize_three_model_oscar_m2_training_recovery_1gpu_relocation_v1.slurm
mkdir -p "$root/logs" "$root/control" "$root/cache" "$root/tmp"
preflight_id="$(sbatch --parsable --export="$exports" slurm/m2/preflight_three_model_oscar_m2_training_recovery_1gpu_relocation_v1.slurm)"
train_id="$(sbatch --parsable --dependency="afterok:${preflight_id}" --export="$exports" slurm/m2/train_three_model_oscar_m2_recovery_1gpu_relocation_v1.slurm)"
finalize_id="$(sbatch --parsable --dependency="afterok:${train_id}" --export="$exports" slurm/m2/finalize_three_model_oscar_m2_training_recovery_1gpu_relocation_v1.slurm)"
printf '{"preflight_job_id":"%s","training_array_job_id":"%s","finalizer_job_id":"%s"}\n' "$preflight_id" "$train_id" "$finalize_id" | tee "$root/control/submission_result.json"
