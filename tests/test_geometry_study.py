import copy
import csv
import importlib.util
import json

import pytest
import torch

from helpers import tiny_model_and_tokenizer
from improving.data import write_jsonl, read_jsonl
from improving.geometry_study import (GeometryStudy, geometry_splits, geometry_budget,
                                      run_geometry, load_geometry_config)
from improving.cli import main


def setup(tmp_path):
    paths = {}
    for index, split in enumerate(('train', 'calibration', 'validation', 'eval')):
        tasks = [{'task_id': f'fixture/{split}', 'prompt': f'Write a function {index}',
                  'source': 'trusted-fixture', 'split': split, 'entry_point': 'f',
                  'tests': 'assert f() == 1', 'reference': 'def f(): return 1'}]
        path = tmp_path / f'{split}.jsonl'
        write_jsonl(path, tasks)
        paths[split] = str(path)
    return {'model': {'name': 'fixture'}, 'data': paths, 'output_dir': str(tmp_path / 'run'),
            'generation': {'max_new_tokens': 10, 'batch_size': 2},
            'discovery': {'samples': 3, 'max_correct_per_task': 2, 'format_controls': True},
            'extraction': {'max_length': 120, 'max_rank': 2, 'method': 'exact'},
            'geometry': {'ranks': [1, 2], 'bank_sizes': [1, 2], 'max_pairs_per_task': 2},
            'relations': {'enabled': True, 'max_tasks': 1, 'rank': 1, 'samples': 2, 'interpolation': [.5]},
            'selection': {'samples': 2, 'correctness_tolerance': 0.0},
            'final': {'samples': 2},
            'evaluation': {'backend': 'local', 'allow_unsafe_local': True, 'workers': 1,
                           'bootstrap_samples': 10, 'correct_budget': 1}}


def fixture_generator(model, tokenizer, tasks, output_path, settings, **kwargs):
    # Deterministic trusted Python programs exercise real verification, gradients,
    # geometry, folding and scoring. This fixture does not simulate performance.
    choices = ['def f():\n    return 1\n', 'def f():\n    x = 1\n    return x\n', 'def f():\n    return 2\n']
    rows = [{'task_id': task['task_id'], 'sample_id': i, 'completion': choices[i % 3],
             'finish_reason': 'eos'} for task in tasks for i in range(settings['samples'])]
    write_jsonl(output_path, rows)
    return rows


def test_frozen_geometry_entire_flow_and_resume(tmp_path, monkeypatch):
    monkeypatch.setattr('improving.geometry_study.generate_to_file', fixture_generator)
    config = setup(tmp_path)
    model, tokenizer = tiny_model_and_tokenizer()
    weights = {name: value.detach().clone() for name, value in model.state_dict().items()}
    result = run_geometry(config, model=model, tokenizer=tokenizer)
    root = tmp_path / 'run'
    assert result['completed_stage'] == 'all'
    assert (root / 'report' / 'summary.md').is_file()
    report = json.loads((root / 'report' / 'summary.json').read_text())
    assert report['final_arms'] == ['plain', 'learned_bank', 'random_bank', 'pooled']
    assert report['lora_trained'] is False
    assert 'learned_bank_vs_random_bank' in report['comparisons']
    assert 'learned_bank_vs_pooled' in report['comparisons']
    with (root / 'report' / 'geometry_pairs.csv').open() as stream:
        pairs = list(csv.DictReader(stream))
    assert pairs and 'overlap_min' in pairs[0] and 'metrics' not in pairs[0]
    if importlib.util.find_spec('matplotlib') is not None:
        assert (root / 'report' / 'geometry_overlap.png').is_file()
        assert (root / 'report' / 'generation_metrics.png').is_file()
    selected = json.loads((root / 'selection' / 'locked.json').read_text())
    assert selected['selection_split'] == 'validation'
    assert selected['validation_task_ids'] == ['fixture/validation']
    bank = torch.load(root / 'selection' / 'bank.pt', weights_only=True)
    assert all(item['task_id'] in {'fixture/train', 'fixture/calibration'} for item in bank)
    for name, value in model.state_dict().items():
        torch.testing.assert_close(value, weights[name], rtol=0, atol=0)
    # Repeated execution reuses sealed extraction/trials and leaves weights fixed.
    run_geometry(config, resume=True, model=model, tokenizer=tokenizer)
    for name, value in model.state_dict().items():
        torch.testing.assert_close(value, weights[name], rtol=0, atol=0)
    path = root / 'final' / 'learned_bank' / 'verified.jsonl'
    path.write_text(path.read_text() + '\n')
    with pytest.raises(ValueError, match='Modified'):
        run_geometry(config, stage='evaluate', resume=True, model=model, tokenizer=tokenizer)


