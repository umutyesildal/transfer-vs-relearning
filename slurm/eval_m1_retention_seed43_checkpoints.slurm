#!/usr/bin/env bash
#SBATCH --job-name=m1-ret43-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx3090:1
#SBATCH --exclude=guppi6,guppi7
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${SLURM_ARRAY_TASK_ID:?Array task required}"; : "${PREFLIGHT_MANIFEST:?Preflight required}"
HOME_ROOT="/vol/fob-vol6/mi25/yesildau"; REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT="/vol/tmp2/yesildau/m1_retention_seed43_v1"; WAVE="${ROOT}/evaluation_v1"; REGISTRY="${WAVE}/checkpoint_registry.csv"
test -s "${PREFLIGHT_MANIFEST}"
expected_commit=$("${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" -c 'import json,sys; p=json.load(open(sys.argv[1])); assert p["status"]=="passed"; print(p["git_commit"])' "${PREFLIGHT_MANIFEST}")
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${expected_commit}"
cd "${REPO_ROOT}"; module load anaconda/3-2024.06
resolve(){ conda run --name xfer-relearn python scripts/resolve_m1_retention_evaluation.py --registry "${REGISTRY}" --task-index "${SLURM_ARRAY_TASK_ID}" --field "$1" | tr -d '\r' | sed '/^[[:space:]]*$/d' | tail -n 1; }
label=$(resolve label); model_manifest=$(resolve model_manifest); expected_sha=$(resolve model_manifest_sha256)
hard_output=$(resolve hard_output); exact_config=$(resolve exact_config); general_config=$(resolve general_config)
test "$(sha256sum "${model_manifest}" | awk '{print $1}')" = "${expected_sha}"
task_tmp="${ROOT}/tmp/evaluation/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,logs} "${task_tmp}"
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface" XDG_CACHE_HOME="${ROOT}/cache"
export TORCH_HOME="${ROOT}/cache/torch" TMPDIR="${task_tmp}" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PROBES=/vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv
conda run --name xfer-relearn python scripts/evaluate_pre_m2_frozen_suite.py --model-label "${label}" --model-manifest "${model_manifest}" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry "${PROBES}" --output-dir "${hard_output}" --candidate-batch-size 64 --checkpoint-interval 25
conda run --name xfer-relearn python scripts/evaluate_facts.py --config "${exact_config}"
conda run --name xfer-relearn python scripts/evaluate_general_capability.py --config "${general_config}"
