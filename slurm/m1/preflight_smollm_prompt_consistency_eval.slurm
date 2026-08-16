#!/usr/bin/env bash
#SBATCH --job-name=smollm-pconsistency-eval-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:20:00
#SBATCH --output=/vol/tmp2/yesildau/smollm_prompt_consistency_v2/evaluation_v1/logs/%x-%A.out
#SBATCH --error=/vol/tmp2/yesildau/smollm_prompt_consistency_v2/evaluation_v1/logs/%x-%A.err
set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT=/vol/tmp2/yesildau/smollm_prompt_consistency_v2/evaluation_v1
RUN=/vol/tmp2/yesildau/smollm_prompt_consistency_v2/training/seed42/20260729T085627Z_smollm_prompt_consistency_seed42_b7938973
cd "${REPO_ROOT}"
mkdir -p "${ROOT}"/{logs,preflight,tmp}
module load anaconda/3-2024.06
items=(checkpoint-25 checkpoint-50 checkpoint-75 checkpoint-100 checkpoint-125 checkpoint-150 checkpoint-175 checkpoint-200 checkpoint-225 checkpoint-250 checkpoint-252 final_model)
args=()
for item in "${items[@]}"; do
  [[ -d "${RUN}/${item}" || -d "${RUN}/checkpoints/${item}" ]]
  args+=(--output-namespace "${ROOT}/smollm_pconsistency_seed42_${item//-/_}/results")
done
conda run --name xfer-relearn python scripts/m1/m1_form_generalization_preflight.py \
  --repo-root "${REPO_ROOT}" \
  --scratch-root "${ROOT}" \
  --manifest "${ROOT}/preflight/manifest.json" \
  --source-config configs/training/smollm_prompt_consistency_seed42.yaml \
  --launcher slurm/m1/eval_smollm_prompt_consistency_array.slurm \
  "${args[@]}" \
  --expected-commit "$(git rev-parse HEAD)"
