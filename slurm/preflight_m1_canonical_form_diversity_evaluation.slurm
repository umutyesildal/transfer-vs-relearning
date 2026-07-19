#!/usr/bin/env bash
#SBATCH --job-name=m1-canonical-eval-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/logs/%x-%A.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_canonical_form_diversity_v1"
cd "${REPO_ROOT}"
mkdir -p "${SCRATCH_ROOT}"/{logs,evaluation_preflight,tmp}
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1_form_generalization_preflight.py --repo-root "${REPO_ROOT}" --scratch-root "${SCRATCH_ROOT}" --manifest "${SCRATCH_ROOT}/evaluation_preflight/manifest.json" --source-config configs/training/m1_canonical_form_diversity_seed42.yaml --launcher slurm/eval_m1_canonical_form_diversity.slurm --output-namespace "${SCRATCH_ROOT}/evaluations" --expected-commit "$(git rev-parse HEAD)"
