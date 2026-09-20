"""Per-task, paired and fixed-cohort exports, and evaluation of saved students.

Exporting never loads a model or executes generated programs. Post-hoc evaluation
is an explicit separate function: it writes a new run, never changes training
artifacts, and never retrains a missing checkpoint.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import re
from typing import Any

import numpy as np

from .metrics import compare_summaries
from .utils import atomic_json, stable_hash


def _read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2**20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(content, encoding='utf-8')
    temporary.replace(path)


def _csv(path, rows):
    rows = list(rows)
    if not rows:
        _write(path, '')
        return
    stream = io.StringIO(newline='')
    fields = list(dict.fromkeys(key for row in rows for key in row))
    writer = csv.DictWriter(stream, fields)
    writer.writeheader()
    writer.writerows(rows)
    _write(path, stream.getvalue())


def _available(root):
    candidates = [('base', 0, root / 'base')]
    for directory in sorted(root.iterdir()):
        if not directory.is_dir() or directory.name == 'base':
            continue
        for child in sorted(directory.iterdir()):
            match = re.fullmatch(r'round_([1-9][0-9]*)', child.name)
            if child.is_dir() and match:
                candidates.append((directory.name, int(match.group(1)), child))
    rows = []
    for method, round_index, directory in candidates:
        path = directory / 'evaluation.metrics.json'
        if not path.exists():
            continue
        summary = _read(path)
        if not summary.get('per_task'):
            continue
        budget = directory / 'evaluation.jsonl.budget.json'
        rows.append({'id': 'base' if method == 'base' else f'{method}/round_{round_index}',
                     'method': method, 'round': round_index, 'directory': directory,
                     'summary': summary, 'budget': _read(budget) if budget.exists() else None,
                     'metrics_sha256': _sha(path)})
    return sorted(rows, key=lambda row: (row['round'], row['method']))


def _values(data):
    """Names expose the exact fingerprint and sample population, not strategies."""
    result = {f'pass@{k}': value for k, value in data['pass_at_k'].items()}
    for source, name in [('implementation_proxy', 'AST'), ('exact_program', 'Exact program'),
                         ('control_flow_proxy', 'Control-flow')]:
        if source not in data:
            continue
        result.update({f'Correct {name} richness @{k}': value
                       for k, value in data[source]['coverage_at_k'].items()})
        result.update({f'Correct-conditioned {name} richness @{b}': value
                       for b, value in data[source]['correct_matched_coverage_at_budgets'].items()})
        for key, label in [('correct_label_entropy', 'correct-label entropy'),
                           ('simpson_diversity', 'Simpson diversity'),
                           ('unique_fraction', 'unique fraction')]:
            result[f'{name} {label}'] = data[source].get(key)
    return result


def _estimate(values, bootstrap_samples, seed):
    ordered = sorted(values)
    array = np.array([np.nan if values[key] is None else values[key] for key in ordered], dtype=float)
    valid = np.isfinite(array)
    replicates = []
    rng = np.random.default_rng(seed)
    # Batched draws keep memory bounded for larger task sets and bootstrap counts.
    if len(array) and valid.any():
        for start in range(0, bootstrap_samples, 128):
            indices = rng.integers(len(array), size=(min(128, bootstrap_samples - start), len(array)))
            draws = array[indices]
            counts = np.isfinite(draws).sum(axis=1)
            replicates.extend((np.nansum(draws[counts > 0], axis=1) / counts[counts > 0]).tolist())
    return {'mean': float(array[valid].mean()) if valid.any() else None,
            'ci95': np.quantile(replicates, [.025, .975]).tolist() if replicates else None,
            'eligible_tasks': int(valid.sum()), 'total_tasks': len(array),
            'eligible_task_ids': [key for key, yes in zip(ordered, valid) if yes],
            'bootstrap_valid_replicates': len(replicates)}


def _sampling_signature(stage):
    protocol = (stage['budget'] or {}).get('protocol')
    if not protocol or 'prompts' not in protocol or 'settings' not in protocol:
        return None
    return {key: value for key, value in protocol.items()
            if key not in {'model_identity', 'method', 'round'}}


def _retention_ratio(before, after, bootstrap_samples, seed):
    tasks = sorted(task for task in before if before[task] is not None and after.get(task) is not None)
    left = np.array([before[task] for task in tasks], dtype=float)
    right = np.array([after[task] for task in tasks], dtype=float)
    ratios = []
    rng = np.random.default_rng(seed)
    if len(tasks):
        for start in range(0, bootstrap_samples, 128):
            indices = rng.integers(len(tasks), size=(min(128, bootstrap_samples - start), len(tasks)))
            denominator, numerator = left[indices].mean(axis=1), right[indices].mean(axis=1)
            ratios.extend((numerator[denominator > 0] / denominator[denominator > 0]).tolist())
    return {'mean_ratio': float(right.mean() / left.mean()) if len(tasks) and left.mean() > 0 else None,
            'ci95': np.quantile(ratios, [.025, .975]).tolist() if ratios else None,
            'eligible_tasks': len(tasks), 'total_tasks': len(before), 'eligible_task_ids': tasks,
            'bootstrap_valid_replicates': len(ratios),
            'definition': 'ratio of task-macro richness, not mean task ratios or fingerprint identity overlap'}


def _comparable(reference, candidate):
    left, right = _sampling_signature(reference), _sampling_signature(candidate)
    if left is None or right is None:
        raise ValueError('explicit sampling metadata unavailable')
    if left != right:
        raise ValueError('sampling settings, prompts or seed differ')
    for stage in (reference, candidate):
        if not stage['summary']['protocol'].get('evaluation'):
            raise ValueError('explicit evaluation provenance unavailable')
    # Checks per-task counts, evaluator identity, task harnesses and metric versions.
    compare_summaries(reference['summary'], candidate['summary'], bootstrap_samples=0)


def _resource_rows(stage):
    directory = stage['directory']
    rows = []
    for path in sorted(directory.glob('*.resources.json')):
        data = _read(path)
        rows.append({'id': stage['id'], 'method': stage['method'], 'round': stage['round'],
                     'stage': data.get('stage', path.stem), 'status': data.get('status'),
                     'elapsed_seconds': data.get('elapsed_seconds'),
                     'cuda_peak_allocated_bytes': data.get('cuda_peak_allocated_bytes'),
                     'cuda_peak_reserved_bytes': data.get('cuda_peak_reserved_bytes'),
                     'attempt_count': len(data.get('attempts', [data])),
                     'resources_path': str(path), 'resources': data})
    return rows


def _length_rows(stage):
    output = []
    for kind in ('train', 'generation_policy', 'evaluation'):
        path = stage['directory'] / f'{kind}.jsonl'
        if not path.exists():
            continue
        lengths, prompt_lengths, capped, count = [], [], 0, 0
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                if not line.strip():
                    continue
                row = json.loads(line)
                count += 1
                if row.get('generation_tokens') is not None:
                    lengths.append(row['generation_tokens'])
                if row.get('prompt_tokens') is not None:
                    prompt_lengths.append(row['prompt_tokens'])
                capped += row.get('finish_reason') == 'length'
        output.append({'id': stage['id'], 'method': stage['method'], 'round': stage['round'],
                       'stage': kind, 'samples': count, 'samples_with_token_count': len(lengths),
                       'generation_tokens': sum(lengths) if lengths else None,
                       'prompt_tokens': sum(prompt_lengths) if prompt_lengths else None,
                       'mean_generation_tokens': float(np.mean(lengths)) if lengths else None,
                       'median_generation_tokens': float(np.median(lengths)) if lengths else None,
                       'p95_generation_tokens': float(np.quantile(lengths, .95)) if lengths else None,
                       'length_capped_samples': capped,
                       'length_capped_fraction': capped / count if count else None,
                       'raw_records_path': str(path)})
    return output


def export_longitudinal(run_dir, output_dir=None, *, bootstrap_samples=2000, seed=None,
                        reference_methods=('plain', 'ssd', 'spd_hard')):
    """Export all available rounds; CIs quantify task, not training-seed uncertainty.

    Outputs include full per-task metrics and label counts, metric trajectories,
    paired arm/adjacent-round differences, and common-eligibility trajectories.
    The fixed cohort intersects *every available included stage* separately for
    each metric. It is descriptive, explicitly selected after observing eligibility.
    Missing raw records or resources are reported as unavailable, not reconstructed.
    """
    root = Path(run_dir).resolve()
    output = Path(output_dir).resolve() if output_dir else root / 'longitudinal'
    if bootstrap_samples < 0:
        raise ValueError('bootstrap_samples must be nonnegative')
    manifest = _read(root / 'manifest.json') if (root / 'manifest.json').exists() else {}
    seed = int(seed if seed is not None else manifest.get('config', {}).get('seed', 42))
    stages = _available(root)
    if not stages:
        raise ValueError('No full per-task evaluation.metrics.json files found; compact reports cannot reconstruct task bootstrap')
    output.mkdir(parents=True, exist_ok=True)
    flattened = {stage['id']: {task: _values(data) for task, data in stage['summary']['per_task'].items()}
                 for stage in stages}
    metric_names = sorted({metric for values in flattened.values() for row in values.values() for metric in row})
    estimates, per_task = [], []
    for stage in stages:
        for task, data in stage['summary']['per_task'].items():
            per_task.append({'id': stage['id'], 'method': stage['method'], 'round': stage['round'],
                             'task_id': task, 'metrics': data})
        for metric in metric_names:
            estimate = _estimate({task: values.get(metric) for task, values in flattened[stage['id']].items()},
                                 bootstrap_samples, seed)
            estimates.append({'id': stage['id'], 'method': stage['method'], 'round': stage['round'],
                              'metric': metric, **estimate})
    by_id = {stage['id']: stage for stage in stages}
    pairs = set()
    for stage in stages:
        if stage['method'] == 'base':
            continue
        if 'base' in by_id:
            pairs.add(('base', stage['id'], 'initial_model'))
        previous = f"{stage['method']}/round_{stage['round'] - 1}"
        if previous in by_id:
            pairs.add((previous, stage['id'], 'adjacent_round'))
        for method in reference_methods:
            reference = f"{method}/round_{stage['round']}"
            if reference in by_id and reference != stage['id']:
                pairs.add((reference, stage['id'], 'same_round_method'))
    comparisons, paired_rows, retention_rows = [], [], []
    for reference, candidate, kind in sorted(pairs):
        row = {'reference': reference, 'candidate': candidate, 'kind': kind}
        try:
            _comparable(by_id[reference], by_id[candidate])
            result = compare_summaries(by_id[reference]['summary'], by_id[candidate]['summary'],
                                       bootstrap_samples=bootstrap_samples, seed=seed)
        except ValueError as exc:
            comparisons.append({**row, 'status': 'incomparable', 'reason': str(exc)})
            continue
        comparisons.append({**row, 'status': 'available', 'result': result})
        for metric in metric_names:
            values = {}
            for task, before in flattened[reference].items():
                left, right = before.get(metric), flattened[candidate][task].get(metric)
                values[task] = None if left is None or right is None else right - left
            paired_rows.append({**row, 'metric': metric,
                                **_estimate(values, bootstrap_samples, seed)})
            if kind == 'initial_model' and metric.startswith('Correct AST richness @'):
                retention_rows.append({**row, 'metric': metric, **_retention_ratio(
                    {task: data.get(metric) for task, data in flattened[reference].items()},
                    {task: data.get(metric) for task, data in flattened[candidate].items()},
                    bootstrap_samples, seed)})
    fixed, fixed_rows = {}, []
    fixed_issues = []
    for stage in stages[1:]:
        try:
            _comparable(stages[0], stage)
        except ValueError as exc:
            fixed_issues.append({'id': stage['id'], 'reason': str(exc)})
    if not fixed_issues:
        for metric in metric_names:
            cohorts = [{task for task, data in flattened[stage['id']].items() if data.get(metric) is not None}
                       for stage in stages]
            cohort = sorted(set.intersection(*cohorts))
            fixed[metric] = {'task_ids': cohort, 'task_count': len(cohort),
                             'included_stages': [stage['id'] for stage in stages]}
            for stage in stages:
                fixed_rows.append({'id': stage['id'], 'method': stage['method'], 'round': stage['round'],
                                   'metric': metric, **_estimate({task: flattened[stage['id']][task][metric]
                                                                for task in cohort}, bootstrap_samples, seed)})
    resources = [row for stage in stages for row in _resource_rows(stage)]
    lengths = [row for stage in stages for row in _length_rows(stage)]
    training = []
    for stage in stages:
        for path in (stage['directory'] / 'training_stats.json', stage['directory'] / 'model' / 'training_stats.json'):
            if path.exists():
                training.append({'id': stage['id'], 'method': stage['method'], 'round': stage['round'], **_read(path)})
                break
    report = {'schema_version': 1, 'run_dir': str(root), 'manifest': manifest,
              'bootstrap': {'unit': 'task', 'samples': bootstrap_samples, 'seed': seed,
                            'confidence': .95, 'interval': 'pointwise_percentile',
                            'training_seed_uncertainty': False},
              'stages': [{key: str(value) if isinstance(value, Path) else value
                          for key, value in stage.items() if key not in {'summary', 'budget'}} |
                         {'metric_protocol': stage['summary']['protocol'], 'generation_budget': stage['budget'],
                          'raw_records_available': (stage['directory'] / 'evaluation.jsonl').exists(),
                          'verified_records_available': (stage['directory'] / 'evaluation.verified.jsonl').exists(),
                          'resource_records_available': bool(list(stage['directory'].glob('*.resources.json')))}
                         for stage in stages],
              'estimates': estimates, 'paired_estimates': paired_rows, 'comparisons': comparisons,
              'retention_ratios': retention_rows, 'training_statistics': training,
              'fixed_cohort': fixed, 'fixed_cohort_issues': fixed_issues,
              'fixed_cohort_estimates': fixed_rows, 'resources': resources, 'sample_lengths': lengths,
              'definitions': stages[0]['summary'].get('definitions', {}),
              'notes': ['Fixed cohorts are intersections of eligibility across all available included stages.',
                        'Task-bootstrap intervals quantify evaluation-task uncertainty, not variation over training seeds.',
                        'Coverage retention is a count ratio; it is not identity overlap between solution sets.',
                        'Raw generation and verified program files remain at their source paths; per_task.jsonl preserves all task metrics and fingerprint counts.']}
    atomic_json(output / 'longitudinal.json', report)
    _write(output / 'per_task.jsonl', ''.join(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n'
                                           for row in per_task))
    for name, rows in [('trajectories', estimates), ('paired_differences', paired_rows),
                        ('fixed_cohort_trajectories', fixed_rows), ('retention_ratios', retention_rows)]:
        _csv(output / f'{name}.csv', [{key: value for key, value in row.items()
                                      if key not in {'ci95', 'eligible_task_ids'}} |
                                     {'ci95_low': row['ci95'][0] if row['ci95'] else None,
                                      'ci95_high': row['ci95'][1] if row['ci95'] else None}
                                     for row in rows])
    _csv(output / 'resources.csv', [{key: value for key, value in row.items() if key != 'resources'} for row in resources])
    _csv(output / 'sample_lengths.csv', lengths)
    _csv(output / 'training_statistics.csv', training)
    _write(output / 'README.md', '# Longitudinal self-distillation export\n\n'
           'Each CSV row is a task-macro estimate or a paired task difference. Intervals are pointwise 95% task-bootstrap intervals. '
           'The JSON preserves evaluation protocols, task eligibility and complete paired outputs. '
           'per_task.jsonl preserves per-task counts and fingerprint frequencies, enabling later fixed-cohort and identity-overlap analyses. '
           'This export does not estimate variation over training seeds. Empty CSV cells mean unavailable, never zero.\n')
    return report


def evaluate_checkpoints(run_dir, output_dir, *, samples=64, rounds=None, methods=None,
                         eval_tasks_path=None, model_settings=None, evaluation_overrides=None,
                         generation_overrides=None, bootstrap_samples=2000, resume=False,
                         evaluator=None, evaluator_identity=None):
    """Evaluate the initial model and retained round checkpoints in a new directory.

    No training is performed. Missing/pruned checkpoints are listed as unavailable.
    External tasks enable transfer evaluation. A custom evaluator must have the
    pipeline.evaluate_file signature and write .verified.jsonl and .metrics.json;
    evaluator_identity must explicitly identify its verifier/version/dataset.
    Historical configuration and completion markers are never altered.
    """
    import gc
    import torch
    from .data import read_jsonl, write_jsonl, validate_tasks, assert_disjoint_splits
    from .generation import generate_to_file
    from .modeling import load_model
    from .pipeline import (checkpoint_fingerprint, evaluate_file, execution_runtime_identity,
                           record_stage, _preflight_verification)

    root, output = Path(run_dir).resolve(), Path(output_dir).resolve()
    if output == root:
        raise ValueError('Use a separate output directory, not the training root')
    if type(samples) is not int or samples < 1:
        raise ValueError('samples must be a positive integer')
    manifest_path = root / 'manifest.json'
    source_manifest = _read(manifest_path)
    config = source_manifest['config']
    selected_methods = list(config['methods'] if methods is None else methods)
    for method in ['base', *config['methods']]:
        training_stage = root / method
        if output == training_stage or training_stage in output.parents:
            raise ValueError('Do not write post-hoc evaluation inside an immutable training stage')
    if not set(selected_methods) <= set(config['methods']):
        raise ValueError('Requested methods are absent from the source training manifest')
    selected_rounds = list(range(1, int(config.get('rounds', 1)) + 1)) if rounds is None else list(rounds)
    if not selected_rounds or any(type(value) is not int or not 1 <= value <= config.get('rounds', 1) for value in selected_rounds):
        raise ValueError('Requested rounds must exist in the source training protocol')
    if len(set(selected_methods)) != len(selected_methods) or len(set(selected_rounds)) != len(selected_rounds):
        raise ValueError('Methods and rounds must be unique')
    task_path = Path(eval_tasks_path) if eval_tasks_path else root / 'tasks' / 'eval.jsonl'
    tasks = read_jsonl(task_path)
    validate_tasks(tasks)
    if not tasks:
        raise ValueError('Evaluation requires nonempty tasks')
    if eval_tasks_path is None and source_manifest.get('selected_task_ids', {}).get('eval') != [task['task_id'] for task in tasks]:
        raise ValueError('Source evaluation task snapshot differs from its manifest')
    fit_snapshots = {name: read_jsonl(root / 'tasks' / f'{name}.jsonl')
                     for name in ('train', 'calibration', 'validation')}
    for name, rows in fit_snapshots.items():
        declared = source_manifest.get('selected_task_ids', {}).get(name)
        if declared is not None and declared != [task['task_id'] for task in rows]:
            raise ValueError(f'Source {name} task snapshot differs from its manifest')
    assert_disjoint_splits({**fit_snapshots, 'eval': tasks})
    seed = int(config.get('seed', 42))
    evaluation = {**config.get('evaluation', {}), **(evaluation_overrides or {}),
                  'bootstrap_samples': bootstrap_samples}
    evaluation.setdefault('correct_budget', 4)
    evaluation['ks'] = sorted({k for k in [1, 4, 8, 16, 32, samples] if k <= samples})
    evaluation['correct_budgets'] = sorted({b for b in [4, 8, 16, 32, samples] if b <= samples})
    evaluation['correct_budget'] = min(evaluation['correct_budget'], samples)
    if evaluation.get('backend', 'docker') == 'none' and evaluator is None:
        raise ValueError('Post-hoc evaluation requires an actual verifier')
    if evaluator is not None and not isinstance(evaluator_identity, dict):
        raise ValueError('Custom evaluators require an explicit evaluator_identity mapping')
    if evaluator is None:
        _preflight_verification(evaluation)
    generation = {key: value for key, value in config.get('generation', {}).items()
                  if key not in {'train_samples', 'eval_samples'}}
    generation.update(generation_overrides or {})
    generation['samples'] = samples
    settings = {**config['model'], **(model_settings or {})}
    base_marker = root / 'base' / 'complete.json'
    base_state = _read(base_marker) if base_marker.exists() else {}
    if base_state.get('resolved_revision') and not (model_settings or {}).get('revision'):
        settings['revision'] = base_state['resolved_revision']
    local_base = Path(settings['name'])
    local_base_sha = checkpoint_fingerprint(local_base) if local_base.is_dir() else None
    original_base_sha = source_manifest.get('local_base_fingerprint')
    if original_base_sha and local_base_sha != original_base_sha:
        raise ValueError('Local initial checkpoint differs from the training source')
    jobs = [('base', 0, None)] + [(method, index, root / method / f'round_{index}' / 'model')
                                for method in selected_methods for index in selected_rounds]
    checkpoint_hashes, missing = {}, []
    for method, index, checkpoint in jobs:
        name = 'base' if method == 'base' else f'{method}/round_{index}'
        if checkpoint is not None:
            if not (checkpoint / 'config.json').exists():
                missing.append({'id': name, 'reason': 'checkpoint_missing_or_pruned', 'checkpoint': str(checkpoint)})
                continue
            checkpoint_hashes[name] = checkpoint_fingerprint(checkpoint)
    protocol = {'source_run': str(root), 'source_manifest_sha256': _sha(manifest_path),
                'source_checkpoint_hashes': checkpoint_hashes, 'model': settings,
                'local_base_fingerprint': local_base_sha, 'task_sha256': _sha(task_path),
                'task_ids': [task['task_id'] for task in tasks], 'methods': selected_methods,
                'task_records_sha256': stable_hash(tasks),
                'fit_snapshot_records_sha256': {name: stable_hash(rows) for name, rows in fit_snapshots.items()},
                'rounds': selected_rounds, 'generation': generation, 'evaluation': evaluation,
                'evaluator_identity': evaluator_identity, 'seed': seed,
                'evaluation_runtime': execution_runtime_identity(evaluation),
                'implementation_hashes': {path.name: _sha(path) for path in Path(__file__).parent.glob('*.py')}}
    fingerprint = stable_hash(protocol)
    target_manifest = output / 'manifest.json'
    if target_manifest.exists():
        if not resume:
            raise FileExistsError('Evaluation output exists; use resume=True')
        if _read(target_manifest).get('fingerprint') != fingerprint:
            raise ValueError('Post-hoc protocol or source checkpoint changed; use a new output directory')
        for name, expected_rows in {**fit_snapshots, 'eval': tasks}.items():
            snapshot = output / 'tasks' / f'{name}.jsonl'
            if not snapshot.exists() or stable_hash(read_jsonl(snapshot)) != stable_hash(expected_rows):
                raise ValueError(f'Post-hoc task snapshot missing or changed: {snapshot}')
    else:
        if output.exists() and any(output.iterdir()):
            raise ValueError('Nonempty post-hoc directory has no manifest')
        atomic_json(target_manifest, {'schema_version': 1, 'fingerprint': fingerprint,
                    'purpose': 'saved_checkpoint_evaluation_without_training', 'protocol': protocol,
                    'config': {**config, 'methods': selected_methods, 'model': settings,
                               'generation': {**generation, 'eval_samples': samples}, 'evaluation': evaluation},
                    'selected_task_ids': {name: [task['task_id'] for task in rows]
                                          for name, rows in {**fit_snapshots, 'eval': tasks}.items()},
                    'unavailable_checkpoints': missing})
        for name, rows in {**fit_snapshots, 'eval': tasks}.items():
            write_jsonl(output / 'tasks' / f'{name}.jsonl', rows)
    verify = evaluate_file if evaluator is None else evaluator
    missing_ids = {row['id'] for row in missing}
    completed = []
    for method, index, checkpoint in jobs:
        name = 'base' if method == 'base' else f'{method}/round_{index}'
        if name in missing_ids:
            continue
        directory = output / name
        marker = directory / 'complete.json'
        if marker.exists():
            state = _read(marker)
            if state.get('protocol_fingerprint') != fingerprint or any(
                    not (directory / relative).exists() or _sha(directory / relative) != digest
                    for relative, digest in state['files'].items()):
                raise ValueError(f'Post-hoc completion integrity failure: {directory}')
            completed.append(name)
            continue
        with record_stage(directory, 'model_loading'):
            model, tokenizer = load_model(settings, checkpoint)
        try:
            revision = getattr(model.config, '_commit_hash', None)
            identity = stable_hash([settings, checkpoint_hashes.get(name, local_base_sha), revision])
            if method == 'base' and base_state.get('resolved_revision') and revision != base_state['resolved_revision']:
                raise ValueError('Loaded initial model revision differs from training source')
            path = directory / 'evaluation.jsonl'
            with record_stage(directory, 'evaluation_generation'):
                records = generate_to_file(model, tokenizer, tasks, path, generation,
                                            seed=seed, model_identity=identity, method=method,
                                            round_index=index, stage='evaluation', resume=resume)
            with record_stage(directory, 'verification_and_metrics'):
                summary = verify(tasks, records, path, evaluation, expected_samples=samples, seed=seed)
            if set(summary.get('per_task', {})) != {task['task_id'] for task in tasks}:
                raise ValueError('Evaluator did not return the complete task universe')
            expected = [path, path.with_suffix('.verified.jsonl'), path.with_suffix('.metrics.json')]
            if any(not item.exists() for item in expected):
                raise ValueError('Evaluator must preserve verified programs and full metrics')
            files = {str(item.relative_to(directory)): _sha(item) for item in directory.rglob('*')
                     if item.is_file() and '.parts' not in item.parts and not any(part.endswith('.parts') for part in item.parts)
                     and item.name != 'complete.json'}
            atomic_json(marker, {'status': 'completed', 'protocol_fingerprint': fingerprint,
                                  'model_identity': identity, 'files': files})
            completed.append(name)
        finally:
            del model, tokenizer
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    status = {'status': 'partial' if missing else 'completed', 'completed': completed,
              'unavailable_checkpoints': missing, 'missing_checkpoints': missing, 'training_performed': False,
              'output_dir': str(output)}
    atomic_json(output / 'run_status.json', status)
    return status
