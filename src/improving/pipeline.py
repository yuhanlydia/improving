"""Stage-separated self-distillation with immutable configuration and provenance."""
from __future__ import annotations

from contextlib import contextmanager, nullcontext
import gc
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import random
import shutil
import subprocess
import sys
import time

import torch
import yaml

from .data import assert_disjoint_splits, read_jsonl, write_jsonl
from .generation import atomic_json, generate_to_file, stable_hash
from .modeling import collate_examples, encode_example, load_model, render_prompt
from .training import train_on_records

METHODS = {'plain', 'ssd', 'spd_hard', 'spectral_soft', 'residual_blend', 'random_hard',
           'random_soft', 'isotropic_soft', 'matched_blend'}


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


def execution_runtime_identity(evaluation):
    """Runtime identity needed to fail closed when unsafe local execution resumes."""
    backend = evaluation.get('backend', 'docker')
    if backend != 'local':
        return {'backend': backend}
    executable = Path(sys.executable).resolve()
    return {'backend': 'local', 'python_version': sys.version,
            'python_executable': str(executable),
            'python_executable_sha256': file_sha(executable)}


@contextmanager
def record_stage(directory, stage):
    devices = list(range(torch.cuda.device_count())) if torch.cuda.is_available() else []
    for device in devices:
        torch.cuda.synchronize(device)
        torch.cuda.reset_peak_memory_stats(device)
    started = time.monotonic()
    succeeded = False
    try:
        yield
        succeeded = True
    finally:
        for device in devices:
            torch.cuda.synchronize(device)
        device_resources = [{
            'device': device, 'name': torch.cuda.get_device_name(device),
            'peak_allocated_bytes': torch.cuda.max_memory_allocated(device),
            'peak_reserved_bytes': torch.cuda.max_memory_reserved(device),
        } for device in devices]
        record = {'stage': stage, 'elapsed_seconds': time.monotonic() - started,
                  'status': 'completed' if succeeded else 'failed',
                  'cuda_devices': device_resources,
                  'cuda_peak_allocated_bytes': max((d['peak_allocated_bytes'] for d in device_resources), default=None),
                  'cuda_peak_reserved_bytes': max((d['peak_reserved_bytes'] for d in device_resources), default=None),
                  'cuda_sum_of_device_peak_allocated_bytes': sum(d['peak_allocated_bytes'] for d in device_resources) if devices else None,
                  'memory_definition': 'peak fields are maximum per-device peaks; sum of device peaks is an upper bound, not a simultaneous peak'}
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
    checkpoint_retention = config.get('checkpoint_retention', 'all')
    if not isinstance(checkpoint_retention, str) or checkpoint_retention not in {'all', 'latest'}:
        raise ValueError('checkpoint_retention must be all or latest')
    gen = config.get('generation', {})
    n = gen.get('eval_samples', 64)
    if (type(n) is not int or n < 1 or type(gen.get('train_samples', 1)) is not int
            or gen.get('train_samples', 1) < 1):
        raise ValueError('Generation sample counts must be positive integers')
    diagnostics = config.get('diagnostics', {})
    if not isinstance(diagnostics, dict):
        raise ValueError('diagnostics must be a mapping')
    if type(diagnostics.get('evaluate_generation_policy', True)) is not bool:
        raise ValueError('diagnostics.evaluate_generation_policy must be boolean')
    for key in ('eval_task_limit', 'eval_samples'):
        value = diagnostics.get(key)
        if value is not None and (type(value) is not int or value < 1):
            raise ValueError(f'diagnostics.{key} must be a positive integer or null')
    calibration = config.get('calibration', {})
    if type(calibration.get('reestimate_each_round', True)) is not bool:
        raise ValueError('calibration.reestimate_each_round must be boolean')
    if calibration.get('rank') is not None and (type(calibration['rank']) is not int
                                               or calibration['rank'] < 0):
        raise ValueError('calibration.rank must be a nonnegative integer or null')
    for key, default, lower, upper in [('tau', 1.0, 0, math.inf), ('rho', .5, 0, 1),
                                       ('rank_fraction', .5, 0, 1)]:
        value = calibration.get(key, default)
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or not lower <= value <= upper
                or (key == 'rank_fraction' and value == 0)):
            raise ValueError(f'Invalid calibration.{key}')
    evaluation = config.get('evaluation', {})
    if any(type(k) is not int or not 1 <= k <= n for k in evaluation.get('ks', [1, 8, 32, 64])):
        raise ValueError('All evaluation ks must fit the declared per-task sample budget')
    if 'correct_budgets' in evaluation and (not evaluation['correct_budgets'] or any(
            type(k) is not int or not 1 <= k <= n for k in evaluation['correct_budgets'])):
        raise ValueError('All evaluation.correct_budgets must fit the declared per-task sample budget')
    if evaluation.get('backend', 'docker') not in {'docker', 'local', 'none'}:
        raise ValueError('evaluation.backend must be docker, local or none')
    if evaluation.get('backend') == 'local' and not evaluation.get('allow_unsafe_local', False):
        raise ValueError('Local generated-code execution requires explicit allow_unsafe_local')
    if evaluation.get('code_extraction', 'strict') not in {'strict', 'first_fence'}:
        raise ValueError('evaluation.code_extraction must be strict or first_fence')
    return config


