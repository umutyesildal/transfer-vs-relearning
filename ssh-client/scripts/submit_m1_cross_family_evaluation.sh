#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
SCRATCH_ROOT=/vol/tmp2/yesildau/m1_cross_family_screen_v1
indices=$($PYTHON - <<'PY'
import json
from pathlib import Path

root = Path('/vol/tmp2/yesildau/m1_cross_family_screen_v1/training')
labels = [('qwen', 0, True), ('stablelm', 1, True), ('gemma', 2, True), ('llama', 3, False)]
ready = []
for label, index, required in labels:
    complete = []
    for manifest in (root / label).glob('*/training_manifest.json'):
        payload = json.loads(manifest.read_text(encoding='utf-8'))
        if payload.get('status') == 'complete' and (manifest.parent / 'final_model').is_dir():
            complete.append(manifest)
    if len(complete) == 1:
        ready.append(index)
    elif required:
        raise SystemExit(f'Required candidate {label} has {len(complete)} completed endpoints')
print(','.join(str(index) for index in ready))
PY
)
test -n "$indices"
preflight_indices="${indices//,/:}"
mkdir -p "$SCRATCH_ROOT/logs"
preflight_id=$(sbatch --parsable \
  --export=ALL,PREFLIGHT_STAGE=evaluation,CANDIDATE_INDICES="$preflight_indices",TARGET_LAUNCHER="$PWD/slurm/m1/eval_m1_cross_family.slurm" \
  slurm/m1/preflight_m1_cross_family.slurm)
evaluation_id=$(sbatch --parsable \
  --dependency="afterok:$preflight_id" \
  --array="$indices" \
  slurm/m1/eval_m1_cross_family.slurm)
echo "__CANDIDATE_INDICES__=$indices"
echo "__PREFLIGHT_JOB_ID__=$preflight_id"
echo "__EVALUATION_ARRAY_JOB_ID__=$evaluation_id"
squeue -h -j "$preflight_id,$evaluation_id" -o "%i %T %M %L %R %j"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
