#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
git pull --ff-only origin corpus-update
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
CONFIG=configs/training/m1_smollm2_360m_relation_v2_500_relation_conditioned_cp250_lr2e-6_ep1.yaml
"$PYTHON" -m pytest -q tests/test_training_ranking.py tests/test_training_core.py
"$PYTHON" - <<'PY'
from pathlib import Path
import json
import yaml
from transfer_vs_relearning.training.ranking import build_ranking_examples

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
config = yaml.safe_load((repo / 'configs/training/m1_smollm2_360m_relation_v2_500_relation_conditioned_cp250_lr2e-6_ep1.yaml').read_text())
manifest = repo / config['model']['base_model_manifest']
payload = json.loads(manifest.read_text())
if not Path(payload['local_path_absolute']).is_dir():
    raise SystemExit('Canonical checkpoint-250 model is missing')
dataset = config['dataset']
examples = build_ranking_examples(
    dataset_dir=repo / dataset['dataset_dir'], training_jsonl=repo / dataset['training_jsonl'],
    include_direct_probes=False, include_qa_train=False, include_training_jsonl_prompts=False,
    include_relation_conditioned_prompts=True, negatives_per_example=15, seed=42,
)
if len(examples) != 1500 or len({example.fact_id for example in examples}) != 500:
    raise SystemExit('Unexpected relation-conditioned example contract')
print(f'base_model={payload["local_path_absolute"]}')
print(f'examples={len(examples)} facts={len({example.fact_id for example in examples})}')
PY
JOB_ID=$(sbatch --parsable --job-name=m1-v2-relcond-lr2 --export=ALL,TRAIN_CONFIG="$CONFIG" slurm/train_m1_ranking.slurm)
echo "__JOB_ID__=$JOB_ID"
squeue -h -j "$JOB_ID" -o "%i %T %M %L %R %j"
EOF
)
quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
