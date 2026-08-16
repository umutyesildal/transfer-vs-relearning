#!/usr/bin/env bash
# Frozen generic English/Turkish PPL baseline for the two selected Qwen M1 artifacts.
#SBATCH --job-name=qwen-pre-m2-ppl
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx3090:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --array=0-1%1
#SBATCH --output=/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1/logs/%x-%A_%a.err
set -euo pipefail

: "${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID is required}"
: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"
HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT="${BASELINE_ROOT:-/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1}"
OUTPUT_ROOT="${ROOT}/ppl_final"
TASK_TMP="${ROOT}/tmp/ppl_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
EN_CORPUS="/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl"
TR_CORPUS="/vol/tmp2/yesildau/turkish_bridge_v1/corpus/trwiki_20260601_bridge_v1/splits/validation_documents.jsonl"

cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test -s "${EN_CORPUS}"
test -s "${TR_CORPUS}"
test -d "${ROOT}/results"

module load anaconda/3-2024.06
python_bin="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"
case "${SLURM_ARRAY_TASK_ID}" in
  0)
    MODEL_LABEL="qwen_m1_seed42_step75"
    MODEL_MANIFEST="/vol/tmp2/yesildau/qwen_scale_selected_v1/seed42_step75/selected_artifact_manifest.json"
    ;;
  1)
    MODEL_LABEL="qwen_m1_seed43_step50"
    MODEL_MANIFEST="/vol/tmp2/yesildau/qwen_scale_selected_v1/seed43_step50/selected_artifact_manifest.json"
    ;;
  *)
    printf 'invalid_task_id=%s\n' "${SLURM_ARRAY_TASK_ID}" >&2
    exit 2
    ;;
esac
test -s "${MODEL_MANIFEST}"
OUTPUT_DIR="${OUTPUT_ROOT}/${MODEL_LABEL}"
test ! -e "${OUTPUT_DIR}"
mkdir -p "${ROOT}"/cache/huggingface "${ROOT}"/cache/torch "${ROOT}/logs" "${TASK_TMP}"
export HF_HOME="${ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache"
export TORCH_HOME="${ROOT}/cache/torch"
export TMPDIR="${TASK_TMP}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

printf 'node=%s\nmodel_label=%s\nmodel_manifest=%s\noutput_root=%s\nenglish_corpus=%s\nturkish_corpus=%s\n' \
  "${SLURMD_NODENAME:-unknown}" "${MODEL_LABEL}" "${MODEL_MANIFEST}" "${OUTPUT_DIR}" \
  "${EN_CORPUS}" "${TR_CORPUS}"
nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used --format=csv,noheader
allocated_gpu="${CUDA_VISIBLE_DEVICES:-${SLURM_JOB_GPUS:-}}"
test -n "${allocated_gpu}"
printf 'allocated_gpu_selector=%s\n' "${allocated_gpu}"
compute_processes=$(nvidia-smi --id="${allocated_gpu}" --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')
if [[ -n "${compute_processes}" ]]; then
  printf 'unexpected_gpu_compute_processes_on_allocated_device:\n%s\n' "${compute_processes}" >&2
  exit 3
fi
printf 'gpu_preflight=clean\n'

conda run --name xfer-relearn python scripts/evaluation/evaluate_corpora_perplexity.py \
  --model-label "${MODEL_LABEL}" \
  --model-manifest "${MODEL_MANIFEST}" \
  --corpus "english=${EN_CORPUS}" \
  --corpus "turkish=${TR_CORPUS}" \
  --output-dir "${OUTPUT_DIR}" \
  --block-size 512 \
  --batch-size 4 \
  --bootstrap-samples 2000 \
  --seed 42

"${python_bin}" - "${OUTPUT_DIR}/summary.json" <<'PY'
import json
from pathlib import Path
import sys

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["status"] == "completed"
assert set(payload["corpora"]) == {"english", "turkish"}
PY
printf 'status=ppl_complete model=%s output=%s\n' "${MODEL_LABEL}" "${OUTPUT_DIR}"
