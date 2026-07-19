#!/usr/bin/env bash
#SBATCH --job-name=m1-qwen-pareto-prepare
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1/logs/%x-%j.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT="/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1"
RUN="/vol/tmp2/yesildau/m1_cross_family_screen_v1/training/qwen/20260719T111230Z_m1_cross_family_qwen_seed42_810f0ee7"
SOURCE="/vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json"
CORPUS="/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl"
PROBES="/vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/prepare_m1_qwen_checkpoint_pareto.py \
  --run-dir "${RUN}" --source-manifest "${SOURCE}" --output-root "${ROOT}" \
  --general-corpus "${CORPUS}" --probe-registry "${PROBES}" --repo-root "${REPO_ROOT}" \
  --resume-preparation
