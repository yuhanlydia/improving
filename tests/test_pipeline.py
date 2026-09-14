import json
import pytest
from helpers import tiny_model_and_tokenizer
from improving.pipeline import run_experiment, load_config, checkpoint_fingerprint, record_stage
from improving.data import write_jsonl


def test_config_rejects_unknown_method_and_incomplete_sample_budget(tmp_path):
    path = tmp_path / 'bad.yaml'
    path.write_text('methods: [magic]\n')
    with pytest.raises(ValueError):
        load_config(path)


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
