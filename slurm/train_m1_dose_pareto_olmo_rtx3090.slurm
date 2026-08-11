#!/usr/bin/env bash
#SBATCH --job-name=m1-v4-train-olmo
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx3090:1
#SBATCH --exclude=guppi6
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/logs/%x-%j.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"; ROOT=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1
REGISTRY="${REPO_ROOT}/configs/experiments/m1_provenance_screen_v4_dose_pareto_v1.yaml"; TEMPLATE="${REPO_ROOT}/configs/training/m1_provenance_screen_v4_olmo_rtx3090_bf16_seed42.yaml"
PYTHON=/vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1/bin/python; PREFLIGHT="${M1_V4_PREFLIGHT:?}"
cd "${REPO_ROOT}"; task_tmp="${ROOT}/tmp/training/olmo_${SLURM_JOB_ID}"
mkdir -p "${task_tmp}" "${ROOT}/configs/training" "${ROOT}/manifests/runtime" "${ROOT}/manifests/tokenization" "${ROOT}/manifests/smoke"
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface" HF_DATASETS_CACHE="${ROOT}/cache/huggingface_datasets" XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TRITON_CACHE_DIR="${ROOT}/cache/triton" CUDA_CACHE_PATH="${ROOT}/cache/cuda" MPLCONFIGDIR="${ROOT}/cache/matplotlib" NUMBA_CACHE_DIR="${ROOT}/cache/numba" WANDB_DIR="${ROOT}/cache/wandb" WANDB_MODE=disabled TMPDIR="${task_tmp}" PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
"${PYTHON}" scripts/preflight_m1_dose_pareto.py --verify --label olmo --registry "${REGISTRY}" --repo-root "${REPO_ROOT}" --expected-commit "${M1_V4_EXPECTED_COMMIT:?}" --output "${PREFLIGHT}"
"${PYTHON}" scripts/validate_m1_dose_pareto_runtime.py --registry "${REGISTRY}" --label olmo --template "${TEMPLATE}" --scratch-root "${ROOT}" --output "${ROOT}/manifests/runtime/olmo_training.json"
config="${ROOT}/configs/training/olmo.yaml"
"${PYTHON}" scripts/prepare_m1_dose_pareto_config.py --registry "${REGISTRY}" --label olmo --repo-root "${REPO_ROOT}" --output "${config}"
"${PYTHON}" scripts/audit_m1_cross_family_tokenization.py --config "${config}" --output "${ROOT}/manifests/tokenization/olmo.json" --repo-root "${REPO_ROOT}" --probe-registry /vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv
"${PYTHON}" scripts/smoke_m1_cross_family_candidate.py --config "${config}" --output "${ROOT}/manifests/smoke/olmo.json" --checkpoint-dir "${task_tmp}/smoke_checkpoint" --repo-root "${REPO_ROOT}" --preserve-checkpoint
"${PYTHON}" scripts/train_clm.py --config "${config}"
