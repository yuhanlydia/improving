import json
import pytest
from helpers import tiny_model_and_tokenizer
from improving.pipeline import (run_experiment, load_config, checkpoint_fingerprint,
                                record_stage, evaluate_file, validate_config,
                                _diagnostic_protocol, _validate_base_outputs)
from improving.data import read_jsonl, write_jsonl


def test_config_rejects_unknown_method_and_incomplete_sample_budget(tmp_path):
    path = tmp_path / 'bad.yaml'
    path.write_text('methods: [magic]\n')
    with pytest.raises(ValueError):
        load_config(path)


def test_config_rejects_unknown_code_extraction_mode():
    config = {
        'model': {'name': 'fixture'}, 'output_dir': 'run', 'methods': ['plain'],
        'data': {name: f'{name}.jsonl' for name in ('train', 'calibration', 'validation', 'eval')},
        'evaluation': {'code_extraction': 'guess'},
    }
    with pytest.raises(ValueError, match='code_extraction'):
        validate_config(config)


def test_config_rejects_correct_diversity_budgets_above_sample_budget():
    config = {
        'model': {'name': 'fixture'}, 'output_dir': 'run', 'methods': ['plain'],
        'data': {name: f'{name}.jsonl' for name in ('train', 'calibration', 'validation', 'eval')},
        'generation': {'eval_samples': 4},
        'evaluation': {'ks': [1, 4], 'correct_budgets': [2, 8]},
    }
    with pytest.raises(ValueError, match='correct_budgets'):
        validate_config(config)


def test_evaluate_file_applies_and_records_first_fence_protocol(tmp_path):
    tasks = [{'task_id': 'Fixture/0', 'prompt': 'Add.', 'source': 'fixture', 'split': 'eval',
              'entry_point': 'add', 'tests': 'assert add(2, 3) == 5'}]
    records = [{'task_id': 'Fixture/0', 'sample_id': 0,
                'completion': 'Prose.\n```python\ndef add(a, b): return a + b\n```\nExplanation.'}]
    summary = evaluate_file(
        tasks, records, tmp_path / 'evaluation.jsonl',
        {'backend': 'local', 'allow_unsafe_local': True, 'workers': 1,
         'code_extraction': 'first_fence', 'ks': [1], 'correct_budget': 1,
         'correct_budgets': [1, 3]},
        expected_samples=1)
    assert summary['aggregate']['correct_count'] == 1
    assert summary['protocol']['evaluation']['code_extraction'] == 'first_fence'
    assert summary['protocol']['correct_budgets'] == [1, 3]


def test_checkpoint_fingerprint_hashes_shard_contents_and_tokenizer(tmp_path):
    (tmp_path / 'config.json').write_text('{}')
    (tmp_path / 'model.safetensors.index.json').write_text('{"weight_map":{}}')
    shard = tmp_path / 'model-00001-of-00002.safetensors'
    shard.write_bytes(b'weights1')
    first = checkpoint_fingerprint(tmp_path)
    shard.write_bytes(b'weights2')
    assert checkpoint_fingerprint(tmp_path) != first
    second = checkpoint_fingerprint(tmp_path)
    (tmp_path / 'tokenizer.json').write_text('{"new":"tokenizer"}')
    assert checkpoint_fingerprint(tmp_path) != second


def test_stage_resume_preserves_actual_prior_compute_time(tmp_path, monkeypatch):
    values = iter([1.0, 4.0, 10.0, 11.0])
    monkeypatch.setattr('improving.pipeline.time.monotonic', lambda: next(values))
    with record_stage(tmp_path, 'calibration'):
        pass
    with record_stage(tmp_path, 'calibration'):
        pass
    record = json.loads((tmp_path / 'calibration.resources.json').read_text())
    assert record['elapsed_seconds'] == 4.0
    assert len(record['attempts']) == 2


