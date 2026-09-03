"""Preserve 21 completed states, recover only indices 21--62; no automatic retry."""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path

from transfer_vs_relearning.study import m2_eval_executor as base
from transfer_vs_relearning.utils.io import sha256_file, write_json

SOURCE = Path('/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1b')
ROOT = Path('/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_recovery_v1a')
CONTROLS = ('task_matrix.json', 'preflight_result.json', 'oscar_heldout_materialization.json',
            'm1_parent_factual_registry.json', 'evaluation_family_result.json')
ACK = 'exact_sha_bound_user_authorization_received'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def state_inventory(root, task):
    directory = root / 'results' / task['role'] / task['checkpoint_id']
    paths = sorted(directory.rglob('*'))
    if directory.is_symlink() or any(p.is_symlink() for p in paths):
        raise ValueError('Source state contains symlinks')
    files = [p for p in paths if p.is_file()]
    if len(files) >= 1000 or sum(p.stat().st_size for p in files) >= 2 * 1024**3:
        raise ValueError('Bounded state inventory exceeded')
    rows = [{'path': str(p.relative_to(directory)), 'bytes': p.stat().st_size,
             'sha256': sha256_file(p)} for p in files]
    result = json.loads((directory / 'task_result.json').read_text())
    index = task['task_index']
    if index >= 21:
        if {row['path'] for row in rows} != {
            'task_result.json', 'configs/exact_prefix.json', 'configs/generation_integrity.json'
        } or result['status'] != 'failed' or result.get('error') != (
            'GPU free-memory gate failed on index 0: 16720592896 bytes free < 21474836480 required'
        ):
            raise ValueError('Failed state has unexpected scientific artifacts or failure')
    elif result['status'] != 'complete':
        raise ValueError('Preserved state is not complete')
    return {'index': index, 'role': task['role'], 'checkpoint_id': task['checkpoint_id'],
            'status': result['status'], 'count': len(rows), 'bytes': sum(x['bytes'] for x in rows),
            'tree_sha256': digest(rows), 'task_result_sha256': sha256_file(directory / 'task_result.json')}


def inventory(source=SOURCE):
    matrix = base.load_matrix(source / 'control/task_matrix.json')
    if [t['task_index'] for t in matrix['tasks']] != list(range(63)):
        raise ValueError('Unexpected source task order')
    return {'source_root': str(source),
            'controls': {n: sha256_file(source / 'control' / n) for n in CONTROLS},
            'states': [state_inventory(source, task) for task in matrix['tasks']],
            'oscar_sha256': sha256_file(source / 'corpora/oscar_heldout_10000.jsonl')}


def identity(matrix):
    repo = Path(matrix['repo_root'])
    auth = matrix['authorization']
    if (subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
            != auth['expected_commit'] or subprocess.check_output(
                ['git', 'status', '--porcelain=v1'], cwd=repo) or auth['authorization_ack'] != ACK):
        raise ValueError('Recovery commit/cleanliness/authorization drift')
    base._verify(Path(auth['contract']), auth['contract_sha256'], 'recovery_contract')
    base._verify(Path(auth['config']), auth['config_sha256'], 'recovery_config')
    if matrix['recovery'] != json.loads(Path(auth['config']).read_text()):
        raise ValueError('Recovery config/matrix mismatch')
    base._verify(base.RUNTIME_LOCK, base.RUNTIME_LOCK_SHA256, 'runtime')
    if Path(matrix['output_root']) != ROOT or Path(matrix['recovery']['source']) != SOURCE:
        raise ValueError('Recovery path drift')
    for name, expected in matrix['recovery']['controls'].items():
        base._verify(SOURCE / 'control' / name, expected, name)
    original = base.load_matrix(SOURCE / 'control/task_matrix.json')
    for key in ('tasks', 'source_matrix', 'source_matrix_sha256', 'm1_parent_projection', 'oscar_source'):
        if matrix[key] != original[key]:
            raise ValueError('Original scientific input mismatch: ' + key)


def validate_sources(matrix):
    identity(matrix)
    evidence = inventory()
    if digest(evidence) != matrix['recovery']['inventory_sha256']:
        raise ValueError('Frozen source inventory drift')
    original = base.load_matrix(SOURCE / 'control/task_matrix.json')
    if matrix['tasks'] != original['tasks']:
        raise ValueError('Scientific task identity drift')
    base._verify(Path(matrix['source_matrix']), matrix['source_matrix_sha256'], 'family_matrix')
    base._verify(base.DATASET_CONTENT_MANIFEST, base.DATASET_CONTENT_MANIFEST_SHA256, 'dataset')
    for label, (path, expected) in base.FROZEN_INPUTS.items():
        path = Path(path)
        base._verify(path if path.is_absolute() else Path(matrix['repo_root']) / path, expected, label)
    for task in matrix['tasks']:
        base._verify(Path(task['model_manifest']), task['model_manifest_sha256'], 'model_manifest')
    parent = matrix['m1_parent_projection']
    base._verify(Path(parent['path']), parent['source_sha256'], 'M1_projection')
    registry = json.loads((SOURCE / 'control/m1_parent_factual_registry.json').read_text())
    for row in registry['rows']:
        base._verify(Path(row['summary']), row['summary_sha256'], 'M1_summary')
        base._verify(Path(row['per_fact']), row['per_fact_sha256'], 'M1_facts')
    return evidence


