import json
from types import SimpleNamespace

import pytest

from transfer_vs_relearning.study import m2_eval_recovery as r
from transfer_vs_relearning.utils.io import write_json


@pytest.fixture
def wave(tmp_path, monkeypatch):
    source, root = tmp_path / 'source', tmp_path / 'recovery'
    for p in (source, root):
        for name in ('control', 'results', 'corpora', 'logs'):
            (p / name).mkdir(parents=True)
    tasks = [dict(task_index=i, role='qwen', checkpoint_id=f'cp-{i}', state_id=str(i))
             for i in range(63)]
    matrix = dict(status='M2_EVAL_V2_READY', total_state_count=63, tasks=tasks,
                  output_root=str(root), repo_root=str(tmp_path), recovery={})
    write_json(source / 'control/task_matrix.json', matrix)
    for name in r.CONTROLS[1:]:
        write_json(source / 'control' / name, {})
    (source / 'corpora/oscar_heldout_10000.jsonl').write_text('{}\n')
    for task in tasks:
        d = source / 'results/qwen' / task['checkpoint_id']
        (d / 'configs').mkdir(parents=True)
        for name in ('exact_prefix', 'generation_integrity'):
            write_json(d / 'configs' / (name + '.json'), {})
        write_json(d / 'task_result.json', dict(status='complete' if task['task_index'] < 21 else 'failed',
            error='GPU free-memory gate failed on index 0: 16720592896 bytes free < 21474836480 required'))
    monkeypatch.setattr(r, 'SOURCE', source)
    monkeypatch.setattr(r, 'ROOT', root)
    evidence = r.inventory(source)
    matrix['recovery']['inventory_sha256'] = r.digest(evidence)
    monkeypatch.setattr(r, 'identity', lambda matrix: None)
    monkeypatch.setattr(r, 'validate_sources', lambda matrix: evidence)
    return matrix, source, root


def test_inventory_detects_byte_drift(wave):
    matrix, source, _ = wave
    before = r.digest(r.inventory(source))
    (source / 'results/qwen/cp-0/configs/exact_prefix.json').write_text('{"changed":true}')
    assert r.digest(r.inventory(source)) != before


def test_failed_scoring_artifact_is_rejected(wave):
    _, source, _ = wave
    (source / 'results/qwen/cp-21/score.csv').write_text('score')
    with pytest.raises(ValueError, match='unexpected'):
        r.inventory(source)


def test_symlink_source_rejected(wave):
    _, source, _ = wave
    (source / 'results/qwen/cp-0/link').symlink_to(source / 'control/task_matrix.json')
    with pytest.raises(ValueError, match='symlinks'):
        r.inventory(source)


def test_preflight_preserves_sources_and_reuses_corpus(wave):
    matrix, source, root = wave
    before = r.digest(r.inventory(source))
    r.preflight(matrix)
    assert (root / 'results/qwen/cp-20').is_symlink()
    assert not (root / 'results/qwen/cp-21').exists()
    copied = root / 'corpora/oscar_heldout_10000.jsonl'
    assert not copied.is_symlink()
    assert copied.read_bytes() == (source / 'corpora/oscar_heldout_10000.jsonl').read_bytes()
    r.base._verify(copied, r.sha256_file(source / 'corpora/oscar_heldout_10000.jsonl'), 'real_verifier')
    assert before == r.digest(r.inventory(source))
    with pytest.raises(FileExistsError):
        r.preflight(matrix)


@pytest.mark.parametrize('index', [-1, 0, 20, 63])
def test_completed_and_invalid_indices_refused(wave, index):
    with pytest.raises(ValueError, match='rescored'):
        r.run_task(wave[0], index)


def test_canary_blocks_followers_and_fail_stop(wave, monkeypatch):
    matrix, _, root = wave
    r.preflight(matrix)
    with pytest.raises(FileNotFoundError):
        r.run_task(matrix, 22)
    assert (root / 'control/STOP').is_dir()


