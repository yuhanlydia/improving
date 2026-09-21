"""Independent n64 MBPP evaluation through the frozen longitudinal implementation."""
import argparse
import json
from pathlib import Path
import sys

RUNTIME = Path('/root/improving/runs/sep20_transfer_runtime')
sys.path.insert(0, str(RUNTIME / 'src'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--methods', required=True)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    from improving.longitudinal import evaluate_checkpoints, export_longitudinal
    from improving.utils import atomic_json
    source = json.loads((Path(args.run_dir) / 'manifest.json').read_text())
    if source['config']['seed'] != 43:
        raise ValueError('This independent n64 protocol requires source seed 43')
    generation = {'batch_size': 8, 'sequence_batch_size': 8,
                  'task_batch_size': 8, 'max_prompt_tokens': 1024,
                  'max_new_tokens': 512}
    result = evaluate_checkpoints(
        args.run_dir, args.output_dir, samples=64, rounds=[5],
        methods=args.methods.split(','), generation_overrides=generation,
        model_settings={'revision': '2e1fd397ee46e1388853d2af2c993145b0f1098a'},
        evaluation_overrides={'backend': 'local', 'allow_unsafe_local': True,
                              'timeout': 5, 'memory_mb': 1024, 'workers': 8},
        bootstrap_samples=2000, resume=args.resume)
    if result['status'] != 'completed':
        print(json.dumps(result, indent=2))
        return 2
    export_longitudinal(args.output_dir, bootstrap_samples=2000)
    atomic_json(Path(args.output_dir) / 'eval64_complete.json', {
        'status': 'completed', 'benchmark': 'mbpp', 'seed': 43,
        'samples_per_task': 64, 'student_round': 5,
        'generation': generation, 'results': result})
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
