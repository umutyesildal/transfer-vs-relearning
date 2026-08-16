#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning

PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
EVAL_CONFIG_DIR=$($PYTHON - <<'PY'
from pathlib import Path
import json
import subprocess
import yaml

repo = Path('/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning')
run_root = repo / 'runs/training/m1_smollm2_360m_diagnostic_all_relations_50_direct_answer_only'
complete_runs = []
for path in run_root.glob('*'):
    manifest_path = path / 'training_manifest.json'
    if manifest_path.exists() and json.loads(manifest_path.read_text(encoding='utf-8')).get('status') == 'complete':
        complete_runs.append(path)
if not complete_runs:
    raise SystemExit('No completed all-relations 50-fact direct-supervision run found')
run_dir = sorted(complete_runs)[-1]
checkpoints = sorted(
    (path for path in (run_dir / 'checkpoints').glob('checkpoint-*') if path.is_dir()),
    key=lambda path: int(path.name.split('-')[-1]),
)

source_manifest = repo / 'artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json'
manifest_dir = repo / 'runs/local_model_manifests/m1_diagnostic_all_relations_50_direct'
config_dir = repo / 'runs/local_configs/m1_diagnostic_all_relations_50_direct'
manifest_dir.mkdir(parents=True, exist_ok=True)
config_dir.mkdir(parents=True, exist_ok=True)

common = {
    'dataset_version': 'synthetic_v1',
    'dataset_dir': 'artifacts/datasets/synthetic_v1',
    'pilot_subject_file': 'artifacts/datasets/acquisition_diagnostics_v1/all_relations_10_subjects_direct_supervision/pilot.json',
    'languages': ['en'],
    'relations': ['profession', 'born_in', 'lives_in', 'studied_at', 'works_at'],
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
    manifest_path = manifest_dir / f'{checkpoint.name}_model_manifest.json'
    subprocess.run(
        [
            '/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python',
            'scripts/operations/create_local_model_manifest.py',
            '--source-manifest', str(source_manifest),
            '--local-model-dir', str(checkpoint),
            '--output-manifest', str(manifest_path),
            '--model-id', f'm1_diagnostic_all_relations_50_direct/{checkpoint.name}',
            '--training-checkpoint', checkpoint.name,
            '--training-run-dir', str(run_dir),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    relative_manifest = str(manifest_path.relative_to(repo))
    views = {
        'exact_prefix': {
            **common,
            'model_manifest': relative_manifest,
            'probe_files': {
                'en': 'artifacts/datasets/acquisition_diagnostics_v1/all_relations_10_subjects_direct_supervision/exact_prefix_probes_en.csv',
            },
            'prompt': {'format': 'direct', 'template': '{question}', 'answer_separator': ' '},
            'output': {'run_root': f'runs/evaluation/m1_diagnostic_all_relations_50_direct_{checkpoint.name}_exact_prefix'},
        },
        'direct': {
            **common,
            'model_manifest': relative_manifest,
            'prompt': {'format': 'direct', 'template': '{question}', 'answer_separator': ' '},
            'output': {'run_root': f'runs/evaluation/m1_diagnostic_all_relations_50_direct_{checkpoint.name}_direct'},
        },
        'qa_matched': {
            **common,
            'model_manifest': relative_manifest,
            'prompt': {
                'format': 'qa_matched',
                'templates_by_language': {'en': 'Question: {question}\nAnswer:'},
                'answer_separator': ' ',
            },
            'output': {'run_root': f'runs/evaluation/m1_diagnostic_all_relations_50_direct_{checkpoint.name}_qa_matched'},
        },
    }
    for view, payload in views.items():
        (config_dir / f'{checkpoint.name}_{view}.yaml').write_text(
            yaml.safe_dump(payload, sort_keys=False),
            encoding='utf-8',
        )

print(config_dir.relative_to(repo))
PY
)

echo "__EVAL_CONFIG_DIR__=$EVAL_CONFIG_DIR"
for manifest in runs/local_model_manifests/m1_diagnostic_all_relations_50_direct/checkpoint-*_model_manifest.json; do
  checkpoint=$(basename "$manifest" _model_manifest.json)
  job_id=$(sbatch --parsable \
    --export=ALL,EVAL_CONFIG_DIR="$EVAL_CONFIG_DIR",CHECKPOINT="$checkpoint" \
    slurm/m1/eval_m1_acquisition_ladder.slurm)
  echo "__EVAL_JOB__=$job_id $checkpoint"
  sleep 1
done

echo "__QUEUE__"
squeue -h -u yesildau -o "%i %T %M %L %R %j" | grep m1-ladder-eval || true
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
