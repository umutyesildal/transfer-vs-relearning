#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx3090:1
#SBATCH --array=0-1%2
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${SLURM_ARRAY_TASK_ID:?Slurm array index is required}"
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
EVALUATION_ROOT="${SCRATCH_ROOT}/evaluation_v1"
CONTRACT_ROOT="${SCRATCH_ROOT}/contracts/v2"
EVALUATION_MANIFEST="${EVALUATION_ROOT}/contract/evaluation_manifest.json"
case "${SLURM_ARRAY_TASK_ID}" in
  0) label="qwen" ;;
  1) label="smollm2" ;;
  *) printf 'invalid_task_id=%s\n' "${SLURM_ARRAY_TASK_ID}" >&2; exit 2 ;;
esac
output_root="${EVALUATION_ROOT}/results/${label}"
task_tmp="${EVALUATION_ROOT}/tmp/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"

cd "${REPO_ROOT}"
"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - \
  "${PREFLIGHT_MANIFEST}" "${EVALUATION_MANIFEST}" "${label}" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

preflight = json.loads(Path(sys.argv[1]).read_text())
assert preflight["status"] == "passed"
assert sys.argv[3] in preflight["models"]
created = datetime.fromisoformat(preflight["created_at"])
assert (datetime.now(timezone.utc) - created).total_seconds() <= 3600
digest = hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest()
assert digest == preflight["evaluation_manifest_sha256"]
PY
test ! -e "${output_root}"
mkdir -p "${EVALUATION_ROOT}"/{cache/huggingface,cache/torch,tmp} "${task_tmp}" "${output_root}"
export HF_HOME="${EVALUATION_ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${EVALUATION_ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${EVALUATION_ROOT}/cache"
export TORCH_HOME="${EVALUATION_ROOT}/cache/torch"
export TMPDIR="${task_tmp}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

module load anaconda/3-2024.06
printf 'label=%s\nnode=%s\ncuda_visible_devices=%s\noutput_root=%s\ncache_root=%s\ntmp_root=%s\n' \
  "${label}" "${SLURMD_NODENAME:-unknown}" "${CUDA_VISIBLE_DEVICES:-unset}" \
  "${output_root}" "${EVALUATION_ROOT}/cache" "${task_tmp}"
nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used --format=csv,noheader
compute_processes=$(nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')
if [[ -n "${compute_processes}" ]]; then
  printf 'unexpected_gpu_compute_processes_before_evaluation:\n%s\n' "${compute_processes}" >&2
  exit 3
fi
printf 'gpu_preflight=clean\n'

for state in m0 m1 low full; do
  state_root="${output_root}/${state}"
  manifest="${EVALUATION_ROOT}/contract/model_manifests/${label}_${state}.json"
  printf 'state_start=%s manifest=%s\n' "${state}" "${manifest}"
  conda run --name xfer-relearn python scripts/evaluate_turkish_bridge.py \
    --model-label "${label}_${state}" \
    --model-manifest "${manifest}" \
    --dataset-dir "${REPO_ROOT}/artifacts/datasets/relation_v2_gate_v1" \
    --probe-registry "${CONTRACT_ROOT}/probes/bridge_probe_registry.csv" \
    --output-dir "${state_root}/bridge" \
    --candidate-batch-size 64 --checkpoint-interval 25
  conda run --name xfer-relearn python scripts/evaluate_corpora_perplexity.py \
    --model-label "${label}_${state}" --model-manifest "${manifest}" \
    --corpus "english=/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl" \
    --corpus "turkish=${CONTRACT_ROOT}/dose/validation_documents.jsonl" \
    --output-dir "${state_root}/ppl" --block-size 512 --batch-size 4 \
    --bootstrap-samples 2000 --seed 42
  printf 'state_complete=%s\n' "${state}"
done

conda run --name xfer-relearn python scripts/finalize_turkish_bridge_evaluation.py \
  --model-label "${label}" --evaluation-root "${EVALUATION_ROOT}" \
  --contract-root "${CONTRACT_ROOT}" \
  --experiment-config "${REPO_ROOT}/configs/experiments/turkish_bridge_v1.yaml"
printf 'status=evaluation_complete label=%s\n' "${label}"
