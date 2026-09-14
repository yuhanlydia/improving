"""Stage-separated self-distillation with immutable configuration and provenance."""
from __future__ import annotations

from contextlib import contextmanager, nullcontext
import gc
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import random
import shutil
import subprocess
import time

import torch
import yaml

from .data import assert_disjoint_splits, read_jsonl, write_jsonl
from .generation import atomic_json, generate_to_file, stable_hash
from .modeling import collate_examples, encode_example, load_model, render_prompt
from .training import train_on_records

METHODS = {'plain', 'ssd', 'spd_hard', 'spectral_soft', 'residual_blend', 'random_hard'}


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2**20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_fingerprint(path):
    """Hash actual weights, all shards, tokenizer and config, not just an index."""
    path = Path(path)
    assets = [p for p in path.iterdir() if p.is_file() and p.suffix in
              {'.safetensors', '.bin', '.json', '.txt', '.model', '.jinja'}
              and p.name != 'training_stats.json']
    if not assets or not (path / 'config.json').exists():
        raise ValueError(f'Not a complete model directory: {path}')
    return stable_hash({p.name: file_sha(p) for p in sorted(assets)})


@contextmanager
def record_stage(directory, stage):
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
    succeeded = False
    try:
        yield
        succeeded = True
    finally:
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        record = {'stage': stage, 'elapsed_seconds': time.monotonic() - started,
                  'status': 'completed' if succeeded else 'failed',
                  'cuda_peak_allocated_bytes': torch.cuda.max_memory_allocated() if torch.cuda.is_available() else None,
                  'cuda_peak_reserved_bytes': torch.cuda.max_memory_reserved() if torch.cuda.is_available() else None}
        path = Path(directory) / f'{stage}.resources.json'
        previous = json.loads(path.read_text()) if path.exists() else None
        attempts = previous.get('attempts', [previous]) if previous else []
        attempts.append(record)
        combined = {**record, 'attempts': attempts,
                    'elapsed_seconds': sum(item['elapsed_seconds'] for item in attempts)}
        for key in ('cuda_peak_allocated_bytes', 'cuda_peak_reserved_bytes'):
            peaks = [item[key] for item in attempts if item.get(key) is not None]
            combined[key] = max(peaks) if peaks else None
        atomic_json(path, combined)


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError('Configuration must be a mapping')
    methods = config.get('methods', [])
    if not methods or len(set(methods)) != len(methods) or any(m not in METHODS for m in methods):
        raise ValueError(f'methods must be unique members of {sorted(METHODS)}')
    for key in ('model', 'data', 'output_dir'):
        if key not in config:
            raise ValueError(f'Missing configuration field: {key}')
    if not config['model'].get('name'):
        raise ValueError('model.name is required')
    for key in ('train', 'calibration', 'validation', 'eval'):
        if key not in config['data']:
            raise ValueError(f'Missing data.{key} path')
    if type(config.get('rounds', 1)) is not int or config.get('rounds', 1) < 1:
        raise ValueError('rounds must be a positive integer')
    gen = config.get('generation', {})
    n = gen.get('eval_samples', 64)
    if type(n) is not int or n < 1 or gen.get('train_samples', 1) < 1:
        raise ValueError('Generation sample counts must be positive integers')
    evaluation = config.get('evaluation', {})
    if any(type(k) is not int or not 1 <= k <= n for k in evaluation.get('ks', [1, 8, 32, 64])):
        raise ValueError('All evaluation ks must fit the declared per-task sample budget')
    if evaluation.get('backend', 'docker') not in {'docker', 'local', 'none'}:
        raise ValueError('evaluation.backend must be docker, local or none')
    if evaluation.get('backend') == 'local' and not evaluation.get('allow_unsafe_local', False):
        raise ValueError('Local generated-code execution requires explicit allow_unsafe_local')
    return config


def load_config(path):
    """Relative data/output paths are relative to the current working directory."""
    with Path(path).open() as stream:
        return validate_config(yaml.safe_load(stream))


