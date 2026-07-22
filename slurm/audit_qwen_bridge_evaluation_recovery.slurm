#!/usr/bin/env bash
#SBATCH --job-name=qwen-bridge-r-aud
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
OUTPUT_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1/evaluation_v2_qwen"
du -xsh "${HOME_ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
printf 'artifacts_resolved=%s\nruns_resolved=%s\nrecovery_root=%s\n' \
  "$(readlink -m "${REPO_ROOT}/artifacts")" "$(readlink -m "${REPO_ROOT}/runs")" \
  "$(readlink -m "${OUTPUT_ROOT}")"
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
if [[ -d "${OUTPUT_ROOT}" ]]; then
  du -sh "${OUTPUT_ROOT}"
  find "${OUTPUT_ROOT}/results" -name classification_by_stratum.json -type f -print 2>/dev/null | sort
fi
printf 'status=qwen_recovery_storage_audit_complete\n'
