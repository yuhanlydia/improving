"""Write explicit configs for preregistered seed, round and spectral controls.

Does not run jobs or select the best result. Output paths are distinct per run.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--base', default='configs/pilot_16gb.yaml')
parser.add_argument('--output-dir', default='configs/generated')
parser.add_argument('--rounds', type=int, default=5)
parser.add_argument('--seeds', nargs='+', type=int, default=[42, 43, 44])
parser.add_argument('--controls', action='store_true')
parser.add_argument('--full-data', action='store_true', help='Remove pilot-only task limits')
args = parser.parse_args()
base = yaml.safe_load(Path(args.base).read_text())
Path(args.output_dir).mkdir(parents=True, exist_ok=True)
for seed in args.seeds:
    config = deepcopy(base)
    config['seed'] = seed
    config['rounds'] = args.rounds
    if args.full_data:
        config.pop('data_limits', None)
    if args.controls:
        config['methods'] = ['plain', 'ssd', 'spd_hard', 'spectral_soft', 'residual_blend', 'random_hard']
    config['output_dir'] = f'runs/rounds{args.rounds}_seed{seed}'
    path = Path(args.output_dir) / f'rounds{args.rounds}_seed{seed}.yaml'
    if path.exists():
        raise FileExistsError(f'Refusing to overwrite {path}')
    path.write_text(yaml.safe_dump(config, sort_keys=False))
    print(path)
