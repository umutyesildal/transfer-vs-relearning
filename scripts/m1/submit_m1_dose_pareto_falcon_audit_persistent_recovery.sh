#!/usr/bin/env bash
set -euo pipefail
preflight="${1:?Usage: $0 PREFLIGHT_JSON EXPECTED_COMMIT CONTRACT_SHA256}"
expected_commit="${2:?Usage: $0 PREFLIGHT_JSON EXPECTED_COMMIT CONTRACT_SHA256}"
contract_sha="${3:?Usage: $0 PREFLIGHT_JSON EXPECTED_COMMIT CONTRACT_SHA256}"
test -f "${preflight}"
preflight_sha="$(sha256sum "${preflight}" | awk '{print $1}')"
dead_present="$(python3 -c 'import json,sys; print(str(bool(json.load(open(sys.argv[1]))["dead_summary_job_present"])).lower())' "${preflight}")"
if [[ "${dead_present}" == true ]]; then scancel 456502; fi
exports="ALL,FALCON_RECOVERY_PREFLIGHT=${preflight},FALCON_RECOVERY_PREFLIGHT_SHA256=${preflight_sha},M1_V4_EXPECTED_COMMIT=${expected_commit},FALCON_AUDIT_PERSISTENT_SHA256=${contract_sha}"
sbatch --test-only --export="${exports}" slurm/m1/eval_m1_dose_pareto_falcon_audit_persistent_recovery.slurm
evaluation_id="$(sbatch --parsable --export="${exports}" slurm/m1/eval_m1_dose_pareto_falcon_audit_persistent_recovery.slurm)"
summary_id="$(sbatch --parsable --dependency=afterok:${evaluation_id} --export="${exports}" slurm/m1/summarize_m1_dose_pareto_falcon_audit_persistent_recovery.slurm)"
printf 'evaluation_job_id=%s\nsummary_job_id=%s\npreflight_sha256=%s\n' "${evaluation_id}" "${summary_id}" "${preflight_sha}"
