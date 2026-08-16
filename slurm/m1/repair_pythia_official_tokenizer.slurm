#!/usr/bin/env bash
#SBATCH --job-name=m1-pythia-tokenizer
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_v1/logs/%x-%j.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="${M1_PYTHIA_REPAIR_ROOT:-/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_v1}"
REGISTRY="${M1_PYTHIA_REPAIR_REGISTRY:-${REPO_ROOT}/configs/experiments/m1_provenance_screen_v3_pythia_repair_v1.yaml}"
TEMPLATE="${REPO_ROOT}/configs/training/m1_provenance_screen_v3_pythia_v100_fp16_seed42.yaml"
PREFLIGHT_MANIFEST="${SCRATCH_ROOT}/preflight/acquisition.json"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
task_tmp="${SCRATCH_ROOT}/tmp/tokenizer_${SLURM_JOB_ID}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/huggingface_datasets,cache/torch,logs,manifests/access,tmp} "${task_tmp}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" HF_DATASETS_CACHE="${SCRATCH_ROOT}/cache/huggingface_datasets" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TMPDIR="${task_tmp}" PYTHONDONTWRITEBYTECODE=1
conda run --name xfer-relearn python scripts/m1/m1_cross_family_preflight.py --stage acquisition --verify-manifest "${PREFLIGHT_MANIFEST}" --max-age-minutes 720 --repo-root "${REPO_ROOT}" --registry "${REGISTRY}" --template "${TEMPLATE}" --launcher slurm/m1/repair_pythia_official_tokenizer.slurm --target-job-name m1-pythia-tokenizer --candidate-index 0
conda run --name xfer-relearn python scripts/m1/repair_pythia_official_tokenizer.py --registry "${REGISTRY}"
