#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning

git pull --ff-only origin corpus-update

PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
"$PYTHON" -m pytest -q tests/test_training_ranking.py tests/test_acquisition_audit.py

CONFIG=configs/training/m1_smollm2_360m_acquisition_500_facts_ranking_continuation_lr5e-6_ep1.yaml
"$PYTHON" - <<'PY'
import json
from pathlib import Path
import yaml

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
config_path = repo / 'configs/training/m1_smollm2_360m_acquisition_500_facts_ranking_continuation_lr5e-6_ep1.yaml'
config = yaml.safe_load(config_path.read_text())
manifest = repo / config['model']['base_model_manifest']
if not manifest.is_file():
    raise SystemExit(f'Missing checkpoint-250 model manifest: {manifest}')
payload = json.loads(manifest.read_text())
model_path = Path(payload['local_path_absolute'])
if not model_path.is_dir():
    raise SystemExit(f'Missing checkpoint-250 model directory: {model_path}')
tokenizer_path = Path(payload.get('tokenizer_source_path_absolute') or payload.get('tokenizer_source_path') or model_path)
if not tokenizer_path.is_absolute():
    tokenizer_path = repo / tokenizer_path
tokenizer_files = [tokenizer_path / 'tokenizer.json', tokenizer_path / 'vocab.json']
if not any(path.is_file() for path in tokenizer_files):
    raise SystemExit(f'Missing tokenizer files under: {tokenizer_path}')
train_path = repo / config['dataset']['training_jsonl']
if sum(1 for line in train_path.open() if line.strip()) != 3500:
    raise SystemExit('Ranking continuation requires exactly 3500 training rows')
print(f'base_model={model_path}')
print(f'tokenizer={tokenizer_path}')
print(f'training_jsonl={train_path}')
PY

JOB_ID=$(sbatch --parsable \
  --job-name=m1-rank-cont \
  --export=ALL,TRAIN_CONFIG="$CONFIG" \
  slurm/m1/train_m1_ranking.slurm)

echo "__JOB_ID__=$JOB_ID"
echo "__QUEUE__"
squeue -h -j "$JOB_ID" -o "%i %T %M %L %R %j"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
