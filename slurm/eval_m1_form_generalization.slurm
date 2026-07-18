#!/usr/bin/env bash
#SBATCH --job-name=m1-form-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:45:00
#SBATCH --output=/vol/tmp2/yesildau/m1_form_generalization_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/m1_form_generalization_v1/logs/%x-%A_%a.err

set -euo pipefail
: "${EVALUATION_REGISTRY:?EVALUATION_REGISTRY is required}"
: "${SLURM_ARRAY_TASK_ID:?Slurm array index is required}"
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_form_generalization_v1"
cd "${REPO_ROOT}"
line="$(sed -n "$((SLURM_ARRAY_TASK_ID + 2))p" "${EVALUATION_REGISTRY}")"
IFS=',' read -r array_index label model_manifest manifest_sha hard_output exact_config general_config <<< "${line}"
test "${array_index}" = "${SLURM_ARRAY_TASK_ID}"
test "$(sha256sum "${model_manifest}" | awk '{print $1}')" = "${manifest_sha}"
for path in "${hard_output}" "${SCRATCH_ROOT}"; do case "${path}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 1 ;; esac; done
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs,tmp}
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TMPDIR="${SCRATCH_ROOT}/tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/evaluate_pre_m2_frozen_suite.py --model-label "${label}" --model-manifest "${model_manifest}" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry "${SCRATCH_ROOT}/datasets/evaluations/four_form_probe_registry.csv" --output-dir "${hard_output}" --candidate-batch-size 64 --checkpoint-interval 25
conda run --name xfer-relearn python scripts/evaluate_facts.py --config "${exact_config}"
conda run --name xfer-relearn python scripts/evaluate_general_capability.py --config "${general_config}"
