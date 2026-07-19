#!/usr/bin/env bash
#SBATCH --job-name=m1-xfam-train
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
DATASET_ROOT="/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets"
PREFLIGHT_MANIFEST="${PREFLIGHT_MANIFEST:-${SCRATCH_ROOT}/preflight/training.json}"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_cross_family_preflight.py --stage training --verify-manifest "${PREFLIGHT_MANIFEST}" --max-age-minutes 720 --repo-root "${REPO_ROOT}" --registry "${REGISTRY}" --template "${TEMPLATE}" --launcher slurm/train_m1_cross_family.slurm --candidate-index "${SLURM_ARRAY_TASK_ID}"
label="$(conda run --name xfer-relearn python scripts/resolve_m1_cross_family_candidate.py --registry "${REGISTRY}" --candidate-index "${SLURM_ARRAY_TASK_ID}" --field label | tr -d '\r' | sed '/^[[:space:]]*$/d' | tail -n 1)"
case "${label}" in qwen|stablelm|gemma|llama) ;; *) echo "Invalid resolved candidate label: '${label}'" >&2; exit 2 ;; esac
config="${SCRATCH_ROOT}/configs/training/${SLURM_ARRAY_TASK_ID}_${label}.yaml"
task_tmp="${SCRATCH_ROOT}/tmp/training/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,configs/training,logs,manifests/tokenization,manifests/smoke} "${task_tmp}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TMPDIR="${task_tmp}" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/prepare_m1_cross_family_config.py --registry "${REGISTRY}" --candidate-index "${SLURM_ARRAY_TASK_ID}" --template "${TEMPLATE}" --dataset-root "${DATASET_ROOT}" --output "${config}"
conda run --name xfer-relearn python scripts/audit_m1_cross_family_tokenization.py --config "${config}" --output "${SCRATCH_ROOT}/manifests/tokenization/${label}.json" --repo-root "${REPO_ROOT}"
conda run --name xfer-relearn python scripts/smoke_m1_cross_family_candidate.py --config "${config}" --output "${SCRATCH_ROOT}/manifests/smoke/${label}.json" --checkpoint-dir "${task_tmp}/checkpoint_smoke_${label}" --repo-root "${REPO_ROOT}"
conda run --name xfer-relearn python scripts/train_clm.py --config "${config}"
