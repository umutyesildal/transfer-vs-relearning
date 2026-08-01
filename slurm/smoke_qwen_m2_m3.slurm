#!/usr/bin/env bash
# Short clean-GPU smoke for one matched Qwen M2/M3 arm.
# This validates pretokenized block loading, finite loss, one optimizer update,
# checkpoint creation, and the real optimizer-checkpoint resume path.
#SBATCH --job-name=qwen-m2-m3-smoke
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --nodelist=gruenau9
#SBATCH --array=0-1%1
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
SMOKE_ROOT="${ROOT}/smoke"

cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test -s "${CONFIG_MANIFEST}"
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "${PREFLIGHT_MANIFEST}")" = passed

mapfile -t task_fields < <(python3 - "${CONFIG_MANIFEST}" "${SLURM_ARRAY_TASK_ID}" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
entries = sorted(manifest["configs"], key=lambda item: (int(item["seed"]), str(item["arm"])))
item = entries[int(sys.argv[2])]
assert int(item["seed"]) == 42, item
print(item["label"])
print(item["config"])
print(item["base_model_manifest"])
PY
)
LABEL="${task_fields[0]}"
SOURCE_CONFIG="${task_fields[1]}"
MODEL_MANIFEST="${task_fields[2]}"
SMOKE_ARM_ROOT="${SMOKE_ROOT}/${LABEL}"
SMOKE_CONFIG="${SMOKE_ARM_ROOT}/config.json"
SMOKE_TRAIN_ROOT="${SMOKE_ARM_ROOT}/training"

test -s "${SOURCE_CONFIG}"
test -s "${MODEL_MANIFEST}"
test ! -e "${SMOKE_ARM_ROOT}"

printf 'node=%s\nlabel=%s\nsource_config=%s\nmodel_manifest=%s\nsmoke_root=%s\n' \
  "${SLURMD_NODENAME:-unknown}" "${LABEL}" "${SOURCE_CONFIG}" "${MODEL_MANIFEST}" "${SMOKE_ARM_ROOT}"
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

module load anaconda/3-2024.06
python_bin="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"
mkdir -p "${SMOKE_ARM_ROOT}" "${ROOT}/cache/huggingface" "${ROOT}/cache/torch" "${ROOT}/logs" "${ROOT}/tmp"
task_tmp="${ROOT}/tmp/${LABEL}_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${task_tmp}"
export HF_HOME="${ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache"
export TORCH_HOME="${ROOT}/cache/torch"
export TMPDIR="${task_tmp}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

"${python_bin}" - "${SOURCE_CONFIG}" "${SMOKE_CONFIG}" "${SMOKE_TRAIN_ROOT}" <<'PY'
import json
import sys
from pathlib import Path

import yaml

source, destination, output_root = map(Path, sys.argv[1:])
config = yaml.safe_load(source.read_text(encoding="utf-8"))
config["training"].update(
    {
        "run_name": f"{config['training']['run_name']}_smoke",
        "output_root": str(output_root),
        "max_steps": 1,
        "save_steps": 1,
        "eval_steps": 1,
        "save_total_limit": 2,
        "logging_steps": 1,
    }
)
destination.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
test -s "${SMOKE_CONFIG}"

PYTHONPATH="${REPO_ROOT}/src" conda run --name xfer-relearn python scripts/train_clm.py --config "${SMOKE_CONFIG}"
run_dir=$(find "${SMOKE_TRAIN_ROOT}" -mindepth 1 -maxdepth 1 -type d | sort)
test -n "${run_dir}"
test "$(printf '%s\n' "${run_dir}" | wc -l)" -eq 1

# Reopen the completed technical smoke manifest only to exercise the actual resume validator.
"${python_bin}" - "${run_dir}" <<'PY'
import json
import math
import sys
from pathlib import Path

run = Path(sys.argv[1])
manifest_path = run / "training_manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
assert manifest["status"] == "complete"
assert manifest["result"]["estimated_optimizer_steps"] == 1
checkpoint = run / "checkpoints/checkpoint-1"
for name in ("optimizer.pt", "scheduler.pt", "trainer_state.json"):
    assert (checkpoint / name).is_file(), name
for metric_path, key in ((run / "train_metrics.json", "train_loss"), (run / "eval_metrics.json", "eval_loss")):
    metrics = json.loads(metric_path.read_text(encoding="utf-8"))
    assert math.isfinite(float(metrics[key])), (metric_path, metrics)
manifest["status"] = "started"
manifest["smoke_resume_rehearsal"] = True
manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

PYTHONPATH="${REPO_ROOT}/src" conda run --name xfer-relearn python scripts/train_clm.py \
  --config "${SMOKE_CONFIG}" --resume-run-dir "${run_dir}"

"${python_bin}" - "${run_dir}" "${SMOKE_ARM_ROOT}/smoke_report.json" <<'PY'
import json
import sys
from pathlib import Path

run, report_path = map(Path, sys.argv[1:])
manifest = json.loads((run / "training_manifest.json").read_text(encoding="utf-8"))
assert manifest["status"] == "complete"
events = manifest.get("resume_events", [])
assert len(events) == 1
assert events[0]["checkpoint"].endswith("checkpoint-1")
report = {
    "status": "passed",
    "scientific_result": False,
    "label": manifest["config"]["training"]["run_name"],
    "run_dir": str(run),
    "optimizer_steps": 1,
    "resume_checkpoint": events[0]["checkpoint"],
    "gpu": manifest["result"]["software"]["gpu_name"],
}
report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(report, sort_keys=True))
PY
