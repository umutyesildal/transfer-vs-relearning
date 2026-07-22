#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$(pwd)}"
TRAINING_EXCLUDE_NODES="${2:-}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
cd "${REPO_ROOT}"

if [[ -n "${TRAINING_EXCLUDE_NODES}" && ! "${TRAINING_EXCLUDE_NODES}" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]]; then
  printf 'invalid_training_exclude_nodes=%s\n' "${TRAINING_EXCLUDE_NODES}" >&2
  exit 2
fi

test "$(sha256sum "${SCRATCH_ROOT}/contracts/v2/manifest.json" | awk '{print $1}')" = \
  "f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e"
mkdir -p "${SCRATCH_ROOT}"/{logs,preflight}

preflight_id=$(sbatch --parsable slurm/preflight_turkish_bridge_training.slurm)
preflight_manifest="${SCRATCH_ROOT}/preflight/training_${preflight_id}.json"
training_sbatch=(
  sbatch --parsable --dependency="afterok:${preflight_id}"
  --export="ALL,PREFLIGHT_MANIFEST=${preflight_manifest}"
)
if [[ -n "${TRAINING_EXCLUDE_NODES}" ]]; then
  training_sbatch+=(--exclude="${TRAINING_EXCLUDE_NODES}")
fi
training_id=$("${training_sbatch[@]}" slurm/train_turkish_bridge.slurm)
audit_id=$(sbatch --parsable --dependency="afterany:${training_id}" \
  slurm/audit_turkish_bridge_training.slurm)

printf 'preflight_id=%s\ntraining_id=%s\naudit_id=%s\npreflight_manifest=%s\ntraining_exclude_nodes=%s\n' \
  "${preflight_id}" "${training_id}" "${audit_id}" "${preflight_manifest}" \
  "${TRAINING_EXCLUDE_NODES:-none}"
squeue -j "${preflight_id},${training_id},${audit_id}" \
  -o '%.18i %.12T %.10M %.24j %.20N %.30R'
