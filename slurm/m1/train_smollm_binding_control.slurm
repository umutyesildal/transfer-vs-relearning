#!/usr/bin/env bash
#SBATCH --job-name=smollm-binding-control
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=16:00:00
#SBATCH --output=/vol/tmp2/yesildau/smollm_binding_control_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/smollm_binding_control_v1/logs/%x-%A.err
set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT=/vol/tmp2/yesildau/smollm_binding_control_v1
SOURCE_CONFIG="${REPO_ROOT}/configs/training/smollm_binding_control_seed42.yaml"
SCRATCH_CONFIG="${ROOT}/configs/seed42.yaml"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1/m1_form_generalization_preflight.py \
  --repo-root "${REPO_ROOT}" \
  --scratch-root "${ROOT}" \
  --manifest "${ROOT}/preflight/manifest.json" \
  --source-config "${SOURCE_CONFIG}" \
  --launcher slurm/m1/train_smollm_binding_control.slurm \
  --output-namespace "${ROOT}/training/seed42" \
  --expected-commit "$(git rev-parse HEAD)"
mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,configs,logs,manifests,tmp}
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface" XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TMPDIR="${ROOT}/tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/m1/build_m1_canonical_form_diversity_dataset.py --repo-root "${REPO_ROOT}" --output-dir "${ROOT}/datasets" --subject-count 100
conda run --name xfer-relearn python scripts/m1/prepare_m1_canonical_form_diversity_config.py --source-config "${SOURCE_CONFIG}" --dataset-root "${ROOT}/datasets" --output-root "${ROOT}/training/seed42" --output "${SCRATCH_CONFIG}"
conda run --name xfer-relearn python scripts/training/train_clm.py --config "${SCRATCH_CONFIG}"
