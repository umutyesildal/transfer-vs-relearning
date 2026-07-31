#!/usr/bin/env bash
# Two-model reload/scoring smoke test for the frozen bilingual pre-M2 baseline.
# This is intentionally probe-limited and writes only to scratch.
#SBATCH --job-name=qwen-pre-m2-smoke
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --exclude=gruenau10
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --array=0-1%1
#SBATCH --output=/vol/tmp2/yesildau/qwen_pre_m2_baseline_smoke_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_pre_m2_baseline_smoke_v1/logs/%x-%A_%a.err
set -euo pipefail

: "${SLURM_ARRAY_TASK_ID:?Slurm array index is required}"
: "${EXPECTED_COMMIT:?EXPECTED_COMMIT must be passed at submission time}"
HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/qwen_pre_m2_baseline_smoke_v3"
CONTRACT_ROOT="/vol/tmp2/yesildau/qwen_pre_m2_contract_v1"
SLICE="${CONTRACT_ROOT}/evaluation/slices/tr_to_tr_form_a_direct.csv"
DATASET_DIR="${REPO_ROOT}/artifacts/datasets/relation_v2_gate_v1"

case "${SLURM_ARRAY_TASK_ID}" in
  0)
    MODEL_LABEL="qwen_m1_seed42_step75"
    MODEL_MANIFEST="/vol/tmp2/yesildau/qwen_scale_selected_v1/seed42_step75/selected_artifact_manifest.json"
    RESULT_ROOT="${SCRATCH_ROOT}/results/seed42_step75"
    EXPECTED_SEED=42
    EXPECTED_STEP=75
    ;;
  1)
    MODEL_LABEL="qwen_m1_seed43_step50"
    MODEL_MANIFEST="/vol/tmp2/yesildau/qwen_scale_selected_v1/seed43_step50/selected_artifact_manifest.json"
    RESULT_ROOT="${SCRATCH_ROOT}/results/seed43_step50"
    EXPECTED_SEED=43
    EXPECTED_STEP=50
    ;;
  *)
    printf 'invalid_array_task=%s\n' "${SLURM_ARRAY_TASK_ID}" >&2
    exit 2
    ;;
esac

cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test -s "${CONTRACT_ROOT}/manifest.json"
test -s "${CONTRACT_ROOT}/evaluation/slice_registry.json"
test -s "${SLICE}"
test -s "${MODEL_MANIFEST}"
test -d "${DATASET_DIR}"
test ! -e "${RESULT_ROOT}"

module load anaconda/3-2024.06
python_bin="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"
"${python_bin}" - "${MODEL_MANIFEST}" "${EXPECTED_SEED}" "${EXPECTED_STEP}" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert manifest["status"] == "frozen_selected_model_only"
assert int(manifest["seed"]) == int(sys.argv[2])
assert int(manifest["checkpoint_step"]) == int(sys.argv[3])
for item in manifest["files"].values():
    assert Path(item["path"]).is_file(), item["path"]
print(f"model_manifest=verified seed={manifest['seed']} step={manifest['checkpoint_step']}")
PY

TASK_TMP="${SCRATCH_ROOT}/tmp/${MODEL_LABEL}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs,tmp} "${TASK_TMP}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${SCRATCH_ROOT}/cache"
export TORCH_HOME="${SCRATCH_ROOT}/cache/torch"
export TMPDIR="${TASK_TMP}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

printf 'node=%s\nmodel_label=%s\nmodel_manifest=%s\nprobe_registry=%s\noutput_root=%s\ncache_root=%s\ntmp_root=%s\nprobe_limit=4\n' \
  "${SLURMD_NODENAME:-unknown}" "${MODEL_LABEL}" "${MODEL_MANIFEST}" \
  "${SLICE}" "${RESULT_ROOT}" "${SCRATCH_ROOT}/cache" "${TASK_TMP}"
nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used --format=csv,noheader
compute_processes=$(nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')
if [[ -n "${compute_processes}" ]]; then
  printf 'unexpected_gpu_compute_processes_before_smoke:\n%s\n' "${compute_processes}" >&2
  exit 3
fi
printf 'gpu_preflight=clean\n'

conda run --name xfer-relearn python scripts/evaluate_pre_m2_frozen_suite.py \
  --model-label "${MODEL_LABEL}" \
  --model-manifest "${MODEL_MANIFEST}" \
  --dataset-dir "${DATASET_DIR}" \
  --probe-registry "${SLICE}" \
  --output-dir "${RESULT_ROOT}" \
  --candidate-batch-size 64 \
  --checkpoint-interval 2 \
  --probe-limit 4

"${python_bin}" - "${RESULT_ROOT}" <<'PY'
import csv
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
rows = list(csv.DictReader((root / "hard_suite_per_fact.csv").open(encoding="utf-8", newline="")))
assert summary["status"] == "completed"
assert summary["probes"] == 4
assert len(rows) == 4
assert {row["direction"] for row in rows} == {"tr_to_tr"}
assert {row["answer_language"] for row in rows} == {"tr"}
assert all(row["predicted_surface"] for row in rows)
print(f"status=smoke_passed probes={len(rows)} top1={summary['top1']} output_root={root}")
PY
