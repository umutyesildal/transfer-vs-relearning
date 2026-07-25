#!/usr/bin/env bash
#SBATCH --job-name=qwen-scale-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:25:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_scale_probe_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_scale_probe_v1/logs/%x-%j.err
set -euo pipefail
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_scale_probe_v2
RESERVE=$((300 * 1024 * 1024 * 1024))
mkdir -p "${ROOT}"/{logs,preflight}
test ! -e "${ROOT}/datasets"; test ! -e "${ROOT}/anchor"; test ! -e "${ROOT}/training"
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
avail_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
test "${home_kib}" -le $((10 * 1024 * 1024)); test $((avail_kib * 1024)) -ge "${RESERVE}"
for p in "${ROOT}" "${ROOT}/datasets" "${ROOT}/anchor" "${ROOT}/training"; do case "$(readlink -m "$p")" in /vol/tmp2/yesildau/*) ;; *) exit 2;; esac; done
for p in "${REPO_ROOT}/configs/training/qwen_scale_probe_replay_w0_5_seed42.yaml" "${REPO_ROOT}/scripts/build_qwen_scale_probe_dataset.py" "${REPO_ROOT}/slurm/prepare_qwen_scale_probe.slurm" "${REPO_ROOT}/slurm/train_qwen_scale_probe.slurm"; do test -f "$p"; done
module load anaconda/3-2024.06
cd "${REPO_ROOT}"
conda run --name xfer-relearn python -c "from pathlib import Path; from transfer_vs_relearning.training.clm import estimate_optimizer_steps,load_training_config; c=load_training_config(Path('configs/training/qwen_scale_probe_replay_w0_5_seed42.yaml')); assert estimate_optimizer_steps(17500,50,50,36.0)==252; assert c['retention']['coefficient']==0.5"
git_commit=$(git rev-parse HEAD)
printf '{"status":"passed","git_commit":"%s","home_kib":%s,"tmp2_available_kib":%s,"reserve_bytes":%s,"updates":252,"train_rows":17500,"validation_rows":2500}\n' "${git_commit}" "${home_kib}" "${avail_kib}" "${RESERVE}" > "${ROOT}/preflight/family_${SLURM_JOB_ID}.json"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2; df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N %.30R'
printf 'status=passed\n'
