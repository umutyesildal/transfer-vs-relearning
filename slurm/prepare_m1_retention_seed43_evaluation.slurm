#!/usr/bin/env bash
#SBATCH --job-name=m1-ret43-eval-prep
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_seed43_v1/logs/%x-%j.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning}"
ROOT="/vol/tmp2/yesildau/m1_retention_seed43_v1"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/prepare_m1_retention_seed43_evaluation.py \
  --training-root "${ROOT}/training/replay_w0_5_seed43" \
  --source-manifest /vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json \
  --output-root "${ROOT}/evaluation_v1" \
  --general-corpus /vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl \
  --probe-registry /vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv \
  --repo-root "${REPO_ROOT}"
