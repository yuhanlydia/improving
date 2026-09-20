#!/usr/bin/env python3
"""Export stored per-task trajectories or evaluate retained checkpoints.

Examples (from the repository root after installation):
  python scripts/export_longitudinal.py export --run-dir runs/my_run
  python scripts/export_longitudinal.py evaluate --run-dir runs/old_eval16 \
      --output-dir runs/old_eval16/posthoc_eval64 --samples 64 --resume

The evaluate command uses the original verifier settings, including its explicit
local-execution consent. It performs no training. Pruned checkpoints stay missing.
"""
import argparse
import json

from improving.longitudinal import evaluate_checkpoints, export_longitudinal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    export = commands.add_parser('export', help='CPU analysis of existing metrics and raw records')
    export.add_argument('--run-dir', required=True)
    export.add_argument('--output-dir')
    export.add_argument('--bootstrap-samples', type=int, default=2000)
    export.add_argument('--seed', type=int)
    export.add_argument('--reference-methods', default='plain,ssd,spd_hard')
    evaluate = commands.add_parser('evaluate', help='GPU post-hoc evaluation; never trains')
    evaluate.add_argument('--run-dir', required=True)
    evaluate.add_argument('--output-dir', required=True)
    evaluate.add_argument('--samples', type=int, default=64)
    evaluate.add_argument('--rounds', help='Comma-separated round numbers; default all source rounds')
    evaluate.add_argument('--methods', help='Comma-separated source method names; default all')
    evaluate.add_argument('--tasks', help='External task JSONL for transfer; default saved evaluation snapshot')
    evaluate.add_argument('--bootstrap-samples', type=int, default=2000)
    evaluate.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.command == 'export':
        result = export_longitudinal(args.run_dir, args.output_dir,
                                     bootstrap_samples=args.bootstrap_samples, seed=args.seed,
                                     reference_methods=tuple(value for value in args.reference_methods.split(',') if value))
        print(json.dumps({'status': 'exported', 'stage_count': len(result['stages']),
                          'paired_comparison_count': len(result['comparisons'])}))
    else:
        result = evaluate_checkpoints(args.run_dir, args.output_dir, samples=args.samples,
                                       rounds=[int(value) for value in args.rounds.split(',')] if args.rounds else None,
                                       methods=args.methods.split(',') if args.methods else None,
                                       eval_tasks_path=args.tasks, bootstrap_samples=args.bootstrap_samples,
                                       resume=args.resume)
        if result['completed']:
            export_longitudinal(args.output_dir, bootstrap_samples=args.bootstrap_samples)
        print(json.dumps(result, indent=2))
        if result['status'] != 'completed':
            raise SystemExit(2)


if __name__ == '__main__':
    main()
