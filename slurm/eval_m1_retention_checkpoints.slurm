#!/usr/bin/env bash
#SBATCH --job-name=m1-ret-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --exclude=gruenau9,gruenau10
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${SLURM_ARRAY_TASK_ID:?Array task is required}"
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT="/vol/tmp2/yesildau/m1_retention_v1/evaluation_v1"
REGISTRY="${ROOT}/checkpoint_registry.csv"
PROBES="/vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv"
test -s "${PREFLIGHT_MANIFEST}"
expected_commit=$("${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); assert p["status"]=="passed"; print(p["git_commit"])' "${PREFLIGHT_MANIFEST}")
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${expected_commit}"

cd "${REPO_ROOT}"
module load anaconda/3-2024.06
resolve_field() {
  conda run --name xfer-relearn python scripts/resolve_m1_retention_evaluation.py \
    --registry "${REGISTRY}" --task-index "${SLURM_ARRAY_TASK_ID}" --field "$1" \
    | tr -d '\r' | sed '/^[[:space:]]*$/d' | tail -n 1
}
label="$(resolve_field label)"
model_manifest="$(resolve_field model_manifest)"
expected_sha="$(resolve_field model_manifest_sha256)"
hard_output="$(resolve_field hard_output)"
exact_config="$(resolve_field exact_config)"
general_config="$(resolve_field general_config)"
test "$(sha256sum "${model_manifest}" | awk '{print $1}')" = "${expected_sha}"
task_tmp="/vol/tmp2/yesildau/m1_retention_v1/tmp/evaluation/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p /vol/tmp2/yesildau/m1_retention_v1/{cache/huggingface,cache/torch,logs} "${task_tmp}"
export HF_HOME=/vol/tmp2/yesildau/m1_retention_v1/cache/huggingface
export TRANSFORMERS_CACHE="${HF_HOME}" XDG_CACHE_HOME=/vol/tmp2/yesildau/m1_retention_v1/cache
export TORCH_HOME=/vol/tmp2/yesildau/m1_retention_v1/cache/torch TMPDIR="${task_tmp}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/evaluate_pre_m2_frozen_suite.py \
  --model-label "${label}" --model-manifest "${model_manifest}" \
  --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry "${PROBES}" \
  --output-dir "${hard_output}" --candidate-batch-size 64 --checkpoint-interval 25
conda run --name xfer-relearn python scripts/evaluate_facts.py --config "${exact_config}"
conda run --name xfer-relearn python scripts/evaluate_general_capability.py --config "${general_config}"
