#!/usr/bin/env python3
"""Score the final SPECTRUM student on one prepared transfer benchmark."""
import argparse
import hashlib
import json
from pathlib import Path

from improving.data import read_jsonl
from improving.longitudinal import evaluate_checkpoints
from improving.utils import atomic_json


DATA_ROOT = Path('/root/improving/data/iclr2027')
BENCHMARKS = ('humanevalplus', 'apps_intro', 'codecontests', 'livecodebench')


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2**20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-run', type=Path, required=True)
    parser.add_argument('--benchmark', choices=BENCHMARKS, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    source = args.source_run.resolve()
    manifest = json.loads((source / 'manifest.json').read_text())
    config = manifest['config']
    if config['seed'] != 43 or 'spectral_soft' not in config['methods'] or config['rounds'] < 5:
        raise ValueError('Expected seed-43 five-round SPECTRUM training source')
    final_dir = source / 'spectral_soft/round_5'
    if not args.validate_only and not (final_dir / 'complete.json').exists():
        raise ValueError('Final SPECTRUM round is incomplete')
    task_path = DATA_ROOT / args.benchmark / 'eval.jsonl'
    prepared = json.loads((task_path.parent / 'manifest.json').read_text())
    task_meta = prepared['output_files']['eval.jsonl']
    tasks = read_jsonl(task_path)
    if prepared['name'] != args.benchmark or len(tasks) != task_meta['count'] or file_sha(task_path) != task_meta['sha256']:
        raise ValueError('Prepared benchmark snapshot changed')
    callback = identity = None
    if args.benchmark == 'humanevalplus':
        from improving.benchmarks import make_humanevalplus_evaluator
        callback, identity = make_humanevalplus_evaluator(task_path,
            settings={'backend': 'local', 'allow_unsafe_local': True, 'parallel': 4})
    elif any(row.get('evaluation_backend') == 'evalplus' for row in tasks):
        raise ValueError('EvalPlus tasks require the official evaluator')
    eager = config['model']['name'] == 'google/gemma-3-4b-it' and args.benchmark == 'livecodebench'
    if args.validate_only:
        print(json.dumps({'source_run': str(source), 'benchmark': args.benchmark,
                          'task_count': len(tasks), 'method': 'spectral_soft', 'round': 5,
                          'samples': 16, 'eager_attention': eager}))
        return
    evaluation = {'backend': 'local', 'allow_unsafe_local': True,
                  'timeout': 30, 'memory_mb': 1024, 'workers': 4,
                  'code_extraction': 'first_fence', 'bootstrap_samples': 2000}
    generation = {'max_prompt_tokens': 4096, 'max_new_tokens': 1024,
                  'batch_size': 4, 'task_batch_size': 4, 'sequence_batch_size': 4}
    result = evaluate_checkpoints(source, args.output_dir, samples=16,
        rounds=[5], methods=['spectral_soft'], eval_tasks_path=task_path,
        evaluation_overrides=evaluation, generation_overrides=generation,
        model_settings={'attn_implementation': 'eager'} if eager else None,
        bootstrap_samples=2000, resume=args.resume,
        evaluator=callback, evaluator_identity=identity)
    expected = {'base', 'spectral_soft/round_5'}
    if result['status'] != 'completed' or set(result['completed']) != expected:
        raise RuntimeError(f'SPECTRUM transfer incomplete: {result}')
    atomic_json(args.output_dir / 'matrix_complete.json', {
        'status': 'completed', 'scope': 'spectrum_final_round5',
        'source_run': str(source), 'benchmark': args.benchmark,
        'method': 'spectral_soft', 'round': 5, 'samples_per_task': 16,
        'task_count': len(tasks), 'training_on_target': False,
        'verifier': 'official_evalplus' if callback else 'native_adapted',
        'eager_attention': eager})


if __name__ == '__main__':
    main()