def evaluate_file(tasks, records, path, settings, *, expected_samples, seed=42):
    if settings.get('backend', 'docker') == 'none':
        return {'status': 'pending_verification', 'samples': len(records)}
    from .verification import verify_completions
    from .metrics import summarize_records
    verified = verify_completions(
        tasks, records, backend=settings.get('backend', 'docker'),
        timeout=float(settings.get('timeout', 5)),
        allow_unsafe_local=bool(settings.get('allow_unsafe_local', False)),
        docker_image=settings.get('docker_image', 'python:3.11-slim'),
        workers=int(settings.get('workers', 4)), expected_samples=expected_samples
    )
    path = Path(path)
    write_jsonl(path.with_suffix('.verified.jsonl'), verified)
    summary = summarize_records(verified, ks=settings.get('ks', [1, 8, 32, 64]),
                                correct_budget=settings.get('correct_budget', 8),
                                bootstrap_samples=settings.get('bootstrap_samples', 1000),
                                seed=seed, expected_samples=expected_samples)
    summary['protocol']['evaluation'] = {
        'backend': settings.get('backend', 'docker'),
        'timeout': float(settings.get('timeout', 5)),
        'docker_image': settings.get('docker_image', 'python:3.11-slim'),
        'task_tests_sha256': stable_hash({t['task_id']: {
            'tests': t.get('tests'), 'entry_point': t.get('entry_point'),
            'completion_mode': t.get('completion_mode'), 'test_mode': t.get('test_mode')
        } for t in tasks}), 'protocol_version': 'task-tests-v1'}
    atomic_json(path.with_suffix('.metrics.json'), summary)
    return summary


def _calibrate(model, tokenizer, tasks, settings, path, model_identity):
    from .calibration import collect_covariances, save_calibration, load_calibration
    from .spectral import target_modules
    if path.exists():
        saved = load_calibration(path)
        if saved['metadata'].get('model_identity') != model_identity:
            raise ValueError('Calibration checkpoint identity mismatch')
        return saved['modules']
    count = int(settings.get('max_examples', 50))
    if count < 1 or not tasks:
        raise ValueError('Calibration requires at least one reference example')
    selected = tasks[:count]
    span_mode = settings.get('span_mode', 'completion')
    if span_mode not in {'completion', 'explicit'}:
        raise ValueError('calibration.span_mode must be completion or explicit')
    batches = []
    for task in selected:
        if not task.get('reference'):
            raise ValueError(f'Missing training-split calibration reference: {task["task_id"]}')
        spans = task.get('calibration_spans') if span_mode == 'explicit' else None
        if span_mode == 'explicit' and not spans:
            raise ValueError('Explicit span protocol requires supplied calibration_spans on every record')
        example = encode_example(tokenizer, render_prompt(tokenizer, task), task['reference'],
                                 max_length=settings.get('max_length', 1536), spans=spans)
        if example['truncated_tokens']:
            raise ValueError('Calibration reference truncated; increase calibration.max_length')
        batches.append(collate_examples([example], tokenizer.pad_token_id))
    names = target_modules(model, layers=settings.get('layers'))
    modules = collect_covariances(model, batches, names)
    save_calibration(path, modules, metadata={'model_identity': model_identity,
                     'task_ids': [x['task_id'] for x in selected], 'span_mode': span_mode,
                     'location': 'native_linear_output_pre_rope_pre_normalization'})
    return modules


def _operators(covariances, method, settings, seed):
    from .spectral import make_operator
    kinds = {'spd_hard': 'hard', 'spectral_soft': 'spectral_soft',
             'residual_blend': 'blend', 'random_hard': 'random'}
    output = {}
    for name, record in covariances.items():
        dimension = record['covariance'].shape[0]
        rank = settings.get('rank')
        if rank is None:
            rank = max(1, int(dimension * float(settings.get('rank_fraction', .5))))
        output[name] = make_operator(record['covariance'], kind=kinds[method], rank=rank,
                                     tau=float(settings.get('tau', 1)), rho=float(settings.get('rho', .5)),
                                     seed=int(stable_hash([seed, name])[:8], 16))
    return output


def _preflight_verification(settings):
    if settings.get('backend', 'docker') != 'docker':
        return
    if not shutil.which('docker'):
        raise RuntimeError('Docker is required for verification; install it or set backend: none and verify externally')
    result = subprocess.run(['docker', 'image', 'inspect', settings.get('docker_image', 'python:3.11-slim')],
                            capture_output=True, text=True, timeout=20)
    if result.returncode:
        raise RuntimeError('Docker image unavailable. Run docker pull python:3.11-slim before the experiment')


