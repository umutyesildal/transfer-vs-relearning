#!/usr/bin/env bash
#SBATCH --job-name=m1-v4-eval-olmo
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx3090:1
#SBATCH --exclude=guppi6
#SBATCH --array=0-5%4
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=05:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/logs/%x-%A_%a.err
set -euo pipefail
steps=(42 84 126 168 210 252); step="${steps[${SLURM_ARRAY_TASK_ID:?}]}"
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"; ROOT=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1
REGISTRY="${REPO_ROOT}/configs/experiments/m1_provenance_screen_v4_dose_pareto_v1.yaml"; TEMPLATE="${REPO_ROOT}/configs/training/m1_provenance_screen_v4_olmo_rtx3090_fp16_seed42.yaml"
PYTHON=/vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1/bin/python
cd "${REPO_ROOT}"; task_tmp="${ROOT}/tmp/evaluation/olmo_${step}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${task_tmp}" "${ROOT}/manifests/runtime"
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface" HF_DATASETS_CACHE="${ROOT}/cache/huggingface_datasets" XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TRITON_CACHE_DIR="${ROOT}/cache/triton" CUDA_CACHE_PATH="${ROOT}/cache/cuda" MPLCONFIGDIR="${ROOT}/cache/matplotlib" NUMBA_CACHE_DIR="${ROOT}/cache/numba" WANDB_DIR="${ROOT}/cache/wandb" WANDB_MODE=disabled TMPDIR="${task_tmp}" PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
"${PYTHON}" scripts/validate_m1_dose_pareto_runtime.py --registry "${REGISTRY}" --label olmo --template "${TEMPLATE}" --scratch-root "${ROOT}" --output "${ROOT}/manifests/runtime/olmo_eval_${step}.json"
"${PYTHON}" scripts/prepare_m1_dose_pareto_evaluation.py --registry "${REGISTRY}" --label olmo --step "${step}" --repo-root "${REPO_ROOT}"
eval_root="${ROOT}/evaluations/olmo/checkpoint-${step}"
exact_run="$("${PYTHON}" scripts/evaluate_facts.py --config "${eval_root}/configs/exact.json" | tail -n 1)"
general_run="$("${PYTHON}" scripts/evaluate_general_capability.py --config "${eval_root}/configs/general.json" | tail -n 1)"
cheap="${eval_root}/cheap_gate.json"
"${PYTHON}" scripts/gate_m1_dose_pareto_checkpoint.py --registry "${REGISTRY}" --label olmo --step "${step}" --exact-summary "${exact_run}/summary_metrics.json" --general-summary "${general_run}/summary_metrics.json" --output "${cheap}"
hard_open="$("${PYTHON}" -c 'import json,sys; print(str(json.load(open(sys.argv[1]))["hard_stage_open"]).lower())' "${cheap}")"
if [[ "${hard_open}" == true ]]; then
  "${PYTHON}" scripts/evaluate_pre_m2_frozen_suite.py --model-label "olmo_update${step}" --model-manifest "${eval_root}/model_manifest.json" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry /vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv --output-dir "${eval_root}/hard_suite" --candidate-batch-size 32 --checkpoint-interval 25
  "${PYTHON}" scripts/gate_m1_dose_pareto_checkpoint.py --registry "${REGISTRY}" --label olmo --step "${step}" --cheap-gate "${cheap}" --hard-csv "${eval_root}/hard_suite/hard_suite_per_fact.csv" --output "${eval_root}/final_gate.json"
fi
