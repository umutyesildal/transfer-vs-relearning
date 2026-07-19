#!/usr/bin/env bash
#SBATCH --job-name=m1-xfam-acquire
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --array=0-3%4
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_cross_family_screen_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/m1_cross_family_screen_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${SLURM_ARRAY_TASK_ID:?Slurm array index is required}"
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_cross_family_screen_v1"
REGISTRY="${REPO_ROOT}/configs/experiments/m1_cross_family_screen_v1.yaml"
TEMPLATE="${REPO_ROOT}/configs/training/m1_cross_family_seed42_template.yaml"
PREFLIGHT_MANIFEST="${PREFLIGHT_MANIFEST:-${SCRATCH_ROOT}/preflight/acquisition.json}"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_cross_family_preflight.py --stage acquisition --verify-manifest "${PREFLIGHT_MANIFEST}" --max-age-minutes 720 --repo-root "${REPO_ROOT}" --registry "${REGISTRY}" --template "${TEMPLATE}" --launcher slurm/acquire_m1_cross_family_models.slurm --candidate-index "${SLURM_ARRAY_TASK_ID}"
label="$(conda run --name xfer-relearn python scripts/resolve_m1_cross_family_candidate.py --registry "${REGISTRY}" --candidate-index "${SLURM_ARRAY_TASK_ID}" --field label | tr -d '\r' | sed '/^[[:space:]]*$/d' | tail -n 1)"
case "${label}" in qwen|stablelm|gemma|llama) ;; *) echo "Invalid resolved candidate label: '${label}'" >&2; exit 2 ;; esac
task_tmp="${SCRATCH_ROOT}/tmp/acquisition/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs,manifests/access} "${task_tmp}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TMPDIR="${task_tmp}"
conda run --name xfer-relearn python scripts/acquire_m1_cross_family_candidate.py --registry "${REGISTRY}" --candidate-index "${SLURM_ARRAY_TASK_ID}"
