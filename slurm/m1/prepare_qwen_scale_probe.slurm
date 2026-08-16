#!/usr/bin/env bash
#SBATCH --job-name=qwen-scale-prep
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_scale_probe_v3/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_scale_probe_v3/logs/%x-%j.err
set -euo pipefail
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_scale_probe_v3
test -s "${PREFLIGHT_MANIFEST}"
mkdir -p "${ROOT}"/{logs,cache/huggingface,cache/torch,tmp}
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TMPDIR="${ROOT}/tmp"
cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1/build_qwen_scale_probe_dataset.py --output-dir "${ROOT}/datasets"
conda run --name xfer-relearn python scripts/m1/prepare_m1_retention_anchor.py \
  --output-dir "${ROOT}/anchor" \
  --model-manifest /vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json \
  --factual-train-file "${ROOT}/datasets/train.jsonl" --subject-count 500 \
  --train-rows 17500 --validation-rows 2301 --max-tokens 64 --seed 42
test -s "${ROOT}/datasets/dataset_manifest.json"
test -s "${ROOT}/anchor/manifest.json"
printf 'status=prepared\n'
