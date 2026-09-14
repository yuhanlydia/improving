"""Deterministic per-batch generation with atomic resumable chunks."""
from __future__ import annotations

import json
from pathlib import Path

import torch

from .modeling import render_prompt, seed_everything
from .utils import atomic_json, stable_hash


def generate_to_file(model, tokenizer, tasks, output_path, settings, *, seed=42,
                     model_identity='', method='base', round_index=0, stage='evaluation', resume=False):
    from .data import validate_tasks, validate_completions, write_jsonl
    validate_tasks(tasks)
    count = int(settings.get('samples', 64))
    batch_size = int(settings.get('batch_size', 1))
    max_new = int(settings.get('max_new_tokens', 512))
    temperature = float(settings.get('temperature', .8))
    top_p = float(settings.get('top_p', .95))
    top_k = int(settings.get('top_k', 0))
    if min(count, batch_size, max_new) < 1 or temperature <= 0 or not 0 < top_p <= 1 or top_k < 0:
        raise ValueError('Invalid sampling parameters')
    path = Path(output_path)
    chunks = path.with_suffix(path.suffix + '.parts')
    manifest_path = chunks / 'manifest.json'
    prompts = {task['task_id']: render_prompt(tokenizer, task) for task in tasks}
    manifest = {'model_identity': model_identity, 'prompts': stable_hash(prompts),
                'settings': settings, 'seed': seed, 'method': method, 'round': round_index,
                'stage': stage, 'format': 1}
    if manifest_path.exists():
        if not resume:
            raise FileExistsError(f'Generation already exists: {chunks}; use --resume')
        if json.loads(manifest_path.read_text()) != manifest:
            raise ValueError('Resume protocol differs from saved generation manifest')
    elif path.exists() or (chunks.exists() and any(chunks.iterdir())):
        raise ValueError('Existing outputs have no matching manifest; use a new output path')
    else:
        atomic_json(manifest_path, manifest)
    model.eval()
    device = next(model.parameters()).device
    all_records = []
    eos_ids = model.generation_config.eos_token_id
    eos_ids = set(eos_ids if isinstance(eos_ids, list) else [eos_ids]) - {None}
    if tokenizer.eos_token_id is not None:
        eos_ids.add(tokenizer.eos_token_id)
    for task in tasks:
        prompt = prompts[task['task_id']]
        ids = tokenizer.encode(prompt, add_special_tokens=False)
        if not ids or len(ids) > int(settings.get('max_prompt_tokens', 1024)):
            raise ValueError(f'Empty/overlong prompt {task["task_id"]}; no task truncation is performed')
        context_limit = getattr(model.config, 'max_position_embeddings', None)
        if context_limit and len(ids) + max_new > context_limit:
            raise ValueError(f'Prompt plus generation exceeds model context: {task["task_id"]}')
        for start in range(0, count, batch_size):
            size = min(batch_size, count - start)
            batch_seed = int(stable_hash([seed, task['task_id'], round_index, stage, start])[:8], 16)
            chunk_path = chunks / f'{stable_hash(task["task_id"])[:24]}.{start:06d}.json'
            if chunk_path.exists():
                records = json.loads(chunk_path.read_text())
                if (len(records) != size or any(r['task_id'] != task['task_id'] or
                        r['sample_id'] != start + j or r.get('batch_seed') != batch_seed
                        for j, r in enumerate(records))):
                    raise ValueError(f'Corrupt generation chunk: {chunk_path}')
            else:
                seed_everything(batch_seed)
                inputs = torch.tensor([ids], device=device)
                with torch.inference_mode():
                    generated = model.generate(
                        input_ids=inputs, attention_mask=torch.ones_like(inputs),
                        do_sample=True, temperature=temperature, top_p=top_p, top_k=top_k,
                        max_new_tokens=max_new, num_return_sequences=size,
                        pad_token_id=tokenizer.pad_token_id, use_cache=True
                    )
                records = []
                for j, sequence in enumerate(generated[:, len(ids):].tolist()):
                    end = next((i + 1 for i, t in enumerate(sequence) if t in eos_ids), len(sequence))
                    token_ids = sequence[:end]
                    records.append({'task_id': task['task_id'], 'sample_id': start + j,
                                    'completion': tokenizer.decode(token_ids, skip_special_tokens=True),
                                    'completion_ids': token_ids, 'prompt_tokens': len(ids),
                                    'generation_tokens': len(token_ids), 'seed': seed,
                                    'batch_seed': batch_seed, 'round': round_index, 'method': method,
                                    'finish_reason': 'eos' if token_ids and token_ids[-1] in eos_ids else 'length',
                                    'prompt_sha256': stable_hash(prompt)})
                atomic_json(chunk_path, records)
            all_records.extend(records)
    validate_completions(all_records, tasks)
    write_jsonl(path, all_records)
    atomic_json(path.with_suffix(path.suffix + '.budget.json'), {
        'samples': len(all_records), 'tasks': len(tasks),
        'prompt_tokens': sum(r['prompt_tokens'] for r in all_records),
        'generation_tokens': sum(r['generation_tokens'] for r in all_records),
        'length_capped_samples': sum(r['finish_reason'] == 'length' for r in all_records),
        'protocol': manifest})
    return all_records
