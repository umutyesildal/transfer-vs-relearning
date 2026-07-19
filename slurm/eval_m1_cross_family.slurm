#!/usr/bin/env bash
#SBATCH --job-name=m1-xfam-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_cross_family_screen_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/m1_cross_family_screen_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${SLURM_ARRAY_TASK_ID:?Slurm array index is required}"
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_cross_family_screen_v1"
REGISTRY="${REPO_ROOT}/configs/experiments/m1_cross_family_screen_v1.yaml"
TEMPLATE="${REPO_ROOT}/configs/training/m1_cross_family_seed42_template.yaml"
PREFLIGHT_MANIFEST="${PREFLIGHT_MANIFEST:-${SCRATCH_ROOT}/preflight/evaluation.json}"
GENERAL_CORPUS="/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl"
PROBE_REGISTRY="/vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_cross_family_preflight.py --stage evaluation --verify-manifest "${PREFLIGHT_MANIFEST}" --max-age-minutes 720 --repo-root "${REPO_ROOT}" --registry "${REGISTRY}" --template "${TEMPLATE}" --launcher slurm/eval_m1_cross_family.slurm --candidate-index "${SLURM_ARRAY_TASK_ID}"
label="$(conda run --name xfer-relearn python scripts/resolve_m1_cross_family_candidate.py --registry "${REGISTRY}" --candidate-index "${SLURM_ARRAY_TASK_ID}" --field label | tr -d '\r' | sed '/^[[:space:]]*$/d' | tail -n 1)"
case "${label}" in qwen|stablelm|gemma|llama) ;; *) echo "Invalid resolved candidate label: '${label}'" >&2; exit 2 ;; esac
evaluation_root="${SCRATCH_ROOT}/evaluations/${label}"
task_tmp="${SCRATCH_ROOT}/tmp/evaluation/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs} "${task_tmp}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TMPDIR="${task_tmp}" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/prepare_m1_cross_family_evaluation.py --registry "${REGISTRY}" --candidate-index "${SLURM_ARRAY_TASK_ID}" --general-corpus "${GENERAL_CORPUS}" --probe-registry "${PROBE_REGISTRY}" --repo-root "${REPO_ROOT}"
conda run --name xfer-relearn python scripts/evaluate_pre_m2_frozen_suite.py --model-label "${label}_trained" --model-manifest "${evaluation_root}/model_manifests/${label}_trained.json" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry "${PROBE_REGISTRY}" --output-dir "${evaluation_root}/hard_suite" --candidate-batch-size 64 --checkpoint-interval 25
conda run --name xfer-relearn python scripts/evaluate_facts.py --config "${evaluation_root}/configs/exact_trained.json"
conda run --name xfer-relearn python scripts/evaluate_general_capability.py --config "${evaluation_root}/configs/general_base.json"
conda run --name xfer-relearn python scripts/evaluate_general_capability.py --config "${evaluation_root}/configs/general_trained.json"
