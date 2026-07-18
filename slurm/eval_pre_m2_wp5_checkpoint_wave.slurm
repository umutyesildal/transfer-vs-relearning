#!/usr/bin/env bash
#SBATCH --job-name=pre-m2-wp5-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/vol/tmp2/yesildau/pre_m2_followup_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/pre_m2_followup_v1/logs/%x-%A_%a.err

set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
HU_HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
SCRATCH_ROOT="/vol/tmp2/yesildau/pre_m2_followup_v1"
: "${WP5_REGISTRY:?WP5_REGISTRY is required}"
: "${SLURM_ARRAY_TASK_ID:?This launcher must run as a Slurm array}"
cd "${REPO_ROOT}"

registry_line="$(sed -n "$((SLURM_ARRAY_TASK_ID + 2))p" "${WP5_REGISTRY}")"
registry_line="${registry_line%$'\r'}"
if [[ -z "${registry_line}" ]]; then
  echo "No registry row for array index ${SLURM_ARRAY_TASK_ID}" >&2
  exit 2
fi
IFS=',' read -r array_index label lr_label checkpoint_step model_manifest manifest_sha hard_output exact_config general_config <<< "${registry_line}"
if [[ "${array_index}" != "${SLURM_ARRAY_TASK_ID}" ]]; then
  echo "Registry index mismatch: expected ${SLURM_ARRAY_TASK_ID}, got ${array_index}" >&2
  exit 2
fi
for output_path in "${hard_output}" "${SCRATCH_ROOT}"; do
  case "${output_path}" in
    /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;;
    *) echo "Refusing non-scratch WP5 output: ${output_path}" >&2; exit 1 ;;
  esac
done

mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs,tmp}
echo "hostname=$(hostname)"
echo "slurm_job_id=${SLURM_JOB_ID}"
echo "array_index=${SLURM_ARRAY_TASK_ID}"
echo "label=${label}"
echo "lr_label=${lr_label}"
echo "checkpoint_step=${checkpoint_step}"
echo "model_manifest=${model_manifest}"
echo "model_manifest_sha256=${manifest_sha}"
echo "hard_output=${hard_output}"
echo "exact_config=${exact_config}"
echo "general_config=${general_config}"
echo "expected_hard_probes=3000"
echo "expected_exact_probes=500"
echo "expected_checkpoints=0"
echo "retention=compact per-fact/per-token/general-capability outputs and manifests"

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
conda run --name xfer-relearn python scripts/evaluate_pre_m2_frozen_suite.py \
  --model-label "${label}" \
  --model-manifest "${model_manifest}" \
  --dataset-dir artifacts/datasets/relation_v2_gate_v1 \
  --probe-registry artifacts/pre_m2_followup_v1/evaluations/paraphrase_probe_registry.csv \
  --output-dir "${hard_output}" \
  --candidate-batch-size 64 \
  --checkpoint-interval 25 \
  --resume
conda run --name xfer-relearn python scripts/evaluate_facts.py --config "${exact_config}"
conda run --name xfer-relearn python scripts/evaluate_general_capability.py --config "${general_config}"

du -xsh "${HU_HOME_ROOT}"
df -h "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