def _prune_completed_checkpoint(directory):
    """Prune a superseded model while keeping its auditable non-model outputs."""
    directory = Path(directory)
    marker = directory / 'complete.json'
    checkpoint = directory / 'model'
    state = json.loads(marker.read_text())
    checkpoint_files = {name: digest for name, digest in state['files'].items()
                        if name.startswith('model/')}
    if not checkpoint_files:
        return
    state['files'] = {name: digest for name, digest in state['files'].items()
                      if not name.startswith('model/')}
    state['checkpoint_status'] = 'pruned'
    state['pruned_checkpoint_files'] = checkpoint_files
    # Publish the pruned marker first. A crash after this write can leave an
    # extra checkpoint, but can never leave a marker that requires deleted files.
    atomic_json(marker, state)
    if checkpoint.exists():
        shutil.rmtree(checkpoint)


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
        memory_mb=int(settings.get('memory_mb', 512)),
        pids_limit=int(settings.get('pids_limit', 64)),
        allow_unsafe_local=bool(settings.get('allow_unsafe_local', False)),
        docker_image=settings.get('docker_image', 'python:3.11-slim'),
        workers=int(settings.get('workers', 4)), expected_samples=expected_samples,
        code_extraction=settings.get('code_extraction', 'strict')
    )
    path = Path(path)
    write_jsonl(path.with_suffix('.verified.jsonl'), verified)
    summary = summarize_records(verified, ks=settings.get('ks', [1, 8, 32, 64]),
                                correct_budget=settings.get('correct_budget', 8),
                                correct_budgets=settings.get('correct_budgets'),
                                bootstrap_samples=settings.get('bootstrap_samples', 1000),
                                seed=seed, expected_samples={task['task_id']: expected_samples for task in tasks})
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
             'residual_blend': 'blend', 'random_hard': 'random',
             'random_soft': 'random_soft', 'isotropic_soft': 'isotropic_soft',
             'matched_blend': 'matched_blend'}
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


