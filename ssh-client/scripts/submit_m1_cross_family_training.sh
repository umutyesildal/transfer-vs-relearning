#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
SCRATCH_ROOT=/vol/tmp2/yesildau/m1_cross_family_screen_v1
for manifest in \
  "$SCRATCH_ROOT/models/Qwen__Qwen2.5-1.5B/model_manifest.json" \
  "$SCRATCH_ROOT/models/stabilityai__stablelm-2-1_6b/model_manifest.json" \
  "$SCRATCH_ROOT/models/google__gemma-2-2b/model_manifest.json"; do
  test -s "$manifest" || { echo "Required model manifest missing: $manifest" >&2; exit 1; }
done
indices=0,1,2
if test -s "$SCRATCH_ROOT/models/meta-llama__Llama-3.2-1B/model_manifest.json"; then
  indices=0,1,2,3
fi
preflight_indices="${indices//,/:}"
mkdir -p "$SCRATCH_ROOT/logs"
preflight_id=$(sbatch --parsable \
  --export=ALL,PREFLIGHT_STAGE=training,CANDIDATE_INDICES="$preflight_indices",TARGET_LAUNCHER="$PWD/slurm/train_m1_cross_family.slurm" \
  slurm/preflight_m1_cross_family.slurm)
training_id=$(sbatch --parsable \
  --dependency="afterok:$preflight_id" \
  --array="$indices" \
  slurm/train_m1_cross_family.slurm)
echo "__CANDIDATE_INDICES__=$indices"
echo "__PREFLIGHT_JOB_ID__=$preflight_id"
echo "__TRAINING_ARRAY_JOB_ID__=$training_id"
squeue -h -j "$preflight_id,$training_id" -o "%i %T %M %L %R %j"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
