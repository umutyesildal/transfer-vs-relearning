#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
ROOT=/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1
mkdir -p "$ROOT/logs"
if test -f "$ROOT/checkpoint_registry.csv" && test -f "$ROOT/wave_manifest.json"; then
  prepare_id=ALREADY_COMPLETE
  preflight_id=$(sbatch --parsable slurm/m1/preflight_m1_qwen_checkpoint_pareto.slurm)
else
  prepare_id=$(sbatch --parsable slurm/m1/prepare_m1_qwen_checkpoint_pareto.slurm)
  preflight_id=$(sbatch --parsable --dependency="afterok:$prepare_id" slurm/m1/preflight_m1_qwen_checkpoint_pareto.slurm)
fi
evaluation_id=$(sbatch --parsable --dependency="afterok:$preflight_id" --array="0-10%3" --exclude=gruenau10 slurm/m1/eval_m1_qwen_checkpoint_pareto.slurm)
echo "__PREPARATION_JOB_ID__=$prepare_id"
echo "__PREFLIGHT_JOB_ID__=$preflight_id"
echo "__EVALUATION_ARRAY_JOB_ID__=$evaluation_id"
squeue -h -j "$preflight_id,$evaluation_id" -o "%i %T %M %L %R %j"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
