import copy
import json
from pathlib import Path
import tarfile

import pytest
import yaml

from improving.cli import main
from improving.data import read_jsonl, write_jsonl
from improving.formal_study import (compile_jobs, formal_budget, load_formal_config,
                                   open_suite, run_formal, validate_formal_config)
from improving.formal_reporting import build_formal_report
from improving.metrics import summarize_records
from improving.pipeline import file_sha
from improving.utils import atomic_json, stable_hash


def config_for(tmp_path):
    config = load_formal_config('configs/formal_16gb.yaml')
    config['model'] = {'name': 'fixture', 'dtype': 'float32'}
    config['output_dir'] = str(tmp_path / 'suite')
    config['data'] = {}
    for index, split in enumerate(('train', 'calibration', 'validation', 'eval')):
        tasks = [{'task_id': f'fixture/{split}/{i}', 'split': split,
                  'source': 'trusted-test-fixture', 'prompt': f'Write fixture {index}, question {i}',
                  'entry_point': 'f', 'reference': 'def f(): return 1', 'tests': 'assert f() == 1'}
                 for i in range(2)]
        path = tmp_path / f'{split}.jsonl'
        write_jsonl(path, tasks)
        config['data'][split] = str(path)
    return config


def seal_stage(directory, tasks, samples, variant, filename):
    choices = ['def f(): return 1', 'def f(): return 2-1',
               'def f(): return sum([1])', 'def f(): return int(True)']
    rows = []
    for task in tasks:
        for i in range(samples):
            code = choices[i % len(choices)] if variant == 'spectral_soft' else choices[0]
            # Analytic fixture labels; no pretrained-model performance simulated.
            rows.append({'task_id': task['task_id'], 'sample_id': i, 'completion': code, 'code': code,
                'correct': True, 'evaluation_provenance': {'backend': 'fixture', 'provenance_version': 2,
                    'code_extraction': 'first_fence', 'task_harness_sha256': stable_hash(task)}})
    verified = directory / filename.replace('.metrics.json', '.verified.jsonl')
    write_jsonl(verified, rows)
    metrics = summarize_records(rows, ks=sorted({1, min(8, samples), min(32, samples), samples}),
        correct_budget=4, correct_budgets=[4, 8, 16], bootstrap_samples=0,
        expected_samples={task['task_id']: samples for task in tasks})
    path = directory / filename
    atomic_json(path, metrics)
    marker = directory / 'complete.json'
    state = json.loads(marker.read_text()) if marker.exists() else {'files': {}}
    state['files'].update({path.name: file_sha(path), verified.name: file_sha(verified)})
    atomic_json(marker, state)


def fake_pipeline(config, resume=False):
    root = Path(config['output_dir'])
    tasks = read_jsonl(config['data']['eval'])
    atomic_json(root / 'manifest.json', {'config': config,
        'selected_task_ids': {'eval': [t['task_id'] for t in tasks]},
        'generation_diagnostic_task_ids': [t['task_id'] for t in tasks]})
    seal_stage(root / 'base', tasks, 64, 'base', 'evaluation.metrics.json')
    for method in config['methods']:
        for r in range(1, config['rounds'] + 1):
            directory = root / method / f'round_{r}'
            seal_stage(directory, tasks, 64, method, 'evaluation.metrics.json')
            seal_stage(directory, tasks, 32, method, 'generation_policy.metrics.json')
    atomic_json(root / 'run_status.json', {'status': 'completed'})
    return {'status': 'completed'}


@pytest.fixture
def fixture_runtime(monkeypatch):
    monkeypatch.setattr('improving.formal_study._resolve_model', lambda settings: {**settings, 'revision': 'f' * 40})
    monkeypatch.setattr('improving.formal_study.run_experiment', fake_pipeline)


def test_compile_freezes_new_seeds_endpoints_and_exact_formal_budget(tmp_path):
    config = config_for(tmp_path)
    jobs = compile_jobs(config)
    assert len(jobs) == 11
    assert {j['seed'] for j in jobs if j['phase'] == 'confirm'} == {43, 44, 45, 46, 47}
    assert all(not j['config'].get('data_limits') for j in jobs)
    assert all(j['config']['calibration']['tau'] == 1 for j in jobs)
    # The full inspected MBPP snapshot counts are checked without downloading.
    for split, count in [('train', 291), ('calibration', 50), ('validation', 30), ('eval', 500)]:
        template = read_jsonl(config['data'][split])[0]
        write_jsonl(config['data'][split], [{**template, 'task_id': f'{split}/{i}',
            'prompt': f'Unique {split} question {i}'} for i in range(count)])
    result = formal_budget(config)
    assert result['candidates_by_phase'] == {'confirm': 887740, 'mechanism': 423483,
        'retention': 1078449, 'transfer': 262400}
    assert result['total_candidates_upper_bound'] == 2652072


