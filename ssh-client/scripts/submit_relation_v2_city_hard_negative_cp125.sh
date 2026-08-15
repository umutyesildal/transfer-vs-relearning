#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
git pull --ff-only origin corpus-update

PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
"$PYTHON" -m pytest -vv tests/test_training_ranking.py tests/test_training_core.py

CONFIG=configs/training/m1_smollm2_360m_relation_v2_city_hard_negative_cp125_lr5e-6_ep1.yaml
"$PYTHON" - <<'PY'
from collections import Counter
from pathlib import Path
import json
import yaml

from transfer_vs_relearning.training.ranking import build_ranking_examples

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
config = yaml.safe_load((repo / 'configs/training/m1_smollm2_360m_relation_v2_city_hard_negative_cp125_lr5e-6_ep1.yaml').read_text())
manifest_path = repo / config['model']['base_model_manifest']
if not manifest_path.is_file():
    raise SystemExit(f'Missing canonical checkpoint-125 manifest: {manifest_path}')
manifest = json.loads(manifest_path.read_text())
model_path = Path(manifest['local_path_absolute'])
if not model_path.is_dir():
    raise SystemExit(f'Missing canonical checkpoint-125 model: {model_path}')
dataset = config['dataset']
examples = build_ranking_examples(
    dataset_dir=repo / dataset['dataset_dir'],
    include_direct_probes=False,
    include_qa_train=False,
    negatives_per_example=dataset['negatives_per_example'],
    seed=config['training']['seed'],
    training_jsonl=repo / dataset['training_jsonl'],
    negative_strategy=dataset['negative_strategy'],
    relations=dataset['relations'],
)
if len(examples) != 140 or len({example.fact_id for example in examples}) != 20:
    raise SystemExit('Expected 140 examples over exactly 20 city facts')
if Counter(example.relation for example in examples) != {'born_in': 70, 'lives_in': 70}:
    raise SystemExit('City relation examples are not symmetric')
if any(len(example.negative_answers) != 1 for example in examples):
    raise SystemExit('Each city example must contain exactly one paired hard negative')
print(f'base_model={model_path}')
print(f'examples={len(examples)} facts={len({example.fact_id for example in examples})}')
PY

JOB_ID=$(sbatch --parsable \
  --job-name=m1-v2-city-rank \
  --export=ALL,TRAIN_CONFIG="$CONFIG" \
  slurm/train_m1_ranking.slurm)
echo "__JOB_ID__=$JOB_ID"
squeue -h -j "$JOB_ID" -o "%i %T %M %L %R %j"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
