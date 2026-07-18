#!/usr/bin/env bash
#SBATCH --job-name=pre-m2-wp3-a
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/vol/tmp2/yesildau/pre_m2_followup_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/pre_m2_followup_v1/logs/%x-%j.err

set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
HU_HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
SCRATCH_ROOT="/vol/tmp2/yesildau/pre_m2_followup_v1"
MODE="${MODE:-train}"
CONFIG_PATH="${CONFIG_PATH:-configs/training/pre_m2_wp3_stage_a_smollm2_1_7b.yaml}"
LAUNCH_MANIFEST="${SCRATCH_ROOT}/launch/wp3_stage_a_${SLURM_JOB_ID}.json"

case "${MODE}" in
  smoke|train) ;;
  *) echo "Unsupported WP3 mode: ${MODE}" >&2; exit 2 ;;
esac

mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs,tmp,launch,smoke}
cd "${REPO_ROOT}"

resolved_artifacts="$(readlink -f "${REPO_ROOT}/artifacts")"
resolved_runs="$(readlink -f "${REPO_ROOT}/runs")"
case "${resolved_artifacts}" in
  /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;;
  *) echo "Artifacts does not resolve to approved scratch: ${resolved_artifacts}" >&2; exit 1 ;;
esac
case "${resolved_runs}" in
  /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;;
  *) echo "Runs does not resolve to approved scratch: ${resolved_runs}" >&2; exit 1 ;;
esac

echo "hostname=$(hostname)"
echo "slurm_job_id=${SLURM_JOB_ID}"
echo "mode=${MODE}"
echo "config=${CONFIG_PATH}"
echo "artifacts=${resolved_artifacts}"
echo "runs=${resolved_runs}"
echo "expected_train_rows=2800"
echo "expected_validation_rows=400"
echo "expected_optimizer_steps=252"
echo "expected_checkpoint_count_upper_bound=11"
echo "estimated_condition_bytes_upper_bound=225000000000"
echo "retention=final model plus manifest and compact evidence; intermediate optimizer checkpoints removable"

du -xsh "${HU_HOME_ROOT}"
df -h "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader

export HF_HOME="${SCRATCH_ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${SCRATCH_ROOT}/cache"
export TORCH_HOME="${SCRATCH_ROOT}/cache/torch"
export TMPDIR="${SCRATCH_ROOT}/tmp"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/freeze_pre_m2_wp3_launch.py \
  --config "${CONFIG_PATH}" \
  --output "${LAUNCH_MANIFEST}"

if [[ "${MODE}" == "smoke" ]]; then
  conda run --name xfer-relearn python scripts/smoke_pre_m2_wp1b_batch.py \
    --config "${CONFIG_PATH}" \
    --batch-size 2
else
  conda run --name xfer-relearn python scripts/train_clm.py --config "${CONFIG_PATH}"
fi

du -xsh "${HU_HOME_ROOT}"
df -h "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
find "${HU_HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
