#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
git pull --ff-only origin corpus-update

PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
"$PYTHON" -m pytest -vv tests/test_training_core.py tests/test_training_answer_only.py tests/test_data_core.py

"$PYTHON" - <<'PY'
from pathlib import Path
import json

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
root = repo / 'artifacts/datasets/relation_v2_gate_v1'
scale = json.loads((root / 'acquisition_100_subjects_direct/summary.json').read_text())
pilot = json.loads((root / 'acquisition_10_subjects_direct/pilot.json').read_text())
if (scale['subjects'], scale['facts'], scale['train_rows'], scale['validation_rows']) != (100, 500, 3500, 500):
    raise SystemExit(f'Unexpected 500-fact summary: {scale}')
if not set(pilot['selected_subject_ids']).issubset(scale['selected_subject_ids']):
    raise SystemExit('The 10-subject gate is not nested in the 100-subject scale set')
train = root / 'acquisition_100_subjects_direct/train.jsonl'
validation = root / 'acquisition_100_subjects_direct/validation.jsonl'
if sum(1 for line in train.open() if line.strip()) != 3500:
    raise SystemExit('Expected exactly 3,500 training rows')
if sum(1 for line in validation.open() if line.strip()) != 500:
    raise SystemExit('Expected exactly 500 validation rows')
print('subjects=100 facts=500 train_rows=3500 validation_rows=500 nested=passed')
PY

sha256sum \
  artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/train.jsonl \
  artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/validation.jsonl \
  artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv

CONFIG=configs/training/m1_smollm2_360m_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36.yaml
JOB_ID=$(sbatch --parsable \
  --job-name=m1-v2-500 \
  --export=ALL,TRAIN_CONFIG="$CONFIG" \
  slurm/train_m1_gpt2_english_facts.slurm)
echo "__JOB_ID__=$JOB_ID"
squeue -h -j "$JOB_ID" -o "%i %T %M %L %R %j"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