def test_tiny_real_round_and_resume_without_training_again(tmp_path):
    model, tok = tiny_model_and_tokenizer()
    model_dir = tmp_path / 'tiny'
    model.save_pretrained(model_dir)
    tok.save_pretrained(model_dir)
    paths = {}
    prompts = ['Write a function', 'Sort the list', 'hello world', 'Write x']
    for split, prompt in zip(['train', 'calibration', 'validation', 'eval'], prompts):
        path = tmp_path / f'{split}.jsonl'
        write_jsonl(path, [{'task_id': f'{split}/1', 'prompt': prompt,
                            'reference': 'def f ( ) : return 1', 'source': 'fixture', 'split': split}])
        paths[split] = str(path)
    config = {'seed': 42, 'model': {'name': str(model_dir), 'device': 'cpu', 'dtype': 'float32'},
              'data': paths, 'output_dir': str(tmp_path / 'run'), 'methods': ['spectral_soft'], 'rounds': 1,
              'generation': {'train_samples': 1, 'eval_samples': 2, 'batch_size': 2,
                             'max_new_tokens': 4, 'max_prompt_tokens': 32, 'temperature': .8},
              'calibration': {'max_length': 64, 'max_examples': 1, 'tau': 1.0},
              'train': {'epochs': 1, 'batch_size': 1, 'gradient_accumulation_steps': 2,
                        'learning_rate': .01, 'max_length': 64, 'lora_rank': 2,
                        'lora_alpha': 2, 'gradient_checkpointing': False},
              'evaluation': {'backend': 'none', 'ks': [1, 2], 'correct_budget': 1},
              'diagnostics': {'evaluate_generation_policy': True}}
    result = run_experiment(config)
    completed = tmp_path / 'run' / 'spectral_soft' / 'round_1' / 'complete.json'
    before = completed.read_bytes()
    run_experiment(config, resume=True)
    assert completed.read_bytes() == before
    assert result['status'] == 'completed'
    assert (completed.parent / 'model' / 'model.safetensors').exists()
    records = [json.loads(line) for line in (completed.parent / 'evaluation.jsonl').read_text().splitlines()]
    assert len(records) == 2


@pytest.mark.parametrize('key,value', [('eval_samples', 0), ('eval_samples', True),
                                      ('eval_task_limit', -1), ('eval_task_limit', 2.5),
                                      ('evaluate_generation_policy', 'false')])
def test_invalid_diagnostic_settings_fail(key, value):
    config = {'model': {'name': 'fixture'}, 'output_dir': 'run', 'methods': ['random_soft'],
              'data': {name: f'{name}.jsonl' for name in ('train', 'calibration', 'validation', 'eval')},
              'diagnostics': {key: value}}
    with pytest.raises(ValueError, match='diagnostics'):
        validate_config(config)


def test_diagnostic_subset_uses_data_seed_and_keeps_full_protocol_unchanged():
    tasks = [{'task_id': f'q{i}'} for i in range(20)]
    config = {'seed': 7, 'data_seed': 31, 'diagnostics': {'eval_task_limit': 5, 'eval_samples': 8},
              'generation': {'eval_samples': 64},
              'evaluation': {'ks': [1, 8, 32, 64], 'correct_budgets': [4, 8, 16]}}
    selected, samples, settings = _diagnostic_protocol(config, tasks)
    assert len(selected) == 5 and samples == 8
    assert settings['ks'] == [1, 8] and settings['correct_budgets'] == [4, 8]
    assert selected == _diagnostic_protocol({**config, 'seed': 900}, list(reversed(tasks)))[0]
    assert selected != _diagnostic_protocol({**config, 'data_seed': 12}, tasks)[0]
    assert config['evaluation']['ks'] == [1, 8, 32, 64]
    assert config['evaluation']['correct_budgets'] == [4, 8, 16]
    all_tasks, default_samples, _ = _diagnostic_protocol({'generation': {'eval_samples': 64}}, tasks)
    assert all_tasks == tasks and default_samples == 64


