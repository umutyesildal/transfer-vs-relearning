#!/usr/bin/env bash
#SBATCH --job-name=m2-oscar-scientific-train-v1
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --array=0-5%3
#SBATCH --output=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${EXPECTED_COMMIT:?}"
: "${TRAINING_CONFIG:?}"
: "${SLURM_ARRAY_TASK_ID:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
root=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_v1
preflight="$root/control/preflight_result.json"
python_bin=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
test "$($python_bin -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$preflight")" = M2_SCIENTIFIC_TRAINING_PREFLIGHT_PASS
manifest="$root/configs/config_manifest.json"
mapfile -t fields < <("$python_bin" - "$manifest" "$SLURM_ARRAY_TASK_ID" <<'PY'
import json, sys
from pathlib import Path
rows=sorted(json.loads(Path(sys.argv[1]).read_text())["entries"], key=lambda r:(r["role"],r["arm"]))
r=rows[int(sys.argv[2])]
print(r["role"]); print(r["arm"]); print(r["config"]); print(r["output_root"])
PY
)
role="${fields[0]}"; arm="${fields[1]}"; config="${fields[2]}"; output_root="${fields[3]}"
test ! -e "$output_root"
smoke=/vol/tmp2/yesildau/vnd_m2_oscar_optimizer_smoke_corrected_v1/roles/$role/smoke_report.json
test "$($python_bin -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["status"],d["role"],d["scientific_training"],d["checkpoint_written"])' "$smoke")" = "OPTIMIZER_SMOKE_PASS $role False False"
module load anaconda/3-2024.06
task_tmp="$root/tmp/train_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$task_tmp" "$root/cache"
allocated_gpu="${CUDA_VISIBLE_DEVICES:-${SLURM_JOB_GPUS:-}}"
test -n "$allocated_gpu"
test -z "$(nvidia-smi --id="$allocated_gpu" --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')"
free_mib="$(nvidia-smi --id="$allocated_gpu" --query-gpu=memory.free --format=csv,noheader,nounits | tr -d ' ')"
test "$free_mib" -ge 61440
export HF_HOME="$root/cache" TRANSFORMERS_CACHE="$root/cache" XDG_CACHE_HOME="$root/cache"
export TORCH_HOME="$root/cache" TMPDIR="$task_tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src:$PWD"
printf 'role=%s\narm=%s\nconfig=%s\noutput_root=%s\n' "$role" "$arm" "$config" "$output_root"
conda run --no-capture-output --name xfer-relearn python scripts/training/train_clm.py --config "$config"
