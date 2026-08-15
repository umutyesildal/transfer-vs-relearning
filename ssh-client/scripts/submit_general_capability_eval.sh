#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
remote_cmd=$(cat <<'EOF'
set -euo pipefail
REPO=/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
SCRATCH=/vol/tmp2/yesildau/general_capability_v1
CONFIG_DIR="$SCRATCH/configs"
LOG_DIR="$SCRATCH/logs"
mkdir -p "$CONFIG_DIR" "$LOG_DIR" "$SCRATCH/runs"
cd "$REPO"

git pull --ff-only origin corpus-update
"$PYTHON" -m pytest -q tests/test_general_capability.py

"$PYTHON" - <<'PY'
import csv
import json
from pathlib import Path

import yaml

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
scratch = Path('/vol/tmp2/yesildau/general_capability_v1')
corpus = scratch / 'wikitext2_raw_test.jsonl'
subjects_file = repo / 'artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv'
if not corpus.is_file():
    raise SystemExit(f'Missing frozen corpus: {corpus}')
if not subjects_file.is_file():
    raise SystemExit(f'Missing synthetic subjects: {subjects_file}')

corpus_text = '\n'.join(
    json.loads(line)['text'] for line in corpus.read_text(encoding='utf-8').splitlines() if line.strip()
).casefold()
with subjects_file.open(encoding='utf-8', newline='') as handle:
    subjects = [row['subject'] for row in csv.DictReader(handle)]
matches = [subject for subject in subjects if subject.casefold() in corpus_text]
if matches:
    raise SystemExit(f'Generic corpus contains synthetic full names: {matches[:10]}')

base = yaml.safe_load((repo / 'configs/general_capability/base_smollm2_1_7b.yaml').read_text(encoding='utf-8'))
models = {
    'base': repo / 'artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json',
    'seed42': Path('/vol/tmp/yesildau/transfer-vs-relearning/artifacts/models/m1_relation_v2_1_7b_500_frozen/seed42_checkpoint200/model_manifest.json'),
    'seed43': Path('/vol/tmp/yesildau/transfer-vs-relearning/artifacts/models/m1_relation_v2_1_7b_500_frozen/seed43_checkpoint75/model_manifest.json'),
}
for label, model_manifest in models.items():
    if not model_manifest.is_file():
        raise SystemExit(f'Missing model manifest for {label}: {model_manifest}')
    config = json.loads(json.dumps(base))
    config['run_name'] = f'{label}_general_capability_v1'
    config['output_root'] = str(scratch / 'runs' / label)
    config['model_manifest'] = str(model_manifest)
    config['data']['corpus_file'] = str(corpus)
    path = scratch / 'configs' / f'{label}.yaml'
    path.write_text(yaml.safe_dump(config, sort_keys=True), encoding='utf-8')
    print(f'CONFIG {label} {path}')
print(f'SYNTHETIC_FULL_NAME_MATCHES={len(matches)}')
PY

for label in base seed42 seed43; do
  CONFIG="$CONFIG_DIR/$label.yaml"
  JOB_ID=$(sbatch --parsable \
    --nodelist=gruenau9 \
    --job-name="gen-cap-$label" \
    --output="$LOG_DIR/%x-%j.out" \
    --error="$LOG_DIR/%x-%j.err" \
    --export=ALL,EVAL_CONFIG="$CONFIG",PYTHONDONTWRITEBYTECODE=1 \
    slurm/eval_m1_general_capability.slurm)
  echo "__JOB_ID_${label}__=$JOB_ID"
done
squeue -h -u yesildau -n gen-cap-base,gen-cap-seed42,gen-cap-seed43 -o '%i %T %M %L %R %j'
EOF
)
quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
