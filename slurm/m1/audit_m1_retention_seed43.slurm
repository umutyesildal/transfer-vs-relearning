#!/usr/bin/env bash
#SBATCH --job-name=m1-ret43-audit
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:20:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_retention_seed43_v1"
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr > \
  "${SCRATCH_ROOT}/preflight/home_large_after.txt"
diff -u "${SCRATCH_ROOT}/preflight/home_large_before.txt" \
  "${SCRATCH_ROOT}/preflight/home_large_after.txt"
printf 'home_kib=%s\n' "${home_kib}"
test "${home_kib}" -le $((10 * 1024 * 1024))
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
du -xsh "${SCRATCH_ROOT}"
if ! sacct -j "${TRAINING_JOB_ID:?TRAINING_JOB_ID is required}" \
  --format=JobID,State,ExitCode,Elapsed,NodeList,AllocTRES -P; then
  printf 'warning=sacct_unavailable_using_training_manifest_and_scontrol_fallback\n' >&2
  scontrol show job "${TRAINING_JOB_ID}" -o 2>/dev/null || true
fi
printf 'status=passed_no_new_large_home_files\n'
