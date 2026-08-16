#!/usr/bin/env bash
set -euo pipefail
preflight="${1:?Usage: $0 PREFLIGHT_JSON EXPECTED_COMMIT RECOVERY_CONTRACT_SHA256}"
expected_commit="${2:?Usage: $0 PREFLIGHT_JSON EXPECTED_COMMIT RECOVERY_CONTRACT_SHA256}"
contract_sha="${3:?Usage: $0 PREFLIGHT_JSON EXPECTED_COMMIT RECOVERY_CONTRACT_SHA256}"
test -f "${preflight}"
preflight_sha="$(sha256sum "${preflight}" | awk '{print $1}')"
evaluation_id="$(sbatch --parsable \
  --export="ALL,FALCON_RECOVERY_PREFLIGHT=${preflight},FALCON_RECOVERY_PREFLIGHT_SHA256=${preflight_sha},M1_V4_EXPECTED_COMMIT=${expected_commit},FALCON_EVALUATION_RECOVERY_SHA256=${contract_sha}" \
  slurm/m1/eval_m1_dose_pareto_falcon_recovery_rtx3090.slurm)"
summary_id="$(sbatch --parsable \
  --dependency=afterok:${evaluation_id} \
  --export="ALL,FALCON_RECOVERY_PREFLIGHT=${preflight},FALCON_RECOVERY_PREFLIGHT_SHA256=${preflight_sha},M1_V4_EXPECTED_COMMIT=${expected_commit},FALCON_EVALUATION_RECOVERY_SHA256=${contract_sha}" \
  slurm/m1/summarize_m1_dose_pareto_falcon_recovery.slurm)"
printf 'evaluation_array_id=%s\nsummary_job_id=%s\npreflight_sha256=%s\n' \
  "${evaluation_id}" "${summary_id}" "${preflight_sha}"
