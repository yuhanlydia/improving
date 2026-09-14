#!/usr/bin/env bash
# Run from any directory; relative config paths are repository-relative.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd -- "$repo_root"
config=${1:-configs/formal_16gb.yaml}
stage=${2:-confirm}
python_bin=${IMPROVING_PYTHON:-python}

if [[ $# -gt 2 || ${1:-} == --help || ${1:-} == -h ]]; then
  echo 'Usage: bash scripts/run_formal.sh [configs/formal_16gb.yaml] [confirm|mechanism|retention|transfer|all|validate|report|export]'
  [[ $# -le 2 ]] || exit 2
  exit 0
fi
[[ -f "$config" ]] || { echo "Configuration does not exist: $config" >&2; exit 2; }
case "$stage" in
  confirm|mechanism|retention|transfer|all|validate|report|export) ;;
  *) echo "Unknown formal stage: $stage" >&2; exit 2 ;;
esac

# Reports/exports read saved artifacts and do not need CUDA, Docker or downloads.
if [[ "$stage" == report || "$stage" == export ]]; then
  "$python_bin" -m improving formal --config "$config" --stage "$stage" --resume
  exit 0
fi

# Prepare only a wholly absent standard MBPP layout. Existing or custom data
# are never silently overwritten or mixed with a partial fresh download.
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
    raise SystemExit('Incomplete dataset; prepare or restore these files: ' + missing)
PY
)
if [[ "$data_state" == prepare ]]; then
  data_seed=$("$python_bin" - "$config" <<'PY'
from pathlib import Path
import sys
import yaml
print(int(yaml.safe_load(Path(sys.argv[1]).read_text()).get('data_seed', 42)))
PY
)
  "$python_bin" -m improving prepare --dataset mbpp --output-dir data/mbpp --seed "$data_seed"
fi

if [[ "$stage" != validate ]]; then
  "$python_bin" -m improving doctor
  command -v docker >/dev/null || { echo 'Docker is required for candidate verification.' >&2; exit 2; }
  docker info >/dev/null
fi

if [[ "$stage" == transfer || "$stage" == all ]]; then
  transfer_image=$("$python_bin" - "$config" <<'PY'
from pathlib import Path
import sys
import yaml
print(yaml.safe_load(Path(sys.argv[1]).read_text())['transfer']['docker_image'])
PY
)
  if ! docker image inspect "$transfer_image" >/dev/null 2>&1; then
    docker build -f docker/EvalPlus.Dockerfile -t "$transfer_image" .
  fi
  transfer_state=$("$python_bin" - "$config" <<'PY'
from pathlib import Path
import sys
import yaml
path = Path(yaml.safe_load(Path(sys.argv[1]).read_text())['transfer']['tasks'])
if path.is_file():
    print('ready')
elif path.resolve() == Path('data/humanevalplus/tasks.jsonl').resolve() and (
        not path.parent.exists() or not any(path.parent.iterdir())):
    print('prepare')
else:
    raise SystemExit('Missing or incomplete custom transfer dataset: ' + str(path))
PY
)
  if [[ "$transfer_state" == prepare ]]; then
    IMPROVING_EVALPLUS_IMAGE="$transfer_image" bash scripts/evalplus_docker.sh prepare humaneval data/humanevalplus
  fi
fi

"$python_bin" -m improving formal --config "$config" --stage validate
[[ "$stage" != validate ]] || exit 0

if [[ "$stage" != transfer ]]; then
  verifier_image=$("$python_bin" - "$config" <<'PY'
from pathlib import Path
import sys
import yaml
print(yaml.safe_load(Path(sys.argv[1]).read_text())['evaluation']['docker_image'])
PY
)
  if ! docker image inspect "$verifier_image" >/dev/null 2>&1; then
    docker pull "$verifier_image"
  fi
fi

"$python_bin" -m improving formal --config "$config" --stage "$stage" --resume
if [[ "$stage" != all ]]; then
  "$python_bin" -m improving formal --config "$config" --stage report --resume
  "$python_bin" -m improving formal --config "$config" --stage export --resume
fi
