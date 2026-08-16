#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning

PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
SCRATCH=/vol/tmp2/yesildau/m1_relation_v2_1_7b_500_seed43_data43
export SCRATCH

EVAL_CONFIG_DIR=$($PYTHON - <<'PY'
from pathlib import Path
import csv
import json
import os
import subprocess
import yaml

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
scratch = Path(os.environ['SCRATCH'])
run_dir = Path('/vol/tmp/yesildau/transfer-vs-relearning/runs/training/m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_seed43_data43/20260713T160909Z_m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36_seed43_data43_f8319fd2')
manifest = json.loads((run_dir / 'training_manifest.json').read_text(encoding='utf-8'))
if manifest.get('status') != 'complete':
    raise SystemExit(f'1.7B training run is not complete: {run_dir}')

expected_steps = [25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252]
checkpoints = sorted(
    (path for path in (run_dir / 'checkpoints').glob('checkpoint-*') if path.is_dir()),
    key=lambda path: int(path.name.split('-')[-1]),
)
observed_steps = [int(path.name.split('-')[-1]) for path in checkpoints]
if observed_steps != expected_steps:
    raise SystemExit(f'Expected checkpoints {expected_steps}, found {observed_steps}')

dataset_root = repo / 'artifacts/datasets/relation_v2_gate_v1'
gate_root = dataset_root / 'acquisition_100_subjects_direct'
namespace = 'm1_relation_v2_1_7b_500_job399078'
config_dir = scratch / 'eval_configs' / namespace
manifest_dir = scratch / 'eval_model_manifests' / namespace
probe_dir = config_dir / 'probes'
config_dir.mkdir(parents=True, exist_ok=True)
manifest_dir.mkdir(parents=True, exist_ok=True)
probe_dir.mkdir(parents=True, exist_ok=True)

with (gate_root / 'validation.jsonl').open(encoding='utf-8') as handle:
    validation = [json.loads(line) for line in handle if line.strip()]
metadata = {row['fact_id']: row for row in validation}
probe_columns = [
    'fact_id', 'row_id', 'subject_id', 'language', 'relation', 'subject', 'question',
    'expected_answer', 'name_type', 'name_rarity_bucket', 'popularity_rank',
    'popularity_bucket', 'frequency_bucket', 'branch_group', 'template_id',
]

heldout_rows = []
for row in validation:
    question_line = row['text'].splitlines()[0]
    if not question_line.startswith('Question: '):
        raise SystemExit(f'Unexpected held-out prompt format for {row["fact_id"]}')
    heldout_rows.append({
        'fact_id': row['fact_id'],
        'row_id': row['row_id'],
        'subject_id': row['subject_id'],
        'language': 'en',
        'relation': row['relation'],
        'subject': row['subject'],
        'question': question_line.removeprefix('Question: '),
        'expected_answer': row['answer'],
        'name_type': row['name_type'],
        'name_rarity_bucket': row['name_rarity_bucket'],
        'popularity_rank': row['popularity_rank'],
        'popularity_bucket': row['popularity_bucket'],
        'frequency_bucket': row['frequency_bucket'],
        'branch_group': row['branch_group'],
        'template_id': row['template_id'],
    })

with (gate_root / 'exact_prefix_probes_en.csv').open(encoding='utf-8', newline='') as handle:
    exact_source = list(csv.DictReader(handle))
exact_rows = []
for row in exact_source:
    source = metadata[row['fact_id']]
    exact_rows.append({
        **{key: source[key] for key in (
            'fact_id', 'row_id', 'subject_id', 'relation', 'subject', 'name_type',
            'name_rarity_bucket', 'popularity_rank', 'popularity_bucket',
            'frequency_bucket', 'branch_group',
        )},
        'language': 'en',
        'question': row['question'],
        'expected_answer': row['expected_answer'],
        'template_id': row['template_id'],
    })

if len(heldout_rows) != 500 or len(exact_rows) != 500:
    raise SystemExit('Expected exactly 500 held-out and 500 exact-prefix probes')
for name, rows in (
    ('heldout_probes_en.csv', heldout_rows),
    ('exact_prefix_probes_en.csv', exact_rows),
):
    with (probe_dir / name).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=probe_columns, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

source_manifest = repo / 'artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json'
common = {
    'dataset_version': 'relation_v2_gate_v1_100_subjects_500_facts',
    'dataset_dir': str(dataset_root),
    'pilot_subject_file': str(gate_root / 'summary.json'),
    'languages': ['en'],
    'relations': ['profession', 'born_in', 'lives_in', 'field_of_study', 'works_in_industry'],
    'scoring': {
        'primary': 'mean_logprob',
        'secondary': 'total_logprob',
        'tie_breaker': 'canonical_object_id',
    },
    'runtime': {
        'bf16': True,
        'device': 'cuda',
        'candidate_batch_size': 64,
        'checkpoint_interval': 10,
        'seed': 42,
    },
}

for checkpoint in checkpoints:
    model_manifest = manifest_dir / f'{checkpoint.name}_model_manifest.json'
    subprocess.run(
        [
            str(Path('/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python')),
            'scripts/operations/create_local_model_manifest.py',
            '--source-manifest', str(source_manifest),
            '--local-model-dir', str(checkpoint),
            '--output-manifest', str(model_manifest),
            '--model-id', f'{namespace}/{checkpoint.name}',
            '--training-checkpoint', checkpoint.name,
            '--training-run-dir', str(run_dir),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    views = {
        'exact_prefix': {
            **common,
            'model_manifest': str(model_manifest),
            'probe_files': {'en': str(probe_dir / 'exact_prefix_probes_en.csv')},
            'prompt': {'format': 'direct', 'template': '{question}', 'answer_separator': ' '},
            'output': {'run_root': str(scratch / 'evaluation' / f'{namespace}_{checkpoint.name}_exact_prefix')},
        },
        'direct': {
            **common,
            'model_manifest': str(model_manifest),
            'probe_files': {'en': str(probe_dir / 'heldout_probes_en.csv')},
            'prompt': {'format': 'direct', 'template': '{question}', 'answer_separator': ' '},
            'output': {'run_root': str(scratch / 'evaluation' / f'{namespace}_{checkpoint.name}_direct')},
        },
        'qa_matched': {
            **common,
            'model_manifest': str(model_manifest),
            'probe_files': {'en': str(probe_dir / 'heldout_probes_en.csv')},
            'prompt': {
                'format': 'qa_matched',
                'templates_by_language': {'en': 'Question: {question}\nAnswer:'},
                'answer_separator': ' ',
            },
            'output': {'run_root': str(scratch / 'evaluation' / f'{namespace}_{checkpoint.name}_qa_matched')},
        },
    }
    for view, payload in views.items():
        (config_dir / f'{checkpoint.name}_{view}.yaml').write_text(
            yaml.safe_dump(payload, sort_keys=False),
            encoding='utf-8',
        )

print(config_dir)
PY
)

echo "__EVAL_CONFIG_DIR__=$EVAL_CONFIG_DIR"
mkdir -p "$SCRATCH/eval_logs" "$SCRATCH/cache"
for config in "$EVAL_CONFIG_DIR"/checkpoint-*_exact_prefix.yaml; do
  checkpoint=$(basename "$config" _exact_prefix.yaml)
  job_id=$(sbatch --parsable \
    --nodelist=gruenau9 \
    --output="$SCRATCH/eval_logs/%x-%j.out" \
    --error="$SCRATCH/eval_logs/%x-%j.err" \
    --export=ALL,EVAL_CONFIG_DIR="$EVAL_CONFIG_DIR",CHECKPOINT="$checkpoint",HF_HOME="$SCRATCH/cache",XDG_CACHE_HOME="$SCRATCH/cache",PYTHONDONTWRITEBYTECODE=1 \
    slurm/m1/eval_m1_acquisition_ladder.slurm)
  echo "__EVAL_JOB__=$job_id $checkpoint"
done

echo "__QUEUE__"
squeue -h -u yesildau -o "%i %T %M %L %R %j" | grep m1-ladder-eval || true
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
