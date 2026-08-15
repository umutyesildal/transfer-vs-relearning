#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning

/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python - <<'PY'
import csv
import json
from pathlib import Path

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
root = repo / 'runs/evaluation'
prefix = 'm1_diagnostic_born_in_10_direct_'


def latest_rows(run_root):
    paths = sorted(run_root.glob('*/per_fact_results.csv'))
    if not paths:
        return None, []
    with paths[-1].open(encoding='utf-8', newline='') as handle:
        return paths[-1], list(csv.DictReader(handle))


def top1_ids(rows):
    return {row['fact_id'] for row in rows if int(row['correct_rank_mean']) == 1}


checkpoints = sorted(
    {path.name[len(prefix):].split('_', 1)[0] for path in root.glob(f'{prefix}checkpoint-*_*')},
    key=lambda value: int(value.split('-')[-1]),
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
        'paths': paths,
    }
    item['passes_gate'] = (
        item['exact_prefix_top1'] >= 9
        and item['direct_top1'] >= 8
        and item['qa_top1'] >= 8
        and item['direct_qa_overlap'] >= 7
    )
    results.append(item)

passing = [item for item in results if item.get('passes_gate')]
print(json.dumps({'results': results, 'earliest_passing_checkpoint': passing[0]['checkpoint'] if passing else None}, indent=2))
PY
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
