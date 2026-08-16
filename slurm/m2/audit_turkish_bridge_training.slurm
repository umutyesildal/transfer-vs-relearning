#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-tr-audit
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
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"

du -xsh "${HOME_ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
printf 'artifacts_resolved=%s\n' "$(readlink -m "${REPO_ROOT}/artifacts")"
printf 'runs_resolved=%s\n' "$(readlink -m "${REPO_ROOT}/runs")"
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
for label in qwen smollm2; do
  root="${SCRATCH_ROOT}/training/${label}"
  if [[ -d "${root}" ]]; then
    du -sh "${root}"
    find "${root}" -mindepth 2 -maxdepth 2 -name training_manifest.json -print
  else
    printf 'missing_training_root=%s\n' "${root}"
  fi
done
printf 'status=post_run_storage_audit_complete\n'
