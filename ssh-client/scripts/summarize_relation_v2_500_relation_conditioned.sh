#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANT="${1:-lr5e6}"
if [[ "$VARIANT" != "lr5e6" && "$VARIANT" != "lr2e6" && "$VARIANT" != "consistency" ]]; then
  echo "Usage: $0 [lr5e6|lr2e6|consistency]" >&2
  exit 2
fi

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
export VARIANT=__VARIANT__
"$PYTHON" - <<'PY'
from collections import Counter
from pathlib import Path
import csv
import os

root = Path('runs/evaluation')
variant = os.environ['VARIANT']
namespace = {
    'lr5e6': 'm1_relation_v2_500_relation_conditioned',
    'lr2e6': 'm1_relation_v2_500_relation_conditioned_lr2e6',
    'consistency': 'm1_relation_v2_500_prompt_consistency',
}[variant]
relations = ['profession', 'born_in', 'lives_in', 'field_of_study', 'works_in_industry']

def load(step, view):
    run_root = root / f'{namespace}_checkpoint-{step}_{view}'
    runs = sorted(path for path in run_root.glob('*') if (path / 'per_fact_results.csv').is_file())
    if len(runs) != 1:
        raise SystemExit(f'Expected one completed run for checkpoint {step} {view}, found {runs}')
    with (runs[0] / 'per_fact_results.csv').open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 500:
        raise SystemExit(f'Expected 500 rows for checkpoint {step} {view}, found {len(rows)}')
    return {row['fact_id']: row for row in rows}

print('checkpoint exact direct qa overlap triple')
results = {}
for step in range(15, 151, 15):
    views = {view: load(step, view) for view in ('exact_prefix', 'direct', 'qa_matched')}
    ids = set(views['exact_prefix'])
    success = {
        view: {fact_id for fact_id, row in rows.items() if int(float(row['correct_rank_mean'])) == 1}
        for view, rows in views.items()
    }
    overlap = success['direct'] & success['qa_matched']
    triple = overlap & success['exact_prefix']
    values = (len(success['exact_prefix']), len(success['direct']), len(success['qa_matched']), len(overlap), len(triple))
    results[step] = (values, views, triple)
    print(step, *values)

best_step = max(results, key=lambda step: (results[step][0][3], results[step][0][4], results[step][0][1], results[step][0][2], -step))
values, views, triple = results[best_step]
print(f'BEST checkpoint-{best_step} values={values}')
relation_counts = Counter(views['direct'][fact_id]['relation'] for fact_id in triple)
print('TRIPLE_BY_RELATION', ' '.join(f'{relation}={relation_counts[relation]}' for relation in relations))

direct = views['direct']
qa = views['qa_matched']
residence_to_birthplace = set()
birthplace_to_residence = set()
by_subject = {}
for row in direct.values():
    by_subject.setdefault(row['subject_id'], {})[row['relation']] = row
for subject_id, rows in by_subject.items():
    if not {'born_in', 'lives_in'} <= rows.keys():
        continue
    birthplace = rows['born_in']['expected_answer']
    residence = rows['lives_in']['expected_answer']
    for view_rows in (direct, qa):
        born = next(row for row in view_rows.values() if row['subject_id'] == subject_id and row['relation'] == 'born_in')
        lives = next(row for row in view_rows.values() if row['subject_id'] == subject_id and row['relation'] == 'lives_in')
        if born['predicted_surface_form'] == residence:
            birthplace_to_residence.add(subject_id)
        if lives['predicted_surface_form'] == birthplace:
            residence_to_birthplace.add(subject_id)
print(f'CITY_SWAPS residence_to_birthplace={len(residence_to_birthplace)} birthplace_to_residence={len(birthplace_to_residence)}')
PY
EOF
)

remote_cmd=${remote_cmd/__VARIANT__/$VARIANT}
quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