def start(repo, config_path, contract, contract_sha, commit, ack):
    config = json.loads(config_path.read_text())
    if ack != ACK:
        raise PermissionError('Missing exact user authorization')
    matrix = base.load_matrix(SOURCE / 'control/task_matrix.json')
    matrix['output_root'] = str(ROOT)
    matrix['repo_root'] = str(repo.resolve())
    matrix['authorization'] = dict(contract=str(contract.resolve()), contract_sha256=contract_sha,
        config=str(config_path.resolve()), config_sha256=sha256_file(config_path),
        expected_commit=commit, authorization_ack=ack)
    matrix['recovery'] = config
    identity(matrix)
    if ROOT.exists() or ROOT.is_symlink() or ROOT.resolve() != ROOT:
        raise FileExistsError('Recovery root not fresh/scratch-resolved')
    storage = os.statvfs(ROOT.parent)
    if storage.f_bavail * storage.f_frsize < 40 * 1024**3 or storage.f_favail < 8192:
        raise ValueError('Recovery storage gate')
    if subprocess.check_output(['squeue', '-h', '-u', 'yesildau', '-n',
            'm2-rec-a-pre,m2-rec-a-canary,m2-rec-a-array,m2-rec-a-final']):
        raise ValueError('Duplicate recovery job')
    base._verify(Path(config['qualification_audit']), config['qualification_sha256'], 'qualification')
    if json.loads(Path(config['qualification_audit']).read_text())['status'] != 'pass':
        raise ValueError('Qualification has not passed')
    # Validate compact source identities here; full tree reproduction runs in the CPU job.
    for name, expected in config['controls'].items():
        base._verify(SOURCE / 'control' / name, expected, name)
    ROOT.mkdir()
    for name in ('control', 'logs', 'tmp', 'cache', 'results', 'corpora'):
        (ROOT / name).mkdir()
    write_json(ROOT / 'control/task_matrix.json', matrix)
    return submit(matrix)


def preflight(matrix):
    evidence = validate_sources(matrix)
    root = Path(matrix['output_root'])
    for row in evidence['states'][:21]:
        dest = root / 'results' / row['role'] / row['checkpoint_id']
        dest.parent.mkdir(exist_ok=True)
        dest.symlink_to(SOURCE / 'results' / row['role'] / row['checkpoint_id'], target_is_directory=True)
    for name in ('oscar_heldout_materialization.json', 'm1_parent_factual_registry.json'):
        (root / 'control' / name).symlink_to(SOURCE / 'control' / name)
    source = SOURCE / 'corpora/oscar_heldout_10000.jsonl'
    dest = root / 'corpora/oscar_heldout_10000.jsonl'
    expected = evidence['oscar_sha256']
    base._verify(source, expected, 'source_oscar')
    if source.stat().st_size > 128 * 1024**2:
        raise ValueError('Bounded heldout copy exceeded 128 MiB')
    # Exclusive regular-file copy, never reconstruction or a source write.
    with source.open('rb') as reader, dest.open('xb') as writer:
        shutil.copyfileobj(reader, writer, length=1024**2)
    base._verify(dest, expected, 'copied_oscar')
    write_json(root / 'control/source_inventory.json', evidence)
    write_json(root / 'control/recovery_preflight.json', {'status': 'pass', 'inventory_sha256': digest(evidence)})


def _run_task(matrix, index):
    if index not in range(21, 63):
        raise ValueError('Completed/out-of-range task cannot be rescored')
    identity(matrix)
    root = Path(matrix['output_root'])
    for relative in ('control/oscar_heldout_materialization.json',
                     'control/m1_parent_factual_registry.json'):
        if (root / relative).resolve() != SOURCE / relative:
            raise ValueError('Read-only input link drift')
    if (root / 'control/STOP').exists():
        raise RuntimeError('Recovery stopped after earlier failure')
    pre = json.loads((root / 'control/recovery_preflight.json').read_text())
    if pre != {'status': 'pass', 'inventory_sha256': matrix['recovery']['inventory_sha256']}:
        raise ValueError('Recovery preflight absent or drifted')
    if index != 21:
        canary = matrix['tasks'][21]
        result = root / 'results' / canary['role'] / canary['checkpoint_id'] / 'task_result.json'
        if json.loads(result.read_text())['status'] != 'complete':
            raise ValueError('Scientific canary incomplete')
    task = matrix['tasks'][index]
    dest = root / 'results' / task['role'] / task['checkpoint_id']
    if dest.resolve() != dest or dest.exists() or dest.is_symlink():
        raise FileExistsError('Recovery task output must be fresh and not redirected')
    try:
        return base.run_task(matrix, index)
    except BaseException:
        (root / 'control/STOP').mkdir(exist_ok=True)
        raise


