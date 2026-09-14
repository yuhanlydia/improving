"""Raw-completion LoRA SFT shared by every experimental arm."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import tempfile

import torch
from torch.utils.data import DataLoader

from .modeling import autocast_for, collate_examples, encode_example, render_prompt, seed_everything


def train_on_records(model, tokenizer, tasks, records, settings, output_dir, *, seed=42):
    from peft import LoraConfig, get_peft_model
    from transformers import get_cosine_schedule_with_warmup
    from .data import validate_tasks, validate_completions
    validate_tasks(tasks)
    validate_completions(records, tasks)
    if not records:
        raise ValueError('No raw completions to train on')
    output_dir = Path(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f'Refusing to overwrite checkpoint: {output_dir}')
    task_map = {x['task_id']: x for x in tasks}
    if set(task_map) != {x['task_id'] for x in records}:
        raise ValueError('Training corpus must include every training task')
    seed_everything(seed)
    examples = [encode_example(
        tokenizer, render_prompt(tokenizer, task_map[r['task_id']]), r['completion'],
        max_length=settings.get('max_length', 1536),
        loss_scope=settings.get('loss_scope', 'all'), completion_ids=r.get('completion_ids'),
        append_eos=r.get('completion_ids') is None and r.get('finish_reason') != 'length'
    ) for r in records]  # Deliberately no `correct`, strategy, length or AST filtering.
    batch_size = int(settings.get('batch_size', 1))
    accumulation = int(settings.get('gradient_accumulation_steps', 16))
    epochs = int(settings.get('epochs', 5))
    if min(batch_size, accumulation, epochs) < 1:
        raise ValueError('batch_size, accumulation and epochs must be positive')
    loader = DataLoader(examples, batch_size=batch_size, shuffle=True,
                        generator=torch.Generator().manual_seed(seed),
                        collate_fn=lambda xs: collate_examples(xs, tokenizer.pad_token_id))
    model = get_peft_model(model, LoraConfig(
        task_type='CAUSAL_LM', r=int(settings.get('lora_rank', 8)),
        lora_alpha=int(settings.get('lora_alpha', 8)),
        lora_dropout=float(settings.get('lora_dropout', .05)), bias='none',
        target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj']
    ))
    model.config.use_cache = False
    if settings.get('gradient_checkpointing', True):
        # Non-reentrant checkpointing works with frozen embeddings; no input hooks.
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),
                                 lr=float(settings.get('learning_rate', 1e-5)),
                                 weight_decay=float(settings.get('weight_decay', .01)))
    total_steps = math.ceil(len(loader) / accumulation) * epochs
    scheduler = get_cosine_schedule_with_warmup(
        optimizer, int(total_steps * float(settings.get('warmup_ratio', .03))), total_steps
    )
    device = next(model.parameters()).device
    model.train()
    losses, optimizer_steps = [], 0
    optimizer.zero_grad(set_to_none=True)
    for _epoch in range(epochs):
        for index, batch in enumerate(loader):
            # Normalize by actual microbatches in final incomplete accumulation group.
            group_start = (index // accumulation) * accumulation
            divisor = min(accumulation, len(loader) - group_start)
            batch = {k: v.to(device) for k, v in batch.items()}
            with autocast_for(model):
                loss = model(**batch).loss
            if not torch.isfinite(loss):
                raise FloatingPointError('Nonfinite SFT loss; checkpoint not saved')
            (loss / divisor).backward()
            losses.append(float(loss.detach().cpu()))
            if (index + 1) % accumulation == 0 or index + 1 == len(loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), float(settings.get('max_grad_norm', 1.0)))
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                optimizer_steps += 1
    # A single merged checkpoint is the next round's model, never an adapter pool.
    model.gradient_checkpointing_disable()
    merged = model.merge_and_unload(safe_merge=True)
    merged.config.use_cache = True
    merged.eval()
    stats = {'examples': len(examples), 'optimizer_steps': optimizer_steps,
             'mean_loss': sum(losses) / len(losses), 'epochs': epochs,
             'truncated_examples': sum(x['truncated_tokens'] > 0 for x in examples),
             'truncated_tokens': sum(x['truncated_tokens'] for x in examples),
             'supervised_tokens_per_epoch': sum(sum(t != -100 for t in x['labels'][1:]) for x in examples),
             'trainable_parameter_count': sum(p.numel() for group in optimizer.param_groups for p in group['params']),
             'loss_scope': settings.get('loss_scope', 'all'), 'seed': seed}
    # Interrupted saves cannot look like a resumable completed checkpoint.
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f'.{output_dir.name}.saving-', dir=output_dir.parent) as temporary:
        temporary_path = Path(temporary)
        merged.save_pretrained(temporary_path, safe_serialization=True)
        tokenizer.save_pretrained(temporary_path)
        (temporary_path / 'training_stats.json').write_text(json.dumps(stats, indent=2) + '\n')
        if output_dir.exists():
            output_dir.rmdir()  # Only an empty destination was permitted above.
        os.replace(temporary_path, output_dir)
    return merged, stats
