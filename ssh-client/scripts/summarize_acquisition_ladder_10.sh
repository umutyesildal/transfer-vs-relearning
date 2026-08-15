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
prefix = 'm1_acquisition_ladder_10_'


def latest_rows(run_root):
    paths = sorted(run_root.glob('*/per_fact_results.csv'))
    if not paths:
        return None, []
    with paths[-1].open(encoding='utf-8', newline='') as handle:
        return paths[-1], list(csv.DictReader(handle))


def top1(rows):
    return {row['fact_id'] for row in rows if int(row['correct_rank_mean']) == 1}


checkpoints = sorted(
    {
        path.name[len(prefix):].split('_', 1)[0]
        for path in root.glob(f'{prefix}checkpoint-*_*')
    },
    key=lambda value: int(value.split('-')[-1]),
)
results = []
for checkpoint in checkpoints:
    paths = {}
    rows = {}
    for view in ('exact_prefix', 'direct', 'qa_matched'):
        path, view_rows = latest_rows(root / f'{prefix}{checkpoint}_{view}')
        paths[view] = str(path.relative_to(repo)) if path else None
        rows[view] = view_rows
    if not all(rows.values()):
        results.append({'checkpoint': checkpoint, 'status': 'incomplete', 'paths': paths})
        continue
    counts = {view: len(top1(view_rows)) for view, view_rows in rows.items()}
    direct_ids = top1(rows['direct'])
    qa_ids = top1(rows['qa_matched'])
    result = {
        'checkpoint': checkpoint,
        'status': 'complete',
        'exact_prefix_top1': counts['exact_prefix'] / 50,
        'direct_top1': counts['direct'] / 50,
        'qa_top1': counts['qa_matched'] / 50,
        'robust_overlap': len(direct_ids & qa_ids) / 50,
        'counts': {**counts, 'robust_overlap': len(direct_ids & qa_ids)},
        'paths': paths,
    }
    result['passes_progression_gate'] = (
        result['exact_prefix_top1'] >= 0.90
        and result['direct_top1'] >= 0.50
        and result['qa_top1'] >= 0.50
        and result['robust_overlap'] >= 0.40
    )
    results.append(result)

passing = [item for item in results if item.get('passes_progression_gate')]
print(json.dumps({'results': results, 'earliest_passing_checkpoint': passing[0]['checkpoint'] if passing else None}, indent=2))
PY
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
