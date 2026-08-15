#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKPOINT_CSV="${1:-25,50,75}"
if [[ ! "$CHECKPOINT_CSV" =~ ^[0-9]+(,[0-9]+)*$ ]]; then
  echo "Checkpoint list must be comma-separated integers" >&2
  exit 2
fi

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning

/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python - <<'PY'
import csv
import json
import os
from pathlib import Path

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
root = repo / 'runs/evaluation'
prefix = 'm1_acquisition_500_facts_direct_'


def latest_rows(run_root):
    paths = sorted(run_root.glob('*/per_fact_results.csv'))
    if not paths:
        return None, []
    with paths[-1].open(encoding='utf-8', newline='') as handle:
        return paths[-1], list(csv.DictReader(handle))


def top1_ids(rows):
    return {row['fact_id'] for row in rows if int(row['correct_rank_mean']) == 1}


checkpoints = tuple(
    f'checkpoint-{value}'
    for value in os.environ['ACQUISITION_EVAL_CHECKPOINTS'].split(',')
)
results = []
for checkpoint in checkpoints:
    rows_by_view = {}
    paths = {}
    for view in ('exact_prefix', 'direct', 'qa_matched'):
        path, rows = latest_rows(root / f'{prefix}{checkpoint}_{view}')
        paths[view] = str(path.relative_to(repo)) if path else None
        rows_by_view[view] = rows
    if not all(rows_by_view.values()):
        results.append({'checkpoint': checkpoint, 'status': 'incomplete', 'paths': paths})
        continue
    ids = {view: top1_ids(rows) for view, rows in rows_by_view.items()}
    relations = sorted({row['relation'] for row in rows_by_view['direct']})
    by_relation = {}
    for relation in relations:
        relation_ids = {
            view: top1_ids([row for row in rows if row['relation'] == relation])
            for view, rows in rows_by_view.items()
        }
        by_relation[relation] = {
            'exact_prefix': len(relation_ids['exact_prefix']),
            'direct': len(relation_ids['direct']),
            'qa': len(relation_ids['qa_matched']),
            'overlap': len(relation_ids['direct'] & relation_ids['qa_matched']),
        }
    item = {
        'checkpoint': checkpoint,
        'status': 'complete',
        'exact_prefix_top1': len(ids['exact_prefix']),
        'direct_top1': len(ids['direct']),
        'qa_top1': len(ids['qa_matched']),
        'direct_qa_overlap': len(ids['direct'] & ids['qa_matched']),
        'mean_ranks': {
            view: sum(int(row['correct_rank_mean']) for row in rows) / len(rows)
            for view, rows in rows_by_view.items()
        },
        'by_relation': by_relation,
        'paths': paths,
    }
    item['passes_gate'] = (
        item['exact_prefix_top1'] >= 450
        and item['direct_top1'] >= 400
        and item['qa_top1'] >= 400
        and item['direct_qa_overlap'] >= 350
    )
    results.append(item)

passing = [item for item in results if item.get('passes_gate')]
print(json.dumps({'results': results, 'earliest_passing_checkpoint': passing[0]['checkpoint'] if passing else None}, indent=2))
PY
EOF
)

remote_cmd="export ACQUISITION_EVAL_CHECKPOINTS=$(printf '%q' "$CHECKPOINT_CSV")"$'\n'"$remote_cmd"

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
