#!/usr/bin/env bash
#SBATCH --job-name=smollm-contrastive-smoke
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/smollm_contrastive_binding_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/smollm_contrastive_binding_v1/logs/%x-%A.err
set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT=/vol/tmp2/yesildau/smollm_contrastive_binding_v1
SOURCE_CONFIG="${REPO_ROOT}/configs/training/smollm_contrastive_binding_seed42.yaml"
CONFIG="${ROOT}/configs/smoke_seed42.yaml"
PREFLIGHT_MANIFEST="${PREFLIGHT_MANIFEST:-${ROOT}/preflight/manifest.json}"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_form_generalization_preflight.py --verify-manifest "${PREFLIGHT_MANIFEST}" --repo-root "${REPO_ROOT}" --source-config "${SOURCE_CONFIG}" --launcher slurm/train_smollm_contrastive_binding.slurm --max-age-minutes 240
mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,configs,logs,tmp}
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface" XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TMPDIR="${ROOT}/tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
conda run --name xfer-relearn python scripts/build_m1_canonical_form_diversity_dataset.py --repo-root "${REPO_ROOT}" --output-dir "${ROOT}/datasets" --subject-count 100
conda run --name xfer-relearn python scripts/prepare_m1_canonical_form_diversity_config.py --source-config "${SOURCE_CONFIG}" --dataset-root "${ROOT}/datasets" --output-root "${ROOT}/smoke/seed42" --output "${CONFIG}"
conda run --name xfer-relearn python -c "import yaml; p='${CONFIG}'; x=yaml.safe_load(open(p)); x['training']['max_steps']=1; x['training']['run_name']='smollm_contrastive_binding_smoke_seed42'; open(p, 'w').write(yaml.safe_dump(x, sort_keys=False))"
conda run --name xfer-relearn python scripts/train_clm.py --config "${CONFIG}"
