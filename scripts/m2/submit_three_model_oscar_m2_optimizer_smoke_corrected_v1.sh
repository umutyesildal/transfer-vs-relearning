#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
: "${EXECUTION_CONTRACT:?}"
: "${EXPECTED_CONTRACT_SHA256:?}"
: "${M2_CORRECTED_OPTIMIZER_SMOKE_AUTHORIZATION_ACK:?}"
test "$M2_CORRECTED_OPTIMIZER_SMOKE_AUTHORIZATION_ACK" = exact_sha_bound_user_authorization_received
test "$(sha256sum "$EXECUTION_CONTRACT" | cut -d' ' -f1)" = "$EXPECTED_CONTRACT_SHA256"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
python_bin=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
readiness=/vol/tmp2/yesildau/vngrs_m2_oscar_training_readiness_evidence_retry_v1
config_manifest="$readiness/configs/config_manifest.json"
config_validation="$readiness/config_validation.json"
readiness_audit="$readiness/control/final_audit.json"
family_root=/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_retry_v2
family_manifest="$family_root/manifest.json"
family_audit="$family_root/control/final_audit.json"
review_validation=artifacts/corpora/vngrs_m2_fact_registry_correction_v1/generated_v2/human_review_validation_corrected.json
smoke_root=/vol/tmp2/yesildau/vnd_m2_oscar_optimizer_smoke_corrected_v1
test ! -e "$smoke_root"
test "$(sha256sum "$config_manifest" | cut -d' ' -f1)" = 755295ddda651466cbf868b52bd24c272475a17e29c7988f9f97c3eb83951784
test "$(sha256sum "$config_validation" | cut -d' ' -f1)" = 5c53f907c26eb3dae602825dbbe0a30aebc0ba0c3c238876cf39ac45a34ab815
test "$(sha256sum "$readiness_audit" | cut -d' ' -f1)" = d8cd44eae03ec1c5b5eea334bf94506417730c30f44dfbfbf6df2bf60a144fc8
test "$(sha256sum "$family_manifest" | cut -d' ' -f1)" = 96f9867c857b08bfd784660331d1a354be7d7c6bc39250091f427fdfaa3c6486
test "$(sha256sum "$family_audit" | cut -d' ' -f1)" = fc2075cbce7f4d51c8013b7977ec64630d2181c8c9ebf30a64f5cab61514e54d
test "$(sha256sum "$review_validation" | cut -d' ' -f1)" = a5e4f04a567de98f85674e8c58e13effe85753738d5de931704e41a153ec20b1
test "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$config_manifest")" = M2_TRAINING_CONFIGS_PREPARED_NOT_AUTHORIZED
test "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$config_validation")" = M2_TRAINING_CONFIG_VALIDATION_PASS
test "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$readiness_audit")" = EVIDENCE_PREPARED_AWAITING_FACT_REVIEW_AND_GPU_SMOKE
test "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$review_validation")" = M2_FACT_REVIEW_PASS
test "$("$python_bin" -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["repair_status"],d["ready_to_train"])' "$family_manifest")" = "M2_FACT_TRANSLATION_REPAIR_PASS False"
test "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$family_audit")" = M2_FACT_TRANSLATION_REPAIR_PASS
test "$(squeue -h -n m2-opt-smoke-corrected | wc -l)" -eq 0
test "$(df --output=avail -B1 /vol/tmp2 | tail -n 1)" -ge 53687091200
test "$(df --output=iavail /vol/tmp2 | tail -n 1)" -ge 8192
mkdir -p "$smoke_root/logs" "$smoke_root/control"
printf '{"schema_version":1,"status":"SUBMISSION_PREPARED","scientific_training":false,"automatic_retry_authorized":false,"ready_to_train":false}\n' > "$smoke_root/control/submission_state.json"
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},CONFIG_MANIFEST=${config_manifest},BLOCK_FAMILY_MANIFEST=${family_manifest},BLOCK_FAMILY_MANIFEST_SHA256=96f9867c857b08bfd784660331d1a354be7d7c6bc39250091f427fdfaa3c6486,SMOKE_ROOT=${smoke_root}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/m2/smoke_three_model_oscar_m2_optimizer_corrected_v1.slurm
smoke_id="$(sbatch --parsable --export="$exports" slurm/m2/smoke_three_model_oscar_m2_optimizer_corrected_v1.slurm)"
printf '{"schema_version":1,"status":"SUBMITTED","job_id":"%s","scientific_training":false,"automatic_retry_authorized":false,"ready_to_train":false}\n' "$smoke_id" > "$smoke_root/control/submission_result.json"
printf 'smoke_job_id=%s\n' "$smoke_id"