def test_canary_failure_stops_followers(wave, monkeypatch):
    matrix, _, root = wave
    r.preflight(matrix)
    def fail(*args):
        raise RuntimeError('GPU guard')
    monkeypatch.setattr(r.base, 'run_task', fail)
    with pytest.raises(RuntimeError, match='GPU guard'):
        r.run_task(matrix, 21)
    assert (root / 'control/STOP').is_dir()
    with pytest.raises(RuntimeError, match='stopped'):
        r.run_task(matrix, 22)


def test_completed_destination_never_overwritten(wave, monkeypatch):
    matrix, _, root = wave
    r.preflight(matrix)
    (root / 'results/qwen/cp-21').mkdir()
    monkeypatch.setattr(r.base, 'run_task', lambda *a: pytest.fail('must not run'))
    with pytest.raises(FileExistsError):
        r.run_task(matrix, 21)


def test_dag_exact_indices_and_durable_ids(wave, monkeypatch):
    matrix, _, root = wave
    calls = []
    def run(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(stdout=str(100 + len(calls)) + '\n')
    monkeypatch.setattr(r.subprocess, 'run', run)
    result = r.submit(matrix)
    assert len(calls) == 8
    assert all('--test-only' in cmd for cmd in calls[:4])
    assert '--dependency=afterok:105' in calls[5]
    assert '--dependency=afterok:106' in calls[6]
    assert '--array=22-62%6' in calls[6]
    assert '--dependency=afterany:107' in calls[7]
    assert all('--no-requeue' in cmd for cmd in calls)
    assert ' --task-index 21' in calls[5][-1]
    assert result['status'] == 'submitted'
    assert json.loads((root / 'control/submission_manifest.json').read_text()) == result


def test_submission_failure_does_not_retry(wave, monkeypatch):
    matrix, _, root = wave
    calls = []
    def run(argv, **kwargs):
        calls.append(argv)
        if len(calls) == 6:
            raise RuntimeError('scheduler failed')
        return SimpleNamespace(stdout='105\n')
    monkeypatch.setattr(r.subprocess, 'run', run)
    with pytest.raises(RuntimeError):
        r.submit(matrix)
    assert len(calls) == 6
    assert len(json.loads((root / 'control/submission_manifest.json').read_text())['jobs']) == 1


def test_finalizer_uses_combined_view_without_rescoring(wave, monkeypatch):
    matrix, source, root = wave
    r.preflight(matrix)
    monkeypatch.setattr(r.base, 'finalize', lambda m: {'root': m['output_root']})
    assert r.finalize(matrix) == {'root': str(root)}
    assert (root / 'results/qwen/cp-0').resolve() == source / 'results/qwen/cp-0'


def test_real_parent_executor_accepts_copied_corpus_before_gpu(wave, monkeypatch):
    matrix, source, root = wave
    r.preflight(matrix)
    manifest = root / 'control/test_manifest.json'
    write_json(manifest, {})
    task = matrix['tasks'][21]
    task.update(model_manifest=str(manifest), model_manifest_sha256=r.sha256_file(manifest),
                task_kind='m1_parent_oscar_baseline_only')
    # Replace linked audit with a test-local regular audit, leaving source untouched.
    audit = root / 'control/oscar_heldout_materialization.json'
    audit.unlink()
    write_json(audit, {'output_sha256': r.sha256_file(root / 'corpora/oscar_heldout_10000.jsonl')})
    monkeypatch.setattr(r.base, '_write_exact_config', lambda *a, **k: root / 'unused-exact')
    monkeypatch.setattr(r.base, '_write_generation_config', lambda *a, **k: root / 'unused-generation')
    class GPUReached(Exception):
        pass
    def stop_before_gpu(*args):
        raise GPUReached()
    monkeypatch.setattr(r.base, 'assert_allocated_gpu_memory', stop_before_gpu)
    with pytest.raises(GPUReached):
        r.base.run_task(matrix, 21)
