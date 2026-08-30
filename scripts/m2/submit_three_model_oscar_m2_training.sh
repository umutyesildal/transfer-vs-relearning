#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
: "${CONFIG_MANIFEST:?}"
: "${EXECUTION_CONTRACT:?}"
: "${EXPECTED_CONTRACT_SHA256:?}"
: "${M2_TRAINING_AUTHORIZATION_ACK:?}"
test "$M2_TRAINING_AUTHORIZATION_ACK" = exact_sha_bound_user_authorization_received
test "$(sha256sum "$EXECUTION_CONTRACT" | cut -d' ' -f1)" = "$EXPECTED_CONTRACT_SHA256"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test -f "$CONFIG_MANIFEST"
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$CONFIG_MANIFEST")" = M2_TRAINING_CONFIGS_PREPARED_NOT_AUTHORIZED
test "$(squeue -h -n m2-oscar-3model-smoke,m2-oscar-3model-train | wc -l)" -eq 0
mkdir -p /vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1/logs
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},CONFIG_MANIFEST=${CONFIG_MANIFEST}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/smoke_three_model_oscar_m2.slurm
smoke_id="$(sbatch --parsable --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/smoke_three_model_oscar_m2.slurm)"
train_exports="${exports},SMOKE_JOB_ID=${smoke_id}"
train_id="$(sbatch --parsable --dependency="afterok:${smoke_id}" --export="$train_exports" slurm/m2/train_three_model_oscar_m2.slurm)"
printf 'smoke_job_id=%s\ntraining_job_id=%s\n' "$smoke_id" "$train_id"