def run_experiment(config, *, resume=False):
    validate_config(config)
    splits = {name: read_jsonl(path) for name, path in config['data'].items()}
    if set(splits) != {'train', 'calibration', 'validation', 'eval'}:
        raise ValueError('Use exactly train, calibration, validation and eval data paths')
    assert_disjoint_splits(splits)
    if any(not rows for rows in splits.values()):
        raise ValueError('Every declared split must be nonempty')
    for name, count in config.get('data_limits', {}).items():
        if name not in splits or type(count) is not int or not 1 <= count <= len(splits[name]):
            raise ValueError(f'Invalid data_limits.{name}')
        ordered = sorted(splits[name], key=lambda row: row['task_id'])
        random.Random(config.get('data_seed', 42)).shuffle(ordered)
        splits[name] = ordered[:count]
    evaluation = config.get('evaluation', {})
    _preflight_verification(evaluation)
    root = Path(config['output_dir'])
    source_hashes = {p.name: file_sha(p) for p in Path(__file__).parent.glob('*.py')}
    fingerprint = stable_hash({'config': config,
                               'data': {k: file_sha(p) for k, p in config['data'].items()},
                               'implementation': source_hashes})
    manifest_path = root / 'manifest.json'
    local_base = Path(config['model']['name'])
    local_base_fingerprint = checkpoint_fingerprint(local_base) if local_base.is_dir() else None
    fingerprint = stable_hash([fingerprint, local_base_fingerprint])
    if manifest_path.exists():
        if not resume:
            raise FileExistsError('Experiment exists; use --resume or a new output_dir')
        if json.loads(manifest_path.read_text())['fingerprint'] != fingerprint:
            raise ValueError('Configuration, dataset or implementation changed; use a new output_dir')
    else:
        if root.exists() and any(root.iterdir()):
            raise ValueError('Existing experiment directory has no manifest')
        atomic_json(manifest_path, {'fingerprint': fingerprint, 'config': config,
                    'implementation_hashes': source_hashes, 'python': platform.python_version(),
                    'torch': torch.__version__, 'status': 'initialized',
                    'dependencies': {p: importlib.metadata.version(p) for p in
                                     ('transformers', 'peft', 'accelerate', 'datasets', 'numpy')},
                    'selected_task_ids': {k: [t['task_id'] for t in rows] for k, rows in splits.items()},
                    'local_base_fingerprint': local_base_fingerprint})
    seed = int(config.get('seed', 42))
    for name, rows in splits.items():
        snapshot = root / 'tasks' / f'{name}.jsonl'
        if snapshot.exists() and stable_hash(read_jsonl(snapshot)) != stable_hash(rows):
            raise ValueError(f'Selected task snapshot changed: {snapshot}')
        if not snapshot.exists():
            write_jsonl(snapshot, rows)
    gen = config.get('generation', {})
    eval_gen = {k: v for k, v in gen.items() if k not in {'train_samples', 'eval_samples'}}
    eval_gen['samples'] = gen.get('eval_samples', 64)
    train_gen = {**eval_gen, 'samples': gen.get('train_samples', 1)}
    cal = config.get('calibration', {})
    started = time.monotonic()
    base_path = root / 'base' / 'evaluation.jsonl'
    # Base evaluated once; the same completions form the reference for every arm.
    base_done = root / 'base' / 'complete.json'
    if not base_done.exists():
        model, tokenizer = load_model(config['model'])
        revision = getattr(model.config, '_commit_hash', None)
        identity = stable_hash([config['model'], revision, local_base_fingerprint])
        with record_stage(base_path.parent, 'evaluation'):
            base_records = generate_to_file(model, tokenizer, splits['eval'], base_path, eval_gen,
                                            seed=seed, model_identity=identity, resume=resume)
            evaluate_file(splits['eval'], base_records, base_path, evaluation,
                          expected_samples=eval_gen['samples'], seed=seed)
        atomic_json(base_done, {'evaluation_sha': file_sha(base_path), 'model_identity': identity,
                                'resolved_revision': revision})
        del model, tokenizer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    elif json.loads(base_done.read_text())['evaluation_sha'] != file_sha(base_path):
        raise ValueError('Base samples changed since completion')
    base_state = json.loads(base_done.read_text())
    base_identity = base_state['model_identity']
    model_settings = dict(config['model'])
    if base_state.get('resolved_revision'):
        model_settings['revision'] = base_state['resolved_revision']
    for method in config['methods']:
        previous_checkpoint = None
        identity = base_identity
        for round_index in range(1, config.get('rounds', 1) + 1):
            directory = root / method / f'round_{round_index}'
            marker = directory / 'complete.json'
            checkpoint = directory / 'model'
            if marker.exists():
                state = json.loads(marker.read_text())
                if any(not (directory / name).exists() or file_sha(directory / name) != digest
                       for name, digest in state['files'].items()):
                    raise ValueError(f'Completed round integrity failure: {directory}')
                previous_checkpoint = checkpoint
                identity = state['model_identity']
                continue
            directory.mkdir(parents=True, exist_ok=True)
            print(f'[{method}] round {round_index}: {"resume" if resume else "start"}', flush=True)
            trained = (checkpoint / 'training_stats.json').exists()
            if local_base_fingerprint and checkpoint_fingerprint(local_base) != local_base_fingerprint:
                raise ValueError('Base model/tokenizer changed during this experiment')
            model, tokenizer = load_model(model_settings, checkpoint if trained else previous_checkpoint)
            if not trained:
                operators = None
                if method not in {'plain', 'ssd'}:
                    with record_stage(directory, 'calibration'):
                        covariances = _calibrate(model, tokenizer, splits['calibration'], cal,
                                                 directory / 'calibration.pt', identity)
                    operators = _operators(covariances, method, cal, seed)
                    atomic_json(directory / 'operator_diagnostics.json', {name: {
                        'eigenvalue_min': float(torch.linalg.eigvalsh(op).min()),
                        'eigenvalue_max': float(torch.linalg.eigvalsh(op).max()),
                        'dimension': op.shape[0], 'frobenius_distance_from_identity':
                        float(torch.linalg.vector_norm(op - torch.eye(op.shape[0], dtype=op.dtype)))}
                        for name, op in operators.items()})
                from .spectral import folded_operators
                training_settings = dict(train_gen)
                if method == 'ssd':
                    training_settings.update({'temperature': 1.5, 'top_p': .8, 'top_k': 20})
                with folded_operators(model, operators) if operators is not None else nullcontext():
                    with record_stage(directory, 'training_generation'):
                        records = generate_to_file(model, tokenizer, splits['train'], directory / 'train.jsonl',
                                                    training_settings, seed=seed, model_identity=identity,
                                                    method=method, round_index=round_index, stage='training', resume=resume)
                    if config.get('diagnostics', {}).get('evaluate_generation_policy', True):
                        diagnostic_path = directory / 'generation_policy.jsonl'
                        diagnostic_settings = {**training_settings, 'samples': eval_gen['samples']}
                        with record_stage(directory, 'generation_policy'):
                            diagnostics = generate_to_file(model, tokenizer, splits['eval'], diagnostic_path,
                                                            diagnostic_settings, seed=seed, model_identity=identity,
                                                            method=method, round_index=round_index,
                                                            stage='evaluation', resume=resume)
                            evaluate_file(splits['eval'], diagnostics, diagnostic_path, evaluation,
                                          expected_samples=eval_gen['samples'], seed=seed)
                # Weight folding has been restored before this function is called.
                with record_stage(directory, 'sft'):
                    model, stats = train_on_records(model, tokenizer, splits['train'], records,
                                                    config.get('train', {}), checkpoint, seed=seed + round_index)
            eval_path = directory / 'evaluation.jsonl'
            model_identity = stable_hash([identity, method, round_index, checkpoint_fingerprint(checkpoint)])
            with record_stage(directory, 'post_training_evaluation'):
                records = generate_to_file(model, tokenizer, splits['eval'], eval_path, eval_gen,
                                            seed=seed, model_identity=model_identity, method=method,
                                            round_index=round_index, stage='evaluation', resume=resume)
                evaluate_file(splits['eval'], records, eval_path, evaluation,
                              expected_samples=eval_gen['samples'], seed=seed)
            files = {str(p.relative_to(directory)): file_sha(p)
                     for p in directory.rglob('*') if p.is_file() and '.parts' not in str(p)
                     and p.name != 'complete.json'}
            atomic_json(marker, {'status': 'completed', 'model_identity': model_identity, 'files': files})
            previous_checkpoint, identity = checkpoint, model_identity
            del model, tokenizer
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    result = {'status': 'completed', 'output_dir': str(root), 'methods': config['methods'],
              'rounds': config.get('rounds', 1), 'elapsed_this_invocation_seconds': time.monotonic() - started,
              'verification': 'pending' if evaluation.get('backend') == 'none' else 'completed'}
    atomic_json(root / 'run_status.json', result)
    return result
