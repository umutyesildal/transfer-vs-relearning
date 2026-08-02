#!/usr/bin/env bash
# One fixed bilingual 2,500-probe slice for one M2/M3 checkpoint-128 endpoint.
#SBATCH --job-name=qwen-m2-m3-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:rtx3090:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --array=0-95%1
#SBATCH --output=/vol/tmp2/yesildau/qwen_m2_m3_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_m2_m3_v1/logs/%x-%A_%a.err
set -euo pipefail

: "${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID is required}"
: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"
: "${EVALUATION_MANIFEST:?EVALUATION_MANIFEST is required}"
ALLOW_EXISTING_EMPTY_RESULT_ROOT="${ALLOW_EXISTING_EMPTY_RESULT_ROOT:-0}"
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_m2_m3_v1
CONTRACT_ROOT=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1
DATASET_DIR="${REPO_ROOT}/artifacts/datasets/relation_v2_gate_v1"
PYTHON_BIN="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"

cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test -s "${PREFLIGHT_MANIFEST}"
test -s "${EVALUATION_MANIFEST}"
mapfile -t fields < <("${PYTHON_BIN}" - "${EVALUATION_MANIFEST}" "${CONTRACT_ROOT}" "${SLURM_ARRAY_TASK_ID}" <<'PY'
import json
import os
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
registry = json.loads((Path(sys.argv[2]) / "evaluation/slice_registry.json").read_text(encoding="utf-8"))
state_index, slice_index = divmod(int(sys.argv[3]), 24)
state = manifest["states"][state_index]
item = registry[slice_index]
print(state["state_id"])
print(state["model_manifest"])
print(state["results_root"])
print(item["slice_id"])
print(item["path"])
print(item["sha256"])
PY
)
STATE_ID="${fields[0]}"
MODEL_MANIFEST="${fields[1]}"
RESULTS_ROOT="${fields[2]}"
SLICE_ID="${fields[3]}"
SLICE_PATH="${fields[4]}"
SLICE_SHA256="${fields[5]}"
RESULT_ROOT="${RESULTS_ROOT}/${SLICE_ID}"

test -s "${MODEL_MANIFEST}"
test -s "${SLICE_PATH}"
test "$(sha256sum "${SLICE_PATH}" | awk '{print $1}')" = "${SLICE_SHA256}"
if [[ "${ALLOW_EXISTING_EMPTY_RESULT_ROOT}" == "1" ]]; then
  : "${RETRY_MANIFEST:?RETRY_MANIFEST is required for an empty-result retry}"
  "${PYTHON_BIN}" - "${RETRY_MANIFEST}" "${SLURM_ARRAY_TASK_ID}" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
task_id = int(sys.argv[2])
assert payload["status"] == "ready_for_fresh_preflight"
assert task_id in [int(value) for value in payload["task_ids"]]
PY
  test -d "${RESULT_ROOT}"
  if find "${RESULT_ROOT}" -type f -print -quit | grep -q .; then
    echo "retry result root is not empty: ${RESULT_ROOT}" >&2
    exit 4
  fi
else
  test ! -e "${RESULT_ROOT}"
fi
"${PYTHON_BIN}" - "${PREFLIGHT_MANIFEST}" "${EXPECTED_COMMIT}" <<'PY'
import json
import os
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["status"] == "passed"
assert payload["git_commit"] == sys.argv[2]
expected_jobs = 4 if os.environ.get("ALLOW_EXISTING_EMPTY_RESULT_ROOT") == "1" else 96
assert payload["expected_jobs"] == expected_jobs
assert payload["expected_new_checkpoints"] == 0
PY

TASK_TMP="${ROOT}/tmp/${STATE_ID}_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,logs,tmp} "${TASK_TMP}"
export HF_HOME="${ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache"
export TORCH_HOME="${ROOT}/cache/torch"
export TMPDIR="${TASK_TMP}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

printf 'node=%s\nstate_id=%s\nmodel_manifest=%s\nslice_id=%s\nprobe_registry=%s\noutput_root=%s\nexpected_probes=2500\n' \
  "${SLURMD_NODENAME:-unknown}" "${STATE_ID}" "${MODEL_MANIFEST}" "${SLICE_ID}" \
  "${SLICE_PATH}" "${RESULT_ROOT}"
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

conda run --name xfer-relearn python scripts/evaluate_pre_m2_frozen_suite.py \
  --model-label "${STATE_ID}" \
  --model-manifest "${MODEL_MANIFEST}" \
  --dataset-dir "${DATASET_DIR}" \
  --probe-registry "${SLICE_PATH}" \
  --output-dir "${RESULT_ROOT}" \
  --candidate-batch-size 64 \
  --checkpoint-interval 25

"${PYTHON_BIN}" - "${RESULT_ROOT}" "${SLICE_ID}" <<'PY'
import csv
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
slice_id = sys.argv[2]
summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
manifest = json.loads((root / "run_manifest.json").read_text(encoding="utf-8"))
rows = list(csv.DictReader((root / "hard_suite_per_fact.csv").open(encoding="utf-8", newline="")))
assert summary["status"] == "completed", slice_id
assert manifest["status"] == "completed", slice_id
assert len(rows) == 2500, (slice_id, len(rows))
assert len({row["probe_id"] for row in rows}) == 2500
print(f"status=m2_m3_eval_slice_complete slice={slice_id} probes={len(rows)} output_root={root}")
PY
