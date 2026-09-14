#!/usr/bin/env bash
# Run from any directory. Relative configuration paths are repository-relative.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd -- "$repo_root"
config=${1:-configs/geometry_100_16gb.yaml}
python_bin=${IMPROVING_PYTHON:-python}

if [[ $# -gt 1 ]]; then
  echo "Usage: bash scripts/run_geometry.sh [configs/geometry_100_16gb.yaml]" >&2
  exit 2
fi
if [[ ! -f "$config" ]]; then
  echo "Configuration does not exist: $config" >&2
  exit 2
fi

"$python_bin" -m improving doctor

# Bootstrap the documented MBPP layout only when it is wholly absent. A partial
# preparation or missing custom dataset is not silently overwritten.
data_state=$("$python_bin" - "$config" <<'PY'
from pathlib import Path
import sys
import yaml

config = yaml.safe_load(Path(sys.argv[1]).read_text())
names = ('train', 'calibration', 'validation', 'eval')
paths = [Path(config['data'][name]) for name in names]
present = [path.is_file() for path in paths]
standard = all(path.resolve() == Path('data/mbpp', name + '.jsonl').resolve()
               for name, path in zip(names, paths))
if all(present):
    print('ready')
elif standard and not any(present):
    print('prepare')
else:
    missing = ', '.join(str(path) for path, exists in zip(paths, present) if not exists)
    raise SystemExit('Dataset is incomplete; prepare or restore these files first: ' + missing)
PY
)

if [[ "$data_state" == prepare ]]; then
  data_seed=$("$python_bin" - "$config" <<'PY'
from pathlib import Path
import sys
import yaml

config = yaml.safe_load(Path(sys.argv[1]).read_text())
print(int(config.get('data_seed', config.get('seed', 42))))
PY
)
  "$python_bin" -m improving prepare --dataset mbpp --output-dir data/mbpp --seed "$data_seed"
fi

"$python_bin" -m improving geometry --config "$config" --stage validate
"$python_bin" -m improving geometry --config "$config" --stage all --resume
