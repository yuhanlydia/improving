"""Consistent prompt serialization, causal labels, and single-device HF loading."""
from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
import random

import numpy as np
import torch


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def render_prompt(tokenizer, task: dict) -> str:
    """One identical native template for every method and training/evaluation stage."""
    prompt = task['prompt']
    if getattr(tokenizer, 'chat_template', None):
        return tokenizer.apply_chat_template(
            [{'role': 'user', 'content': prompt}], tokenize=False, add_generation_prompt=True
        )
    return prompt


def encode_example(tokenizer, prompt: str, completion: str, *, max_length: int,
                   loss_scope: str = 'completion', spans=None,
                   completion_ids: list[int] | None = None, append_eos: bool = True) -> dict:
    """Concatenate tokenized prefix and continuation, preserving the generation prefix.

    Character spans address the reference completion only. Padding labels are masked
    by POSITION rather than by pad token ID, since many LMs reuse EOS for padding.
    """
    if loss_scope not in {'completion', 'all'}:
        raise ValueError('loss_scope must be completion or all')
    prefix = tokenizer.encode(prompt, add_special_tokens=False)
    if not prefix or len(prefix) >= max_length:
        raise ValueError('Empty/overlong prompt leaves no target; increase max_length')
    if spans is not None:
        if not spans or any(len(s) != 2 or not 0 <= s[0] < s[1] <= len(completion) for s in spans):
            raise ValueError('calibration_spans must be valid nonempty completion character intervals')
        encoded = tokenizer(completion, add_special_tokens=False, return_offsets_mapping=True)
        suffix = encoded['input_ids']
        target = [token if any(a < end and b > start for a, b in spans) else -100
                  for token, (start, end) in zip(suffix, encoded['offset_mapping'])]
    else:
        suffix = list(completion_ids) if completion_ids is not None else tokenizer.encode(
            completion, add_special_tokens=False)
        target = suffix.copy()
        eos = tokenizer.eos_token_id
        if append_eos and completion_ids is None and eos is not None and (not suffix or suffix[-1] != eos):
            suffix.append(eos)
            target.append(eos)
    labels = (prefix.copy() if loss_scope == 'all' and spans is None else [-100] * len(prefix)) + target
    ids = (prefix + suffix)[:max_length]
    labels = labels[:max_length]
    if not any(x != -100 for x in labels[1:]):
        raise ValueError('No supervised next-token target remains after truncation')
    return {'input_ids': ids, 'attention_mask': [1] * len(ids), 'labels': labels,
            'truncated_tokens': max(0, len(prefix) + len(suffix) - max_length)}


def collate_examples(examples: list[dict], pad_token_id: int) -> dict[str, torch.Tensor]:
    if not examples:
        raise ValueError('Cannot collate an empty batch')
    width = max(len(x['input_ids']) for x in examples)
    batch = {}
    for key, padding in [('input_ids', pad_token_id), ('attention_mask', 0), ('labels', -100)]:
        batch[key] = torch.tensor([x[key] + [padding] * (width - len(x[key])) for x in examples],
                                  dtype=torch.long)
    return batch


def load_model(settings: dict, checkpoint: str | Path | None = None):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    name = str(checkpoint or settings['name'])
    device = settings.get('device', 'auto')
    if device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    dtype_name = settings.get('dtype', 'bfloat16') if device.startswith('cuda') else 'float32'
    if dtype_name == 'bfloat16' and device.startswith('cuda') and not torch.cuda.is_bf16_supported():
        raise ValueError('This GPU does not support BF16; use dtype float32 or a compatible GPU')
    if dtype_name not in {'float32', 'bfloat16'}:
        raise ValueError('This tested training path supports float32 or bfloat16; FP16 needs a scaler')
    kwargs = {'trust_remote_code': False}
    if checkpoint is None and settings.get('revision'):
        kwargs['revision'] = settings['revision']
    tokenizer = AutoTokenizer.from_pretrained(name, use_fast=True, **kwargs)
    if tokenizer.pad_token_id is None:
        if tokenizer.eos_token_id is None:
            raise ValueError('Tokenizer must define padding or EOS')
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        name, torch_dtype=getattr(torch, dtype_name),
        attn_implementation=settings.get('attn_implementation', 'sdpa'), **kwargs
    ).to(device)
    return model, tokenizer


def autocast_for(model):
    parameter = next(model.parameters())
    if parameter.device.type == 'cuda' and parameter.dtype == torch.bfloat16:
        return torch.autocast('cuda', dtype=torch.bfloat16)
    return nullcontext()
