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
