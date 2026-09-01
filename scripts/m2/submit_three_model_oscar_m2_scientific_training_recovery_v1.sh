#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
: "${EXECUTION_CONTRACT:?}"
: "${EXPECTED_CONTRACT_SHA256:?}"
: "${M2_TRAINING_RECOVERY_AUTHORIZATION_ACK:?}"
test "$M2_TRAINING_RECOVERY_AUTHORIZATION_ACK" = exact_sha_bound_user_authorization_received
test "$(sha256sum "$EXECUTION_CONTRACT" | cut -d' ' -f1)" = "$EXPECTED_CONTRACT_SHA256"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
root=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_v1
test ! -e "$root"
test "$(squeue -h -n m2-oscar-recovery-v1-preflight,m2-oscar-scientific-recovery-v1,m2-oscar-recovery-v1-finalize | wc -l)" -eq 0
dead_job=482208
dead_line="$(squeue -h -j "$dead_job" -o '%i|%T|%r|%S|%E')"
IFS='|' read -r observed_id observed_state observed_reason observed_start observed_dependency <<<"$dead_line"
test "$observed_id" = "$dead_job"
test "$observed_state" = PENDING
test "$observed_reason" = DependencyNeverSatisfied
test "$observed_start" = N/A -o "$observed_start" = Unknown
case "$observed_dependency" in *482207*) ;; *) exit 1 ;; esac
dead_control="$(scontrol show job -o "$dead_job")"
case "$dead_control" in *JobState=PENDING*) ;; *) exit 1 ;; esac
case "$dead_control" in *Reason=DependencyNeverSatisfied*) ;; *) exit 1 ;; esac
case "$dead_control" in *RunTime=00:00:00*) ;; *) exit 1 ;; esac
training_config=configs/training/m2_oscar_scientific_training_recovery_v1.yaml
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},EXECUTION_CONTRACT=${EXECUTION_CONTRACT},EXPECTED_CONTRACT_SHA256=${EXPECTED_CONTRACT_SHA256},TRAINING_CONFIG=${training_config}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/preflight_three_model_oscar_m2_training_recovery_v1.slurm
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/train_three_model_oscar_m2_recovery_v1.slurm
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/finalize_three_model_oscar_m2_training_recovery_v1.slurm
scancel "$dead_job"
mkdir -p "$root/logs" "$root/control" "$root/cache" "$root/tmp"
preflight_id="$(sbatch --parsable --export="$exports" slurm/m2/preflight_three_model_oscar_m2_training_recovery_v1.slurm)"
train_id="$(sbatch --parsable --dependency="afterok:${preflight_id}" --export="$exports" slurm/m2/train_three_model_oscar_m2_recovery_v1.slurm)"
finalize_id="$(sbatch --parsable --dependency="afterok:${train_id}" --export="$exports" slurm/m2/finalize_three_model_oscar_m2_training_recovery_v1.slurm)"
printf '{"cancelled_dependency_dead_finalizer":"%s","preflight_job_id":"%s","training_array_job_id":"%s","finalizer_job_id":"%s"}\n' \
  "$dead_job" "$preflight_id" "$train_id" "$finalize_id" | tee "$root/control/submission_result.json"
