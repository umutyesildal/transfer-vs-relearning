#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
git pull --ff-only origin corpus-update

PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
CONFIG=configs/training/m1_smollm2_360m_relation_v2_500_relation_conditioned_cp250_lr5e-6_ep1.yaml
"$PYTHON" -m pytest -q tests/test_training_ranking.py tests/test_training_core.py

"$PYTHON" - <<'PY'
from collections import Counter
from pathlib import Path
import json
import subprocess
import yaml

from transfer_vs_relearning.training.ranking import build_ranking_examples

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
config = yaml.safe_load((repo / 'configs/training/m1_smollm2_360m_relation_v2_500_relation_conditioned_cp250_lr5e-6_ep1.yaml').read_text())
canonical_run = repo / (
    'runs/training/m1_smollm2_360m_relation_v2_100_subjects_500_facts_direct/'
    '20260712T082510Z_m1_smollm2_360m_relation_v2_100_subjects_500_facts_'
    'direct_lr1e-4_ep36_dc3cef7f'
)
checkpoint = canonical_run / 'checkpoints/checkpoint-250'
if not checkpoint.is_dir():
    raise SystemExit(f'Missing canonical job 391918 checkpoint 250: {checkpoint}')

manifest_dir = repo / 'runs/local_model_manifests/m1_relation_v2_500_job391918'
manifest_dir.mkdir(parents=True, exist_ok=True)
manifest = manifest_dir / 'checkpoint-250_model_manifest.json'
subprocess.run(
    [
        str(Path('/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python')),
        'scripts/create_local_model_manifest.py',
        '--source-manifest', 'artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json',
        '--local-model-dir', str(checkpoint),
        '--output-manifest', str(manifest),
        '--model-id', 'm1_relation_v2_500_job391918/checkpoint-250',
        '--training-checkpoint', 'checkpoint-250',
        '--training-run-dir', str(canonical_run),
    ],
    check=True,
)
payload = json.loads(manifest.read_text())
if Path(payload['local_path_absolute']) != checkpoint:
    raise SystemExit('Canonical checkpoint manifest points to the wrong model')

dataset = config['dataset']
examples = build_ranking_examples(
    dataset_dir=repo / dataset['dataset_dir'],
    training_jsonl=repo / dataset['training_jsonl'],
    include_direct_probes=False,
    include_qa_train=False,
    include_training_jsonl_prompts=False,
    include_relation_conditioned_prompts=True,
    negatives_per_example=15,
    seed=42,
)
if len(examples) != 1500 or len({example.fact_id for example in examples}) != 500:
    raise SystemExit('Expected 1,500 examples over 500 facts')
if Counter(example.relation for example in examples) != {
    'profession': 300,
    'born_in': 300,
    'lives_in': 300,
    'field_of_study': 300,
    'works_in_industry': 300,
}:
    raise SystemExit('Relation-conditioned examples are not balanced')
if any(len(example.candidates) != 16 for example in examples):
    raise SystemExit('Each example must have sixteen candidates')
print(f'base_model={checkpoint}')
print(f'examples={len(examples)} facts={len({example.fact_id for example in examples})}')
PY

JOB_ID=$(sbatch --parsable \
  --job-name=m1-v2-relcond \
  --export=ALL,TRAIN_CONFIG="$CONFIG" \
  slurm/train_m1_ranking.slurm)
echo "__JOB_ID__=$JOB_ID"
squeue -h -j "$JOB_ID" -o "%i %T %M %L %R %j"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