def test_diagnostic_budget_real_training_and_verification_preserve_final_budget(tmp_path, monkeypatch):
    model, tokenizer = tiny_model_and_tokenizer()
    model_dir = tmp_path / 'tiny'
    model.save_pretrained(model_dir)
    tokenizer.save_pretrained(model_dir)
    paths = {}
    for split in ('train', 'calibration', 'validation', 'eval'):
        path = tmp_path / f'{split}.jsonl'
        write_jsonl(path, [{'task_id': f'{split}/{i}', 'prompt': f'Write a function {split} {i}',
                            'reference': 'def f(): return 1', 'tests': 'assert f() == 1',
                            'entry_point': 'f', 'source': 'fixture', 'split': split}
                           for i in range(6 if split == 'eval' else 1)])
        paths[split] = str(path)
    calls = []

    def trusted_generation(model, tokenizer, tasks, path, settings, **kwargs):
        calls.append({'path': str(path), 'tasks': [t['task_id'] for t in tasks],
                      'samples': settings['samples'], **kwargs})
        records = [{'task_id': task['task_id'], 'sample_id': i,
                    'completion': f'```python\ndef f(): return {1 if i % 2 == 0 else 2}\n```'}
                   for task in tasks for i in range(settings['samples'])]
        write_jsonl(path, records)
        return records

    monkeypatch.setattr('improving.pipeline.generate_to_file', trusted_generation)
    config = {'seed': 11, 'data_seed': 31,
              'model': {'name': str(model_dir), 'device': 'cpu', 'dtype': 'float32'},
              'data': paths, 'output_dir': str(tmp_path / 'run'), 'methods': ['random_soft'],
              'generation': {'train_samples': 2, 'eval_samples': 4},
              'calibration': {'max_length': 128, 'max_examples': 1, 'tau': 1., 'rank': 2},
              'train': {'epochs': 1, 'batch_size': 2, 'gradient_accumulation_steps': 1,
                        'learning_rate': .001, 'max_length': 128, 'lora_rank': 2,
                        'lora_alpha': 2, 'gradient_checkpointing': False},
              'evaluation': {'backend': 'local', 'allow_unsafe_local': True, 'workers': 1,
                             'ks': [1, 2, 4], 'correct_budget': 2, 'correct_budgets': [1, 2, 4],
                             'bootstrap_samples': 5, 'code_extraction': 'first_fence'},
              'diagnostics': {'evaluate_generation_policy': True, 'eval_task_limit': 2, 'eval_samples': 2}}
    run_experiment(config)
    root = tmp_path / 'run'
    directory = root / 'random_soft' / 'round_1'
    assert [(len(c['tasks']), c['samples']) for c in calls] == [(6, 4), (1, 2), (2, 2), (6, 4)]
    assert all(c['seed'] == 11 for c in calls)
    assert calls[1]['stage'] == 'training'
    assert calls[2]['stage'] == calls[3]['stage'] == 'evaluation'
    selected = [r['task_id'] for r in read_jsonl(root / 'tasks' / 'generation_diagnostic.jsonl')]
    assert calls[2]['tasks'] == selected
    manifest = json.loads((root / 'manifest.json').read_text())
    assert manifest['generation_diagnostic_task_ids'] == selected
    assert manifest['generation_diagnostic_samples'] == 2
    assert set(selected).isdisjoint(manifest['selected_task_ids']['train'])
    assert len(read_jsonl(directory / 'train.jsonl')) == 2  # No correctness filtering.
    assert json.loads((directory / 'model' / 'training_stats.json').read_text())['examples'] == 2
    diagnostic_metrics = json.loads((directory / 'generation_policy.metrics.json').read_text())
    final_metrics = json.loads((directory / 'evaluation.metrics.json').read_text())
    assert '4' not in diagnostic_metrics['aggregate']['pass_at_k']
    assert '4' in final_metrics['aggregate']['pass_at_k']
    assert final_metrics['aggregate']['correct_count'] == 12
    norms = json.loads((directory / 'operator_diagnostics.json').read_text())
    for item in norms.values():
        assert item['matching_absolute_error'] < 1e-12
        assert item['matches_soft_eigenvalues']
        assert item['folded_weight_relative_delta'] > 0
        assert not item['activation_rms_matched'] and not item['output_kl_matched']
    run_experiment(config, resume=True)
    assert len(calls) == 4
    base_done = root / 'base' / 'complete.json'
    state = json.loads(base_done.read_text())
    assert set(state['files']) == {'evaluation.jsonl', 'evaluation.verified.jsonl', 'evaluation.metrics.json'}
    metrics_path = root / 'base' / 'evaluation.metrics.json'
    original_metrics = metrics_path.read_text()
    metrics_path.write_text('{}')
    with pytest.raises(ValueError, match='Base verification or metrics integrity'):
        run_experiment(config, resume=True)
    # Legacy markers have no verified-output hashes. Reverification from their
    # sealed raw samples repairs the metrics and records the explicit migration.
    del state['files']
    base_done.write_text(json.dumps(state))
    _validate_base_outputs(base_done, root / 'base' / 'evaluation.jsonl', read_jsonl(paths['eval']),
                           config['evaluation'], 4, 11)
    assert metrics_path.read_text() == original_metrics
    upgraded = json.loads(base_done.read_text())
    assert upgraded['integrity_migration'] == 'legacy_raw_marker_reverified_before_hashing'
    assert 'evaluation.verified.jsonl' in upgraded['files']
