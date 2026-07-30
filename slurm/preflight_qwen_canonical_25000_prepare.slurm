#!/usr/bin/env bash
#SBATCH --job-name=qwen25k-prepcheck
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1
PREPARED_ROOT="${ROOT}/prepared"
TRAINING_ROOT="${ROOT}/training/replay_w0_5_seed42"
SMOKE_ROOT="${ROOT}/smoke"
SOURCE_ANCHOR=/vol/tmp2/yesildau/qwen_scale_probe_v3/anchor
RESERVE_BYTES=$((300 * 1024 * 1024 * 1024))
MIN_FREE_BYTES=$((1024 * 1024 * 1024 * 1024))

mkdir -p "${ROOT}"/{logs,preflight}
test ! -e "${PREPARED_ROOT}"
test ! -e "${TRAINING_ROOT}"
test ! -e "${SMOKE_ROOT}"
test -s "${SOURCE_ANCHOR}/manifest.json"
test -s "${SOURCE_ANCHOR}/train.jsonl"
test -s "${SOURCE_ANCHOR}/validation.jsonl"

home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
avail_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
avail_inodes=$(df -Pi /vol/tmp2 | tail -n 1 | awk '{print $4}')
test "${home_kib}" -le $((10 * 1024 * 1024))
test $((avail_kib * 1024)) -ge "${MIN_FREE_BYTES}"
test "${avail_inodes}" -ge 100000

for path in "${ROOT}" "${PREPARED_ROOT}" "${TRAINING_ROOT}" "${ROOT}/cache" "${ROOT}/logs" "${ROOT}/tmp"; do
  case "$(readlink -m "${path}")" in
    /vol/tmp2/yesildau/*) ;;
    *) printf 'unsafe_path=%s\n' "${path}" >&2; exit 2 ;;
  esac
done

for path in \
  "${REPO_ROOT}/configs/training/qwen_canonical_25000_replay_w0_5_seed42.yaml" \
  "${REPO_ROOT}/scripts/build_qwen_canonical_scale_dataset.py" \
  "${REPO_ROOT}/slurm/prepare_qwen_canonical_25000.slurm" \
  "${REPO_ROOT}/slurm/train_qwen_canonical_25000.slurm"; do
  test -f "${path}"
done

find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr > \
  "${ROOT}/preflight/home_large_before.txt"

module load anaconda/3-2024.06
cd "${REPO_ROOT}"
conda run --name xfer-relearn python -c \
  "from pathlib import Path; from transfer_vs_relearning.training.clm import estimate_optimizer_steps,load_training_config; c=load_training_config(Path('configs/training/qwen_canonical_25000_replay_w0_5_seed42.yaml')); assert estimate_optimizer_steps(175000,50,500,36.0)==252; assert c['runtime']['world_size']==1"
git_commit=$(git rev-parse HEAD)
created_at=$(date --iso-8601=seconds)
printf '{"status":"passed","created_at":"%s","git_commit":"%s","home_kib":%s,"tmp2_available_kib":%s,"tmp2_available_inodes":%s,"reserve_bytes":%s,"minimum_free_bytes":%s,"subjects":5000,"facts":25000,"train_rows":175000,"updates":252,"checkpoints":11,"requested_a100_gpus":1,"exclusive":false}\n' \
  "${created_at}" "${git_commit}" "${home_kib}" "${avail_kib}" "${avail_inodes}" "${RESERVE_BYTES}" "${MIN_FREE_BYTES}" > \
  "${ROOT}/preflight/prepare_${SLURM_JOB_ID}.json"

du -xsh "${HOME_ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
squeue -o '%.18i %.12u %.12T %.10M %.24j %.20N %.30R'
printf 'status=passed resolved_output_root=%s resolved_cache_root=%s checkpoints=11 estimated_family_bytes=%s retention=preserve_all_until_frozen_evaluation\n' \
  "$(readlink -m "${TRAINING_ROOT}")" "$(readlink -m "${ROOT}/cache")" "${RESERVE_BYTES}"
