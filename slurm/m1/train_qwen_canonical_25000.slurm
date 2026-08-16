#!/usr/bin/env bash
#SBATCH --job-name=qwen25k-train
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=60G
#SBATCH --time=2-12:00:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.err
set -euo pipefail
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"

HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1
OUTPUT_ROOT="${ROOT}/training/replay_w0_5_seed42"
CONFIG="${REPO_ROOT}/configs/training/qwen_canonical_25000_replay_w0_5_seed42.yaml"
CUTOFF="2026-07-31T19:30:00+02:00"

cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/operations/check_training_start_window.py --cutoff "${CUTOFF}"
test -s "${PREFLIGHT_MANIFEST}"
test -s "${ROOT}/prepared/dataset_manifest.json"
test ! -e "${OUTPUT_ROOT}"
conda run --name xfer-relearn python - "${PREFLIGHT_MANIFEST}" "${ROOT}/prepared/dataset_manifest.json" "${CONFIG}" "$(git rev-parse HEAD)" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

preflight_path, dataset_path, config_path = map(Path, sys.argv[1:4])
expected_commit = sys.argv[4]
preflight = json.loads(preflight_path.read_text())
assert preflight["status"] == "passed"
assert preflight["git_commit"] == expected_commit
created = datetime.fromisoformat(preflight["created_at"])
assert (datetime.now(timezone.utc) - created.astimezone(timezone.utc)).total_seconds() <= 3600
sha256 = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert preflight["dataset_manifest_sha256"] == sha256(dataset_path)
assert preflight["config_file_sha256"] == sha256(config_path)
assert preflight["requested_a100_gpus"] == 1
assert preflight["exclusive"] is False
assert preflight["updates"] == 252 and preflight["checkpoints"] == 11
print("training_preflight=fresh_and_verified")
PY

task_tmp="${ROOT}/tmp/training_${SLURM_JOB_ID}"
mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,logs,tmp} "${task_tmp}"
export HF_HOME="${ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache"
export TORCH_HOME="${ROOT}/cache/torch"
export TMPDIR="${task_tmp}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

printf 'node=%s\ncuda_visible_devices=%s\noutput_root=%s\ncache_root=%s\ntmp_root=%s\nexclusive=false\n' \
  "${SLURMD_NODENAME:-unknown}" "${CUDA_VISIBLE_DEVICES:-unset}" "${OUTPUT_ROOT}" "${ROOT}/cache" "${task_tmp}"
nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used --format=csv,noheader
compute_processes=$(nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')
if [[ -n "${compute_processes}" ]]; then
  printf 'unexpected_gpu_compute_processes_before_training:\n%s\n' "${compute_processes}" >&2
  exit 3
fi
printf 'gpu_preflight=clean\n'

conda run --name xfer-relearn python scripts/training/train_clm.py --config "${CONFIG}"
conda run --name xfer-relearn python - "${OUTPUT_ROOT}" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
runs = sorted(path for path in root.iterdir() if path.is_dir())
assert len(runs) == 1, runs
manifest = json.loads((runs[0] / "training_manifest.json").read_text())
assert manifest["status"] == "complete"
assert manifest["result"]["estimated_optimizer_steps"] == 252
assert len(manifest["result"]["checkpoint_dirs"]) == 11
assert (runs[0] / "final_model").is_dir()
print(f"status=training_complete run={runs[0]}")
PY