def run_task(matrix, index):
    if index not in range(21, 63):
        raise ValueError('Completed/out-of-range task cannot be rescored')
    try:
        return _run_task(matrix, index)
    except BaseException:
        # Also stop on pre-model input/identity errors, not only evaluator failures.
        (ROOT / 'control/STOP').mkdir(exist_ok=True)
        raise


def finalize(matrix):
    validate_sources(matrix)
    root = Path(matrix['output_root'])
    if (root / 'control/m1_parent_factual_registry.json').resolve() != SOURCE / 'control/m1_parent_factual_registry.json':
        raise ValueError('Final analysis baseline link drift')
    for task in matrix['tasks'][:21]:
        path = root / 'results' / task['role'] / task['checkpoint_id']
        if not path.is_symlink() or path.resolve() != SOURCE / 'results' / task['role'] / task['checkpoint_id']:
            raise ValueError('Preserved result binding drift')
    if (root / 'control/evaluation_family_result.json').exists():
        raise FileExistsError('Finalizer already ran')
    return base.finalize(matrix)


def submit(matrix):
    root = Path(matrix['output_root'])
    script = Path(matrix['repo_root']) / 'scripts/study/execute_m2_eval_recovery.py'
    shared = ['sbatch', '--parsable', '--account=yesildau', '--no-requeue',
              '--chdir=' + matrix['repo_root'], '--output=' + str(root / 'logs/%x-%A_%a.out'),
              '--error=' + str(root / 'logs/%x-%A_%a.err')]
    exports = {'PYTHONPATH': 'src', 'PYTHONDONTWRITEBYTECODE': '1', 'TMPDIR': str(root / 'tmp'),
               'HF_HOME': str(root / 'cache'), 'XDG_CACHE_HOME': str(root / 'cache'),
               'HF_DATASETS_CACHE': str(base.DATASET_CACHE_ROOT / 'huggingface_datasets'),
               'HF_HUB_OFFLINE': '1', 'HF_DATASETS_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
               'WANDB_MODE': 'disabled'}
    prefix = 'export ' + ' '.join(k + '=' + shlex.quote(v) for k, v in exports.items()) + '; exec '
    def command(stage, suffix=''):
        return '--wrap=' + prefix + shlex.join([str(base.RUNTIME_PYTHON), str(script), stage,
            '--matrix', str(root / 'control/task_matrix.json')]) + suffix
    gpu = ['--partition=gpu', '--gres=gpu:a10080gb:1', '--cpus-per-task=8', '--mem=64G', '--time=2-12:00:00']
    specs = [(['--partition=longrun', '--cpus-per-task=4', '--mem=64G', '--time=02:00:00'], 'm2-rec-a-pre', command('preflight')),
             (gpu, 'm2-rec-a-canary', command('run-task', ' --task-index 21')),
             (gpu + ['--array=22-62%6'], 'm2-rec-a-array', command('run-task', ' --task-index "$SLURM_ARRAY_TASK_ID"')),
             (['--partition=std', '--cpus-per-task=2', '--mem=8G', '--time=01:00:00'], 'm2-rec-a-final', command('finalize'))]
    for resources, name, cmd in specs:
        subprocess.run([*shared, *resources, '--job-name=' + name, '--test-only', cmd], check=True)
    ledger = {'status': 'submitting', 'jobs': [], 'automatic_retry': False}
    path = root / 'control/submission_manifest.json'
    if path.exists():
        raise FileExistsError(path)
    write_json(path, ledger)
    for i, (resources, name, cmd) in enumerate(specs):
        deps = [] if i == 0 else ['--dependency=' + ('afterany:' if i == 3 else 'afterok:') + ledger['jobs'][-1]['id']]
        result = subprocess.run([*shared, *resources, '--job-name=' + name, *deps, cmd],
                                check=True, capture_output=True, text=True)
        job = result.stdout.strip().split(';')[0]
        if not job.isdigit():
            raise ValueError('Ambiguous submission; inspect without resubmission')
        ledger['jobs'].append({'name': name, 'id': job})
        write_json(path, ledger)
    ledger['status'] = 'submitted'
    write_json(path, ledger)
    return ledger
