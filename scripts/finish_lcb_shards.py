#!/usr/bin/env python3
"""Generate a disjoint final sample batch for an existing single-task-batch run.

The original evaluator remains the sole owner of the final JSONL and scoring.
This helper only writes atomic per-task chunks, using the frozen generator's
seed, prompt, and sampling logic. It requires task_batch_size to resolve to 1.
"""
import argparse
import builtins
import json
from pathlib import Path

from improving.data import read_jsonl
from improving.modeling import load_model
from improving.utils import stable_hash
import improving.generation as generation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--rank', type=int, required=True)
    parser.add_argument('--workers', type=int, required=True)
    parser.add_argument('--start', type=int, default=12)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    run = args.run.resolve()
    manifest = json.loads((run / 'base/evaluation.jsonl.parts/manifest.json').read_text())
    settings = manifest['settings']
    tasks = read_jsonl(run / 'tasks/eval.jsonl')
    count, batch = settings['samples'], settings['batch_size']
    effective_task_batch = min(settings['task_batch_size'],
                               max(1, settings['sequence_batch_size'] // batch))
    if not (0 <= args.rank < args.workers and args.workers >= 2):
        raise ValueError('invalid worker partition')
    if effective_task_batch != 1 or count != 16 or batch != 4 or args.start not in range(0, 16, 4):
        raise ValueError('this helper requires the pinned single-task-batch protocol')
    selected = list(range(args.rank, len(tasks), args.workers))
    parts = run / 'base/evaluation.jsonl.parts'
    target = [parts / f'{stable_hash(tasks[i]["task_id"])[:24]}.{args.start:06d}.json'
              for i in selected]
    if args.validate_only:
        print(json.dumps({'run': str(run), 'rank': args.rank, 'workers': args.workers,
                          'start': args.start, 'assigned': len(target),
                          'already_present': sum(path.exists() for path in target)}))
        return
    config = json.loads((run / 'manifest.json').read_text())['config']['model']
    if config['name'] != 'google/gemma-3-4b-it':
        raise ValueError('Gemma-only eager attention helper')
    model, tokenizer = load_model({**config, 'attn_implementation': 'eager'})
    original_range = builtins.range
    def selected_range(*values):
        if values == (0, count, batch):
            return (args.start,)
        if values == (0, len(tasks), 1):
            return selected
        return original_range(*values)
    generation.range = selected_range
    try:
        # Validation of the full population is expected to fail here: this
        # process owns only its assigned chunks. The original run finalizes.
        generation.generate_to_file(model, tokenizer, tasks,
            run / 'base/evaluation.jsonl', settings,
            seed=manifest['seed'], model_identity=manifest['model_identity'],
            method=manifest['method'], round_index=manifest['round'],
            stage=manifest['stage'], resume=True)
    except ValueError:
        if not all(path.exists() for path in target):
            raise
    else:
        raise RuntimeError('partitioned generator unexpectedly finalized output')
    finally:
        del generation.range
        del model
    for path in target:
        records = json.loads(path.read_text())
        if len(records) != batch or [r['sample_id'] for r in records] != list(original_range(args.start, args.start + batch)):
            raise ValueError(f'Invalid generated chunk: {path}')
    print(f'completed {len(target)} assigned chunks')


if __name__ == '__main__':
    main()
