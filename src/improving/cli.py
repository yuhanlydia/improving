"""Command line entrypoints. Dataset downloads and GPU work are explicit commands."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


def _parser():
    parser = argparse.ArgumentParser(prog='improving', description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('doctor', help='Inspect local dependencies and GPU; no downloads')
    geometry = commands.add_parser('geometry', help='Frozen-model correct-solution subspace study')
    geometry.add_argument('--config', required=True)
    geometry.add_argument('--stage', default='all', choices=['validate', 'discover', 'extract', 'analyze',
                         'relations', 'select', 'evaluate', 'report', 'all'])
    geometry.add_argument('--resume', action='store_true')
    prepare = commands.add_parser('prepare', help='Download and prepare a coding benchmark')
    prepare.add_argument('--dataset', choices=['mbpp', 'humaneval'], required=True)
    prepare.add_argument('--output-dir', required=True)
    prepare.add_argument('--seed', type=int, default=42)
    prepare.add_argument('--calibration-size', type=int, default=50)
    prepare.add_argument('--validation-size', type=int, default=30)
    prepare.add_argument('--revision')
    for name in ('validate', 'run'):
        sub = commands.add_parser(name)
        sub.add_argument('--config', required=True)
        if name == 'run':
            sub.add_argument('--resume', action='store_true')
    for name in ('calibrate', 'generate', 'train'):
        sub = commands.add_parser(name)
        sub.add_argument('--config', required=True)
        sub.add_argument('--checkpoint')
        sub.add_argument('--output', required=True)
        if name != 'calibrate':
            sub.add_argument('--tasks', required=True)
        if name == 'generate':
            sub.add_argument('--samples', type=int, default=64)
            sub.add_argument('--resume', action='store_true')
        elif name == 'train':
            sub.add_argument('--samples', required=True, help='Raw completion JSONL')
    verify = commands.add_parser('verify', help='Run task tests; Docker by default')
    verify.add_argument('--tasks', required=True)
    verify.add_argument('--samples', required=True)
    verify.add_argument('--output', required=True)
    verify.add_argument('--backend', choices=['docker', 'local'], default='docker')
    verify.add_argument('--allow-unsafe-local', action='store_true')
    verify.add_argument('--timeout', type=float, default=5.0)
    verify.add_argument('--workers', type=int, default=4)
    verify.add_argument('--expected-samples', type=int)
    verify.add_argument('--docker-image', default='python:3.11-slim')
    metrics = commands.add_parser('metrics')
    metrics.add_argument('--samples', required=True, help='Verified completion JSONL')
    metrics.add_argument('--tasks', required=True, help='Full intended evaluation task universe')
    metrics.add_argument('--output', required=True)
    metrics.add_argument('--ks', default='1,8,32,64')
    metrics.add_argument('--correct-budget', type=int, default=8)
    metrics.add_argument('--expected-samples', type=int, required=True)
    metrics.add_argument('--bootstrap-samples', type=int, default=1000)
    metrics.add_argument('--seed', type=int, default=42)
    annotate = commands.add_parser('annotate', help='Join independently audited algorithm labels for evaluation only')
    annotate.add_argument('--samples', required=True)
    annotate.add_argument('--annotations', required=True)
    annotate.add_argument('--output', required=True)
    report = commands.add_parser('report')
    report.add_argument('--run-dir', required=True)
    report.add_argument('--output')
    for name in ('evalplus-export', 'evalplus-import'):
        sub = commands.add_parser(name)
        sub.add_argument('--tasks', required=True)
        sub.add_argument('--samples', required=True)
        sub.add_argument('--output', required=True)
        if name == 'evalplus-import':
            sub.add_argument('--results', required=True)
            sub.add_argument('--manifest')
            sub.add_argument('--base-only', action='store_true')
    return parser


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        result = _dispatch(args)
    except (ValueError, RuntimeError, FileNotFoundError, FileExistsError, ImportError) as error:
        parser.exit(2, f'error: {error}\n')
    if result is not None:
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


def _dispatch(args):
    from .data import read_jsonl, write_jsonl
    command = args.command
    if command == 'geometry':
        from .geometry_study import load_geometry_config, run_geometry
        return run_geometry(load_geometry_config(args.config), stage=args.stage, resume=args.resume)
    if command == 'doctor':
        packages = {p: importlib.util.find_spec(p) is not None
                    for p in ('torch', 'transformers', 'peft', 'datasets', 'evalplus')}
        result = {'python': sys.version.split()[0], 'packages': packages}
        if packages['torch']:
            import torch
            result.update(torch=torch.__version__, cuda=torch.cuda.is_available(),
                          devices=[{'name': torch.cuda.get_device_name(i),
                                    'memory_gib': round(torch.cuda.get_device_properties(i).total_memory / 2**30, 1)}
                                   for i in range(torch.cuda.device_count())])
        return result
    if command == 'prepare':
        from .data import prepare_mbpp, prepare_humaneval
        if args.dataset == 'mbpp':
            splits = prepare_mbpp(args.output_dir, seed=args.seed, calibration_size=args.calibration_size,
                                  validation_size=args.validation_size, revision=args.revision)
        else:
            splits = prepare_humaneval(args.output_dir)
        return {'output_dir': args.output_dir, 'splits': {k: len(v) for k, v in splits.items()}}
    if command in {'validate', 'run', 'calibrate', 'generate', 'train'}:
        from .pipeline import load_config, run_experiment
        config = load_config(args.config)
        if command == 'validate':
            from .data import assert_disjoint_splits
            splits = {k: read_jsonl(p) for k, p in config['data'].items()}
            assert_disjoint_splits(splits)
            selected = {k: len(v) for k, v in splits.items()}
            for split, count in config.get('data_limits', {}).items():
                if split not in selected or type(count) is not int or not 1 <= count <= selected[split]:
                    raise ValueError(f'Invalid data_limits.{split}')
                selected[split] = count
            return {'valid': True, 'methods': config['methods'], 'rounds': config.get('rounds', 1),
                    'split_counts': {k: len(v) for k, v in splits.items()},
                    'selected_split_counts': selected,
                    'evaluation_samples_per_task': config.get('generation', {}).get('eval_samples', 64),
                    'training_samples_per_task': config.get('generation', {}).get('train_samples', 1)}
        if command == 'run':
            return run_experiment(config, resume=args.resume)
        from .modeling import load_model
        from .generation import generate_to_file, stable_hash
        model, tokenizer = load_model(config['model'], args.checkpoint)
        from .pipeline import checkpoint_fingerprint
        local_path = Path(args.checkpoint or config['model']['name'])
        asset_hash = checkpoint_fingerprint(local_path) if local_path.is_dir() else None
        identity = stable_hash([config['model'], args.checkpoint,
                                getattr(model.config, '_commit_hash', None), asset_hash])
        if command == 'calibrate':
            from .pipeline import _calibrate
            if Path(args.output).exists():
                raise FileExistsError('Calibration output already exists')
            covariance = _calibrate(model, tokenizer, read_jsonl(config['data']['calibration']),
                                    config.get('calibration', {}), Path(args.output), identity)
            return {'output': args.output, 'modules': list(covariance)}
        tasks = read_jsonl(args.tasks)
        if command == 'generate':
            settings = {k: v for k, v in config.get('generation', {}).items()
                        if k not in {'train_samples', 'eval_samples'}}
            records = generate_to_file(model, tokenizer, tasks, args.output,
                                        {**settings, 'samples': args.samples},
                                        seed=config.get('seed', 42), model_identity=identity, resume=args.resume)
            return {'output': args.output, 'samples': len(records)}
        from .training import train_on_records
        _, stats = train_on_records(model, tokenizer, tasks, read_jsonl(args.samples),
                                    config.get('train', {}), args.output, seed=config.get('seed', 42))
        return {'output': args.output, **stats}
    if command == 'verify':
        from .verification import verify_completions
        rows = verify_completions(read_jsonl(args.tasks), read_jsonl(args.samples),
                                  backend=args.backend, timeout=args.timeout, workers=args.workers,
                                  allow_unsafe_local=args.allow_unsafe_local, docker_image=args.docker_image,
                                  expected_samples=args.expected_samples)
        write_jsonl(args.output, rows)
        return {'output': args.output, 'samples': len(rows), 'correct': sum(r['correct'] for r in rows)}
    if command == 'metrics':
        from .data import validate_completions
        from .metrics import summarize_records
        from .utils import atomic_json
        tasks = read_jsonl(args.tasks)
        rows = validate_completions(read_jsonl(args.samples), tasks)
        summary = summarize_records(rows, ks=[int(x) for x in args.ks.split(',')],
                                    correct_budget=args.correct_budget,
                                    bootstrap_samples=args.bootstrap_samples, seed=args.seed,
                                    expected_samples={t['task_id']: args.expected_samples for t in tasks})
        atomic_json(args.output, summary)
        return {'output': args.output, 'tasks': len(tasks)}
    if command == 'annotate':
        from .reporting import annotate_records
        rows = annotate_records(read_jsonl(args.samples), read_jsonl(args.annotations))
        write_jsonl(args.output, rows)
        return {'output': args.output, 'samples': len(rows)}
    if command == 'report':
        from .reporting import build_report
        return build_report(args.run_dir, args.output)
    if command == 'evalplus-export':
        from .verification import export_evalplus
        manifest = export_evalplus(read_jsonl(args.tasks), read_jsonl(args.samples), args.output)
        return {'output': args.output, 'manifest': str(manifest)}
    if command == 'evalplus-import':
        from .verification import import_evalplus_results
        rows = import_evalplus_results(read_jsonl(args.samples), args.results, tasks=read_jsonl(args.tasks),
                                        require_plus=not args.base_only, manifest_path=args.manifest)
        write_jsonl(args.output, rows)
        return {'output': args.output, 'samples': len(rows)}
    raise ValueError(f'Unknown command: {command}')


if __name__ == '__main__':
    main()
