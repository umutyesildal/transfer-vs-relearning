#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-qwen
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --nodelist=gruenau10
#SBATCH --gres=gpu:a10080gb:2
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
CONTRACT_ROOT="${SCRATCH_ROOT}/contracts/v2"
EXPECTED_CONTRACT_SHA256="f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e"
config="${CONTRACT_ROOT}/training_configs/qwen.json"
output_root="${SCRATCH_ROOT}/training/qwen"
task_tmp="${SCRATCH_ROOT}/tmp/training/qwen_recovery_${SLURM_JOB_ID}"

cd "${REPO_ROOT}"
test ! -e "${output_root}"
test "$(sha256sum "${CONTRACT_ROOT}/manifest.json" | awk '{print $1}')" = "${EXPECTED_CONTRACT_SHA256}"
"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - "${PREFLIGHT_MANIFEST}" "${EXPECTED_CONTRACT_SHA256}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text())
assert payload["status"] == "passed"
assert payload["model"] == "qwen"
assert payload["contract_manifest_sha256"] == sys.argv[2]
assert payload["requested_a100_gpus"] == 2
assert payload["training_gpu_count"] == 1
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
printf 'label=qwen\nnode=%s\nallocated_cuda_visible_devices=%s\noutput_root=%s\ncache_root=%s\ntmp_root=%s\n' \
  "${SLURMD_NODENAME:-unknown}" "${CUDA_VISIBLE_DEVICES:-unset}" \
  "${output_root}" "${SCRATCH_ROOT}/cache" "${task_tmp}"
nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used --format=csv,noheader

clean_uuid=""
allocated_count=0
while IFS=',' read -r raw_uuid raw_used; do
  uuid="${raw_uuid//[[:space:]]/}"
  used="${raw_used//[^0-9]/}"
  allocated_count=$((allocated_count + 1))
  processes=$(nvidia-smi --id="${uuid}" --query-compute-apps=pid,process_name,used_memory \
    --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')
  if [[ -z "${processes}" && "${used}" -lt 1024 && -z "${clean_uuid}" ]]; then
    clean_uuid="${uuid}"
    printf 'gpu_candidate=%s status=clean baseline_memory_mib=%s\n' "${uuid}" "${used}"
  elif [[ -n "${processes}" ]]; then
    printf 'gpu_candidate=%s status=occupied baseline_memory_mib=%s processes=%s\n' \
      "${uuid}" "${used}" "${processes}"
  else
    printf 'gpu_candidate=%s status=not_selected baseline_memory_mib=%s\n' "${uuid}" "${used}"
  fi
done < <(nvidia-smi --query-gpu=uuid,memory.used --format=csv,noheader,nounits)

test "${allocated_count}" -eq 2
if [[ -z "${clean_uuid}" ]]; then
  printf 'no_clean_allocated_gpu_before_training\n' >&2
  exit 3
fi
export CUDA_VISIBLE_DEVICES="${clean_uuid}"
printf 'selected_training_gpu_uuid=%s\ngpu_preflight=clean\n' "${clean_uuid}"

conda run --name xfer-relearn python scripts/train_clm.py --config "${config}"

"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - "${output_root}" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
runs = sorted(path for path in root.iterdir() if path.is_dir())
assert len(runs) == 1, runs
run = runs[0]
manifest = json.loads((run / "training_manifest.json").read_text())
assert manifest["status"] == "complete"
assert manifest["result"]["estimated_optimizer_steps"] == 128
assert len(manifest["result"]["checkpoint_dirs"]) == 4
assert (run / "final_model").is_dir()
print(f"status=training_complete label=qwen run={run}")
PY
