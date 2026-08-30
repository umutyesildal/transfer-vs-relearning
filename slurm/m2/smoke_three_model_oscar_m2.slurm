#!/usr/bin/env bash
#SBATCH --job-name=m2-oscar-3model-smoke
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --array=0-2%1
#SBATCH --output=/vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${CONFIG_MANIFEST:?}"
: "${EXPECTED_COMMIT:?}"
: "${SLURM_ARRAY_TASK_ID:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
module load anaconda/3-2024.06
python_bin=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
mapfile -t fields < <("$python_bin" - "$CONFIG_MANIFEST" "$SLURM_ARRAY_TASK_ID" <<'PY'
import json, sys
from pathlib import Path
rows=json.loads(Path(sys.argv[1]).read_text())["entries"]
rows=sorted((r for r in rows if r["arm"] == "M2-A"), key=lambda r:r["role"])
r=rows[int(sys.argv[2])]
print(r["role"]); print(r["config"])
PY
)
role="${fields[0]}"
source_config="${fields[1]}"
root=/vol/tmp2/yesildau/vngrs_m2_oscar_training_family_v1
smoke_root="${root}/smoke/${role}"
test ! -e "$smoke_root"
task_tmp="${root}/tmp/smoke_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$smoke_root" "${root}/cache" "$task_tmp" "${root}/logs"
allocated_gpu="${CUDA_VISIBLE_DEVICES:-${SLURM_JOB_GPUS:-}}"
test -n "$allocated_gpu"
test -z "$(nvidia-smi --id="$allocated_gpu" --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')"
free_mib="$(nvidia-smi --id="$allocated_gpu" --query-gpu=memory.free --format=csv,noheader,nounits | tr -d ' ')"
test "$free_mib" -ge 61440
smoke_config="${smoke_root}/config.yaml"
"$python_bin" - "$source_config" "$smoke_config" "$smoke_root" <<'PY'
import sys, yaml
from pathlib import Path
source,destination,root=map(Path,sys.argv[1:])
c=yaml.safe_load(source.read_text())
c["training"].update({"run_name":c["training"]["run_name"]+"_optimizer_smoke","output_root":str(root/"run"),"max_steps":1,"checkpoint_updates":[1],"in_training_eval_updates":[1],"save_total_limit":1,"logging_steps":1})
destination.write_text(yaml.safe_dump(c,sort_keys=False,allow_unicode=True))
PY
export HF_HOME="${root}/cache" TRANSFORMERS_CACHE="${root}/cache" XDG_CACHE_HOME="${root}/cache"
export TORCH_HOME="${root}/cache" TMPDIR="$task_tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PYTHONPATH="$PWD/src" conda run --name xfer-relearn python scripts/training/train_clm.py --config "$smoke_config"
run_dir="$(find "${smoke_root}/run" -mindepth 1 -maxdepth 1 -type d)"
test -f "${run_dir}/checkpoints/checkpoint-1/optimizer.pt"
test -f "${run_dir}/train_metrics.json"
printf '{"status":"OPTIMIZER_SMOKE_PASS","role":"%s","scientific_training":false}\n' "$role" > "${smoke_root}/smoke_report.json"
