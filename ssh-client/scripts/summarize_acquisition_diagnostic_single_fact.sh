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
prefix = 'm1_diagnostic_single_fact_'


def latest_rows(run_root):
    paths = sorted(run_root.glob('*/per_fact_results.csv'))
    if not paths:
        return None, []
    with paths[-1].open(encoding='utf-8', newline='') as handle:
        return paths[-1], list(csv.DictReader(handle))


checkpoints = sorted(
    {path.name[len(prefix):].split('_', 1)[0] for path in root.glob(f'{prefix}checkpoint-*_*')},
    key=lambda value: int(value.split('-')[-1]),
)
results = []
for checkpoint in checkpoints:
    item = {'checkpoint': checkpoint}
    top1 = {}
    paths = {}
    for view in ('exact_prefix', 'direct', 'qa_matched'):
        path, rows = latest_rows(root / f'{prefix}{checkpoint}_{view}')
        paths[view] = str(path.relative_to(repo)) if path else None
        top1[view] = bool(rows) and int(rows[0]['correct_rank_mean']) == 1
        if rows:
            item[f'{view}_rank'] = int(rows[0]['correct_rank_mean'])
            item[f'{view}_margin'] = float(rows[0]['margin'])
    item['paths'] = paths
    item['passes_gate'] = all(top1.values())
    results.append(item)

passing = [item for item in results if item['passes_gate']]
print(json.dumps({'results': results, 'earliest_passing_checkpoint': passing[0]['checkpoint'] if passing else None}, indent=2))
PY
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
