#!/usr/bin/env bash
#SBATCH --job-name=smollm-pconsistency-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:20:00
#SBATCH --output=/vol/tmp2/yesildau/smollm_prompt_consistency_v2/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/smollm_prompt_consistency_v2/logs/%x-%A.err
set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT=/vol/tmp2/yesildau/smollm_prompt_consistency_v2
cd "${REPO_ROOT}"
mkdir -p "${ROOT}"/{logs,preflight,tmp}
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1/m1_form_generalization_preflight.py \
  --repo-root "${REPO_ROOT}" \
  --scratch-root "${ROOT}" \
  --manifest "${ROOT}/preflight/manifest.json" \
  --source-config configs/training/smollm_prompt_consistency_seed42.yaml \
  --launcher slurm/m1/train_smollm_prompt_consistency.slurm \
  --output-namespace "${ROOT}/training/seed42" \
  --expected-commit "$(git rev-parse HEAD)"
