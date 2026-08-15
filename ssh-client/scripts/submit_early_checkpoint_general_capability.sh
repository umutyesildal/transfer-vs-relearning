#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
remote_cmd=$(cat <<'EOF'
set -euo pipefail
REPO=/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
SCRATCH=/vol/tmp2/yesildau/general_capability_v1
TRAIN_RUN=/vol/tmp2/yesildau/m1_relation_v2_1_7b_500/runs/20260713T082249Z_m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36_1a413394
MANIFEST_DIR="$SCRATCH/early_checkpoint_manifests"
CONFIG_DIR="$SCRATCH/configs"
LOG_DIR="$SCRATCH/logs"
mkdir -p "$MANIFEST_DIR" "$CONFIG_DIR" "$LOG_DIR"
cd "$REPO"

for checkpoint in 50 75; do
  MODEL_DIR="$TRAIN_RUN/checkpoints/checkpoint-$checkpoint"
  MANIFEST="$MANIFEST_DIR/seed42_checkpoint${checkpoint}.json"
  "$PYTHON" scripts/create_local_model_manifest.py \
    --source-manifest artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json \
    --local-model-dir "$MODEL_DIR" \
    --output-manifest "$MANIFEST" \
    --model-id "m1_relation_v2_1_7b_500/seed42_checkpoint${checkpoint}" \
    --resolved-revision "seed42-checkpoint-$checkpoint" \
    --training-checkpoint "checkpoint-$checkpoint" \
    --training-run-dir "$TRAIN_RUN"
done

"$PYTHON" - <<'PY'
import json
from pathlib import Path
import yaml

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
scratch = Path('/vol/tmp2/yesildau/general_capability_v1')
base = yaml.safe_load((scratch / 'configs/base.yaml').read_text(encoding='utf-8'))
for checkpoint in (50, 75):
    label = f'seed42_checkpoint{checkpoint}'
    config = json.loads(json.dumps(base))
    config['run_name'] = f'{label}_general_capability_v1'
    config['output_root'] = str(scratch / 'runs' / label)
    config['model_manifest'] = str(scratch / 'early_checkpoint_manifests' / f'{label}.json')
    path = scratch / 'configs' / f'{label}.yaml'
    path.write_text(yaml.safe_dump(config, sort_keys=True), encoding='utf-8')
    print(f'CONFIG {label} {path}')
PY

for checkpoint in 50 75; do
  label="seed42_checkpoint$checkpoint"
  CONFIG="$CONFIG_DIR/$label.yaml"
  JOB_ID=$(sbatch --parsable \
    --nodelist=gruenau9 \
    --job-name="gen-cap-s42c$checkpoint" \
    --output="$LOG_DIR/%x-%j.out" \
    --error="$LOG_DIR/%x-%j.err" \
    --export=ALL,EVAL_CONFIG="$CONFIG",PYTHONDONTWRITEBYTECODE=1 \
    slurm/eval_m1_general_capability.slurm)
  echo "__JOB_ID_${label}__=$JOB_ID"
done
squeue -h -u yesildau -n gen-cap-s42c50,gen-cap-s42c75 -o '%i %T %M %L %R %j'
EOF
)
quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
