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
scale_100 = json.loads((root / 'acquisition_100_subjects_direct/summary.json').read_text())
scale_500 = json.loads((root / 'acquisition_500_subjects_direct/summary.json').read_text())
if (scale_500['subjects'], scale_500['facts'], scale_500['train_rows'], scale_500['validation_rows']) != (500, 2500, 17500, 2500):
    raise SystemExit(f'Unexpected 2,500-fact summary: {scale_500}')
if not set(scale_100['selected_subject_ids']).issubset(scale_500['selected_subject_ids']):
    raise SystemExit('The 100-subject set is not nested in the 500-subject scale set')
train = root / 'acquisition_500_subjects_direct/train.jsonl'
validation = root / 'acquisition_500_subjects_direct/validation.jsonl'
if sum(1 for line in train.open() if line.strip()) != 17500:
    raise SystemExit('Expected exactly 17,500 training rows')
if sum(1 for line in validation.open() if line.strip()) != 2500:
    raise SystemExit('Expected exactly 2,500 validation rows')
print('subjects=500 facts=2500 train_rows=17500 validation_rows=2500 nested=passed exploratory=true')
PY

sha256sum \
  artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/train.jsonl \
  artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/validation.jsonl \
  artifacts/datasets/relation_v2_gate_v1/acquisition_500_subjects_direct/exact_prefix_probes_en.csv

CONFIG=configs/training/m1_smollm2_360m_relation_v2_500_subjects_2500_facts_direct_lr1e-4_ep36.yaml
JOB_ID=$(sbatch --parsable \
  --job-name=m1-v2-2500 \
  --export=ALL,TRAIN_CONFIG="$CONFIG" \
  slurm/m1/train_m1_gpt2_english_facts.slurm)
echo "__JOB_ID__=$JOB_ID"
squeue -h -j "$JOB_ID" -o "%i %T %M %L %R %j"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
