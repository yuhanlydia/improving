"""Frozen-model, question-disjoint solution-subspace experiments.

This diagnostic intentionally precedes LoRA/co-evolution. Every learned bank is
fit on discovery tasks and selected on validation tasks before final evaluation.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from contextlib import nullcontext
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import random
import tempfile

import torch
import yaml

from .data import assert_disjoint_splits, read_jsonl, write_jsonl
from .generation import generate_to_file
from .metrics import summarize_records, compare_summaries
from .modeling import load_model
from .pipeline import file_sha, checkpoint_fingerprint, record_stage, _preflight_verification
from .spectral import folded_operators
from .utils import atomic_json, stable_hash
from .verification import verify_completions

STAGES = ('discover', 'extract', 'analyze', 'relations', 'select', 'evaluate', 'report')


def _positive(value, name):
    if type(value) is not int or value < 1:
        raise ValueError(f'{name} must be a positive integer')
    return value


def load_geometry_config(path):
    with Path(path).open() as stream:
        return validate_geometry_config(yaml.safe_load(stream))


def validate_geometry_config(config):
    if not isinstance(config, dict):
        raise ValueError('Geometry configuration must be a mapping')
    for key in ('model', 'data', 'output_dir'):
        if not config.get(key):
            raise ValueError(f'Missing geometry configuration {key}')
    if not config['model'].get('name'):
        raise ValueError('model.name is required')
    if set(config['data']) != {'train', 'calibration', 'validation', 'eval'}:
        raise ValueError('data requires prepared train/calibration/validation/eval paths')
    for key in ('seed', 'data_seed'):
        if type(config.get(key, 42)) is not int:
            raise ValueError(f'{key} must be an integer')
    for section, key, default in [('discovery', 'samples', 32),
            ('discovery', 'max_correct_per_task', 10), ('extraction', 'max_length', 1536),
            ('extraction', 'max_rank', 32), ('selection', 'samples', 16),
            ('final', 'samples', 32), ('relations', 'samples', 16),
            ('relations', 'max_tasks', 16), ('relations', 'rank', 8),
            ('generation', 'batch_size', 4), ('generation', 'max_new_tokens', 512)]:
        _positive(config.get(section, {}).get(key, default), f'{section}.{key}')
    geometry = config.get('geometry', {})
    for key, default in [('ranks', [4, 8, 16, 32]), ('bank_sizes', [1, 2, 4, 8])]:
        values = geometry.get(key, default)
        if not isinstance(values, list) or not values or len(set(values)) != len(values):
            raise ValueError(f'geometry.{key} must be a nonempty unique list')
        for value in values:
            _positive(value, f'geometry.{key}')
    if max(geometry.get('ranks', [4, 8, 16, 32])) > config.get('extraction', {}).get('max_rank', 32):
        raise ValueError('extraction.max_rank must cover the entire rank grid')
    for stage in ('selection', 'final'):
        n = config.get(stage, {}).get('samples', 16 if stage == 'selection' else 32)
        if max(geometry.get('bank_sizes', [1, 2, 4, 8])) > n:
            raise ValueError(f'{stage}.samples must allow one rollout per bank member')
    if config.get('extraction', {}).get('span_mode', 'completion') not in {'completion', 'explicit'}:
        raise ValueError('extraction.span_mode must be completion or explicit')
    for section in ('selection', 'relations'):
        value = config.get(section, {}).get('strength', 1.0)
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f'{section}.strength must be finite and positive')
    tolerance = config.get('selection', {}).get('correctness_tolerance', .05)
    if not isinstance(tolerance, (int, float)) or not math.isfinite(tolerance) or not 0 <= tolerance <= 1:
        raise ValueError('selection.correctness_tolerance must lie in [0,1]')
    if config.get('selection', {}).get('metric', 'ast_proxy_coverage') != 'ast_proxy_coverage':
        raise ValueError('Only explicitly labelled ast_proxy_coverage selection is implemented')
    ev = config.get('evaluation', {})
    if ev.get('backend', 'docker') not in {'docker', 'local'}:
        raise ValueError('Geometry requires verification; backend must be docker or explicitly trusted local')
    if ev.get('backend') == 'local' and not ev.get('allow_unsafe_local', False):
        raise ValueError('Local execution requires evaluation.allow_unsafe_local')
    if ev.get('code_extraction', 'strict') not in {'strict', 'first_fence'}:
        raise ValueError('evaluation.code_extraction must be strict or first_fence')
    return config


def geometry_splits(config):
    source = {name: read_jsonl(path) for name, path in config['data'].items()}
    assert_disjoint_splits(source)
    splits = {'train': [dict(row, split='train') for name in ('train', 'calibration') for row in source[name]],
              'validation': source['validation'], 'eval': source['eval']}
    for name, count in config.get('data_limits', {}).items():
        if name not in splits or type(count) is not int or not 1 <= count <= len(splits[name]):
            raise ValueError(f'Invalid data_limits.{name}')
        ordered = sorted(splits[name], key=lambda row: row['task_id'])
        random.Random(config.get('data_seed', 42)).shuffle(ordered)
        splits[name] = ordered[:count]
    if any(not rows for rows in splits.values()):
        raise ValueError('Discovery, validation and final evaluation partitions must be nonempty')
    assert_disjoint_splits(splits)
    return splits


def geometry_budget(config, splits):
    nt, nv, ne = (len(splits[key]) for key in ('train', 'validation', 'eval'))
    grid = len(config.get('geometry', {}).get('ranks', [4, 8, 16, 32])) * len(
        config.get('geometry', {}).get('bank_sizes', [1, 2, 4, 8]))
    relations = config.get('relations', {})
    relation_arms = 7 + len(relations.get('interpolation', [.25, .5, .75]))
    counts = {'discovery': nt * config.get('discovery', {}).get('samples', 32),
              'validation_upper_bound': nv * (grid + 1) * config.get('selection', {}).get('samples', 16),
              'test_upper_bound': ne * 4 * config.get('final', {}).get('samples', 32),
              'relations_upper_bound': (min(nt, relations.get('max_tasks', 16)) * relation_arms *
                   relations.get('samples', 16)) if relations.get('enabled', True) else 0}
    return {'split_counts': {key: len(value) for key, value in splits.items()},
            'candidates': counts, 'total_candidates_upper_bound': sum(counts.values()),
            'generated_tokens_upper_bound': sum(counts.values()) * config.get('generation', {}).get('max_new_tokens', 512),
            'gradient_extractions_upper_bound': nt * (config.get('discovery', {}).get('max_correct_per_task', 10) +
                int(config.get('discovery', {}).get('format_controls', True))),
            'note': 'Candidate counts are not correct-program or algorithm counts. No GPU runtime/memory claim.'}


def _write_pt(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            name = stream.name
            torch.save(value, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name and Path(name).exists():
            Path(name).unlink()


def _seal(path, identity):
    path = Path(path)
    atomic_json(path.with_suffix(path.suffix + '.done.json'), {'identity': identity, 'sha256': file_sha(path)})


def _completed(path, identity):
    path = Path(path)
    seal = path.with_suffix(path.suffix + '.done.json')
    if not seal.exists():
        return False
    value = json.loads(seal.read_text())
    if value.get('identity') != identity or not path.exists() or file_sha(path) != value.get('sha256'):
        raise ValueError(f'Modified or incompatible completed artifact: {path}')
    return True


def _tensor_hash(value):
    return hashlib.sha256(value.detach().cpu().double().contiguous().numpy().tobytes()).hexdigest()


class GeometryStudy:
    def __init__(self, config, *, resume=False, model=None, tokenizer=None):
        self.config = validate_geometry_config(config)
        self.splits = geometry_splits(config)
        self.root = Path(config['output_dir'])
        self.seed = config.get('seed', 42)
        self.resume = resume
        self.model, self.tokenizer = model, tokenizer
        files = {p.name: file_sha(p) for p in Path(__file__).parent.glob('*.py')}
        local = Path(config['model']['name'])
        self.fingerprint = stable_hash({'config': config, 'data': {key: file_sha(path) for key, path in config['data'].items()},
            'implementation': files, 'local_model': checkpoint_fingerprint(local) if local.is_dir() else None})
        manifest_path = self.root / 'manifest.json'
        if manifest_path.exists():
            if not resume:
                raise FileExistsError('Geometry run exists; use --resume or a new output_dir')
            self.manifest = json.loads(manifest_path.read_text())
            if self.manifest['fingerprint'] != self.fingerprint:
                raise ValueError('Geometry resume configuration/data/implementation differs')
        else:
            if self.root.exists() and any(self.root.iterdir()):
                raise ValueError('Nonempty output directory has no geometry manifest')
            self.manifest = {'format_version': 1, 'fingerprint': self.fingerprint, 'config': config,
                             'budget': geometry_budget(config, self.splits), 'model_revision': None}
            atomic_json(manifest_path, self.manifest)
        for name, tasks in self.splits.items():
            path = self.root / 'tasks' / f'{name}.jsonl'
            if path.exists() and read_jsonl(path) != tasks:
                raise ValueError('Saved geometry task partition changed')
            if not path.exists():
                write_jsonl(path, tasks)

    def load(self):
        if self.model is None:
            settings = dict(self.config['model'])
            if self.manifest.get('model_revision'):
                settings['revision'] = self.manifest['model_revision']
            self.model, self.tokenizer = load_model(settings)
        revision = getattr(self.model.config, '_commit_hash', None)
        saved = self.manifest.get('model_revision')
        if saved is not None and revision is not None and saved != revision:
            raise ValueError('Loaded model revision differs from run')
        if saved is None and revision is not None:
            self.manifest['model_revision'] = revision
            atomic_json(self.root / 'manifest.json', self.manifest)
        return self.model, self.tokenizer

    def _identity(self, value):
        return stable_hash([self.fingerprint, self.manifest.get('model_revision'), value])

    def _verify(self, tasks, records, directory):
        directory = Path(directory)
        grouped = defaultdict(list)
        for row in records:
            grouped[row['task_id']].append(row)
        result = []
        for task in tasks:
            rows = grouped[task['task_id']]
            if not rows:
                raise ValueError(f'Missing generated candidates for {task["task_id"]}')
            path = directory / f'{stable_hash(task["task_id"])[:20]}.jsonl'
            identity = self._identity([task, rows, self.config.get('evaluation', {})])
            if _completed(path, identity):
                verified = read_jsonl(path)
            else:
                ev = self.config.get('evaluation', {})
                verified = verify_completions([task], rows, backend=ev.get('backend', 'docker'),
                    docker_image=ev.get('docker_image', 'python:3.11-slim'),
                    timeout=ev.get('timeout', 5), workers=ev.get('workers', 4),
                    memory_mb=ev.get('memory_mb', 512), pids_limit=ev.get('pids_limit', 64),
                    code_extraction=ev.get('code_extraction', 'strict'),
                    allow_unsafe_local=ev.get('allow_unsafe_local', False), expected_samples=len(rows))
                write_jsonl(path, verified)
                _seal(path, identity)
            result.extend(verified)
        return result

    def discover(self):
        model, tokenizer = self.load()
        n = self.config.get('discovery', {}).get('samples', 32)
        settings = {**self.config.get('generation', {}), 'samples': n}
        counts = []
        for task in self.splits['train']:
            directory = self.root / 'discovery' / stable_hash(task['task_id'])[:20]
            records = generate_to_file(model, tokenizer, [task], directory / 'samples.jsonl', settings,
                seed=self.seed, model_identity=self._identity('native'), method='geometry_discovery',
                stage='geometry_discovery', resume=self.resume)
            verified = self._verify([task], records, directory / 'verification')
            write_jsonl(directory / 'verified.jsonl', verified)
            counts.append({'task_id': task['task_id'], 'candidates': len(records),
                           'correct': sum(row['correct'] for row in verified)})
            print(f'geometry discovery {len(counts)}/{len(self.splits["train"])}: {task["task_id"]}', flush=True)
        atomic_json(self.root / 'discovery' / 'counts.json', counts)

    def extract(self):
        from .geometry_extraction import collect_solution_subspaces, SolutionTooLongError
        model, tokenizer = self.load()
        settings = {**self.config.get('extraction', {}), 'seed': self.seed}
        cap = self.config.get('discovery', {}).get('max_correct_per_task', 10)
        index, controls = [], []
        for task in self.splits['train']:
            key = stable_hash(task['task_id'])[:20]
            discovery = self.root / 'discovery' / key
            records = read_jsonl(discovery / 'verified.jsonl')
            # Validate the original sealed verifier artifacts, not merely an unsealed aggregate.
            raw = read_jsonl(discovery / 'samples.jsonl')
            if records != self._verify([task], raw, discovery / 'verification'):
                raise ValueError('Discovery verification aggregate changed')
            correct = [row for row in records if row['correct']]
            selected = sorted(correct, key=lambda row: stable_hash([self.seed, task['task_id'], row['sample_id']]))[:cap]
            work = [(row, False, None) for row in selected]
            format_controls = self.config.get('discovery', {}).get('format_controls', True)
            if selected and format_controls and settings.get('span_mode') == 'explicit':
                controls.append({'task_id': task['task_id'], 'source_sample_id': selected[0]['sample_id'],
                    'status': 'skipped', 'reason': 'Formatting changes character offsets; no remapped explicit spans provided.'})
            elif selected and format_controls:
                base = selected[0]
                try:
                    # Use exactly the executable program verified above. In
                    # first_fence mode the completion may also contain prose.
                    formatted = ast.unparse(ast.parse(base['code'])) + '\n'
                except (SyntaxError, ValueError):
                    formatted = None
                if formatted and formatted != base['completion']:
                    control = {'task_id': task['task_id'], 'sample_id': 1000000 + base['sample_id'],
                               'completion': formatted, 'source_sample_id': base['sample_id'],
                               'control': 'ast_unparse', 'finish_reason': 'eos'}
                    verified = self._verify([task], [control], discovery / 'format_verification')[0]
                    controls.append({'task_id': task['task_id'], 'source_sample_id': base['sample_id'],
                                     'correct': verified['correct'], 'status': verified['status']})
                    if verified['correct']:
                        work.append((verified, True, base['sample_id']))
            for record, is_control, source in work:
                if settings.get('span_mode') == 'explicit' and not record.get('loss_spans'):
                    raise ValueError('Explicit mask needs implementation-specific loss_spans; never reuse reference spans')
                path = self.root / 'subspaces' / key / f'{record["sample_id"]}.pt'
                identity = self._identity([record, settings])
                if not _completed(path, identity):
                    try:
                        artifact = collect_solution_subspaces(model, tokenizer, task, record, settings)
                    except SolutionTooLongError as error:
                        if not is_control:
                            raise
                        controls.append({'task_id': task['task_id'], 'source_sample_id': source,
                            'status': 'extraction_skipped', 'reason': str(error)})
                        continue
                    artifact['metadata'].update({'model_identity': self._identity('native'), 'record_hash': stable_hash(record),
                        'is_format_control': is_control, 'source_sample_id': source, 'completion': record['completion'],
                        'record': record, 'split': 'train'})
                    _write_pt(path, artifact)
                    _seal(path, identity)
                index.append({'task_id': task['task_id'], 'sample_id': record['sample_id'],
                              'path': str(path.relative_to(self.root)), 'sha256': file_sha(path),
                              'is_format_control': is_control, 'source_sample_id': source})
            print(f'geometry extract {task["task_id"]}: {len(selected)}/{len(correct)} correct candidates', flush=True)
        path = self.root / 'subspaces' / 'index.json'
        atomic_json(path, index)
        _seal(path, self._identity('subspace_index'))
        atomic_json(self.root / 'analysis' / 'format_verification.json', controls)

    def artifacts(self, include_controls=False):
        path = self.root / 'subspaces' / 'index.json'
        if not _completed(path, self._identity('subspace_index')):
            raise ValueError('Run geometry extract before analysis/selection')
        output = []
        for row in json.loads(path.read_text()):
            artifact_path = self.root / row['path']
            if not artifact_path.exists() or file_sha(artifact_path) != row['sha256']:
                raise ValueError(f'Modified subspace artifact: {artifact_path}')
            if include_controls or not row['is_format_control']:
                output.append(torch.load(artifact_path, map_location='cpu', weights_only=True))
        return output

    def analyze(self):
        from .geometry_analysis import summarize_geometry
        from .geometry import compare_subspaces
        settings = self.config.get('geometry', {})
        artifacts = self.artifacts()
        result = summarize_geometry(artifacts, ranks=settings.get('ranks', [4, 8, 16, 32]),
            max_pairs_per_task=settings.get('max_pairs_per_task', 20), seed=self.seed)
        result['discovery_task_universe'] = len(self.splits['train'])
        result['tasks_with_any_extracted_correct'] = len({item['task_id'] for item in artifacts})
        result['counts'] = json.loads((self.root / 'discovery' / 'counts.json').read_text())
        atomic_json(self.root / 'analysis' / 'geometry.json', result)
        originals = {(item['task_id'], item['sample_id']): item for item in artifacts}
        controls = []
        for item in self.artifacts(include_controls=True):
            if not item['metadata']['is_format_control']:
                continue
            source = originals[(item['task_id'], item['metadata']['source_sample_id'])]
            for name, module in item['modules'].items():
                for rank in settings.get('ranks', [4, 8, 16, 32]):
                    left, right = source['modules'][name]['basis'], module['basis']
                    if min(left.shape[1], right.shape[1]) >= rank:
                        controls.append({'task_id': item['task_id'], 'module': name, 'rank': rank,
                            'control': 'verified_ast_unparse', **compare_subspaces(left[:, :rank], right[:, :rank])})
        atomic_json(self.root / 'analysis' / 'format_controls.json', controls)

    def _operator_stats(self, operators):
        result = {}
        model, _ = self.load()
        for name, matrix in operators.items():
            delta = matrix.detach().double() - torch.eye(matrix.shape[0], dtype=torch.float64)
            weight = model.get_submodule(name).weight.detach().cpu().double()
            result[name] = {'residual_frobenius': float(delta.norm()),
                            'weight_delta_relative_frobenius': float((delta.T @ weight).norm() / weight.norm().clamp_min(1e-30)),
                            'operator_sha256': _tensor_hash(matrix)}
        return result

    def trial(self, tasks, directory, operator_sets, samples, name):
        model, tokenizer = self.load()
        directory = Path(directory)
        if not operator_sets:
            operator_sets = [{}]
        if samples < len(operator_sets):
            raise ValueError('Sampling budget smaller than number of sources')
        operator_ids = [{key: _tensor_hash(value) for key, value in item.items()} for item in operator_sets]
        identity = self._identity([name, [task['task_id'] for task in tasks], operator_ids, samples])
        summary_path = directory / 'summary.json'
        if _completed(summary_path, identity):
            candidate_path = directory / 'verified.jsonl'
            if not _completed(candidate_path, identity):
                raise ValueError('Completed trial lacks intact verified candidates')
            return json.loads(summary_path.read_text())
        combined, diagnostics, offset = [], [], 0
        for source, operators in enumerate(operator_sets):
            count = samples // len(operator_sets) + int(source < samples % len(operator_sets))
            settings = {**self.config.get('generation', {}), 'samples': count}
            source_dir = directory / f'source_{source}'
            diagnostics.append(self._operator_stats(operators))
            with folded_operators(model, operators) if operators else nullcontext(model):
                raw = generate_to_file(model, tokenizer, tasks, source_dir / 'samples.jsonl', settings,
                    seed=self.seed + source * 104729, model_identity=identity,
                    method=name, stage='geometry_probe', resume=self.resume)
            verified = self._verify(tasks, raw, source_dir / 'verification')
            for row in verified:
                combined.append({**row, 'sample_id': row['sample_id'] + offset, 'subspace_source': source,
                                 'source_sample_id': row['sample_id']})
            offset += count
        write_jsonl(directory / 'verified.jsonl', combined)
        _seal(directory / 'verified.jsonl', identity)
        ev = self.config.get('evaluation', {})
        ks = sorted({1, min(8, samples), samples})
        summary = summarize_records(combined, ks=ks, correct_budget=ev.get('correct_budget', 4),
            bootstrap_samples=ev.get('bootstrap_samples', 1000), seed=self.seed,
            expected_samples={task['task_id']: samples for task in tasks})
        summary['geometry_protocol'] = {'arm': name, 'sources': len(operator_sets), 'operator_diagnostics': diagnostics,
            'allocation': 'fixed approximately equal counts per source',
            'estimator_caveat': 'For stratified sources, combinatorial pass/coverage@k describe a random subset of the finite candidate set; not an unbiased iid-mixture pass@k estimator.',
            'matched': 'candidate budget and per-module operator residual Frobenius norm; activation RMS/output KL not matched',
            'identity': identity}
        atomic_json(summary_path, summary)
        _seal(summary_path, identity)
        return summary

    def relations(self):
        from .geometry_analysis import build_bank, operator_family
        from .geometry_extraction import score_solution
        settings = self.config.get('relations', {})
        if not settings.get('enabled', True):
            atomic_json(self.root / 'relations' / 'index.json', {'status': 'disabled', 'tasks': []})
            return
        grouped = defaultdict(list)
        for item in self.artifacts():
            grouped[item['task_id']].append(item)
        tasks = {task['task_id']: task for task in self.splits['train']}
        eligible, skipped = [], []
        for task_id in sorted(grouped, key=lambda key: stable_hash([self.seed, key])):
            try:
                pair = build_bank(grouped[task_id], rank=settings.get('rank', 8), count=2, seed=self.seed)
            except ValueError as error:
                skipped.append({'task_id': task_id, 'reason': str(error)})
                continue
            eligible.append((task_id, pair))
            if len(eligible) >= settings.get('max_tasks', 16):
                break
        completed = []
        for task_id, pair in eligible:
            directory = self.root / 'relations' / stable_hash(task_id)[:20]
            operators = operator_family(pair, strength=settings.get('strength', 1),
                interpolation=settings.get('interpolation', [.25, .5, .75]), seed=self.seed)
            operators = {'plain': {}, **operators}
            scores = []
            for name, operation in operators.items():
                self.trial([tasks[task_id]], directory / name, [operation], settings.get('samples', 16), name)
                model, tokenizer = self.load()
                with folded_operators(model, operation) if operation else nullcontext(model):
                    for target in pair:
                        value = score_solution(model, tokenizer, tasks[task_id], target['metadata']['record'],
                                               self.config.get('extraction', {}))
                        scores.append({'task_id': task_id, 'arm': name, 'target_sample_id': target['sample_id'], **value})
            atomic_json(directory / 'cross_likelihood.json', {'rows': scores,
                'caveat': 'Source-program teacher-forced fit is descriptive; fresh generation is the causal outcome.'})
            completed.append({'task_id': task_id, 'path': str(directory.relative_to(self.root)), 'arms': list(operators)})
            print(f'geometry relations {len(completed)}/{len(eligible)}: {task_id}', flush=True)
        atomic_json(self.root / 'relations' / 'index.json', {'status': 'completed', 'tasks': completed,
            'skipped': skipped, 'population': 'discovery-only tasks with at least two sufficiently ranked correct implementations'})

    def _bank_operators(self, bank, strength, randomize=False):
        from .geometry import normalized_operator
        output = []
        for index, artifact in enumerate(bank):
            modules = {}
            for name, record in artifact['modules'].items():
                basis = record['basis']
                if randomize:
                    generator = torch.Generator().manual_seed(int(stable_hash([self.seed, name, index])[:8], 16))
                    basis = torch.linalg.qr(torch.randn(basis.shape, generator=generator, dtype=torch.float64), mode='reduced')[0]
                modules[name] = normalized_operator(basis, strength=strength)
            output.append(modules)
        return output

    def select(self):
        from .geometry_analysis import build_bank
        settings = self.config.get('selection', {})
        directory = self.root / 'selection'
        lock = directory / 'locked.json'
        if _completed(lock, self._identity('selection_lock')):
            return
        # Final outputs are never consulted during selection.
        if (self.root / 'final').exists():
            raise ValueError('Cannot select after final evaluation has started without an intact selection lock')
        baseline = self.trial(self.splits['validation'], directory / 'plain', [{}], settings.get('samples', 16), 'plain')
        native_accuracy = baseline['aggregate']['correct_fraction']['mean']
        artifacts = self.artifacts()
        rows, candidates = [], []
        geometry = self.config.get('geometry', {})
        for rank in geometry.get('ranks', [4, 8, 16, 32]):
            for count in geometry.get('bank_sizes', [1, 2, 4, 8]):
                name = f'r{rank}_m{count}'
                try:
                    bank = build_bank(artifacts, rank=rank, count=count, seed=self.seed)
                except ValueError as error:
                    rows.append({'rank': rank, 'count': count, 'name': name, 'status': 'insufficient_support', 'reason': str(error)})
                    continue
                summary = self.trial(self.splits['validation'], directory / name,
                    self._bank_operators(bank, settings.get('strength', 1)), settings.get('samples', 16), name)
                accuracy = summary['aggregate']['correct_fraction']['mean']
                coverage = summary['aggregate']['implementation_proxy']['coverage_at_k'][str(settings.get('samples', 16))]['all_task_mean']
                allowed = accuracy >= native_accuracy - settings.get('correctness_tolerance', .05) and coverage is not None
                row = {'rank': rank, 'count': count, 'name': name, 'status': 'eligible' if allowed else 'rejected',
                       'correct_fraction': accuracy, 'ast_proxy_coverage': coverage,
                       'baseline_correct_fraction': native_accuracy}
                rows.append(row)
                if allowed:
                    candidates.append((row, bank))
                atomic_json(directory / 'grid.json', rows)
                print(f'geometry selection {name}: {row["status"]}', flush=True)
        atomic_json(directory / 'grid.json', rows)
        if candidates:
            winner, bank = sorted(candidates, key=lambda item: (-item[0]['ast_proxy_coverage'],
                -item[0]['correct_fraction'], item[0]['count'], item[0]['rank']))[0]
            _write_pt(directory / 'bank.pt', bank)
            result = {'status': 'selected', **winner, 'bank_sha256': file_sha(directory / 'bank.pt')}
            # Do not let the row's eligibility label override the lifecycle status.
            result['status'] = 'selected'
        else:
            result = {'status': 'no_eligible_bank', 'reason': 'No supported bank passed validation correctness/proxy requirements'}
        result.update({'criterion': 'max validation full-budget correct AST-proxy coverage within correctness tolerance; ties: accuracy, fewer sources, smaller rank',
                       'semantic_claim': False, 'source_split': 'train', 'selection_split': 'validation',
                       'validation_task_ids': [task['task_id'] for task in self.splits['validation']]})
        atomic_json(lock, result)
        _seal(lock, self._identity('selection_lock'))

    def evaluate(self):
        from .geometry_analysis import operator_family
        lock = self.root / 'selection' / 'locked.json'
        if not _completed(lock, self._identity('selection_lock')):
            raise ValueError('An intact validation selection lock is required before final evaluation')
        selection = json.loads(lock.read_text())
        n = self.config.get('final', {}).get('samples', 32)
        arms = {'plain': [{}]}
        if selection['status'] == 'selected':
            path = self.root / 'selection' / 'bank.pt'
            if not path.exists() or file_sha(path) != selection['bank_sha256']:
                raise ValueError('Selected bank changed after validation lock')
            bank = torch.load(path, map_location='cpu', weights_only=True)
            strength = self.config.get('selection', {}).get('strength', 1)
            arms['learned_bank'] = self._bank_operators(bank, strength)
            arms['random_bank'] = self._bank_operators(bank, strength, randomize=True)
            arms['pooled'] = [operator_family(bank, strength=strength, interpolation=[], seed=self.seed)['pooled']]
        summaries = {}
        for name, operators in arms.items():
            summaries[name] = self.trial(self.splits['eval'], self.root / 'final' / name, operators, n, name)
        comparisons = {name: compare_summaries(summaries['plain'], summary,
            correctness_margin=self.config.get('selection', {}).get('correctness_tolerance', .05),
            bootstrap_samples=self.config.get('evaluation', {}).get('bootstrap_samples', 1000), seed=self.seed)
            for name, summary in summaries.items() if name != 'plain'}
        for control in ('random_bank', 'pooled'):
            if 'learned_bank' in summaries and control in summaries:
                comparisons[f'learned_bank_vs_{control}'] = compare_summaries(
                    summaries[control], summaries['learned_bank'],
                    correctness_margin=self.config.get('selection', {}).get('correctness_tolerance', .05),
                    bootstrap_samples=self.config.get('evaluation', {}).get('bootstrap_samples', 1000), seed=self.seed)
        atomic_json(self.root / 'final' / 'comparisons.json', comparisons)
        atomic_json(self.root / 'final' / 'index.json', {'arms': list(arms), 'selection': selection,
                    'test_task_ids': [task['task_id'] for task in self.splits['eval']]})

    def report(self):
        return build_geometry_report(self.root)


def _csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                             for key, value in row.items()})


def build_geometry_report(root):
    root = Path(root)
    directory = root / 'report'
    directory.mkdir(parents=True, exist_ok=True)
    def optional(path, default):
        path = root / path
        return json.loads(path.read_text()) if path.exists() else default
    manifest = optional('manifest.json', {})
    geometry = optional('analysis/geometry.json', {})
    grid = optional('selection/grid.json', [])
    selection = optional('selection/locked.json', {'status': 'not_run'})
    final = optional('final/index.json', {'arms': []})
    rows = []
    paths = sorted((root / 'relations').glob('*/*/summary.json')) if (root / 'relations').exists() else []
    paths += sorted((root / 'final').glob('*/summary.json')) if (root / 'final').exists() else []
    for path in paths:
        summary = json.loads(path.read_text())
        aggregate = summary['aggregate']
        k = str(max(summary['protocol']['ks']))
        rows.append({'stage': 'final' if path.parent.parent.name == 'final' else 'relations',
                     'arm': path.parent.name, 'path': str(path.relative_to(root)),
                     'tasks': aggregate['task_count'], 'samples': aggregate['sample_count'],
                     'correct_fraction': aggregate['correct_fraction']['mean'],
                     'full_budget': int(k),
                     'ast_proxy_coverage': aggregate['implementation_proxy']['coverage_at_k'][k]['all_task_mean'],
                     'algorithm_coverage': aggregate['strategy']['coverage_at_k'][k]['all_task_mean']})
    pairs = [{**{key: value for key, value in row.items() if key != 'metrics'}, **row.get('metrics', {})}
             for row in geometry.get('pairs', geometry.get('pairwise', []))]
    _csv(directory / 'geometry_pairs.csv', pairs)
    _csv(directory / 'bank_selection.csv', grid)
    _csv(directory / 'generation_metrics.csv', rows)
    result = {'selection': selection, 'budget': manifest.get('budget'), 'generation': rows,
              'discovery_task_universe': geometry.get('discovery_task_universe'),
              'tasks_with_any_extracted_correct': geometry.get('tasks_with_any_extracted_correct'),
              'final_arms': final.get('arms', []), 'comparisons': optional('final/comparisons.json', {}),
              'model_frozen': True, 'lora_trained': False,
              'limitations': ['AST proxy is not algorithm identity; no semantic coverage claim without independent annotations.',
                  'Different subspace rank or basis does not imply a different algorithm.',
                  'Only validation selects rank/source count; final test is locked.',
                  'Operator Frobenius norm is matched; activation RMS and output KL are not matched.',
                  'Completion mask differs from SPD assertion-relevant spans.',
                  'No LoRA absorption or coevolution has been tested by this diagnostic.']}
    atomic_json(directory / 'summary.json', result)
    lines = ['# Solution-subspace geometry study', '', f'Selection status: `{selection["status"]}`.',
             '', 'Model weights stayed fixed. This run does not establish LoRA absorption or coevolution.', '',
             '| Stage | Arm | Tasks | Correct fraction | Correct AST proxy coverage |', '|---|---|---:|---:|---:|']
    for row in rows:
        lines.append(f'| {row["stage"]} | {row["arm"]} | {row["tasks"]} | {row["correct_fraction"]:.4f} | {row["ast_proxy_coverage"]} |')
    lines += ['', '## Limits', ''] + [f'- {line}' for line in result['limitations']]
    (directory / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        final_rows = [row for row in rows if row['stage'] == 'final']
        if final_rows:
            fig, axes = plt.subplots(1, 2, figsize=(10, 4))
            names = [row['arm'] for row in final_rows]
            for ax, key, label in zip(axes, ['correct_fraction', 'ast_proxy_coverage'],
                                     ['Correct fraction', 'Correct implementation coverage (AST proxy)']):
                ax.bar(names, [row[key] or 0 for row in final_rows])
                ax.set_ylabel(label)
                ax.tick_params(axis='x', rotation=25)
            fig.tight_layout()
            fig.savefig(directory / 'generation_metrics.png', dpi=180)
            plt.close(fig)
        groups = defaultdict(list)
        for row in pairs:
            if row.get('comparison') == 'fixed_rank' and row.get('overlap_min') is not None:
                groups[(row['module'], row['rank_a'])].append(row['overlap_min'])
        if groups:
            modules = sorted({key[0] for key in groups})
            ranks = sorted({key[1] for key in groups})
            fig, axes = plt.subplots(len(modules), len(ranks), squeeze=False,
                                     figsize=(4 * len(ranks), 3 * len(modules)))
            for i, module in enumerate(modules):
                for j, rank in enumerate(ranks):
                    ax = axes[i, j]
                    values = groups.get((module, rank), [])
                    ax.hist(values, bins=20, range=(0, 1))
                    ax.set(xlabel='Subspace overlap', ylabel='Pairs',
                           title=f'{module}\nrank {rank} (descriptive)')
            fig.tight_layout()
            fig.savefig(directory / 'geometry_overlap.png', dpi=180)
            plt.close(fig)
    except ImportError:
        result['plots'] = 'Install improving-code[analysis] for PNG plots; CSV/JSON reports are complete.'
        atomic_json(directory / 'summary.json', result)
    return {'output_dir': str(directory), 'selection_status': selection['status'], 'final_arms': result['final_arms']}


def run_geometry(config, *, stage='all', resume=False, model=None, tokenizer=None):
    validate_geometry_config(config)
    if stage == 'validate':
        return {'valid': True, **geometry_budget(config, geometry_splits(config))}
    if stage not in (*STAGES, 'all'):
        raise ValueError(f'Unknown geometry stage: {stage}')
    if stage == 'report':
        return build_geometry_report(config['output_dir'])
    if stage != 'analyze':
        _preflight_verification(config.get('evaluation', {}))
    study = GeometryStudy(config, resume=resume, model=model, tokenizer=tokenizer)
    for name in STAGES if stage == 'all' else (stage,):
        with record_stage(study.root, f'geometry_{name}'):
            getattr(study, name)()
    return {'output_dir': str(study.root), 'completed_stage': stage,
            'report': str(study.root / 'report' / 'summary.md') if stage == 'all' else None}
