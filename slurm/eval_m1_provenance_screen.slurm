#!/usr/bin/env bash
#SBATCH --job-name=m1-prov-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${SLURM_ARRAY_TASK_ID:?Slurm array index is required}"
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="${M1_PROVENANCE_SCREEN_ROOT:-/vol/tmp2/yesildau/m1_provenance_screen_v1}"
REGISTRY="${M1_PROVENANCE_REGISTRY:-${REPO_ROOT}/configs/experiments/m1_provenance_screen_v1.yaml}"
TEMPLATE="${M1_PROVENANCE_TEMPLATE:-${REPO_ROOT}/configs/training/m1_provenance_screen_seed42_template.yaml}"
PREFLIGHT_MANIFEST="${PREFLIGHT_MANIFEST:-${SCRATCH_ROOT}/preflight/evaluation.json}"
GENERAL_CORPUS="/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl"
PROBE_REGISTRY="/vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
run_python() {
  if [[ -n "${M1_PROVENANCE_PYTHON:-}" ]]; then
    test -x "${M1_PROVENANCE_PYTHON}"
    "${M1_PROVENANCE_PYTHON}" "$@"
  else
    conda run --name xfer-relearn python "$@"
  fi
}
PREFLIGHT_TMP="${SCRATCH_ROOT}/tmp/preflight/evaluation_verify_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/huggingface_datasets,cache/torch,cache/triton,cache/cuda,cache/matplotlib,cache/numba,cache/wandb} "${PREFLIGHT_TMP}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" HF_DATASETS_CACHE="${SCRATCH_ROOT}/cache/huggingface_datasets" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TRITON_CACHE_DIR="${SCRATCH_ROOT}/cache/triton" CUDA_CACHE_PATH="${SCRATCH_ROOT}/cache/cuda" MPLCONFIGDIR="${SCRATCH_ROOT}/cache/matplotlib" NUMBA_CACHE_DIR="${SCRATCH_ROOT}/cache/numba" WANDB_DIR="${SCRATCH_ROOT}/cache/wandb" WANDB_MODE=disabled TMPDIR="${PREFLIGHT_TMP}" PYTHONDONTWRITEBYTECODE=1
run_python scripts/m1_cross_family_preflight.py --stage evaluation --verify-manifest "${PREFLIGHT_MANIFEST}" --max-age-minutes 720 --repo-root "${REPO_ROOT}" --registry "${REGISTRY}" --template "${TEMPLATE}" --launcher slurm/eval_m1_provenance_screen.slurm --target-job-name m1-prov-eval --candidate-index "${SLURM_ARRAY_TASK_ID}"
label="$(run_python scripts/resolve_m1_cross_family_candidate.py --registry "${REGISTRY}" --candidate-index "${SLURM_ARRAY_TASK_ID}" --field label | tr -d '\r' | sed '/^[[:space:]]*$/d' | tail -n 1)"
case "${label}" in olmo|pythia|falcon) ;; *) echo "Invalid resolved candidate label: '${label}'" >&2; exit 2 ;; esac
registry_version="$(run_python scripts/resolve_m1_cross_family_candidate.py --registry "${REGISTRY}" --candidate-index "${SLURM_ARRAY_TASK_ID}" --field registry_version | tr -d '\r' | sed '/^[[:space:]]*$/d' | tail -n 1)"
hard_precision_args=()
if [[ "${registry_version}" == "m1_provenance_screen_v3_pythia_repair_v1" ]]; then
  hard_precision_args+=(--no-bf16)
fi
base_manifest="$(run_python scripts/resolve_m1_cross_family_candidate.py --registry "${REGISTRY}" --candidate-index "${SLURM_ARRAY_TASK_ID}" --field model_manifest | tr -d '\r' | sed '/^[[:space:]]*$/d' | tail -n 1)"
evaluation_root="${SCRATCH_ROOT}/evaluations/${label}"
task_tmp="${SCRATCH_ROOT}/tmp/evaluation/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs} "${task_tmp}"
export TMPDIR="${task_tmp}" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
run_python scripts/prepare_m1_cross_family_evaluation.py --registry "${REGISTRY}" --candidate-index "${SLURM_ARRAY_TASK_ID}" --general-corpus "${GENERAL_CORPUS}" --probe-registry "${PROBE_REGISTRY}" --repo-root "${REPO_ROOT}"
run_python scripts/evaluate_pre_m2_frozen_suite.py --model-label "${label}_base" --model-manifest "${base_manifest}" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry "${PROBE_REGISTRY}" --output-dir "${evaluation_root}/hard_suite/base" --candidate-batch-size 64 --checkpoint-interval 25 "${hard_precision_args[@]}"
run_python scripts/evaluate_pre_m2_frozen_suite.py --model-label "${label}_trained" --model-manifest "${evaluation_root}/model_manifests/${label}_trained.json" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry "${PROBE_REGISTRY}" --output-dir "${evaluation_root}/hard_suite/trained" --candidate-batch-size 64 --checkpoint-interval 25 "${hard_precision_args[@]}"
run_python scripts/evaluate_facts.py --config "${evaluation_root}/configs/exact_base.json"
run_python scripts/evaluate_facts.py --config "${evaluation_root}/configs/exact_trained.json"
run_python scripts/evaluate_general_capability.py --config "${evaluation_root}/configs/general_base.json"
run_python scripts/evaluate_general_capability.py --config "${evaluation_root}/configs/general_trained.json"
