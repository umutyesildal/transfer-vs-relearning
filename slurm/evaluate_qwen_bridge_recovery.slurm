#!/usr/bin/env bash
#SBATCH --job-name=qwen-bridge-recov
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx3090:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
OUTPUT_ROOT="${SCRATCH_ROOT}/evaluation_v2_qwen"
CONTRACT_ROOT="${SCRATCH_ROOT}/contracts/v2"
RECOVERY_MANIFEST="${OUTPUT_ROOT}/contract/recovery_manifest.json"
RESULT_ROOT="${OUTPUT_ROOT}/results/qwen"
TASK_TMP="${OUTPUT_ROOT}/tmp/qwen_${SLURM_JOB_ID}"

cd "${REPO_ROOT}"
"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - \
  "${PREFLIGHT_MANIFEST}" "${RECOVERY_MANIFEST}" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

preflight = json.loads(Path(sys.argv[1]).read_text())
assert preflight["status"] == "passed"
assert preflight["states"] == ["m1", "low", "full"]
created = datetime.fromisoformat(preflight["created_at"])
assert (datetime.now(timezone.utc) - created).total_seconds() <= 3600
assert hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest() == preflight["recovery_manifest_sha256"]
PY
test ! -e "${RESULT_ROOT}"
mkdir -p "${OUTPUT_ROOT}"/{cache/huggingface,cache/torch,tmp} "${TASK_TMP}" "${RESULT_ROOT}"
export HF_HOME="${OUTPUT_ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${OUTPUT_ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${OUTPUT_ROOT}/cache"
export TORCH_HOME="${OUTPUT_ROOT}/cache/torch"
export TMPDIR="${TASK_TMP}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

module load anaconda/3-2024.06
printf 'node=%s\ncuda_visible_devices=%s\noutput_root=%s\ncache_root=%s\ntmp_root=%s\n' \
  "${SLURMD_NODENAME:-unknown}" "${CUDA_VISIBLE_DEVICES:-unset}" \
  "${RESULT_ROOT}" "${OUTPUT_ROOT}/cache" "${TASK_TMP}"
nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used --format=csv,noheader
compute_processes=$(nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')
if [[ -n "${compute_processes}" ]]; then
  printf 'unexpected_gpu_compute_processes_before_evaluation:\n%s\n' "${compute_processes}" >&2
  exit 3
fi
printf 'gpu_preflight=clean\n'

for state in m1 low full; do
  state_root="${RESULT_ROOT}/${state}"
  manifest="${OUTPUT_ROOT}/contract/model_manifests/qwen_${state}.json"
  printf 'state_start=%s manifest=%s\n' "${state}" "${manifest}"
  conda run --name xfer-relearn python scripts/evaluate_turkish_bridge.py \
    --model-label "qwen_${state}_recovery" --model-manifest "${manifest}" \
    --dataset-dir "${REPO_ROOT}/artifacts/datasets/relation_v2_gate_v1" \
    --probe-registry "${CONTRACT_ROOT}/probes/bridge_probe_registry.csv" \
    --output-dir "${state_root}/bridge" --candidate-batch-size 64 --checkpoint-interval 25
  conda run --name xfer-relearn python scripts/evaluate_corpora_perplexity.py \
    --model-label "qwen_${state}_recovery" --model-manifest "${manifest}" \
    --corpus "english=/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl" \
    --corpus "turkish=${CONTRACT_ROOT}/dose/validation_documents.jsonl" \
    --output-dir "${state_root}/ppl" --block-size 512 --batch-size 4 \
    --bootstrap-samples 2000 --seed 42
  printf 'state_complete=%s\n' "${state}"
done

conda run --name xfer-relearn python scripts/finalize_turkish_bridge_evaluation.py \
  --model-label qwen --evaluation-root "${OUTPUT_ROOT}" --contract-root "${CONTRACT_ROOT}" \
  --experiment-config "${REPO_ROOT}/configs/experiments/turkish_bridge_v1.yaml" \
  --m0-source-root "${SCRATCH_ROOT}/evaluation_v1/results/qwen/m0"
printf 'status=qwen_recovery_evaluation_complete\n'
