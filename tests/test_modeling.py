import pytest
from tests.helpers import tiny_model_and_tokenizer
from improving.modeling import encode_example, collate_examples, render_prompt


def test_completion_targets_and_real_eos_are_not_masked_as_padding():
    _, tok = tiny_model_and_tokenizer()
    tok.pad_token = tok.eos_token
    one = encode_example(tok, 'Write a function', 'return 1', max_length=32)
    two = encode_example(tok, 'Write a function', 'return x + 1', max_length=32)
    batch = collate_examples([one, two], tok.pad_token_id)
    assert one['labels'][:3] == [-100] * 3
    assert one['labels'][-1] == tok.eos_token_id
    assert batch['labels'][0, len(one['input_ids']) - 1].item() == tok.eos_token_id
    assert batch['labels'][0, -1].item() == -100


def test_spans_mask_only_reference_targets_and_reject_empty_target():
    _, tok = tiny_model_and_tokenizer()
    ex = encode_example(tok, 'Write', 'return 1', max_length=16, spans=[[7, 8]])
    assert [x for x in ex['labels'] if x != -100] == [tok.convert_tokens_to_ids('1')]
    with pytest.raises(ValueError):
        encode_example(tok, 'Write', 'return 1', max_length=16, spans=[[50, 51]])


def test_prompt_is_preserved_and_overlong_prompt_fails():
    _, tok = tiny_model_and_tokenizer()
    assert render_prompt(tok, {'prompt': 'Write a function'}) == 'Write a function'
    with pytest.raises(ValueError):
        encode_example(tok, 'Write a function', 'return 1', max_length=3)


def test_length_capped_generation_does_not_create_a_false_eos_target():
    _, tok = tiny_model_and_tokenizer()
    ids = tok.encode('return 1', add_special_tokens=False)
    ex = encode_example(tok, 'Write', 'return 1', max_length=16,
                        completion_ids=ids, append_eos=False)
    assert ex['labels'][-1] == tok.convert_tokens_to_ids('1')
    assert tok.eos_token_id not in ex['labels']


def test_native_generated_ids_are_authoritative_even_with_alternate_stop_token():
    _, tok = tiny_model_and_tokenizer()
    native_ids = tok.encode('return world', add_special_tokens=False)
    ex = encode_example(tok, 'Write', 'return world', max_length=16, completion_ids=native_ids)
    assert ex['input_ids'][1:] == native_ids
