#!/usr/bin/env bash
# Four matched Qwen adaptation runs: M2/M3 for seeds 42/43.
# Submit only through scripts/submit_qwen_m2_m3.sh after the frozen contract exists.
#SBATCH --job-name=qwen-m2-m3-train
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
# gruenau10 currently has an unrelated compute process on one A100 device.
# Keep the clean-GPU guard and exclude that node for future principal tasks.
#SBATCH --exclude=gruenau10
#SBATCH --array=0-3%2
#SBATCH --output=/vol/tmp2/yesildau/qwen_m2_m3_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_m2_m3_v1/logs/%x-%A_%a.err
set -euo pipefail

: "${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID is required}"
: "${CONFIG_MANIFEST:?CONFIG_MANIFEST is required}"
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"
: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_m2_m3_v1
cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test -s "${PREFLIGHT_MANIFEST}"
module load anaconda/3-2024.06
python_bin="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"
test "$(${python_bin} -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "${PREFLIGHT_MANIFEST}")" = passed
mapfile -t task_fields < <(PYTHONPATH="${REPO_ROOT}/src" "${python_bin}" - "${CONFIG_MANIFEST}" "${SLURM_ARRAY_TASK_ID}" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
entries = sorted(manifest["configs"], key=lambda item: (int(item["seed"]), str(item["arm"])))
item = entries[int(sys.argv[2])]
print(item["label"])
print(item["config"])
print(item["output_root"])
PY
)
LABEL="${task_fields[0]}"
CONFIG="${task_fields[1]}"
OUTPUT_ROOT="${task_fields[2]}"
test -s "${CONFIG}"
test ! -e "${OUTPUT_ROOT}"
task_tmp="${ROOT}/tmp/${LABEL}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${ROOT}/cache/huggingface" "${ROOT}/cache/torch" "${ROOT}/logs" "${task_tmp}"
export HF_HOME="${ROOT}/cache/huggingface" TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache" TORCH_HOME="${ROOT}/cache/torch" TMPDIR="${task_tmp}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used --format=csv,noheader
allocated_gpu="${CUDA_VISIBLE_DEVICES:-${SLURM_JOB_GPUS:-}}"
test -n "${allocated_gpu}"
printf 'allocated_gpu_selector=%s\n' "${allocated_gpu}"
compute_processes=$(nvidia-smi --id="${allocated_gpu}" --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')
if [[ -n "${compute_processes}" ]]; then
  printf 'unexpected_gpu_compute_processes_on_allocated_device:\n%s\n' "${compute_processes}" >&2
  exit 3
fi
printf 'gpu_preflight=clean\nlabel=%s\nconfig=%s\noutput_root=%s\n' "${LABEL}" "${CONFIG}" "${OUTPUT_ROOT}"
PYTHONPATH="${REPO_ROOT}/src" conda run --name xfer-relearn python scripts/train_clm.py --config "${CONFIG}"
