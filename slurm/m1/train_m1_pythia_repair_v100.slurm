#!/usr/bin/env bash
#SBATCH --job-name=m1-pythia-train
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v10032gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_v1/logs/%x-%j.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="${M1_PYTHIA_REPAIR_ROOT:-/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_v1}"
REGISTRY="${M1_PYTHIA_REPAIR_REGISTRY:-${REPO_ROOT}/configs/experiments/m1_provenance_screen_v3_pythia_repair_v1.yaml}"
TEMPLATE="${M1_PYTHIA_REPAIR_TEMPLATE:-${REPO_ROOT}/configs/training/m1_provenance_screen_v3_pythia_v100_fp16_seed42.yaml}"
DATASET_ROOT="/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets"
PROBE_REGISTRY="/vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv"
PREFLIGHT_MANIFEST="${M1_PYTHIA_PREFLIGHT_MANIFEST:-${SCRATCH_ROOT}/preflight/training.json}"
PYTHON="/vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1/bin/python"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
task_tmp="${SCRATCH_ROOT}/tmp/training/pythia_${SLURM_JOB_ID}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/huggingface_datasets,cache/torch,cache/triton,cache/cuda,cache/matplotlib,cache/numba,cache/wandb,configs/training,logs,manifests/runtime,manifests/tokenization,manifests/smoke} "${task_tmp}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" HF_DATASETS_CACHE="${SCRATCH_ROOT}/cache/huggingface_datasets" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TRITON_CACHE_DIR="${SCRATCH_ROOT}/cache/triton" CUDA_CACHE_PATH="${SCRATCH_ROOT}/cache/cuda" MPLCONFIGDIR="${SCRATCH_ROOT}/cache/matplotlib" NUMBA_CACHE_DIR="${SCRATCH_ROOT}/cache/numba" WANDB_DIR="${SCRATCH_ROOT}/cache/wandb" WANDB_MODE=disabled TMPDIR="${task_tmp}" PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
test -x "${PYTHON}"
"${PYTHON}" scripts/m1/m1_cross_family_preflight.py --stage training --verify-manifest "${PREFLIGHT_MANIFEST}" --max-age-minutes 720 --repo-root "${REPO_ROOT}" --registry "${REGISTRY}" --template "${TEMPLATE}" --launcher slurm/m1/train_m1_pythia_repair_v100.slurm --target-job-name m1-pythia-train --candidate-index 0
"${PYTHON}" scripts/m1/validate_m1_pythia_v100_runtime.py --registry "${REGISTRY}" --output "${SCRATCH_ROOT}/manifests/runtime/training.json"
config="${SCRATCH_ROOT}/configs/training/0_pythia.yaml"
"${PYTHON}" scripts/m1/prepare_m1_cross_family_config.py --registry "${REGISTRY}" --candidate-index 0 --template "${TEMPLATE}" --dataset-root "${DATASET_ROOT}" --output "${config}"
"${PYTHON}" scripts/m1/audit_m1_cross_family_tokenization.py --config "${config}" --output "${SCRATCH_ROOT}/manifests/tokenization/pythia.json" --repo-root "${REPO_ROOT}" --probe-registry "${PROBE_REGISTRY}"
"${PYTHON}" scripts/m1/smoke_m1_cross_family_candidate.py --config "${config}" --output "${SCRATCH_ROOT}/manifests/smoke/pythia.json" --checkpoint-dir "${task_tmp}/checkpoint_smoke_pythia" --repo-root "${REPO_ROOT}"
"${PYTHON}" scripts/training/train_clm.py --config "${config}"
