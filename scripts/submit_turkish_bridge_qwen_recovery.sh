#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
cd "${REPO_ROOT}"

test "$(sha256sum "${SCRATCH_ROOT}/contracts/v2/manifest.json" | awk '{print $1}')" = \
  "f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e"
test ! -e "${SCRATCH_ROOT}/training/qwen"
test -d "${SCRATCH_ROOT}/training/smollm2"
mkdir -p "${SCRATCH_ROOT}"/{logs,preflight}

preflight_id=$(sbatch --parsable slurm/preflight_turkish_bridge_qwen_recovery.slurm)
preflight_manifest="${SCRATCH_ROOT}/preflight/qwen_recovery_${preflight_id}.json"
training_id=$(sbatch --parsable --dependency="afterok:${preflight_id}" \
  --export="ALL,PREFLIGHT_MANIFEST=${preflight_manifest}" \
  slurm/train_turkish_bridge_qwen_recovery.slurm)
audit_id=$(sbatch --parsable --dependency="afterany:${training_id}" \
  slurm/audit_turkish_bridge_training.slurm)

printf 'preflight_id=%s\ntraining_id=%s\naudit_id=%s\npreflight_manifest=%s\n' \
  "${preflight_id}" "${training_id}" "${audit_id}" "${preflight_manifest}"
squeue -j "${preflight_id},${training_id},${audit_id}" \
  -o '%.18i %.12T %.10M %.24j %.20N %.30R'
