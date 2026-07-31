#!/usr/bin/env bash
# One frozen bilingual baseline slice. The 48-task wave is 2 models x 24 slices.
#SBATCH --job-name=qwen-pre-m2-base-eval
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --array=0-47%1
#SBATCH --output=/vol/tmp2/yesildau/qwen_pre_m2_baseline_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_pre_m2_baseline_v1/logs/%x-%A_%a.err
set -euo pipefail

: "${SLURM_ARRAY_TASK_ID:?Slurm array index is required}"
: "${EXPECTED_COMMIT:?EXPECTED_COMMIT must be passed at submission time}"
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"
HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT="${BASELINE_SCRATCH_ROOT:-/vol/tmp2/yesildau/qwen_pre_m2_baseline_v1}"
CONTRACT_ROOT="/vol/tmp2/yesildau/qwen_pre_m2_contract_v1"
REGISTRY="${CONTRACT_ROOT}/evaluation/slice_registry.json"
DATASET_DIR="${REPO_ROOT}/artifacts/datasets/relation_v2_gate_v1"

cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test -s "${PREFLIGHT_MANIFEST}"
test -s "${REGISTRY}"
test -d "${DATASET_DIR}"

module load anaconda/3-2024.06
python_bin="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"
mapfile -t task_fields < <("${python_bin}" - "${SLURM_ARRAY_TASK_ID}" "${REGISTRY}" "${ROOT}" <<'PY'
import json
import sys
from pathlib import Path

task_index = int(sys.argv[1])
registry = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
assert len(registry) == 24
model_index, slice_index = divmod(task_index, 24)
assert model_index in {0, 1}
item = registry[slice_index]
labels = ("qwen_m1_seed42_step75", "qwen_m1_seed43_step50")
manifests = (
    "/vol/tmp2/yesildau/qwen_scale_selected_v1/seed42_step75/selected_artifact_manifest.json",
    "/vol/tmp2/yesildau/qwen_scale_selected_v1/seed43_step50/selected_artifact_manifest.json",
)
print(labels[model_index])
print(manifests[model_index])
print(item["slice_id"])
print(item["path"])
print(item["sha256"])
print(str(Path(sys.argv[3]) / "results" / labels[model_index] / item["slice_id"]))
PY
)
MODEL_LABEL="${task_fields[0]}"
MODEL_MANIFEST="${task_fields[1]}"
SLICE_ID="${task_fields[2]}"
SLICE_PATH="${task_fields[3]}"
SLICE_SHA256="${task_fields[4]}"
RESULT_ROOT="${task_fields[5]}"

test -s "${MODEL_MANIFEST}"
test -s "${SLICE_PATH}"
test "$(sha256sum "${SLICE_PATH}" | awk '{print $1}')" = "${SLICE_SHA256}"
test ! -e "${RESULT_ROOT}"
"${python_bin}" - "${PREFLIGHT_MANIFEST}" "${EXPECTED_COMMIT}" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["status"] == "passed"
assert payload["git_commit"] == sys.argv[2]
assert payload["expected_jobs"] == 48
assert payload["expected_new_checkpoints"] == 0
PY

TASK_TMP="${ROOT}/tmp/${MODEL_LABEL}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,logs,tmp} "${TASK_TMP}"
export HF_HOME="${ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache"
export TORCH_HOME="${ROOT}/cache/torch"
export TMPDIR="${TASK_TMP}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

printf 'node=%s\nmodel_label=%s\nmodel_manifest=%s\nslice_id=%s\nprobe_registry=%s\noutput_root=%s\ncache_root=%s\ntmp_root=%s\nexpected_probes=2500\n' \
  "${SLURMD_NODENAME:-unknown}" "${MODEL_LABEL}" "${MODEL_MANIFEST}" "${SLICE_ID}" \
  "${SLICE_PATH}" "${RESULT_ROOT}" "${ROOT}/cache" "${TASK_TMP}"
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
  --model-label "${MODEL_LABEL}" \
  --model-manifest "${MODEL_MANIFEST}" \
  --dataset-dir "${DATASET_DIR}" \
  --probe-registry "${SLICE_PATH}" \
  --output-dir "${RESULT_ROOT}" \
  --candidate-batch-size 64 \
  --checkpoint-interval 25

"${python_bin}" - "${RESULT_ROOT}" "${SLICE_ID}" <<'PY'
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
assert len(rows) == 2_500, (slice_id, len(rows))
assert len({row["probe_id"] for row in rows}) == 2_500
print(f"status=baseline_slice_complete slice={slice_id} probes={len(rows)} output_root={root}")
PY
