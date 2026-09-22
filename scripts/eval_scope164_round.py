#!/usr/bin/env python3
"""Evaluate one retained self-distillation checkpoint on one transfer set."""
import argparse
import gc
import hashlib
import json
from pathlib import Path

from improving.data import assert_disjoint_splits, read_jsonl, validate_tasks
from improving.generation import generate_to_file
from improving.modeling import load_model
from improving.pipeline import checkpoint_fingerprint, evaluate_file
from improving.utils import atomic_json, stable_hash

DATA_ROOT = Path('/root/improving/data/iclr2027')
BENCHMARKS = ('humanevalplus', 'apps_intro', 'codecontests', 'livecodebench')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2**20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-run', type=Path, required=True)
    parser.add_argument('--method', choices=('plain', 'spectral_soft'), required=True)
    parser.add_argument('--round', type=int, choices=range(1, 5), required=True)
    parser.add_argument('--benchmark', choices=BENCHMARKS, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    source = args.source_run.resolve()
    output = args.output_dir.resolve()
    if source == output or source in output.parents:
        raise ValueError('Evaluation output must be separate from source run')
    manifest_path = source / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    config = manifest['config']
    if config.get('seed') != 43 or args.method not in config['methods'] or args.round > config['rounds']:
        raise ValueError('Unexpected training source or round')
    stage = source / args.method / f'round_{args.round}'
    checkpoint = stage / 'model'
    if not args.validate_only and (not (stage / 'complete.json').exists() or not (checkpoint / 'config.json').exists()):
        raise ValueError('Selected checkpoint is incomplete')
    task_path = DATA_ROOT / args.benchmark / 'eval.jsonl'
    prepared = json.loads((task_path.parent / 'manifest.json').read_text())
    tasks = read_jsonl(task_path)
    validate_tasks(tasks)
    task_meta = prepared['output_files']['eval.jsonl']
    if prepared['name'] != args.benchmark or len(tasks) != task_meta['count'] or sha(task_path) != task_meta['sha256']:
        raise ValueError('Prepared benchmark snapshot changed')
    fit = {name: read_jsonl(source / 'tasks' / f'{name}.jsonl') for name in ('train', 'calibration', 'validation')}
    for name, rows in fit.items():
        if manifest['selected_task_ids'][name] != [row['task_id'] for row in rows]:
            raise ValueError(f'Training split changed: {name}')
    assert_disjoint_splits({**fit, 'eval': tasks})
    callback = identity = None
    if args.benchmark == 'humanevalplus':
        from improving.benchmarks import make_humanevalplus_evaluator
        callback, identity = make_humanevalplus_evaluator(task_path,
            settings={'backend': 'local', 'allow_unsafe_local': True, 'parallel': 4})
    elif any(row.get('evaluation_backend') == 'evalplus' for row in tasks):
        raise ValueError('EvalPlus tasks require official evaluation')
    eager = config['model']['name'] == 'google/gemma-3-4b-it' and args.benchmark == 'livecodebench'
    if args.validate_only:
        print(json.dumps({'source': str(source), 'method': args.method, 'round': args.round,
                          'benchmark': args.benchmark, 'tasks': len(tasks), 'samples': 16,
                          'eager_attention': eager}))
        return
    settings = dict(config['model'])
    base = json.loads((source / 'base/complete.json').read_text())
    if base.get('resolved_revision'):
        settings['revision'] = base['resolved_revision']
    if eager:
        settings['attn_implementation'] = 'eager'
    generation = {key: value for key, value in config['generation'].items()
                  if key not in ('train_samples', 'eval_samples')}
    generation.update({'max_prompt_tokens': 4096, 'max_new_tokens': 1024,
                       'batch_size': 4, 'task_batch_size': 4, 'sequence_batch_size': 4,
                       'samples': 16})
    evaluation = {**config['evaluation'], 'backend': 'local', 'allow_unsafe_local': True,
                  'timeout': 30, 'memory_mb': 1024, 'workers': 4,
                  'code_extraction': 'first_fence', 'bootstrap_samples': 2000,
                  'ks': [1, 4, 8, 16], 'correct_budget': 4,
                  'correct_budgets': [4, 8, 16], 'async_scoring': False}
    checkpoint_sha = checkpoint_fingerprint(checkpoint)
    protocol = {'source_manifest_sha256': sha(manifest_path), 'checkpoint_sha256': checkpoint_sha,
                'task_sha256': sha(task_path), 'task_ids': [row['task_id'] for row in tasks],
                'fit_hashes': {key: stable_hash(rows) for key, rows in fit.items()},
                'method': args.method, 'round': args.round, 'settings': settings,
                'generation': generation, 'evaluation': evaluation, 'evaluator_identity': identity,
                'seed': 43}
    fingerprint = stable_hash(protocol)
    marker = output / 'matrix_complete.json'
    if marker.exists():
        done = json.loads(marker.read_text())
        if done.get('fingerprint') != fingerprint or any(sha(output / name) != value
                for name, value in done['files'].items()):
            raise ValueError('Completed matrix cell differs from source or protocol')
        print(json.dumps({'status': 'completed', 'output_dir': str(output), 'resumed': True}))
        return
    if output.exists() and any(output.iterdir()) and not args.resume:
        raise FileExistsError('Use --resume for an existing evaluation directory')
    if (output / 'manifest.json').exists():
        if json.loads((output / 'manifest.json').read_text())['fingerprint'] != fingerprint:
            raise ValueError('Evaluation protocol changed during resume')
    else:
        atomic_json(output / 'manifest.json', {'fingerprint': fingerprint, 'protocol': protocol})
    model, tokenizer = load_model(settings, checkpoint)
    try:
        revision = getattr(model.config, '_commit_hash', None)
        model_identity = stable_hash([settings, checkpoint_sha, revision])
        path = output / 'evaluation.jsonl'
        records = generate_to_file(model, tokenizer, tasks, path, generation, seed=43,
            model_identity=model_identity, method=args.method, round_index=args.round,
            stage='evaluation', resume=args.resume)
    finally:
        del model, tokenizer
        gc.collect()
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    verify = callback or evaluate_file
    summary = verify(tasks, records, path, evaluation, expected_samples=16, seed=43)
    if set(summary['per_task']) != {row['task_id'] for row in tasks}:
        raise ValueError('Incomplete evaluation task universe')
    files = {p.name: sha(p) for p in (path, path.with_suffix('.verified.jsonl'),
             path.with_suffix('.metrics.json'))}
    atomic_json(marker, {'status': 'completed', 'fingerprint': fingerprint,
        'scope': 'scope164_round_evaluation', 'method': args.method, 'round': args.round,
        'benchmark': args.benchmark, 'task_count': len(tasks), 'samples_per_task': 16,
        'training_on_target': False, 'verifier': 'official_evalplus' if callback else 'native_adapted',
        'files': files})
    print(json.dumps({'status': 'completed', 'output_dir': str(output)}))


if __name__ == '__main__':
    main()
