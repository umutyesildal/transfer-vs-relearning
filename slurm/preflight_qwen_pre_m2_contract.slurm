#!/usr/bin/env bash
#SBATCH --job-name=qwen-pre-m2-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:20:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1_logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1_logs/%x-%j.err
set -euo pipefail

: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"

HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
OUTPUT_ROOT=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1
LOG_ROOT=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1_logs
RESERVE_BYTES=$((512 * 1024 * 1024))
HOME_LIMIT_BYTES=30000000000

test -d "${REPO_ROOT}"
test ! -e "${OUTPUT_ROOT}"
test -f "${REPO_ROOT}/scripts/build_qwen_pre_m2_contract.py"
test -f "${REPO_ROOT}/src/transfer_vs_relearning/data/qwen_pre_m2.py"
test -s "${REPO_ROOT}/artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv"
test -s "${REPO_ROOT}/artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/summary.json"

observed_commit=$(git -C "${REPO_ROOT}" rev-parse HEAD)
test "${observed_commit}" = "${EXPECTED_COMMIT}"

tmp2_available_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
tmp2_available_inodes=$(df -Pi /vol/tmp2 | tail -n 1 | awk '{print $4}')
test $((tmp2_available_kib * 1024)) -ge "${RESERVE_BYTES}"
test "${tmp2_available_inodes}" -gt 0

for path in "${OUTPUT_ROOT}" "${LOG_ROOT}"; do
  case "$(readlink -m "${path}")" in
    /vol/tmp2/yesildau/*) ;;
    *) printf 'unsafe_path=%s\n' "${path}" >&2; exit 2 ;;
  esac
done

mkdir -p "${LOG_ROOT}"
home_du_human_path="${LOG_ROOT}/home_du_human_${SLURM_JOB_ID}.txt"
home_usage_method="direct_du"
if ! timeout 120s du -xsh "${HOME_ROOT}" > "${home_du_human_path}" 2>&1; then
  home_usage_method="top_level_sum_after_du_timeout"
  printf '%s\n' 'warning=full_home_du_timed_out_using_top_level_sum' >&2
  : > "${LOG_ROOT}/home_top_level_${SLURM_JOB_ID}.txt"
  home_kib=0
  while IFS= read -r child_path; do
    child_kib=$(timeout 30s du -xsk "${child_path}" 2>/dev/null | awk 'NR == 1 {print $1}')
    test -n "${child_kib}"
    printf '%s %s\n' "${child_kib}" "${child_path}" | tee -a "${LOG_ROOT}/home_top_level_${SLURM_JOB_ID}.txt"
    home_kib=$((home_kib + child_kib))
  done < <(find "${HOME_ROOT}" -mindepth 1 -maxdepth 1 -print | sort)
else
  home_kib=$(timeout 120s du -xsk "${HOME_ROOT}" | awk 'NR == 1 {print $1}')
  test -n "${home_kib}"
fi
test $((home_kib * 1024)) -lt "${HOME_LIMIT_BYTES}"

find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr > \
  "${LOG_ROOT}/home_large_before_${SLURM_JOB_ID}.txt"

bash -n \
  "${REPO_ROOT}/slurm/preflight_qwen_pre_m2_contract.slurm" \
  "${REPO_ROOT}/slurm/prepare_qwen_pre_m2_contract.slurm"

created_at=$(date --iso-8601=seconds)
printf '{"status":"passed","created_at":"%s","git_commit":"%s","home_kib":%s,"home_usage_method":"%s","home_limit_bytes":%s,"tmp2_available_kib":%s,"tmp2_available_inodes":%s,"reserve_bytes":%s,"expected_checkpoints":0,"estimated_family_bytes":%s,"retention_policy":"preserve_compact_registry_manifest_and_hashes"}\n' \
  "${created_at}" "${observed_commit}" "${home_kib}" "${home_usage_method}" "${HOME_LIMIT_BYTES}" \
  "${tmp2_available_kib}" "${tmp2_available_inodes}" "${RESERVE_BYTES}" "${RESERVE_BYTES}" > \
  "${LOG_ROOT}/preflight_${SLURM_JOB_ID}.json"

if test -s "${home_du_human_path}"; then
  cat "${home_du_human_path}"
else
  printf '%s\n' 'warning=full_home_du_output_unavailable_top_level_sum_recorded' >&2
fi
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
readlink -f "${HOME_ROOT}/transfer-vs-relearning/runs"
readlink -f "${HOME_ROOT}/transfer-vs-relearning/artifacts"
printf 'status=passed resolved_output_root=%s resolved_log_root=%s expected_checkpoints=0 estimated_family_bytes=%s retention=preserve_compact_registry_manifest_and_hashes\n' \
  "$(readlink -m "${OUTPUT_ROOT}")" "$(readlink -m "${LOG_ROOT}")" "${RESERVE_BYTES}"
