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

EVAL_CONFIG_DIR=$($PYTHON - <<'PY'
from pathlib import Path
import csv
import json
import os
import subprocess
import yaml

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
variant = os.environ['VARIANT']
if variant == 'consistency':
    run_root = repo / 'runs/training/m1_smollm2_360m_relation_v2_500_prompt_consistency_cp250'
    namespace = 'm1_relation_v2_500_prompt_consistency'
elif variant == 'lr2e6':
    run_root = repo / 'runs/training/m1_smollm2_360m_relation_v2_500_relation_conditioned_cp250_lr2e-6'
    namespace = 'm1_relation_v2_500_relation_conditioned_lr2e6'
else:
    run_root = repo / 'runs/training/m1_smollm2_360m_relation_v2_500_relation_conditioned_cp250'
    namespace = 'm1_relation_v2_500_relation_conditioned'
runs = sorted(path for path in run_root.glob('*') if (path / 'training_manifest.json').is_file())
if not runs:
    raise SystemExit(f'No relation-conditioned run found under {run_root}')
run_dir = runs[-1]
manifest = json.loads((run_dir / 'training_manifest.json').read_text())
if manifest.get('status') != 'complete':
    raise SystemExit(f'Latest relation-conditioned run is not complete: {run_dir}')

checkpoints = sorted(
    (path for path in (run_dir / 'checkpoints').glob('checkpoint-*') if path.is_dir()),
    key=lambda path: int(path.name.split('-')[-1]),
)
expected_steps = list(range(15, 151, 15))
observed_steps = [int(path.name.split('-')[-1]) for path in checkpoints]
if observed_steps != expected_steps:
    raise SystemExit(f'Expected checkpoints {expected_steps}, found {observed_steps}')

dataset_root = repo / 'artifacts/datasets/relation_v2_gate_v1'
gate_root = dataset_root / 'acquisition_100_subjects_direct'
config_dir = repo / f'runs/local_configs/{namespace}'
manifest_dir = repo / f'runs/local_model_manifests/{namespace}'
probe_dir = config_dir / 'probes'
config_dir.mkdir(parents=True, exist_ok=True)
manifest_dir.mkdir(parents=True, exist_ok=True)
probe_dir.mkdir(parents=True, exist_ok=True)

validation = [json.loads(line) for line in (gate_root / 'validation.jsonl').read_text().splitlines() if line]
metadata = {row['fact_id']: row for row in validation}
columns = ['fact_id','row_id','subject_id','language','relation','subject','question','expected_answer','name_type','name_rarity_bucket','popularity_rank','popularity_bucket','frequency_bucket','branch_group','template_id']
heldout = []
for row in validation:
    question = row['text'].splitlines()[0].removeprefix('Question: ')
    heldout.append({**{key: row[key] for key in columns if key in row}, 'language':'en', 'question':question, 'expected_answer':row['answer']})
with (gate_root / 'exact_prefix_probes_en.csv').open(newline='') as handle:
    exact_source = list(csv.DictReader(handle))
exact = []
for row in exact_source:
    source = metadata[row['fact_id']]
    exact.append({**{key: source[key] for key in columns if key in source}, 'language':'en', 'question':row['question'], 'expected_answer':row['expected_answer'], 'template_id':row['template_id']})
for name, rows in [('heldout.csv', heldout), ('exact.csv', exact)]:
    with (probe_dir / name).open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)

common = {
    'dataset_version':'relation_v2_gate_v1_100_subjects_500_facts',
    'dataset_dir':'artifacts/datasets/relation_v2_gate_v1',
    'pilot_subject_file':'artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json',
    'languages':['en'],
    'relations':['profession','born_in','lives_in','field_of_study','works_in_industry'],
    'scoring':{'primary':'mean_logprob','secondary':'total_logprob','tie_breaker':'canonical_object_id'},
    'runtime':{'bf16':True,'device':'cuda','candidate_batch_size':64,'checkpoint_interval':10,'seed':42},
}
for checkpoint in checkpoints:
    model_manifest = manifest_dir / f'{checkpoint.name}_model_manifest.json'
    subprocess.run([
        str(Path('/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python')),
        'scripts/create_local_model_manifest.py', '--source-manifest',
        'artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json',
        '--local-model-dir', str(checkpoint), '--output-manifest', str(model_manifest),
        '--model-id', f'{namespace}/{checkpoint.name}',
        '--training-checkpoint', checkpoint.name, '--training-run-dir', str(run_dir),
    ], check=True, stdout=subprocess.DEVNULL)
    relative_manifest = str(model_manifest.relative_to(repo))
    views = {
        'exact_prefix': ('exact.csv', {'format':'direct','template':'{question}','answer_separator':' '}),
        'direct': ('heldout.csv', {'format':'direct','template':'{question}','answer_separator':' '}),
        'qa_matched': ('heldout.csv', {'format':'qa_matched','templates_by_language':{'en':'Question: {question}\nAnswer:'},'answer_separator':' '}),
    }
    for view, (probe, prompt) in views.items():
        payload = {**common, 'model_manifest':relative_manifest, 'probe_files':{'en':str((probe_dir/probe).relative_to(repo))}, 'prompt':prompt, 'output':{'run_root':f'runs/evaluation/{namespace}_{checkpoint.name}_{view}'}}
        (config_dir / f'{checkpoint.name}_{view}.yaml').write_text(yaml.safe_dump(payload, sort_keys=False))
print(config_dir.relative_to(repo))
PY
)

echo "__EVAL_CONFIG_DIR__=$EVAL_CONFIG_DIR"
for config in "$EVAL_CONFIG_DIR"/checkpoint-*_exact_prefix.yaml; do
  checkpoint=$(basename "$config" _exact_prefix.yaml)
  job_id=$(sbatch --parsable --export=ALL,EVAL_CONFIG_DIR="$EVAL_CONFIG_DIR",CHECKPOINT="$checkpoint" slurm/eval_m1_acquisition_ladder.slurm)
  echo "__EVAL_JOB__=$job_id $checkpoint"
done
squeue -h -u yesildau -o "%i %T %M %L %R %j" | grep m1-ladder-eval || true
EOF
)

remote_cmd=${remote_cmd/__VARIANT__/$VARIANT}
quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
