#!/usr/bin/env bash
# Final 2,000-bootstrap aggregation for the completed Qwen pre-M2 factual baseline.
# This job only reads completed scratch evidence and writes compact summaries to scratch.
#SBATCH --job-name=qwen-pre-m2-final-ci
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1/logs/%x-%j.err
set -euo pipefail

: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"
HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT="${BASELINE_ROOT:-/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1}"
CONTRACT_ROOT="/vol/tmp2/yesildau/qwen_pre_m2_contract_v1"
RESULTS_ROOT="${ROOT}/results"
SUMMARY_ROOT="${ROOT}/summaries_final"
TMP_ROOT="${ROOT}/tmp/final_ci_${SLURM_JOB_ID}"

cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test -s "${ROOT}/preflight/manifest.json"
test -d "${RESULTS_ROOT}"
test ! -e "${SUMMARY_ROOT}"
test -s "${CONTRACT_ROOT}/manifest.json"

home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
test "${home_kib}" -lt $((30 * 1024 * 1024))
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
readlink -f "${REPO_ROOT}/runs"
readlink -f "${REPO_ROOT}/artifacts"

module load anaconda/3-2024.06
python_bin="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"
mkdir -p "${SUMMARY_ROOT}" "${TMP_ROOT}"
export TMPDIR="${TMP_ROOT}"

"${python_bin}" - "${ROOT}/preflight/manifest.json" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["status"] == "passed"
assert payload["expected_jobs"] == 48
assert payload["expected_new_checkpoints"] == 0
assert payload.get("git_commit")
print(f"baseline_preflight_commit={payload['git_commit']}")
PY

for model_label in qwen_m1_seed42_step75 qwen_m1_seed43_step50; do
  case "${model_label}" in
    qwen_m1_seed42_step75)
      model_manifest="/vol/tmp2/yesildau/qwen_scale_selected_v1/seed42_step75/selected_artifact_manifest.json"
      ;;
    qwen_m1_seed43_step50)
      model_manifest="/vol/tmp2/yesildau/qwen_scale_selected_v1/seed43_step50/selected_artifact_manifest.json"
      ;;
  esac
  output_dir="${SUMMARY_ROOT}/${model_label}"
  test -s "${model_manifest}"
  printf 'summary_start model=%s output=%s bootstrap_samples=2000\n' "${model_label}" "${output_dir}"
  conda run --name xfer-relearn python scripts/summarize_qwen_pre_m2_baseline.py \
    --model-label "${model_label}" \
    --model-manifest "${model_manifest}" \
    --contract-root "${CONTRACT_ROOT}" \
    --results-root "${RESULTS_ROOT}/${model_label}" \
    --output-dir "${output_dir}" \
    --bootstrap-samples 2000 \
    --bootstrap-seed 20260717
done

printf 'status=baseline_final_ci_complete output_root=%s\n' "${SUMMARY_ROOT}"
