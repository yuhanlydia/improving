"""Read-only formal inference and portable evidence from completed artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import tarfile
import tempfile
import os

from .formal_statistics import compare_seed_summaries
from .pipeline import file_sha
from .utils import atomic_json, stable_hash


def _load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _csv(path, rows):
    keys = sorted({k for row in rows for k in row})
    with Path(path).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def _signature(config, method, stage):
    gen = {k: v for k, v in config['generation'].items() if k not in {'train_samples', 'eval_samples'}}
    if stage == 'generation_policy' and method == 'ssd':
        gen.update(temperature=1.5, top_p=.8, top_k=20)
    return stable_hash({'model': config['model'], 'generation': gen, 'data': config['data'],
                        'data_seed': config.get('data_seed', 42)})


def _completed_summary(directory, filename, *, expected_tasks, expected_samples):
    marker = directory / 'complete.json'
    if not marker.exists():
        return None
    state = _load(marker)
    path = directory / filename
    verified = path.with_name(filename.replace('.metrics.json', '.verified.jsonl'))
    for artifact in (path, verified):
        expected = state.get('files', {}).get(artifact.name)
        if not expected or not artifact.exists() or file_sha(artifact) != expected:
            raise ValueError(f'Missing/modified sealed evaluation artifact: {artifact}')
    summary = _load(path)
    if set(summary.get('per_task', {})) != set(expected_tasks):
        raise ValueError(f'Wrong evaluation task universe: {path}')
    if any(row['sample_count'] != expected_samples for row in summary['per_task'].values()):
        raise ValueError(f'Wrong completion budget: {path}')
    return summary, path, verified


def collect_entries(suite):
    entries = []
    for job in suite['jobs']:
        config, seed = job['config'], job['seed']
        root = Path(config['output_dir'])
        manifest = root / 'manifest.json'
        if not manifest.exists():
            continue
        run = _load(manifest)
        if run.get('config') != config:
            raise ValueError(f'Run configuration differs from registered job: {job["id"]}')
        tasks = run['selected_task_ids']['eval']
        diagnostic_tasks = run.get('generation_diagnostic_task_ids', tasks)
        n = config['generation']['eval_samples']
        dn = config.get('diagnostics', {}).get('eval_samples') or n
        stages = [('base', 0, 'base', root / 'base', 'evaluation.metrics.json', tasks, n)]
        for method in config['methods']:
            for r in range(1, config['rounds'] + 1):
                directory = root / method / f'round_{r}'
                stages.append((method, r, 'evaluation', directory, 'evaluation.metrics.json', tasks, n))
                if config.get('diagnostics', {}).get('evaluate_generation_policy', True):
                    stages.append((method, r, 'generation_policy', directory, 'generation_policy.metrics.json', diagnostic_tasks, dn))
        for method, r, stage, directory, filename, task_ids, samples in stages:
            value = _completed_summary(directory, filename, expected_tasks=task_ids, expected_samples=samples)
            if value is None:
                continue
            summary, path, verified = value
            entries.append({'phase': job['phase'], 'seed': seed, 'method': method,
                            'round': r, 'stage': stage, 'summary': summary,
                            'path': str(path), 'verified_path': str(verified),
                            'sampling_signature': _signature(config, method, stage)})
    index = Path(suite['config']['output_dir']) / 'transfer' / 'index.json'
    if index.exists():
        transfer_index = _load(index)
        transfer_manifest = index.parent / 'humanevalplus' / 'manifest.json'
        if (transfer_index.get('status') != 'completed' or not transfer_manifest.exists() or
                _load(transfer_manifest).get('identity') != transfer_index.get('identity')):
            raise ValueError('Transfer index differs from sealed source manifest')
        transfer_state = _load(transfer_manifest)
        sources = {(s['seed'], s['method']): s for s in transfer_state['sources']}
        generation = {k: v for k, v in suite['config']['generation'].items()
                      if k not in {'train_samples', 'eval_samples'}}
        generation['samples'] = 64
        for item in transfer_index.get('trials', []):
            if (item['seed'] not in suite['config']['formal']['confirm_seeds'] or
                    item['method'] not in ['base', *suite['config']['formal']['core_methods']] or
                    item.get('round') != (0 if item['method'] == 'base' else 1)):
                raise ValueError('Transfer seed/method/checkpoint differs from registered protocol')
            path = Path(item['metrics_path'])
            marker = Path(item['complete_path'])
            state = _load(marker)
            if state.get('status') != 'completed' or not state.get('identity'):
                raise ValueError('Invalid transfer completion marker')
            source = sources.get((item['seed'], item['method']))
            expected_identity = stable_hash([transfer_state['identity'], source, generation,
                suite['config']['evaluation']['code_extraction']])
            if source is None or state['identity'] != expected_identity:
                raise ValueError('Transfer trial label differs from its sealed source checkpoint')
            for artifact in (path, Path(item['verified_path'])):
                artifact = artifact.resolve()
                if not artifact.is_relative_to(marker.parent.resolve()):
                    raise ValueError('Transfer artifact lies outside its sealed trial')
                key = str(artifact.relative_to(marker.parent.resolve()))
                if not artifact.exists() or file_sha(artifact) != state.get('files', {}).get(key):
                    raise ValueError(f'Modified transfer evaluation artifact: {artifact}')
            summary = _load(path)
            if set(summary.get('per_task', {})) != {f'HumanEval/{i}' for i in range(164)} or any(
                    row['sample_count'] != 64 for row in summary['per_task'].values()):
                raise ValueError('Incomplete HumanEval+ transfer population')
            entries.append({'phase': 'transfer', 'seed': item['seed'], 'method': item['method'],
                'round': item.get('round', 0 if item['method'] == 'base' else 1),
                'stage': 'evaluation', 'summary': summary, 'path': str(path),
                'verified_path': item['verified_path'],
                'sampling_signature': stable_hash(suite['config']['generation'])})
    return entries


def _rows(entries):
    rows, per_task = [], []
    for item in entries:
        labels = {k: item[k] for k in ('phase', 'seed', 'method', 'round', 'stage')}
        data = item['summary']
        aggregate, proxy = data['aggregate'], data['aggregate']['implementation_proxy']
        row = {**labels, 'task_count': len(data['per_task']),
               'pass_at_1': aggregate['correct_fraction']['mean'],
               'ast_unique_fraction': proxy['unique_fraction']['mean'],
               'ast_simpson': proxy['simpson_diversity']['mean'],
               'metrics_path': item['path'], 'metrics_sha256': file_sha(item['path'])}
        for k, value in aggregate['pass_at_k'].items():
            row[f'pass_at_{k}'] = value['mean']
        for k, value in proxy['coverage_at_k'].items():
            row[f'ast_coverage_at_{k}'] = value['all_task_mean']
        for budget, value in proxy['correct_matched_coverage_at_budgets'].items():
            row[f'ast_correct_coverage_{budget}'] = value['mean']
            row[f'eligible_tasks_{budget}'] = value['eligible_tasks']
        rows.append(row)
        for task_id, task in data['per_task'].items():
            # Scalar sufficient statistics for paired comparisons; label counts
            # and executable programs remain in separately preserved source files.
            def compact(value):
                return {k: v for k, v in value.items() if k != 'counts'}
            per_task.append({**labels, 'task_id': task_id, 'sample_count': task['sample_count'],
                'correct_count': task['correct_count'], 'correct_fraction': task['correct_fraction'],
                'pass_at_k': task['pass_at_k'],
                'implementation_proxy': compact(task['implementation_proxy']),
                'exact_program': compact(task['exact_program']), 'control_flow_proxy': compact(task['control_flow_proxy']),
                'strategy': compact(task['strategy']), 'lexical': task['lexical'],
                'source_metrics': item['path'], 'protocol_hash': stable_hash(data['protocol'])})
    return rows, per_task


def build_formal_report(manifest_path):
    suite = _load(manifest_path)
    config = suite['config']
    root = Path(config['output_dir'])
    directory = root / 'report'
    directory.mkdir(parents=True, exist_ok=True)
    entries = collect_entries(suite)
    rows, task_rows = _rows(entries)
    cache = {(e['phase'], e['stage'], e['round'], e['method'], e['seed']): e for e in entries}
    if len(cache) != len(entries):
        raise ValueError('Duplicate formal trial identity')
    comparisons = []

    def compare(phase, stage, r, control, *, reference_phase=None, seeds=None, family=4, primary=False):
        expected = seeds or config['formal'][f'{phase}_seeds']
        current_phase = 'confirm' if phase == 'mechanism' else phase
        old_phase = reference_phase or phase
        old_stage = 'base' if control == 'base' and phase != 'transfer' else stage
        old_round = 0 if control == 'base' else r
        result = {'phase': phase, 'stage': stage, 'round': r, 'candidate': 'spectral_soft',
                  'reference': control, 'primary': primary, 'expected_seeds': expected}
        current, previous, signatures = {}, {}, []
        missing = []
        for seed in expected:
            newer = cache.get((current_phase, stage, r, 'spectral_soft', seed))
            older = cache.get((old_phase, old_stage, old_round, control, seed))
            if newer is None or older is None:
                missing.append(seed)
                continue
            current[str(seed)], previous[str(seed)] = newer['summary'], older['summary']
            signatures.append(newer['sampling_signature'] == older['sampling_signature'])
        if missing:
            result.update(status='pending', missing_seeds=missing)
        elif not all(signatures):
            result.update(status='incomparable_decoding', reason='Generating-policy decoding differs; no representation-only attribution.')
        else:
            result.update(status='completed', statistics=compare_seed_summaries(previous, current,
                correctness_margin=.01, correct_budgets=(4, 8, 16),
                bootstrap_samples=config['formal'].get('bootstrap_samples', 2000),
                seed=config.get('data_seed', 42), family_size=family))
        comparisons.append(result)

    for stage in ('evaluation', 'generation_policy'):
        for control in ('plain', 'spd_hard', 'ssd'):
            compare('confirm', stage, 1, control, family=4 if control != 'ssd' else 2,
                    primary=stage == 'evaluation' and control != 'ssd')
    compare('confirm', 'evaluation', 1, 'base', family=2)
    for stage in ('evaluation', 'generation_policy'):
        for control in config['formal']['mechanism_methods']:
            compare('mechanism', stage, 1, control, family=6)
    for r in range(1, config['formal'].get('retention_rounds', 3) + 1):
        for control in ('plain', 'spd_hard'):
            compare('retention', 'evaluation', r, control, family=4 * config['formal'].get('retention_rounds', 3))
    for control in ('plain', 'spd_hard', 'ssd', 'base'):
        compare('transfer', 'evaluation', 1, control, seeds=config['formal']['confirm_seeds'], family=8)
    primary = [c for c in comparisons if c['primary']]
    decision = 'pending'
    if all(c['status'] == 'completed' for c in primary):
        successes = [c['statistics']['decision']['success'] for c in primary]
        decision = ('supported' if all(v is True for v in successes) else
                    'inconclusive' if any(v is None for v in successes) else 'not_supported')
    result = {'suite_identity': suite['identity'], 'primary_decision': decision,
              'definition': 'Final round-one AST correct-coverage@4 superior and correctness noninferior versus BOTH plain and SPD-hard under the declared simultaneous intervals.',
              'completed_trial_count': len(entries), 'budget': suite['budget'],
              'comparisons': comparisons,
              'limits': ['AST/lexical metrics are implementation proxies, not semantic algorithm labels.',
                  'Fixed-correct metrics use matched eligible questions; available populations and null bootstrap replicates are explicit.',
                  'Bootstrap uncertainty is approximate; five seeds do not establish all-backbone robustness.',
                  'Generating policy and post-LoRA results are separate. SSD policy decoding differs.',
                  'Operator norm matching does not match activation RMS or output KL.',
                  'Main confirmation, mechanism, retention and HumanEval+ transfer are distinct claims.']}
    atomic_json(directory / 'summary.json', result)
    _csv(directory / 'per_seed.csv', rows)
    with (directory / 'per_task.jsonl').open('w', encoding='utf-8') as stream:
        for row in task_rows:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
    comparative_rows = []
    for comp in comparisons:
        row = {k: comp[k] for k in ('phase', 'stage', 'round', 'candidate', 'reference', 'primary', 'status')}
        if comp['status'] == 'completed':
            stats = comp['statistics']
            for name, delta in [('correctness', stats['correctness']['delta']),
                ('AST_correct_coverage_4', stats['implementation_proxy']['correct_matched_coverage_at_budgets']['4'])]:
                row.update({f'{name}_delta': delta['mean'], f'{name}_ci95': delta['ci95'],
                            f'{name}_simultaneous_ci': delta['ci95_family']})
            row['decision'] = stats['decision']['success']
        comparative_rows.append(row)
    _csv(directory / 'comparisons.csv', comparative_rows)
    lines = ['# Formal Spectral-soft evidence', '', f'Primary confirmation: **{decision}**.', '', result['definition'], '',
             '| Phase | Stage | Round | Comparator | Status | Correctness delta | AST@4 delta |',
             '|---|---|---:|---|---|---:|---:|']
    for row in comparative_rows:
        def number(key):
            value = row.get(key)
            return '—' if value is None else f'{value:.5f}'
        lines.append(f'| {row["phase"]} | {row["stage"]} | {row["round"]} | {row["reference"]} | {row["status"]} | {number("correctness_delta")} | {number("AST_correct_coverage_4_delta")} |')
    lines += ['', 'Pointwise and simultaneous intervals, per-seed effects and matched eligibility are in `summary.json` and `comparisons.csv`.', '', '## Interpretation', '']
    lines += [f'- {s}' for s in result['limits']]
    (directory / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return {'report': str(directory / 'summary.md'), 'primary_decision': decision,
            'completed_trial_count': len(entries)}


def export_evidence(manifest_path, *, include_programs=False):
    suite = _load(manifest_path)
    root = Path(suite['config']['output_dir']).resolve()
    build_formal_report(manifest_path)
    files = {Path(manifest_path).resolve()}
    for path in (root / 'configs').glob('*.yaml'):
        files.add(path.resolve())
    for path in (root / 'report').glob('*'):
        if path.is_file():
            files.add(path.resolve())
    for job in suite['jobs']:
        job_root = Path(job['config']['output_dir'])
        for path in job_root.rglob('*'):
            if not path.is_file() or any(part in {'model'} or part.endswith('.parts') for part in path.relative_to(job_root).parts):
                continue
            if (path.name.endswith(('.metrics.json', '.resources.json')) or
                    path.name in {'manifest.json', 'run_status.json', 'complete.json', 'operator_diagnostics.json', 'budget.json'} or
                    path.parent.name == 'tasks' or
                    (include_programs and path.suffix == '.jsonl')):
                files.add(path.resolve())
    transfer = root / 'transfer'
    if transfer.exists():
        for path in transfer.rglob('*'):
            if not path.is_file() or any(part.endswith('.parts') for part in path.relative_to(transfer).parts):
                continue
            if (path.name in {'index.json', 'manifest.json', 'results.json', 'complete.json', 'identity.json', 'metrics.json', 'environment.txt',
                              'evaluation_metadata.json', 'dataset_metadata.json'} or
                    path.name.endswith(('.metrics.json', '.resources.json')) or
                    (include_programs and path.suffix in {'.jsonl', '.json'})):
                files.add(path.resolve())
    directory = root / 'evidence'
    directory.mkdir(parents=True, exist_ok=True)
    index = []
    for path in sorted(files):
        if not path.is_relative_to(root):
            raise ValueError(f'Evidence file is outside the suite: {path}')
        index.append({'path': str(path.relative_to(root)), 'sha256': file_sha(path), 'bytes': path.stat().st_size})
    manifest = directory / ('programs_manifest.json' if include_programs else 'compact_manifest.json')
    atomic_json(manifest, {'suite_identity': suite['identity'], 'includes_programs': include_programs,
                           'files': index, 'excludes': ['model weights', 'generation batch caches', 'credentials']})
    destination = directory / ('programs.tar.gz' if include_programs else 'compact.tar.gz')
    handle, temporary = tempfile.mkstemp(dir=directory, suffix='.tar.gz')
    os.close(handle)
    try:
        with tarfile.open(temporary, 'w:gz') as archive:
            for path in sorted(files | {manifest.resolve()}):
                archive.add(path, arcname=str(path.relative_to(root)), recursive=False)
        os.replace(temporary, destination)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()
    return {'archive': str(destination), 'sha256': file_sha(destination),
            'files': len(index), 'includes_programs': include_programs}
