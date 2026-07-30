#!/usr/bin/env bash
#SBATCH --job-name=qwen25k-smoke
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=60G
#SBATCH --time=01:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.err
set -euo pipefail
: "${PREP_MANIFEST:?PREP_MANIFEST is required}"

HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1
SMOKE_ROOT="${ROOT}/smoke"
SOURCE_CONFIG="${REPO_ROOT}/configs/training/qwen_canonical_25000_replay_w0_5_seed42.yaml"
SMOKE_CONFIG="${SMOKE_ROOT}/config.json"
test -s "${PREP_MANIFEST}"
test -s "${ROOT}/prepared/dataset_manifest.json"

printf 'node=%s\ncuda_visible_devices=%s\nsmoke_config=%s\n' \
  "${SLURMD_NODENAME:-unknown}" "${CUDA_VISIBLE_DEVICES:-unset}" "${SMOKE_CONFIG}"
nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used --format=csv,noheader
compute_processes=$(nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')
if [[ -n "${compute_processes}" ]]; then
  printf 'unexpected_gpu_compute_processes_before_smoke:\n%s\n' "${compute_processes}" >&2
  exit 3
fi
printf 'gpu_preflight=clean\n'

# A contaminated allocation must leave no canonical smoke directory behind. This keeps an
# environment-only abort distinguishable from an attempted model load and permits a clean retry.
test ! -e "${SMOKE_ROOT}"
mkdir -p "${SMOKE_ROOT}" "${ROOT}"/{cache/huggingface,cache/torch,logs,tmp}
task_tmp="${ROOT}/tmp/smoke_${SLURM_JOB_ID}"
mkdir -p "${task_tmp}"
export HF_HOME="${ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache"
export TORCH_HOME="${ROOT}/cache/torch"
export TMPDIR="${task_tmp}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python - "${SOURCE_CONFIG}" "${SMOKE_CONFIG}" "${SMOKE_ROOT}/training" <<'PY'
import json
import sys
from pathlib import Path
import yaml

source, destination, output_root = map(Path, sys.argv[1:])
config = yaml.safe_load(source.read_text())
config["training"].update({
    "run_name": "qwen_canonical_25000_replay_smoke",
    "output_root": str(output_root),
    "max_steps": 1,
    "save_steps": 1,
    "eval_steps": 1,
    "save_total_limit": 2,
})
destination.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
PY

conda run --name xfer-relearn python scripts/train_clm.py --config "${SMOKE_CONFIG}"
run_dir=$(find "${SMOKE_ROOT}/training" -mindepth 1 -maxdepth 1 -type d | sort)
test -n "${run_dir}"
test "$(printf '%s\n' "${run_dir}" | wc -l)" -eq 1

# This is a disposable technical smoke, not scientific evidence. Reopen its completed manifest
# only to exercise the real Trainer optimizer-checkpoint resume path with the byte-identical config.
conda run --name xfer-relearn python - "${run_dir}" <<'PY'
import json
import sys
from pathlib import Path

run = Path(sys.argv[1])
manifest_path = run / "training_manifest.json"
manifest = json.loads(manifest_path.read_text())
assert manifest["status"] == "complete"
assert (run / "checkpoints/checkpoint-1/optimizer.pt").is_file()
assert (run / "checkpoints/checkpoint-1/scheduler.pt").is_file()
assert (run / "checkpoints/checkpoint-1/trainer_state.json").is_file()
manifest["status"] = "started"
manifest["smoke_resume_rehearsal"] = True
manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
PY
conda run --name xfer-relearn python scripts/train_clm.py \
  --config "${SMOKE_CONFIG}" --resume-run-dir "${run_dir}"
conda run --name xfer-relearn python - "${run_dir}" "${SMOKE_ROOT}/resume_rehearsal.json" <<'PY'
import json
import sys
from pathlib import Path

run, report_path = map(Path, sys.argv[1:])
manifest = json.loads((run / "training_manifest.json").read_text())
assert manifest["status"] == "complete"
assert len(manifest.get("resume_events", [])) == 1
assert manifest["resume_events"][0]["checkpoint"].endswith("checkpoint-1")
report = {
    "status": "passed",
    "scientific_result": False,
    "run_dir": str(run),
    "optimizer_steps": 1,
    "physical_batch": 50,
    "gradient_accumulation_steps": 500,
    "replay_coefficient": 0.5,
    "resume_checkpoint": manifest["resume_events"][0]["checkpoint"],
}
report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(json.dumps(report, sort_keys=True))
PY
