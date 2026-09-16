import pytest
from tests.helpers import tiny_model_and_tokenizer
from improving.generation import generate_to_file


def test_generation_preserves_all_samples_and_resume_is_identical(tmp_path):
    model, tok = tiny_model_and_tokenizer()
    tasks = [{'task_id': 'toy/1', 'prompt': 'Write a function', 'source': 'fixture', 'split': 'test'}]
    settings = {'samples': 3, 'batch_size': 2, 'max_new_tokens': 4,
                'max_prompt_tokens': 32, 'temperature': 0.8, 'top_p': 0.95, 'top_k': 0}
    path = tmp_path / 'samples.jsonl'
    records = generate_to_file(model, tok, tasks, path, settings, seed=42, model_identity='tiny')
    again = generate_to_file(model, tok, tasks, path, settings, seed=42, model_identity='tiny', resume=True)
    assert records == again
    assert [r['sample_id'] for r in records] == [0, 1, 2]
    assert all(r['generation_tokens'] <= 4 for r in records)
    with pytest.raises(ValueError):
        generate_to_file(model, tok, tasks, path, {**settings, 'temperature': 1.0},
                         seed=42, model_identity='tiny', resume=True)


def test_generation_batches_multiple_tasks_and_resumes_by_fixed_group(tmp_path, monkeypatch):
    model, tok = tiny_model_and_tokenizer()
    tasks = [
        {'task_id': f'toy/{i}', 'prompt': prompt, 'source': 'fixture', 'split': 'test'}
        for i, prompt in enumerate([
            'Write a function', 'Sort the list', 'hello', 'Write a function', 'Sort the list'
        ])
    ]
    settings = {'samples': 2, 'batch_size': 2, 'task_batch_size': 4,
                'sequence_batch_size': 4, 'max_new_tokens': 3,
                'max_prompt_tokens': 32, 'temperature': 0.8, 'top_p': 0.95, 'top_k': 0}
    calls = []
    native_generate = model.generate

    def counted_generate(*args, **kwargs):
        calls.append((kwargs['input_ids'].shape[0], kwargs['num_return_sequences']))
        return native_generate(*args, **kwargs)

    monkeypatch.setattr(model, 'generate', counted_generate)
    path = tmp_path / 'samples.jsonl'
    records = generate_to_file(model, tok, tasks, path, settings, seed=42, model_identity='tiny')
    assert calls == [(2, 2), (2, 2), (1, 2)]
    assert [(row['task_id'], row['sample_id']) for row in records] == [
        (task['task_id'], sample) for task in tasks for sample in range(2)
    ]
    calls.clear()
    assert generate_to_file(model, tok, tasks, path, settings, seed=42,
                            model_identity='tiny', resume=True) == records
    assert calls == []
