#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
git pull --ff-only origin corpus-update

PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
CONFIG=configs/training/m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36_seed43_data43.yaml
SCRATCH=/vol/tmp2/yesildau/m1_relation_v2_1_7b_500_seed43_data43
mkdir -p "$SCRATCH/logs" "$SCRATCH/cache"

"$PYTHON" -m pytest -q tests/test_training_core.py
"$PYTHON" - <<'PY'
from pathlib import Path
import json
import yaml

from transfer_vs_relearning.training.clm import estimate_optimizer_steps
from transfer_vs_relearning.utils.io import read_jsonl

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
config_path = repo / 'configs/training/m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36_seed43_data43.yaml'
config = yaml.safe_load(config_path.read_text())
manifest_path = repo / config['model']['base_model_manifest']
manifest = json.loads(manifest_path.read_text())
model_path = Path(manifest['local_path_absolute'])
if not model_path.is_dir():
    raise SystemExit(f'Missing 1.7B model snapshot: {model_path}')

rows = read_jsonl(repo / config['dataset']['train_file'])
facts = {row['fact_id'] for row in rows}
if len(rows) != 3500 or len(facts) != 500:
    raise SystemExit('Expected 3,500 rows over 500 facts')
if any(sum(row['fact_id'] == fact_id for row in rows) != 7 for fact_id in facts):
    raise SystemExit('Expected exactly seven rows per fact')

training = config['training']
effective_batch = training['per_device_train_batch_size'] * training['gradient_accumulation_steps']
steps = estimate_optimizer_steps(
    len(rows),
    training['per_device_train_batch_size'],
    training['gradient_accumulation_steps'],
    training['num_train_epochs'],
)
if effective_batch != 500 or steps != 252:
    raise SystemExit(f'Budget mismatch: effective_batch={effective_batch}, steps={steps}')
if config['dataset']['split_seed'] != 42 or training['seed'] != 43 or training['data_seed'] != 43:
    raise SystemExit('Replication must preserve split seed 42 and use training/data seed 43')
print(f'model={model_path}')
print(f'rows={len(rows)} facts={len(facts)} effective_batch={effective_batch} updates={steps}')
print(
    f'split_seed={config["dataset"]["split_seed"]} '
    f'training_seed={training["seed"]} data_seed={training["data_seed"]}'
)
PY

JOB_ID=$(sbatch --parsable \
  --nodelist=gruenau9 \
  --job-name=m1-v2-1p7b-s43 \
  --output="$SCRATCH/logs/%x-%j.out" \
  --error="$SCRATCH/logs/%x-%j.err" \
  --export=ALL,TRAIN_CONFIG="$CONFIG",HF_HOME="$SCRATCH/cache",XDG_CACHE_HOME="$SCRATCH/cache",PYTHONDONTWRITEBYTECODE=1 \
  slurm/m1/train_m1_gpt2_english_facts.slurm)
echo "__JOB_ID__=$JOB_ID"
squeue -h -j "$JOB_ID" -o "%i %T %M %L %R %j"
EOF
)
quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
