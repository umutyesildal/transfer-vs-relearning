#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-train
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --array=0-1%2
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${SLURM_ARRAY_TASK_ID:?Slurm array index is required}"
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
CONTRACT_ROOT="${SCRATCH_ROOT}/contracts/v2"
EXPECTED_CONTRACT_SHA256="f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e"

case "${SLURM_ARRAY_TASK_ID}" in
  0) label="qwen" ;;
  1) label="smollm2" ;;
  *) printf 'invalid_task_id=%s\n' "${SLURM_ARRAY_TASK_ID}" >&2; exit 2 ;;
esac

config="${CONTRACT_ROOT}/training_configs/${label}.json"
output_root="${SCRATCH_ROOT}/training/${label}"
task_tmp="${SCRATCH_ROOT}/tmp/training/${label}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"

cd "${REPO_ROOT}"
test ! -e "${output_root}"
test "$(sha256sum "${CONTRACT_ROOT}/manifest.json" | awk '{print $1}')" = "${EXPECTED_CONTRACT_SHA256}"
"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - "${PREFLIGHT_MANIFEST}" "${EXPECTED_CONTRACT_SHA256}" "${label}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text())
assert payload["status"] == "passed"
assert payload["contract_manifest_sha256"] == sys.argv[2]
assert sys.argv[3] in payload["models"]
created = datetime.fromisoformat(payload["created_at"])
assert (datetime.now(timezone.utc) - created).total_seconds() <= 3600
PY

mkdir -p "${SCRATCH_ROOT}"/{cache/huggingface,cache/torch,logs,tmp/training} "${task_tmp}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${SCRATCH_ROOT}/cache"
export TORCH_HOME="${SCRATCH_ROOT}/cache/torch"
export TMPDIR="${task_tmp}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

module load anaconda/3-2024.06
printf 'label=%s\nnode=%s\ncuda_visible_devices=%s\noutput_root=%s\ncache_root=%s\ntmp_root=%s\n' \
  "${label}" "${SLURMD_NODENAME:-unknown}" "${CUDA_VISIBLE_DEVICES:-unset}" \
  "${output_root}" "${SCRATCH_ROOT}/cache" "${task_tmp}"
nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used --format=csv,noheader
compute_processes=$(nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')
if [[ -n "${compute_processes}" ]]; then
  printf 'unexpected_gpu_compute_processes_before_training:\n%s\n' "${compute_processes}" >&2
  exit 3
fi
printf 'gpu_preflight=clean\n'

conda run --name xfer-relearn python scripts/train_clm.py --config "${config}"

"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - "${output_root}" "${label}" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
runs = sorted(path for path in root.iterdir() if path.is_dir())
assert len(runs) == 1, (sys.argv[2], runs)
run = runs[0]
manifest = json.loads((run / "training_manifest.json").read_text())
assert manifest["status"] == "complete"
assert manifest["result"]["estimated_optimizer_steps"] == 128
assert len(manifest["result"]["checkpoint_dirs"]) == 4
assert (run / "final_model").is_dir()
print(f"status=training_complete label={sys.argv[2]} run={run}")
PY
