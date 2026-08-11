#!/usr/bin/env bash
#SBATCH --job-name=m1-pythia-bf16-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx3090:1
#SBATCH --exclude=guppi6
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=06:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_retry_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_retry_v1/logs/%x-%j.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT=/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_retry_v1
REGISTRY="${REPO_ROOT}/configs/experiments/m1_provenance_screen_v3_pythia_repair_rtx3090_bf16_v1.yaml"
TEMPLATE="${REPO_ROOT}/configs/training/m1_provenance_screen_v3_pythia_rtx3090_bf16_seed42.yaml"
PREFLIGHT_MANIFEST="${SCRATCH_ROOT}/preflight/evaluation_rtx3090_bf16.json"
GENERAL_CORPUS=/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl
PROBE_REGISTRY=/vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv
PYTHON=/vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1/bin/python
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
task_tmp="${SCRATCH_ROOT}/tmp/evaluation/pythia_bf16_${SLURM_JOB_ID}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/huggingface_datasets,cache/torch,cache/triton,cache/cuda,cache/matplotlib,cache/numba,cache/wandb,logs,manifests/runtime} "${task_tmp}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" HF_DATASETS_CACHE="${SCRATCH_ROOT}/cache/huggingface_datasets" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TRITON_CACHE_DIR="${SCRATCH_ROOT}/cache/triton" CUDA_CACHE_PATH="${SCRATCH_ROOT}/cache/cuda" MPLCONFIGDIR="${SCRATCH_ROOT}/cache/matplotlib" NUMBA_CACHE_DIR="${SCRATCH_ROOT}/cache/numba" WANDB_DIR="${SCRATCH_ROOT}/cache/wandb" WANDB_MODE=disabled TMPDIR="${task_tmp}" PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
test -x "${PYTHON}"
"${PYTHON}" scripts/m1_cross_family_preflight.py --stage evaluation --verify-manifest "${PREFLIGHT_MANIFEST}" --max-age-minutes 720 --repo-root "${REPO_ROOT}" --registry "${REGISTRY}" --template "${TEMPLATE}" --launcher slurm/eval_m1_pythia_repair_rtx3090_bf16.slurm --target-job-name m1-pythia-bf16-eval --candidate-index 0
"${PYTHON}" scripts/validate_m1_pythia_v100_runtime.py --registry "${REGISTRY}" --template "${TEMPLATE}" --scratch-root "${SCRATCH_ROOT}" --output "${SCRATCH_ROOT}/manifests/runtime/evaluation_bf16.json"
base_manifest="${SCRATCH_ROOT}/models/EleutherAI__pythia-1.4b/model_manifest.json"
evaluation_root="${SCRATCH_ROOT}/evaluations/pythia"
"${PYTHON}" scripts/prepare_m1_cross_family_evaluation.py --registry "${REGISTRY}" --candidate-index 0 --general-corpus "${GENERAL_CORPUS}" --probe-registry "${PROBE_REGISTRY}" --repo-root "${REPO_ROOT}"
"${PYTHON}" scripts/evaluate_pre_m2_frozen_suite.py --model-label pythia_base --model-manifest "${base_manifest}" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry "${PROBE_REGISTRY}" --output-dir "${evaluation_root}/hard_suite/base" --candidate-batch-size 64 --checkpoint-interval 25 --no-bf16
"${PYTHON}" scripts/evaluate_pre_m2_frozen_suite.py --model-label pythia_trained --model-manifest "${evaluation_root}/model_manifests/pythia_trained.json" --dataset-dir artifacts/datasets/relation_v2_gate_v1 --probe-registry "${PROBE_REGISTRY}" --output-dir "${evaluation_root}/hard_suite/trained" --candidate-batch-size 64 --checkpoint-interval 25 --no-bf16
"${PYTHON}" scripts/evaluate_facts.py --config "${evaluation_root}/configs/exact_base.json"
"${PYTHON}" scripts/evaluate_facts.py --config "${evaluation_root}/configs/exact_trained.json"
"${PYTHON}" scripts/evaluate_general_capability.py --config "${evaluation_root}/configs/general_base.json"
"${PYTHON}" scripts/evaluate_general_capability.py --config "${evaluation_root}/configs/general_trained.json"
