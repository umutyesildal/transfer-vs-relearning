#!/usr/bin/env bash
#SBATCH --job-name=qwen25k-audit
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT=/vol/fob-vol6/mi25/yesildau
ROOT=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1
HOME_LIMIT_BYTES=30000000000
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
test $((home_kib * 1024)) -lt "${HOME_LIMIT_BYTES}"
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr > \
  "${ROOT}/preflight/training_home_large_after.txt"
diff -u "${ROOT}/preflight/training_home_large_before.txt" \
  "${ROOT}/preflight/training_home_large_after.txt"
du -xsh "${HOME_ROOT}" "${ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
if ! sacct -j "${TRAINING_JOB_ID:?TRAINING_JOB_ID is required}" \
  --format=JobID,State,ExitCode,Elapsed,NodeList,AllocTRES -P; then
  printf 'warning=sacct_unavailable_using_scontrol_fallback\n' >&2
  scontrol show job "${TRAINING_JOB_ID}" -o 2>/dev/null || true
fi
printf 'status=passed_no_new_large_home_files\n'