def test_split_is_by_question_and_rejects_overlap(tmp_path):
    config = setup(tmp_path)
    splits = geometry_splits(config)
    assert [len(splits[key]) for key in ('train', 'validation', 'eval')] == [2, 1, 1]
    assert {row['split'] for row in splits['train']} == {'train'}
    rows = read_jsonl(config['data']['eval'])
    rows[0]['prompt'] = read_jsonl(config['data']['train'])[0]['prompt']
    write_jsonl(config['data']['eval'], rows)
    with pytest.raises(ValueError, match='leakage'):
        geometry_splits(config)


def test_changed_config_cannot_resume_or_reselect_after_final(tmp_path):
    config = setup(tmp_path)
    model, tokenizer = tiny_model_and_tokenizer()
    study = GeometryStudy(config, model=model, tokenizer=tokenizer)
    changed = copy.deepcopy(config)
    changed['seed'] = 123
    with pytest.raises(ValueError, match='differs'):
        GeometryStudy(changed, resume=True, model=model, tokenizer=tokenizer)
    (study.root / 'final').mkdir()
    with pytest.raises(ValueError, match='Cannot select'):
        study.select()


def test_zero_correct_is_reported_without_fabricated_subspaces(tmp_path, monkeypatch):
    config = setup(tmp_path)
    config['relations']['enabled'] = False
    def wrong(model, tokenizer, tasks, output_path, settings, **kwargs):
        rows = [{'task_id': task['task_id'], 'sample_id': i, 'completion': 'def f(): return 2'}
                for task in tasks for i in range(settings['samples'])]
        write_jsonl(output_path, rows)
        return rows
    monkeypatch.setattr('improving.geometry_study.generate_to_file', wrong)
    model, tokenizer = tiny_model_and_tokenizer()
    run_geometry(config, model=model, tokenizer=tokenizer)
    root = tmp_path / 'run'
    assert json.loads((root / 'subspaces' / 'index.json').read_text()) == []
    lock = json.loads((root / 'selection' / 'locked.json').read_text())
    assert lock['status'] == 'no_eligible_bank'
    assert json.loads((root / 'final' / 'index.json').read_text())['arms'] == ['plain']


def test_cli_validate_has_no_model_load(tmp_path, capsys):
    import yaml
    config = setup(tmp_path)
    path = tmp_path / 'config.yaml'
    path.write_text(yaml.safe_dump(config))
    assert main(['geometry', '--config', str(path), '--stage', 'validate']) == 0
    assert json.loads(capsys.readouterr().out)['valid']


@pytest.mark.parametrize('span_mode', ['completion', 'explicit'])
def test_optional_format_control_cannot_abort_valid_extraction(tmp_path, monkeypatch, span_mode):
    from improving.geometry_extraction import collect_solution_subspaces, SolutionTooLongError
    def generate(model, tokenizer, tasks, output_path, settings, **kwargs):
        completion = 'def f(): return 1'
        rows = [{'task_id': task['task_id'], 'sample_id': i, 'completion': completion,
                 'loss_spans': [[0, len(completion)]]}
                for task in tasks for i in range(settings['samples'])]
        write_jsonl(output_path, rows)
        return rows
    def extract(model, tokenizer, task, record, settings):
        if record.get('control'):
            raise SolutionTooLongError('Formatted control exceeds context')
        return collect_solution_subspaces(model, tokenizer, task, record, settings)
    monkeypatch.setattr('improving.geometry_study.generate_to_file', generate)
    monkeypatch.setattr('improving.geometry_extraction.collect_solution_subspaces', extract)
    config = setup(tmp_path)
    config['extraction']['span_mode'] = span_mode
    model, tokenizer = tiny_model_and_tokenizer()
    study = GeometryStudy(config, model=model, tokenizer=tokenizer)
    study.discover()
    study.extract()
    artifacts = study.artifacts(include_controls=True)
    assert len(artifacts) == 4
    assert not any(item['metadata']['is_format_control'] for item in artifacts)
    controls = json.loads((study.root / 'analysis' / 'format_verification.json').read_text())
    assert any(row['status'] == ('skipped' if span_mode == 'explicit' else 'extraction_skipped')
               for row in controls)


def test_declared_configs_validate_and_budget_is_explicit():
    from pathlib import Path
    for path in Path('configs').glob('geometry_*.yaml'):
        config = load_geometry_config(path)
        assert config['evaluation']['backend'] == 'docker'
        assert config['extraction']['span_mode'] == 'completion'
        splits = {name: [None] * n for name, n in [('train', 64), ('validation', 16), ('eval', 20)]}
        if '100' in path.name:
            assert geometry_budget(config, splits)['total_candidates_upper_bound'] == 8832