def _operator_diagnostics(model, operators, covariances, method, settings):
    """Record actual parameter effects as well as the operator matching contract."""
    from .spectral import make_operator
    matched = method in {'random_soft', 'isotropic_soft', 'matched_blend'}
    diagnostics = {}
    for name, op in operators.items():
        dimension = op.shape[0]
        rank = settings.get('rank')
        if rank is None:
            rank = max(1, int(dimension * float(settings.get('rank_fraction', .5))))
        reference = make_operator(covariances[name]['covariance'], tau=float(settings.get('tau', 1)))
        identity = torch.eye(dimension, dtype=op.dtype)
        distance = float(torch.linalg.vector_norm(op - identity))
        target = float(torch.linalg.vector_norm(reference - identity))
        module = model.get_submodule(name)
        # Mirror folded_operators' actual float32 multiply and original-dtype cast.
        weight = module.weight.detach()
        transform = op.to(device=weight.device, dtype=torch.float32)
        folded = (transform.T @ weight.float()).to(weight.dtype)
        weight64 = weight.to(device='cpu', dtype=torch.float64)
        delta = folded.to(device='cpu', dtype=torch.float64) - weight64
        weight_norm = float(torch.linalg.vector_norm(weight64))
        spectrum = torch.linalg.eigvalsh(op)
        diagnostics[name] = {
            'method': method, 'dimension': dimension, 'configured_hard_rank': rank,
            'eigenvalue_min': float(spectrum.min()), 'eigenvalue_max': float(spectrum.max()),
            'operator_frobenius_norm': float(torch.linalg.vector_norm(op)),
            'frobenius_distance_from_identity': distance,
            'spectral_soft_distance_from_identity': target,
            'matching_contract': 'operator_distance_from_identity_frobenius' if matched else 'none',
            'matching_absolute_error': abs(distance - target) if matched else None,
            'matches_soft_eigenvalues': method == 'random_soft',
            'activation_rms_matched': False, 'output_kl_matched': False,
            'folded_weight_delta_frobenius': float(torch.linalg.vector_norm(delta)),
            'folded_weight_relative_delta': float(torch.linalg.vector_norm(delta)) / weight_norm
                if weight_norm > 0 else None,
            'folding_arithmetic': 'float32_product_then_original_parameter_dtype',
        }
        if method == 'matched_blend':
            diagnostics[name]['matched_rho'] = 1 - target / math.sqrt(dimension - rank) if rank < dimension else 1.0
        if method == 'isotropic_soft':
            diagnostics[name]['isotropic_gain'] = float(op[0, 0])
        if module.bias is not None:
            bias = module.bias.detach()
            folded_bias = (transform.T @ bias.float()).to(bias.dtype)
            diagnostics[name]['folded_bias_delta_frobenius'] = float(torch.linalg.vector_norm(
                folded_bias.to(device='cpu', dtype=torch.float64) - bias.to(device='cpu', dtype=torch.float64)))
    return diagnostics


def _diagnostic_protocol(config, tasks):
    """Fixed held-out diagnostic subset; never used for model or operator fitting."""
    settings = config.get('diagnostics', {})
    selected = list(tasks)
    limit = settings.get('eval_task_limit')
    if limit is not None:
        selected = sorted(selected, key=lambda row: row['task_id'])
        random.Random(config.get('data_seed', 42)).shuffle(selected)
        selected = selected[:limit]
    samples = settings.get('eval_samples') or config.get('generation', {}).get('eval_samples', 64)
    evaluation = dict(config.get('evaluation', {}))
    evaluation['ks'] = [k for k in evaluation.get('ks', [1, 8, 32, 64]) if k <= samples]
    if not evaluation['ks']:
        evaluation['ks'] = [1]
    evaluation['correct_budget'] = min(evaluation.get('correct_budget', 8), samples)
    if 'correct_budgets' in evaluation:
        evaluation['correct_budgets'] = [k for k in evaluation['correct_budgets'] if k <= samples]
        if not evaluation['correct_budgets']:
            evaluation['correct_budgets'] = [evaluation['correct_budget']]
    return selected, samples, evaluation


def _base_output_hashes(path, evaluation):
    outputs = [path]
    budget_path = path.with_suffix(path.suffix + '.budget.json')
    if budget_path.exists():
        outputs.append(budget_path)
    if evaluation.get('backend', 'docker') != 'none':
        outputs.extend([path.with_suffix('.verified.jsonl'), path.with_suffix('.metrics.json')])
    return {item.name: file_sha(item) for item in outputs}


