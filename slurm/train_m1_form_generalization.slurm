#!/usr/bin/env bash
#SBATCH --job-name=m1-form-generalization
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_form_generalization_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/m1_form_generalization_v1/logs/%x-%A.err

set -euo pipefail

: "${CONDITION:?Set CONDITION to control or balanced_ab}"
case "${CONDITION}" in control|balanced_ab) ;; *) echo "Unsupported CONDITION=${CONDITION}" >&2; exit 2 ;; esac
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
HU_HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_form_generalization_v1"
SOURCE_CONFIG="${REPO_ROOT}/configs/training/m1_form_generalization_${CONDITION}_seed42.yaml"
SCRATCH_CONFIG="${SCRATCH_ROOT}/configs/${CONDITION}_seed42.yaml"
DATASET_ROOT="${SCRATCH_ROOT}/datasets"
OUTPUT_ROOT="${SCRATCH_ROOT}/training/${CONDITION}_seed42"
LAUNCH_MANIFEST="${SCRATCH_ROOT}/manifests/${CONDITION}_${SLURM_JOB_ID}.json"
PREFLIGHT_MANIFEST="${PREFLIGHT_MANIFEST:-${SCRATCH_ROOT}/preflight/manifest.json}"

cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_form_generalization_preflight.py \
  --verify-manifest "${PREFLIGHT_MANIFEST}" \
  --repo-root "${REPO_ROOT}" \
  --source-config configs/training/m1_form_generalization_control_seed42.yaml \
  --source-config configs/training/m1_form_generalization_balanced_ab_seed42.yaml \
  --launcher slurm/train_m1_form_generalization.slurm
for path in "${SCRATCH_ROOT}" "${DATASET_ROOT}" "${OUTPUT_ROOT}"; do
  case "${path}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) echo "Refusing non-scratch path: ${path}" >&2; exit 1 ;; esac
done
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,configs,logs,manifests,tmp}
echo "hostname=$(hostname)"
echo "slurm_job_id=${SLURM_JOB_ID}"
echo "condition=${CONDITION}"
echo "expected_optimizer_updates=252"
echo "expected_checkpoint_count_upper_bound=11"
echo "estimated_condition_bytes_upper_bound=225000000000"
echo "retention=selected endpoint plus compact evidence; intermediates are scratch cleanup candidates"
du -xsh "${HU_HOME_ROOT}"
df -h "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${SCRATCH_ROOT}/cache"
export TORCH_HOME="${SCRATCH_ROOT}/cache/torch"
export TMPDIR="${SCRATCH_ROOT}/tmp"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/build_m1_form_generalization_datasets.py --repo-root "${REPO_ROOT}" --output-dir "${DATASET_ROOT}"
conda run --name xfer-relearn python scripts/prepare_m1_form_generalization_config.py --source-config "${SOURCE_CONFIG}" --dataset-root "${DATASET_ROOT}" --output-root "${OUTPUT_ROOT}" --output "${SCRATCH_CONFIG}"
conda run --name xfer-relearn python scripts/freeze_m1_form_generalization_launch.py --config "${SCRATCH_CONFIG}" --condition "${CONDITION}" --output "${LAUNCH_MANIFEST}" --repo-root "${REPO_ROOT}"
conda run --name xfer-relearn python scripts/smoke_pre_m2_wp1b_batch.py --config "${SCRATCH_CONFIG}"
conda run --name xfer-relearn python scripts/train_clm.py --config "${SCRATCH_CONFIG}"
du -xsh "${HU_HOME_ROOT}"
df -h "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
find "${HU_HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
