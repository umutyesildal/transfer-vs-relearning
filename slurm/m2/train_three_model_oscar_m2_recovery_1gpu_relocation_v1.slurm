#!/usr/bin/env bash
#SBATCH --job-name=m2-oscar-scientific-1gpu-v1
#SBATCH --account=yesildau
#SBATCH --partition=gpu
#SBATCH --nodelist=gruenau10
#SBATCH --gres=gpu:a10080gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --array=0-5%1
#SBATCH --output=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_1gpu_relocation_v1/logs/%x-%A_%a.out
#SBATCH --error=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_1gpu_relocation_v1/logs/%x-%A_%a.err
set -euo pipefail
: "${EXPECTED_COMMIT:?}" "${TRAINING_CONFIG:?}" "${SLURM_ARRAY_TASK_ID:?}"
cd "${SLURM_SUBMIT_DIR:?}"
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
root=/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_1gpu_relocation_v1
python_bin=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
test "$($python_bin -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$root/control/preflight_result.json")" = M2_SCIENTIFIC_TRAINING_PREFLIGHT_PASS
mapfile -t fields < <("$python_bin" - "$root/configs/config_manifest.json" "$SLURM_ARRAY_TASK_ID" <<'PY'
import json,sys
rows=sorted(json.load(open(sys.argv[1]))["entries"],key=lambda r:(r["role"],r["arm"]))
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
selector_audit="$root/control/gpu_selection_task_${SLURM_ARRAY_TASK_ID}.json"
task_audit="$root/control/training_task_${SLURM_ARRAY_TASK_ID}.json"
mkdir -p "$task_tmp" "$root/cache"
selected_gpu=""; completed=0
record() {
  "$python_bin" scripts/m2/record_m2_training_task_audit_v1.py --output "$task_audit" --status "$1" --role "$role" --arm "$arm" --config "$config" --training-output-root "$output_root" --selector-audit "$selector_audit" --selected-gpu "$selected_gpu" --exit-code "$2" --job-id "${SLURM_JOB_ID:?}" --array-job-id "${SLURM_ARRAY_JOB_ID:?}" --array-task-id "$SLURM_ARRAY_TASK_ID"
}
on_exit() { code=$?; if test "$completed" -eq 0; then set +e; record TRAINING_TASK_FAIL "$code"; fi; exit "$code"; }
trap on_exit EXIT
record TRAINING_TASK_LAUNCH 0
selected_gpu="$($python_bin scripts/m2/select_allocated_gpu_for_m2_training_recovery_v1.py --output "$selector_audit" --minimum-free-mib 61440 --maximum-used-mib 20480 --expected-device-count 1)"
test -n "$selected_gpu"
record TRAINING_TASK_LAUNCH 0
export CUDA_VISIBLE_DEVICES="$selected_gpu" HF_HOME="$root/cache" TRANSFORMERS_CACHE="$root/cache" XDG_CACHE_HOME="$root/cache" TORCH_HOME="$root/cache" TMPDIR="$task_tmp" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src:$PWD"
conda run --no-capture-output --name xfer-relearn python scripts/training/train_clm.py --config "$config"
record TRAINING_TASK_PASS 0
completed=1
