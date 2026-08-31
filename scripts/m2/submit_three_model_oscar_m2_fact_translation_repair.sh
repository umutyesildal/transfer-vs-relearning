#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
: "${EXECUTION_CONTRACT:?}"
: "${EXPECTED_CONTRACT_SHA256:?}"
: "${M2_FACT_TRANSLATION_REPAIR_AUTHORIZATION_ACK:?}"
test "$M2_FACT_TRANSLATION_REPAIR_AUTHORIZATION_ACK" = exact_sha_bound_user_authorization_received
test "$(sha256sum "$EXECUTION_CONTRACT" | cut -d' ' -f1)" = "$EXPECTED_CONTRACT_SHA256"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
config=configs/corpora/vngrs_m2_oscar_fact_translation_repair_v1.yaml
root=/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_v1
test ! -e "$root"
test "$(squeue -h -n m2-fact-tr-repair | wc -l)" -eq 0
test "$(df --output=avail -B1 /vol/tmp2 | tail -n 1)" -ge 5368709120
test "$(df --output=iavail /vol/tmp2 | tail -n 1)" -ge 4096
test "$(sha256sum /vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_adapter_repair_v1/manifest.json | cut -d' ' -f1)" = 68dd7ca18d794c09ce3e1b1aa8b2b4b9f6ddb175195959b24b0103c7ea65dd63
test "$(sha256sum artifacts/corpora/vngrs_m2_fact_registry_correction_v1/generated_v2/branch_b_turkish_facts_corrected.jsonl | cut -d' ' -f1)" = 46a1071d228758013d73fae4ab3925538523eb338001e00bde9d5fe178f1c4a2
mkdir -p "$root/logs" "$root/control"
printf '{"schema_version":1,"status":"SUBMISSION_PREPARED","automatic_retry_authorized":false,"ready_to_train":false}\n' > "$root/control/submission_state.json"
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" slurm/corpora/vngrs_m2_oscar_fact_translation_repair_v1.slurm
job_id="$(sbatch --parsable --export="$exports" slurm/corpora/vngrs_m2_oscar_fact_translation_repair_v1.slurm)"
printf '{"schema_version":1,"status":"SUBMITTED","job_id":"%s","automatic_retry_authorized":false,"ready_to_train":false}\n' "$job_id" > "$root/control/submission_result.json"
printf 'job_id=%s\n' "$job_id"
