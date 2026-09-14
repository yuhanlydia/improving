import torch
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from transformers import PreTrainedTokenizerFast, Qwen2Config, Qwen2ForCausalLM


def tiny_model_and_tokenizer():
    vocab = {w: i for i, w in enumerate([
        '<pad>', '<eos>', '<unk>', 'Write', 'a', 'function', 'def', 'f', '(', ')',
        ':', 'return', '1', '2', 'x', '+', 'Sort', 'the', 'list', 'hello', 'world',
    ])}
    raw = Tokenizer(WordLevel(vocab, unk_token='<unk>'))
    raw.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(tokenizer_object=raw, pad_token='<pad>',
                                       eos_token='<eos>', unk_token='<unk>')
    torch.manual_seed(123)
    config = Qwen2Config(vocab_size=len(vocab), hidden_size=16, intermediate_size=32,
                         num_hidden_layers=2, num_attention_heads=2,
                         num_key_value_heads=1, max_position_embeddings=128,
                         pad_token_id=0, eos_token_id=1, attention_dropout=0.0)
    model = Qwen2ForCausalLM(config)
    return model, tokenizer
