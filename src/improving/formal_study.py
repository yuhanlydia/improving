"""Preregistered, resumable Spectral-soft experiment orchestration.

Each job uses the ordinary raw-corpus self-distillation pipeline. No evaluation
outcome changes the protocol, methods, seeds, or number of rounds.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml

from .data import assert_disjoint_splits, read_jsonl
from .pipeline import checkpoint_fingerprint, file_sha, run_experiment, validate_config
from .utils import atomic_json, stable_hash

PHASES = ('confirm', 'mechanism', 'retention')
STAGES = ('validate', *PHASES, 'transfer', 'report', 'export', 'all')
CORE = ['plain', 'ssd', 'spd_hard', 'spectral_soft']
CONTROLS = ['matched_blend', 'random_soft', 'isotropic_soft']
RETENTION = ['plain', 'spd_hard', 'spectral_soft']


def load_formal_config(path):
    with Path(path).open(encoding='utf-8') as stream:
        return validate_formal_config(yaml.safe_load(stream))


def validate_formal_config(config):
    if not isinstance(config, dict):
        raise ValueError('Formal configuration must be a mapping')
    for key in ('model', 'data', 'output_dir', 'formal', 'transfer'):
        if not config.get(key):
            raise ValueError(f'Missing formal configuration {key}')
    formal = config['formal']
    for phase in PHASES:
        values = formal.get(f'{phase}_seeds')
        if (not isinstance(values, list) or not values or
                any(type(value) is not int or value < 0 for value in values) or len(set(values)) != len(values)):
            raise ValueError(f'formal.{phase}_seeds must contain unique nonnegative integers')
    if len(formal['confirm_seeds']) < 5 or 42 in formal['confirm_seeds']:
        raise ValueError('Confirmation needs at least five new seeds; pilot seed42 remains exploratory')
    for key, expected in [('core_methods', CORE), ('mechanism_methods', CONTROLS),
                          ('retention_methods', RETENTION)]:
        if formal.get(key) != expected:
            raise ValueError(f'formal.{key} must be {expected}; use a separately named protocol for different comparisons')
    if not set(formal['mechanism_seeds']) <= set(formal['confirm_seeds']):
        raise ValueError('Mechanism seeds need matching confirmation references')
    rounds = formal.get('retention_rounds', 3)
    if type(rounds) is not int or rounds < 2:
        raise ValueError('retention_rounds must be at least two')
    if config.get('data_limits'):
        raise ValueError('Formal profiles use all prepared tasks; use geometry/pilot for subsets')
    ev, gen, cal = (config.get(name, {}) for name in ('evaluation', 'generation', 'calibration'))
    if ev.get('backend') != 'docker' or ev.get('code_extraction') != 'first_fence':
        raise ValueError('Formal task-test protocol requires Docker and first_fence extraction')
    if ev.get('correctness_margin') != .01 or ev.get('correct_budget') != 4:
        raise ValueError('Formal primary endpoints fix correctness_margin=.01 and correct_budget=4')
    if ev.get('correct_budgets') != [4, 8, 16] or gen.get('eval_samples') != 64:
        raise ValueError('Formal protocol requires 64 samples and correct budgets [4,8,16]')
    if ev.get('ks') != [1, 8, 32, 64] or gen.get('train_samples') != 1:
        raise ValueError('Formal protocol fixes ks=[1,8,32,64] and one raw training completion')
    if cal.get('tau') != 1 or cal.get('rank_fraction') != .5 or cal.get('rank') is not None:
        raise ValueError('Formal v1 freezes tau=1 and hard rank_fraction=.5 before confirmation')
    if config.get('train', {}).get('loss_scope') != 'all':
        raise ValueError('Formal v1 uses raw-corpus all-token LoRA loss')
    reps = formal.get('bootstrap_samples', 2000)
    if type(reps) is not int or reps < 1000:
        raise ValueError('Formal bootstrap_samples must be at least 1000')
    if config['transfer'].get('samples', 64) != 64 or config['transfer'].get('methods', CORE) != CORE:
        raise ValueError('HumanEval+ transfer uses the same four methods and 64 samples')
    if not config['transfer'].get('tasks'):
        raise ValueError('transfer.tasks is required')
    for job in compile_jobs(config):
        validate_config(job['config'])
    return config


def compile_jobs(config):
    formal, jobs = config['formal'], []
    for phase, key in [('confirm', 'core_methods'), ('mechanism', 'mechanism_methods'),
                       ('retention', 'retention_methods')]:
        for seed in formal[f'{phase}_seeds']:
            job_id = f'{phase}_seed{seed}'
            job = copy.deepcopy({k: v for k, v in config.items() if k not in {'formal', 'transfer'}})
            job.update(seed=seed, methods=list(formal[key]),
                       rounds=formal.get('retention_rounds', 3) if phase == 'retention' else 1,
                       output_dir=str(Path(config['output_dir']) / phase / f'seed_{seed}'))
            jobs.append({'id': job_id, 'phase': phase, 'seed': seed, 'config': job})
    return jobs


def formal_budget(config):
    splits = {name: read_jsonl(path) for name, path in config['data'].items()}
    if set(splits) != {'train', 'calibration', 'validation', 'eval'} or any(not v for v in splits.values()):
        raise ValueError('Four nonempty prepared MBPP partitions are required')
    assert_disjoint_splits(splits)
    nt, ne = len(splits['train']), len(splits['eval'])
    gen, diag = config['generation'], config.get('diagnostics', {})
    n = gen['eval_samples']
    dn = diag.get('eval_samples') or n
    dt = min(diag.get('eval_task_limit') or ne, ne)
    diagnostic = dn * dt if diag.get('evaluate_generation_policy', True) else 0
    counts = {}
    for job in compile_jobs(config):
        settings = job['config']
        counts[job['id']] = {'phase': job['phase'], 'base': ne * n,
            'training': len(settings['methods']) * settings['rounds'] * nt * gen['train_samples'],
            'generating_policy': len(settings['methods']) * settings['rounds'] * diagnostic,
            'post_lora': len(settings['methods']) * settings['rounds'] * ne * n}
        counts[job['id']]['total'] = sum(counts[job['id']][key] for key in ('base', 'training', 'generating_policy', 'post_lora'))
    by_phase = {phase: sum(row['total'] for row in counts.values() if row['phase'] == phase) for phase in PHASES}
    # Full, pinned official HumanEval+ population. The transfer worker checks it.
    by_phase['transfer'] = len(config['formal']['confirm_seeds']) * (len(CORE) + 1) * 164 * 64
    total = sum(by_phase.values())
    return {'split_counts': {k: len(v) for k, v in splits.items()}, 'jobs': counts,
            'candidates_by_phase': by_phase, 'total_candidates_upper_bound': total,
            'generated_tokens_upper_bound': total * gen.get('max_new_tokens', 512),
            'note': 'Includes repeated base/round-one runs for independent sealed phases. These are candidate and token caps, not walltime/FLOP estimates. No stage is skipped on a favorable or unfavorable result.'}


def _suite_identity(config):
    local = Path(config['model']['name'])
    source_root = Path(__file__).parent
    scripts = source_root.parents[1] / 'scripts'
    source = {p.name: file_sha(p) for p in source_root.glob('*.py')}
    source.update({f'scripts/{p.name}': file_sha(p) for p in scripts.glob('*.sh')})
    return stable_hash({'config': config, 'source': source,
        'data': {k: file_sha(p) for k, p in config['data'].items()},
        'local_model': checkpoint_fingerprint(local) if local.is_dir() else None})


def _resolve_model(settings):
    """Resolve once before any job; every seed uses the same base revision."""
    result = dict(settings)
    if not Path(settings['name']).is_dir():
        from huggingface_hub import HfApi
        revision = HfApi().model_info(settings['name'], revision=settings.get('revision')).sha
        if not isinstance(revision, str) or len(revision) != 40:
            raise ValueError('Could not resolve an immutable model revision')
        result['revision'] = revision
    return result


def open_suite(config, *, resume=False):
    root = Path(config['output_dir'])
    path = root / 'suite.json'
    saved = json.loads(path.read_text()) if path.exists() else None
    if saved is not None and not resume:
        raise FileExistsError('Formal suite exists; use --resume or a new output_dir')
    if saved is None and root.exists() and any(root.iterdir()):
        raise ValueError('Nonempty suite directory has no suite.json identity')
    resolved_model = saved['resolved_model'] if saved is not None else _resolve_model(config['model'])
    resolved_config = {**config, 'model': resolved_model}
    identity = stable_hash([_suite_identity(config), resolved_model])
    payload = {'schema_version': 1, 'identity': identity, 'config': config,
               'resolved_model': resolved_model,
               'jobs': compile_jobs(resolved_config), 'budget': formal_budget(config),
               'protocol': {'primary': 'post_lora_round1_correct_matched_AST_coverage_at4',
                            'primary_comparators': ['plain', 'spd_hard'], 'correctness_margin': .01,
                            'confirmatory_family_size': 4, 'posthoc_selection': False}}
    if path.exists():
        if saved != payload:
            raise ValueError('Formal suite configuration/data/implementation changed; resume is refused')
    else:
        atomic_json(path, payload)
    for job in payload['jobs']:
        job_path = root / 'configs' / f'{job["id"]}.yaml'
        if job_path.exists() and yaml.safe_load(job_path.read_text()) != job['config']:
            raise ValueError(f'Compiled job configuration changed: {job_path}')
        if not job_path.exists():
            job_path.parent.mkdir(parents=True, exist_ok=True)
            job_path.write_text(yaml.safe_dump(job['config'], sort_keys=False), encoding='utf-8')
    return payload


def _check_job_result(job):
    root = Path(job['config']['output_dir'])
    status = root / 'run_status.json'
    if not status.exists() or json.loads(status.read_text()).get('status') != 'completed':
        raise ValueError(f'Pipeline did not complete: {job["id"]}')
    for method in job['config']['methods']:
        for r in range(1, job['config']['rounds'] + 1):
            path = root / method / f'round_{r}' / 'complete.json'
            if not path.exists():
                raise ValueError(f'Missing completed checkpoint: {path}')


def run_formal(config, *, stage='confirm', resume=False, include_programs=False, job_id=None):
    validate_formal_config(config)
    if stage not in STAGES:
        raise ValueError(f'Unknown formal stage {stage}')
    if stage == 'validate':
        return {'valid': True, **formal_budget(config)}
    suite = open_suite(config, resume=resume)
    if job_id and stage not in PHASES:
        raise ValueError('--job-id is only supported for confirm/mechanism/retention')
    if job_id and not any(j['id'] == job_id and j['phase'] == stage for j in suite['jobs']):
        raise ValueError(f'No job {job_id!r} in phase {stage}')
    stages = (*PHASES, 'transfer', 'report', 'export') if stage == 'all' else (stage,)
    completed = []
    for phase in stages:
        if phase in PHASES:
            for job in suite['jobs']:
                if job['phase'] != phase or (job_id and job['id'] != job_id):
                    continue
                print(f'formal {job["id"]}: starting/resuming', flush=True)
                run_experiment(job['config'], resume=resume)
                _check_job_result(job)
                completed.append(job['id'])
        elif phase == 'transfer':
            from .formal_transfer import run_transfer
            result = run_transfer(config, [j for j in suite['jobs'] if j['phase'] == 'confirm'], resume=resume)
            atomic_json(Path(config['output_dir']) / 'transfer' / 'index.json', result)
        elif phase == 'report':
            from .formal_reporting import build_formal_report
            build_formal_report(Path(config['output_dir']) / 'suite.json')
        elif phase == 'export':
            from .formal_reporting import export_evidence
            export_evidence(Path(config['output_dir']) / 'suite.json', include_programs=include_programs)
    return {'output_dir': config['output_dir'], 'stage': stage, 'completed_jobs': completed,
            'report': str(Path(config['output_dir']) / 'report' / 'summary.md')}
