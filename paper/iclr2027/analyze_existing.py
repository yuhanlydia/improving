#!/usr/bin/env python3
"""Extract and analyze committed results only. Never imports a model/evaluator.

Run from any directory. --refresh-sources copies exact selected fields from
the repository archives; the default rebuilds derived summaries from the
included compact source data. New bootstrap intervals resample saved tasks,
not training runs or model outputs. No code samples are executed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = HERE / 'source-data'
SOURCE = DATA / 'rewrite_sources.json'
SEED, NBOOT = 20260924, 2000

def read(path):
    return json.loads(path.read_text())

def small(value):
    if isinstance(value, dict):
        return {k: small(v) for k, v in value.items()
                if k not in {'unavailable_tasks', 'runtime_identity', 'implementation_hashes'}}
    if isinstance(value, list):
        return [small(v) for v in value]
    return value

def extract():
    provenance = []
    def get(rel):
        p = ROOT / rel
        provenance.append({'path': rel, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
        return read(p)
    old = 'results/retention_5round_train16_eval16_seed43/'
    report = get(old + 'report.json')
    stages = {s['id']: small(s['metrics']) for s in report['stages']
              if s['stage'] == 'evaluation' and s.get('metrics') is not None}
    comparisons = {c['candidate'] + ' - ' + c['reference']: small(c['result'])
                   for c in report['comparisons'] if c.get('result')}
    result = {'source_commit': subprocess.check_output(
        ['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'mbpp16': stages, 'mbpp16_comparisons': comparisons,
        'mbpp64': small(get(old + 'eval64/metrics_compact.json')),
        'mbpp64_comparisons': small(get(old + 'eval64/comparisons_compact.json')),
        'training': small(report['rounds']), 'config': report['manifest']['config'],
        'ssd': {}, 'transfer': {}}
    cont = 'results/sep20_continuation/'
    ssdroot = cont + 'sep20_ssd_5round_seed43_eval16_3090/'
    for stage in ['base'] + [f'ssd_round_{r}' for r in range(1, 6)]:
        d = get(ssdroot + stage + '/evaluation.metrics.json')
        result['ssd'][stage] = small(d['aggregate'])
    result['ssd_training'] = {f'ssd/round_{r}': {
        'training_stats': get(ssdroot + f'ssd_round_{r}/training_stats.json'),
        'training_budget': get(ssdroot + f'ssd_round_{r}/train.jsonl.budget.json')}
        for r in range(1, 6)}
    for name, folder in [('HumanEval+', 'sep20_transfer_humanevalplus_seed43_n16_b64'),
                         ('APPS Intro', 'sep20_transfer_apps_intro_seed43_n16_b8')]:
        rows = {}
        for m in ['base', 'plain', 'spd_hard', 'spectral_soft']:
            stage = 'base' if m == 'base' else m + '_round_5'
            d = get(cont + folder + '/' + stage + '/evaluation.metrics.json')
            rows[m] = {'aggregate': small(d['aggregate']), 'per_task': {
                tid: {k: small(t[k]) for k in ['sample_count', 'correct_count', 'correct_fraction',
                     'pass_at_k', 'implementation_proxy', 'control_flow_proxy']}
                for tid, t in d['per_task'].items()}}
        result['transfer'][name] = rows
    result['provenance'] = provenance
    DATA.mkdir(exist_ok=True)
    SOURCE.write_text(json.dumps(result, indent=2) + '\n')
    return result

def boot(vals):
    vals = np.asarray(vals, float)
    if not len(vals):
        return {'mean': None, 'ci95': None, 'n': 0}
    rng = np.random.default_rng(SEED)
    means = vals[rng.integers(len(vals), size=(NBOOT, len(vals)))].mean(axis=1)
    return {'mean': float(vals.mean()), 'ci95': np.quantile(means, [.025, .975]).tolist(),
            'n': len(vals), 'bootstrap_seed': SEED, 'bootstrap_replicates': NBOOT,
            'unit': 'evaluation task; conditional on the trained checkpoints'}

def rarefaction(counts, n, b):
    return sum(1 - (math.comb(n-v, b) if n-v >= b else 0) / math.comb(n, b)
               for v in counts)

def analyze(d):
    ans = {'source_commit': d['source_commit'], 'data_status': 'existing samples only',
           'transfer_comparisons': {}, 'equal_correct_count_examples': {}, 'training_resources': {}}
    for dataset, methods in d['transfer'].items():
        comparisons = {}
        for ref in ['base', 'plain', 'spd_hard']:
            cur, prev = methods['spectral_soft']['per_task'], methods[ref]['per_task']
            keys = sorted(set(cur) & set(prev))
            assert len(keys) == len(cur) == len(prev)
            comparison = {}
            for metric, getter in {
                'pass1': lambda x: x['correct_fraction'],
                'pass16': lambda x: x['pass_at_k']['16'],
                'C16': lambda x: x['implementation_proxy']['coverage_at_k']['16'],
                'D4': lambda x: x['implementation_proxy']['correct_matched_coverage_at_budgets']['4'],
                'flow_D4': lambda x: x['control_flow_proxy']['correct_matched_coverage_at_budgets']['4']}.items():
                paired = [(getter(cur[k]), getter(prev[k])) for k in keys]
                vals = [a-b for a, b in paired if a is not None and b is not None]
                comparison[metric] = boot(vals)
            comparisons[ref] = comparison
        ans['transfer_comparisons'][dataset] = comparisons
        # Two signs, same selection rule: numerically lowest task id, equal
        # correct counts >=4, unequal numbers of observed correct AST classes.
        cur, prev = methods['spectral_soft']['per_task'], methods['plain']['per_task']
        for sign, word in [(1, 'broader'), (-1, 'narrower')]:
            choices = []
            for tid in cur:
                a, b = cur[tid], prev[tid]
                if a['correct_count'] != b['correct_count'] or a['correct_count'] < 4:
                    continue
                ca, cb = a['implementation_proxy']['counts'], b['implementation_proxy']['counts']
                if sign * (len(ca)-len(cb)) <= 0:
                    continue
                choices.append(tid)
            if choices:
                tid = min(choices, key=lambda x: (int(x.rsplit('/',1)[-1]), x))
                a, b = cur[tid], prev[tid]
                ans['equal_correct_count_examples'][dataset+' / '+word] = {
                    'task_id': tid, 'samples': a['sample_count'], 'correct_count': a['correct_count'],
                    'selection': 'lowest numeric task ID among equal-correct-count tasks with this sign of AST richness difference',
                    'SPECTRUM': a['implementation_proxy'], 'Plain': b['implementation_proxy']}
    for m in ['plain', 'spd_hard', 'spectral_soft', 'ssd']:
        records = d['ssd_training'] if m == 'ssd' else d['training']
        rows = [v for k,v in records.items() if k.startswith(m+'/')]
        budgets = [r['training_budget'] for r in rows]
        n = sum(b['samples'] for b in budgets)
        tokens = sum(b['generation_tokens'] for b in budgets)
        ans['training_resources'][m] = {'rounds': len(rows), 'candidates': n,
            'generation_tokens': tokens, 'mean_tokens': tokens/n,
            'length_capped_samples': sum(b['length_capped_samples'] for b in budgets),
            'supervised_tokens': sum(r['training_stats']['supervised_tokens_per_epoch'] for r in rows)}
    # Validate the exact combinatorial estimators against saved task metrics.
    for methods in d['transfer'].values():
        for method in methods.values():
            for task in method['per_task'].values():
                counts = list(task['implementation_proxy']['counts'].values())
                assert sum(counts) == task['correct_count']
                assert abs(rarefaction(counts, task['sample_count'], 16)-
                           task['implementation_proxy']['coverage_at_k']['16']) < 1e-10
                if task['correct_count'] >= 4:
                    assert abs(rarefaction(counts, task['correct_count'], 4)-
                               task['implementation_proxy']['correct_matched_coverage_at_budgets']['4']) < 1e-10
    (DATA/'derived_analysis.json').write_text(json.dumps(ans, indent=2)+'\n')
    print(json.dumps({'transfer_comparisons': ans['transfer_comparisons'],
                      'training_resources': ans['training_resources'],
                      'cases': {k: {'task_id': v['task_id'], 'correct_count': v['correct_count'],
                        'Plain_counts': sorted(v['Plain']['counts'].values(), reverse=True),
                        'SPECTRUM_counts': sorted(v['SPECTRUM']['counts'].values(), reverse=True)}
                        for k,v in ans['equal_correct_count_examples'].items()}}, indent=2))

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--refresh-sources', action='store_true')
    args = p.parse_args()
    analyze(extract() if args.refresh_sources else read(SOURCE))
