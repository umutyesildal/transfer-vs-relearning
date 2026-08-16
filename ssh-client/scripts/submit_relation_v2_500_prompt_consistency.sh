#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
git pull --ff-only origin corpus-update
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
CONFIG=configs/training/m1_smollm2_360m_relation_v2_500_prompt_consistency_cp250_lr5e-6_ep3.yaml
"$PYTHON" -m pytest -q tests/test_training_ranking.py tests/test_training_core.py
"$PYTHON" - <<'PY'
from collections import Counter
from pathlib import Path
import json
import yaml
from transfer_vs_relearning.training.clm import estimate_optimizer_steps
from transfer_vs_relearning.training.ranking import build_ranking_examples

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
config = yaml.safe_load((repo / 'configs/training/m1_smollm2_360m_relation_v2_500_prompt_consistency_cp250_lr5e-6_ep3.yaml').read_text())
manifest = json.loads((repo / config['model']['base_model_manifest']).read_text())
if not Path(manifest['local_path_absolute']).is_dir():
    raise SystemExit('Canonical checkpoint-250 model is missing')
dataset = config['dataset']
examples = build_ranking_examples(
    dataset_dir=repo / dataset['dataset_dir'], training_jsonl=repo / dataset['training_jsonl'],
    include_direct_probes=False, include_qa_train=False, include_training_jsonl_prompts=False,
    include_prompt_consistency_groups=True, negatives_per_example=15, seed=42,
)
groups = {}
for example in examples:
    groups.setdefault(example.fact_id, []).append(example)
if len(examples) != 3000 or len(groups) != 500 or any(len(group) != 6 for group in groups.values()):
    raise SystemExit('Expected 3,000 examples in 500 six-prompt groups')
if any(len({tuple(example.candidates) for example in group}) != 1 for group in groups.values()):
    raise SystemExit('Candidates differ within a prompt-consistency group')
relation_counts = Counter(group[0].relation for group in groups.values())
if set(relation_counts.values()) != {100}:
    raise SystemExit(f'Unbalanced relation groups: {relation_counts}')
steps = estimate_optimizer_steps(train_blocks=500, per_device_train_batch_size=2, gradient_accumulation_steps=5, num_train_epochs=3.0, world_size=1)
if steps != 150:
    raise SystemExit(f'Expected 150 optimizer updates, found {steps}')
print(f'base_model={manifest["local_path_absolute"]}')
print(f'examples={len(examples)} groups={len(groups)} updates={steps}')
PY
JOB_ID=$(sbatch --parsable --job-name=m1-v2-consistency --export=ALL,TRAIN_CONFIG="$CONFIG" slurm/m1/train_m1_ranking.slurm)
echo "__JOB_ID__=$JOB_ID"
squeue -h -j "$JOB_ID" -o "%i %T %M %L %R %j"
EOF
)
quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
