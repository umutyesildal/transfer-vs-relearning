#!/usr/bin/env bash
#SBATCH --job-name=m2-opt-smoke-corrected
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --array=0-2%1
#SBATCH --output=/vol/tmp2/yesildau/vnd_m2_oscar_optimizer_smoke_corrected_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/vnd_m2_oscar_optimizer_smoke_corrected_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${CONFIG_MANIFEST:?}"
: "${BLOCK_FAMILY_MANIFEST:?}"
: "${BLOCK_FAMILY_MANIFEST_SHA256:?}"
: "${EXPECTED_COMMIT:?}"
: "${SMOKE_ROOT:?}"
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
print(r["role"]); print(r["config"]); print(r["config_sha256"])
PY
)
role="${fields[0]}"
source_config="${fields[1]}"
expected_config_sha="${fields[2]}"
test "$(sha256sum "$source_config" | cut -d' ' -f1)" = "$expected_config_sha"
role_root="${SMOKE_ROOT}/roles/${role}"
test ! -e "$role_root"
mkdir -p "$role_root" "${SMOKE_ROOT}/cache" "${SMOKE_ROOT}/tmp"
failure_audit="${role_root}/failure_audit.json"
trap 'code=$?; if [ "$code" -ne 0 ]; then printf "{\"schema_version\":1,\"status\":\"OPTIMIZER_SMOKE_BLOCKED\",\"role\":\"%s\",\"exit_code\":%s,\"scientific_training\":false,\"ready_to_train\":false}\n" "$role" "$code" > "${failure_audit}.tmp"; mv "${failure_audit}.tmp" "$failure_audit"; fi' EXIT
allocated_gpu="${CUDA_VISIBLE_DEVICES:-${SLURM_JOB_GPUS:-}}"
test -n "$allocated_gpu"
test -z "$(nvidia-smi --id="$allocated_gpu" --query-compute-apps=pid --format=csv,noheader,nounits | sed '/^[[:space:]]*$/d')"
free_mib="$(nvidia-smi --id="$allocated_gpu" --query-gpu=memory.free --format=csv,noheader,nounits | tr -d ' ')"
test "$free_mib" -ge 61440
nvidia-smi --id="$allocated_gpu" --query-gpu=index,uuid,name,memory.total,memory.free,memory.used --format=csv,noheader,nounits > "${role_root}/gpu_before.csv"
export HF_HOME="${SMOKE_ROOT}/cache" TRANSFORMERS_CACHE="${SMOKE_ROOT}/cache"
export XDG_CACHE_HOME="${SMOKE_ROOT}/cache" TORCH_HOME="${SMOKE_ROOT}/cache"
export TMPDIR="${SMOKE_ROOT}/tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PYTHONPATH="$PWD/src" conda run --no-capture-output --name xfer-relearn \
  python scripts/m2/smoke_three_model_oscar_m2_optimizer.py \
  --config "$source_config" \
  --block-family-manifest "$BLOCK_FAMILY_MANIFEST" \
  --expected-block-family-manifest-sha256 "$BLOCK_FAMILY_MANIFEST_SHA256" \
  --output "${role_root}/smoke_report.json"
test "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "${role_root}/smoke_report.json")" = OPTIMIZER_SMOKE_PASS
