#!/usr/bin/env bash
#SBATCH --job-name=m1-canonical-form
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/logs/%x-%A.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_canonical_form_diversity_v1"
SOURCE_CONFIG="${REPO_ROOT}/configs/training/m1_canonical_form_diversity_seed42.yaml"
SCRATCH_CONFIG="${SCRATCH_ROOT}/configs/seed42.yaml"
PREFLIGHT_MANIFEST="${PREFLIGHT_MANIFEST:-${SCRATCH_ROOT}/preflight/manifest.json}"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_form_generalization_preflight.py --verify-manifest "${PREFLIGHT_MANIFEST}" --repo-root "${REPO_ROOT}" --source-config "${SOURCE_CONFIG}" --launcher slurm/train_m1_canonical_form_diversity.slurm
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,configs,logs,manifests,tmp}
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface" XDG_CACHE_HOME="${SCRATCH_ROOT}/cache" TORCH_HOME="${SCRATCH_ROOT}/cache/torch" TMPDIR="${SCRATCH_ROOT}/tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/build_m1_canonical_form_diversity_dataset.py --repo-root "${REPO_ROOT}" --output-dir "${SCRATCH_ROOT}/datasets"
conda run --name xfer-relearn python scripts/audit_m1_canonical_form_diversity_exposure.py --output "${SCRATCH_ROOT}/manifests/exposure_audit.json"
conda run --name xfer-relearn python scripts/prepare_m1_canonical_form_diversity_config.py --source-config "${SOURCE_CONFIG}" --dataset-root "${SCRATCH_ROOT}/datasets" --output-root "${SCRATCH_ROOT}/training/seed42" --output "${SCRATCH_CONFIG}"
conda run --name xfer-relearn python scripts/train_clm.py --config "${SCRATCH_CONFIG}"
