#!/usr/bin/env bash
#SBATCH --job-name=pre-m2-frozen
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
: "${MODEL_LABEL:?MODEL_LABEL is required}"
: "${MODEL_MANIFEST:?MODEL_MANIFEST is required}"

DATASET_DIR="${DATASET_DIR:-artifacts/datasets/relation_v2_gate_v1}"
PROBE_REGISTRY="${PROBE_REGISTRY:-artifacts/pre_m2_followup_v1/evaluations/paraphrase_probe_registry.csv}"
OUTPUT_DIR="${OUTPUT_DIR:-${SCRATCH_ROOT}/evaluations/${MODEL_LABEL}}"

mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs,tmp,evaluations}
cd "${REPO_ROOT}"

resolved_output="$(readlink -m "${OUTPUT_DIR}")"
resolved_model_manifest="$(readlink -f "${MODEL_MANIFEST}")"
resolved_dataset="$(readlink -f "${DATASET_DIR}")"
resolved_probes="$(readlink -f "${PROBE_REGISTRY}")"

case "${resolved_output}" in
  /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;;
  *) echo "Refusing non-scratch output path: ${resolved_output}" >&2; exit 1 ;;
esac

echo "hostname=$(hostname)"
echo "slurm_job_id=${SLURM_JOB_ID:-none}"
echo "model_label=${MODEL_LABEL}"
echo "model_manifest=${resolved_model_manifest}"
echo "dataset_dir=${resolved_dataset}"
echo "probe_registry=${resolved_probes}"
echo "output_dir=${resolved_output}"
echo "expected_probe_count=3000"
echo "retention=per-fact/per-token CSV, summaries, manifests; no model checkpoints"

du -xsh "${HU_HOME_ROOT}"
df -h "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
readlink -f "${REPO_ROOT}/runs"
readlink -f "${REPO_ROOT}/artifacts"
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
  --model-label "${MODEL_LABEL}" \
  --model-manifest "${resolved_model_manifest}" \
  --dataset-dir "${resolved_dataset}" \
  --probe-registry "${resolved_probes}" \
  --output-dir "${resolved_output}" \
  --candidate-batch-size 64 \
  --checkpoint-interval 25

du -xsh "${HU_HOME_ROOT}"
df -h "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HU_HOME_ROOT}" /vol/tmp /vol/tmp2
find "${HU_HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