def _validate_base_outputs(done, path, tasks, evaluation, expected_samples, seed):
    """Upgrade legacy markers by reverification instead of trusting unhashed outputs."""
    state = json.loads(done.read_text())
    if not path.exists() or state['evaluation_sha'] != file_sha(path):
        raise ValueError('Base samples changed since completion')
    if 'files' in state:
        expected_names = {path.name}
        if evaluation.get('backend', 'docker') != 'none':
            expected_names.update([path.with_suffix('.verified.jsonl').name, path.with_suffix('.metrics.json').name])
        allowed_names = expected_names | {path.with_suffix(path.suffix + '.budget.json').name}
        if not expected_names <= set(state['files']) <= allowed_names or any(
                not (path.parent / name).exists() or file_sha(path.parent / name) != digest
                for name, digest in state['files'].items()):
            raise ValueError('Base verification or metrics integrity failure')
        return
    # Old schema protected raw generation only. Recompute from that immutable
    # source once, explicitly documenting the migration, rather than blessing
    # possibly edited historical verified records or metrics.
    with record_stage(path.parent, 'legacy_reverification'):
        evaluate_file(tasks, read_jsonl(path), path, evaluation,
                      expected_samples=expected_samples, seed=seed)
    state.update({'files': _base_output_hashes(path, evaluation), 'integrity_schema': 2,
                  'integrity_migration': 'legacy_raw_marker_reverified_before_hashing'})
    atomic_json(done, state)


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
    diagnostic_tasks, diagnostic_samples, diagnostic_evaluation = _diagnostic_protocol(config, splits['eval'])
    evaluation = config.get('evaluation', {})
    _preflight_verification(evaluation)
    runtime_identity = execution_runtime_identity(evaluation)
    root = Path(config['output_dir'])
    source_hashes = {p.name: file_sha(p) for p in Path(__file__).parent.glob('*.py')}
    fingerprint = stable_hash({'config': config,
                               'data': {k: file_sha(p) for k, p in config['data'].items()},
                               'implementation': source_hashes,
                               'evaluation_runtime': runtime_identity})
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
                    'evaluation_runtime': runtime_identity,
                    'dependencies': {p: importlib.metadata.version(p) for p in
                                     ('transformers', 'peft', 'accelerate', 'datasets', 'numpy')},
                    'selected_task_ids': {k: [t['task_id'] for t in rows] for k, rows in splits.items()},
                    'generation_diagnostic_task_ids': [t['task_id'] for t in diagnostic_tasks],
                    'generation_diagnostic_samples': diagnostic_samples,
                    'local_base_fingerprint': local_base_fingerprint})
    seed = int(config.get('seed', 42))
    for name, rows in {**splits, 'generation_diagnostic': diagnostic_tasks}.items():
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
        with record_stage(base_path.parent, 'model_loading'):
            model, tokenizer = load_model(config['model'])
        revision = getattr(model.config, '_commit_hash', None)
        identity = stable_hash([config['model'], revision, local_base_fingerprint])
        with record_stage(base_path.parent, 'evaluation'):
            base_records = generate_to_file(model, tokenizer, splits['eval'], base_path, eval_gen,
                                            seed=seed, model_identity=identity, resume=resume)
            evaluate_file(splits['eval'], base_records, base_path, evaluation,
                          expected_samples=eval_gen['samples'], seed=seed)
        atomic_json(base_done, {'evaluation_sha': file_sha(base_path), 'model_identity': identity,
                                'resolved_revision': revision, 'integrity_schema': 2,
                                'files': _base_output_hashes(base_path, evaluation)})
        del model, tokenizer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    else:
        _validate_base_outputs(base_done, base_path, splits['eval'], evaluation, eval_gen['samples'], seed)
    base_state = json.loads(base_done.read_text())
    base_identity = base_state['model_identity']
    model_settings = dict(config['model'])
    if base_state.get('resolved_revision'):
        model_settings['revision'] = base_state['resolved_revision']
    for method in config['methods']:
        previous_checkpoint = None
        previous_directory = None
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
                if checkpoint.is_dir():
                    previous_checkpoint = checkpoint
                    previous_directory = directory
                identity = state['model_identity']
                continue
            directory.mkdir(parents=True, exist_ok=True)
            print(f'[{method}] round {round_index}: {"resume" if resume else "start"}', flush=True)
            trained = (checkpoint / 'training_stats.json').exists()
            if local_base_fingerprint and checkpoint_fingerprint(local_base) != local_base_fingerprint:
                raise ValueError('Base model/tokenizer changed during this experiment')
            with record_stage(directory, 'model_loading'):
                model, tokenizer = load_model(model_settings, checkpoint if trained else previous_checkpoint)
            if trained and not (directory / 'training_stats.json').exists():
                atomic_json(directory / 'training_stats.json', json.loads(
                    (checkpoint / 'training_stats.json').read_text()))
            if not trained:
                operators = None
                if method not in {'plain', 'ssd'}:
                    reestimate = cal.get('reestimate_each_round', True)
                    calibration_path = (directory if reestimate else root / method / 'round_1') / 'calibration.pt'
                    calibration_identity = identity if reestimate else base_identity
                    if not reestimate and round_index > 1 and not calibration_path.exists():
                        raise ValueError('Fixed geometry requires the saved round-1 calibration; do not fit it on a later checkpoint')
                    with record_stage(directory, 'calibration'):
                        covariances = _calibrate(model, tokenizer, splits['calibration'], cal,
                                                 calibration_path, calibration_identity)
                    atomic_json(directory / 'calibration_provenance.json', {
                        'mode': 'reestimated' if reestimate else 'fixed_round_1',
                        'calibration_round': round_index if reestimate else 1,
                        'calibration_model_identity': calibration_identity,
                        'student_model_identity': identity,
                        'calibration_path': str(calibration_path.relative_to(root)),
                        'calibration_sha256': file_sha(calibration_path),
                        'method': method, 'seed': seed,
                        'calibration_task_ids': [task['task_id'] for task in splits['calibration'][:int(cal.get('max_examples', 50))]],
                    })
                    operators = _operators(covariances, method, cal, seed)
                    atomic_json(directory / 'operator_diagnostics.json', _operator_diagnostics(
                        model, operators, covariances, method, cal))
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
                        diagnostic_settings = {**training_settings, 'samples': diagnostic_samples}
                        with record_stage(directory, 'generation_policy'):
                            diagnostics = generate_to_file(model, tokenizer, diagnostic_tasks, diagnostic_path,
                                                            diagnostic_settings, seed=seed, model_identity=identity,
                                                            method=method, round_index=round_index,
                                                            stage='evaluation', resume=resume)
                            evaluate_file(diagnostic_tasks, diagnostics, diagnostic_path, diagnostic_evaluation,
                                          expected_samples=diagnostic_samples, seed=seed)
                # Weight folding has been restored before this function is called.
                with record_stage(directory, 'sft'):
                    model, stats = train_on_records(model, tokenizer, splits['train'], records,
                                                    config.get('train', {}), checkpoint, seed=seed + round_index)
                atomic_json(directory / 'training_stats.json', stats)
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
            if config.get('checkpoint_retention', 'all') == 'latest' and previous_directory is not None:
                _prune_completed_checkpoint(previous_directory)
            previous_checkpoint, identity = checkpoint, model_identity
            previous_directory = directory
            del model, tokenizer
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    result = {'status': 'completed', 'output_dir': str(root), 'methods': config['methods'],
              'rounds': config.get('rounds', 1), 'elapsed_this_invocation_seconds': time.monotonic() - started,
              'verification': 'pending' if evaluation.get('backend') == 'none' else 'completed'}
    atomic_json(root / 'run_status.json', result)
    return result
