#!/usr/bin/env bash
#SBATCH --job-name=m1-ret-anchor
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_v1/logs/%x-%j.err
set -euo pipefail
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/m1_retention_v1"
test -s "${PREFLIGHT_MANIFEST}"
expected_commit=$("${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" -c \
  'import json,sys; print(json.load(open(sys.argv[1]))["git_commit"])' "${PREFLIGHT_MANIFEST}")
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${expected_commit}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,tmp}
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${SCRATCH_ROOT}/cache"
export TORCH_HOME="${SCRATCH_ROOT}/cache/torch"
export TMPDIR="${SCRATCH_ROOT}/tmp"

cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/prepare_m1_retention_anchor.py \
  --output-dir "${SCRATCH_ROOT}/anchor" \
  --model-manifest /vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json \
  --subject-registry artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv \
  --subject-count 100 --train-rows 3500 --validation-rows 500 --max-tokens 64 --seed 42
