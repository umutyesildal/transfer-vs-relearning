#!/usr/bin/env bash
# CPU-only family preflight for the four matched Qwen M2/M3 training configs.
# The contract/config manifest is created only after Phase E freezes dose and endpoint.
#SBATCH --job-name=qwen-m2-m3-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:20:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_m2_m3_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_m2_m3_v1/logs/%x-%j.err
set -euo pipefail

: "${CONFIG_MANIFEST:?CONFIG_MANIFEST is required}"
: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_m2_m3_v1
mkdir -p "${ROOT}/logs" "${ROOT}/preflight"
test -s "${CONFIG_MANIFEST}"
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
test "${home_kib}" -lt $((30 * 1024 * 1024))
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
module load anaconda/3-2024.06
python_bin="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"
PYTHONPATH="${REPO_ROOT}/src" "${python_bin}" scripts/m2/validate_qwen_m2_m3_training_family.py \
  --config-manifest "${CONFIG_MANIFEST}" \
  --expected-commit "${EXPECTED_COMMIT}" \
  --output "${ROOT}/preflight/manifest.json"
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N %.30R'
printf 'status=passed\nconfig_manifest=%s\nexpected_commit=%s\n' "${CONFIG_MANIFEST}" "${EXPECTED_COMMIT}"
