#!/usr/bin/env bash
#SBATCH --job-name=qwen-s43-eval-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:20:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1/logs/%x-%j.err
set -euo pipefail
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
ROOT=/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1
RUN_ROOT="${ROOT}/training/replay_w0_5_seed43"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
mkdir -p "${ROOT}"/{logs,evaluation_preflight}
test ! -e "${ROOT}/evaluation_v1"
test "$(find "${RUN_ROOT}" -name training_manifest.json -type f | wc -l)" -eq 1
test "$(find "${RUN_ROOT}" -type d -name 'checkpoint-*' | wc -l)" -eq 11
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
avail_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
test "${home_kib}" -le $((10 * 1024 * 1024)); test $((avail_kib * 1024)) -ge $((50 * 1024 * 1024 * 1024))
for p in "${ROOT}/evaluation_v1" "${ROOT}/cache" "${ROOT}/logs"; do case "$(readlink -m "$p")" in /vol/tmp2/yesildau/*) ;; *) exit 2;; esac; done
for p in "${REPO_ROOT}/slurm/m1/prepare_qwen_scale_probe_seed43_evaluation.slurm" "${REPO_ROOT}/slurm/m1/eval_qwen_scale_probe_seed43_checkpoints.slurm"; do test -f "$p"; done
printf '{"status":"passed","home_kib":%s,"tmp2_available_kib":%s,"tasks":11,"checkpoint_count":11,"reserve_bytes":%s}\n' "${home_kib}" "${avail_kib}" $((50 * 1024 * 1024 * 1024)) > "${ROOT}/evaluation_preflight/family_${SLURM_JOB_ID}.json"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2; df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