def test_formal_rejects_posthoc_changes_and_resume_tampering(tmp_path, fixture_runtime):
    config = config_for(tmp_path)
    suite = open_suite(config)
    assert suite['resolved_model']['revision'] == 'f' * 40
    assert all(j['config']['model'] == suite['resolved_model'] for j in suite['jobs'])
    assert open_suite(config, resume=True) == suite
    with pytest.raises(FileExistsError):
        open_suite(config)
    changed = copy.deepcopy(config)
    changed['generation']['temperature'] = 1.2
    with pytest.raises(ValueError, match='changed'):
        open_suite(changed, resume=True)
    changed = copy.deepcopy(config)
    changed['formal']['confirm_seeds'][0] = 42
    with pytest.raises(ValueError, match='pilot seed42'):
        validate_formal_config(changed)
    path = Path(config['output_dir']) / 'configs/confirm_seed43.yaml'
    path.write_text('methods: [spectral_soft]')
    with pytest.raises(ValueError, match='Compiled'):
        open_suite(config, resume=True)


def test_formal_accepts_only_explicit_fully_local_evaluation_opt_in(tmp_path):
    config = config_for(tmp_path)
    config['evaluation'].update(backend='local', allow_unsafe_local=True)
    config['transfer'].update(backend='local', allow_unsafe_local=True)
    assert validate_formal_config(config)['evaluation']['backend'] == 'local'

    missing_mbpp_opt_in = copy.deepcopy(config)
    missing_mbpp_opt_in['evaluation']['allow_unsafe_local'] = False
    with pytest.raises(ValueError, match='allow_unsafe_local'):
        validate_formal_config(missing_mbpp_opt_in)

    mixed_backends = copy.deepcopy(config)
    mixed_backends['transfer']['backend'] = 'docker'
    with pytest.raises(ValueError, match='same execution backend'):
        validate_formal_config(mixed_backends)


def test_local_suite_resume_rejects_changed_python_runtime(tmp_path, fixture_runtime, monkeypatch):
    config = config_for(tmp_path)
    config['evaluation'].update(backend='local', allow_unsafe_local=True)
    config['transfer'].update(backend='local', allow_unsafe_local=True)
    open_suite(config)
    monkeypatch.setattr('improving.formal_study.execution_runtime_identity',
                        lambda _: {'backend': 'local', 'python': 'changed'})
    with pytest.raises(ValueError, match='changed'):
        open_suite(config, resume=True)


def test_formal_confirm_report_export_and_immutable_evidence(tmp_path, fixture_runtime):
    config = config_for(tmp_path)
    result = run_formal(config, stage='confirm')
    assert len(result['completed_jobs']) == 5
    run_formal(config, stage='report', resume=True)
    root = Path(config['output_dir'])
    report = json.loads((root / 'report/summary.json').read_text())
    assert report['primary_decision'] == 'supported'
    assert any(c['status'] == 'pending' and c['phase'] == 'retention' for c in report['comparisons'])
    assert any(c['status'] == 'incomparable_decoding' and c['reference'] == 'ssd' for c in report['comparisons'])
    run_formal(config, stage='export', resume=True)
    with tarfile.open(root / 'evidence/compact.tar.gz') as archive:
        names = archive.getnames()
        assert 'report/per_task.jsonl' in names
        assert not any(name.endswith('.verified.jsonl') for name in names)
        assert any(name.endswith('.metrics.json') for name in names)
    run_formal(config, stage='export', resume=True, include_programs=True)
    with tarfile.open(root / 'evidence/programs.tar.gz') as archive:
        assert any(name.endswith('.verified.jsonl') for name in archive.getnames())
    metrics = root / 'confirm/seed_43/spectral_soft/round_1/evaluation.metrics.json'
    metrics.write_text(metrics.read_text() + '\n')
    with pytest.raises(ValueError, match='sealed'):
        build_formal_report(root / 'suite.json')


def test_single_job_execution_cannot_manufacture_complete_result(tmp_path, fixture_runtime):
    config = config_for(tmp_path)
    result = run_formal(config, stage='confirm', job_id='confirm_seed43')
    assert result['completed_jobs'] == ['confirm_seed43']
    run_formal(config, stage='report', resume=True)
    report = json.loads((Path(config['output_dir']) / 'report/summary.json').read_text())
    assert report['primary_decision'] == 'pending'
    with pytest.raises(ValueError, match='No job'):
        run_formal(config, stage='confirm', job_id='retention_seed43', resume=True)


def test_formal_validate_cli_loads_no_model_and_writes_nothing(tmp_path, monkeypatch, capsys):
    config = config_for(tmp_path)
    path = tmp_path / 'formal.yaml'
    path.write_text(yaml.safe_dump(config))
    monkeypatch.setattr('improving.formal_study._resolve_model', lambda _: pytest.fail('network/model resolution during validation'))
    assert main(['formal', '--config', str(path), '--stage', 'validate']) == 0
    assert json.loads(capsys.readouterr().out)['valid'] is True
    assert not Path(config['output_dir']).exists()
