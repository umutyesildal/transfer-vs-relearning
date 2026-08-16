#!/usr/bin/env bash
#SBATCH --job-name=m1-ret43-eval-audit
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:20:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.err
set -euo pipefail
HOME_ROOT=/vol/fob-vol6/mi25/yesildau; ROOT=/vol/tmp2/yesildau/m1_retention_seed43_v1
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr > \
  "${ROOT}/preflight/evaluation_home_large_after.txt"
diff -u "${ROOT}/preflight/evaluation_home_large_before.txt" \
  "${ROOT}/preflight/evaluation_home_large_after.txt"
test "${home_kib}" -le $((10*1024*1024)); printf 'home_kib=%s\n' "${home_kib}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2; df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2; du -xsh "${ROOT}/evaluation_v1"
printf 'status=passed_no_new_large_home_files\n'
