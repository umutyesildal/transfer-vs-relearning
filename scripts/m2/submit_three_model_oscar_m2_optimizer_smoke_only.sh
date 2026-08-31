#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
: "${CONFIG_MANIFEST:?}"
: "${CONFIG_VALIDATION:?}"
: "${READINESS_FINAL_AUDIT:?}"
: "${REVIEW_VALIDATION:?}"
: "${EXECUTION_CONTRACT:?}"
: "${EXPECTED_CONTRACT_SHA256:?}"
: "${M2_OPTIMIZER_SMOKE_AUTHORIZATION_ACK:?}"
test "$M2_OPTIMIZER_SMOKE_AUTHORIZATION_ACK" = exact_sha_bound_user_authorization_received
test "$(sha256sum "$EXECUTION_CONTRACT" | cut -d' ' -f1)" = "$EXPECTED_CONTRACT_SHA256"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
python_bin=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
test "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$CONFIG_MANIFEST")" = M2_TRAINING_CONFIGS_PREPARED_NOT_AUTHORIZED
test "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$CONFIG_VALIDATION")" = M2_TRAINING_CONFIG_VALIDATION_PASS
test "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$READINESS_FINAL_AUDIT")" = EVIDENCE_PREPARED_AWAITING_FACT_REVIEW_AND_GPU_SMOKE
test "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$REVIEW_VALIDATION")" = M2_FACT_REVIEW_PASS
test "$(squeue -h -n m2-oscar-opt-smoke | wc -l)" -eq 0
smoke_root=/vol/tmp2/yesildau/vngrs_m2_oscar_optimizer_smoke_v1
test ! -e "$smoke_root"
test "$(df --output=avail -B1 /vol/tmp2 | tail -n 1)" -ge 53687091200
test "$(df --output=iavail /vol/tmp2 | tail -n 1)" -ge 8192
mkdir -p "$smoke_root/logs" "$smoke_root/control"
printf '{"schema_version":1,"status":"SUBMISSION_PREPARED","scientific_training":false,"automatic_retry_authorized":false,"ready_to_train":false}\n' > "$smoke_root/control/submission_state.json"
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},CONFIG_MANIFEST=${CONFIG_MANIFEST},SMOKE_ROOT=${smoke_root}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/smoke_three_model_oscar_m2_optimizer_only.slurm
smoke_id="$(sbatch --parsable --export="$exports" slurm/m2/smoke_three_model_oscar_m2_optimizer_only.slurm)"
printf '{"schema_version":1,"status":"SUBMITTED","job_id":"%s","scientific_training":false,"automatic_retry_authorized":false,"ready_to_train":false}\n' "$smoke_id" > "$smoke_root/control/submission_result.json"
printf 'smoke_job_id=%s\n' "$smoke_id"
