#!/usr/bin/env bash
#SBATCH --job-name=m1-v4-eval-falcon-recovery
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx3090:1
#SBATCH --nodelist=guppi5
#SBATCH --array=2,4,5%1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=05:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/logs/%x-%A_%a.err
set -euo pipefail
case "${SLURM_ARRAY_TASK_ID:?}" in 2) step=126 ;; 4) step=210 ;; 5) step=252 ;; *) echo "Forbidden recovery task" >&2; exit 2 ;; esac
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1
REGISTRY="${REPO_ROOT}/configs/experiments/m1_provenance_screen_v4_dose_pareto_v1.yaml"
TEMPLATE="${REPO_ROOT}/configs/training/m1_provenance_screen_v4_falcon_rtx3090_bf16_seed42.yaml"
PYTHON=/vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1/bin/python
cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${M1_V4_EXPECTED_COMMIT:?}"
test -f "${FALCON_RECOVERY_PREFLIGHT:?}"
test "$(sha256sum "${FALCON_RECOVERY_PREFLIGHT}" | awk '{print $1}')" = "${FALCON_RECOVERY_PREFLIGHT_SHA256:?}"
"${PYTHON}" -c 'import json,sys; p=json.load(open(sys.argv[1])); assert p["status"]=="PASS"; assert p["expected_commit"]==sys.argv[2]; assert p["recovery_contract_sha256"]==sys.argv[3]; assert p["array_indices"]==[2,4,5] and p["recovery_steps"]==[126,210,252]' "${FALCON_RECOVERY_PREFLIGHT}" "${M1_V4_EXPECTED_COMMIT}" "${FALCON_EVALUATION_RECOVERY_SHA256:?}"
eval_root="${ROOT}/evaluations/falcon/checkpoint-${step}"
test ! -e "${eval_root}"
task_tmp="${ROOT}/tmp/evaluation/falcon_recovery_${step}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${task_tmp}" "${ROOT}/manifests/runtime"
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface" HF_DATASETS_CACHE="${ROOT}/cache/huggingface_datasets" XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TRITON_CACHE_DIR="${ROOT}/cache/triton" CUDA_CACHE_PATH="${ROOT}/cache/cuda" MPLCONFIGDIR="${ROOT}/cache/matplotlib" NUMBA_CACHE_DIR="${ROOT}/cache/numba" WANDB_DIR="${ROOT}/cache/wandb" WANDB_MODE=disabled TMPDIR="${task_tmp}" PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
runtime_manifest="${ROOT}/manifests/runtime/falcon_recovery_eval_${step}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.json"
"${PYTHON}" scripts/validate_m1_dose_pareto_runtime.py --registry "${REGISTRY}" --label falcon --template "${TEMPLATE}" --scratch-root "${ROOT}" --output "${runtime_manifest}"
"${PYTHON}" scripts/prepare_m1_dose_pareto_evaluation.py --registry "${REGISTRY}" --label falcon --step "${step}" --repo-root "${REPO_ROOT}"
exact_run="$("${PYTHON}" scripts/evaluate_facts.py --config "${eval_root}/configs/exact.json" | tail -n 1)"
general_run="$("${PYTHON}" scripts/evaluate_general_capability.py --config "${eval_root}/configs/general.json" | tail -n 1)"
cheap="${eval_root}/cheap_gate.json"
"${PYTHON}" scripts/gate_m1_dose_pareto_checkpoint.py --registry "${REGISTRY}" --label falcon --step "${step}" --exact-summary "${exact_run}/summary_metrics.json" --general-summary "${general_run}/summary_metrics.json" --output "${cheap}"
hard_open="$("${PYTHON}" -c 'import json,sys; print(str(json.load(open(sys.argv[1]))["hard_stage_open"]).lower())' "${cheap}")"
if [[ "${hard_open}" == true ]]; then
  "${PYTHON}" scripts/evaluate_pre_m2_frozen_suite.py --model-label "falcon_update${step}" --model-manifest "${eval_root}/model_manifest.json" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry /vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv --output-dir "${eval_root}/hard_suite" --candidate-batch-size 64 --checkpoint-interval 25
  "${PYTHON}" scripts/gate_m1_dose_pareto_checkpoint.py --registry "${REGISTRY}" --label falcon --step "${step}" --cheap-gate "${cheap}" --hard-csv "${eval_root}/hard_suite/hard_suite_per_fact.csv" --output "${eval_root}/final_gate.json"
fi
