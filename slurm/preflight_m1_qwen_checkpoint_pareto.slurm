#!/usr/bin/env bash
#SBATCH --job-name=m1-qwen-pareto-pre
#SBATCH --account=yesildau
#SBATCH --partition=standard
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:20:00
#SBATCH --output=/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1/logs/%x-%j.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT="/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
commit="$(git rev-parse HEAD)"
conda run --name xfer-relearn python scripts/m1_qwen_checkpoint_pareto_preflight.py \
  --repo-root "${REPO_ROOT}" \
  --registry "${ROOT}/checkpoint_registry.csv" \
  --wave-manifest "${ROOT}/wave_manifest.json" \
  --launcher "${REPO_ROOT}/slurm/eval_m1_qwen_checkpoint_pareto.slurm" \
  --manifest "${ROOT}/preflight/manifest.json" \
  --expected-commit "${commit}"
