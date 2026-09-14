# Offline EvalPlus evaluation

The container uses the official `evalplus==0.3.1` evaluator and preserves every
exported sample. Build it once with network access, then run candidate programs
with networking disabled. Docker was unavailable in the development environment:
the Dockerfile and wrapper have been inspected and their boundary behavior
checked, but the image has **not** been built or evaluated there.

## Build

```bash
docker build -f docker/EvalPlus.Dockerfile -t improving-evalplus:0.3.1 .
docker image inspect improving-evalplus:0.3.1 --format '{{.Id}}'
```

Keep the reported image ID with experiment records. The build installs an
explicit evaluation dependency set and the official EvalPlus wheel without its
generation SDK dependencies; it intentionally excludes PyTorch, CUDA, model
weights, and provider credentials. A build check imports the evaluator and
asserts that PyTorch is absent. Transitive package versions are recorded in the
image's `environment.txt`; rebuilding from a tag is not a byte-identical lock.

The build downloads HumanEval+ **v0.1.10** and MBPP+ **v0.2.0**, validates their
required fields with the official loaders, and records file SHA-256 hashes. It
does not execute reference or candidate programs. Official dataset override
variables point runtime loaders at these baked JSONL files. The official
`appdirs.user_cache_dir("evalplus")` cache is directed by `XDG_CACHE_HOME` to
ephemeral `/tmp`; reference outputs are computed inside the runtime container.

## Recommended HumanEval+ route

Prepare the exact heldout task set from the offline image:

```bash
scripts/evalplus_docker.sh prepare humaneval data/humanevalplus
```

This produces `data/humanevalplus/tasks.jsonl` and dataset provenance. Use that
task file as `data.eval` in your experiment configuration, with evaluation
`backend: none` while generating. Each task preserves the official prompt and
function-completion interface. Its reference is heldout metadata; do not add
these tasks to calibration, training, or hyperparameter validation. The task
file intentionally has no builtin `tests` field: this route is evaluated by
the external EvalPlus command.

Generate all configured samples for every prepared task. Assuming the resulting
raw completion file is `runs/example/eval_raw.jsonl`:

```bash
.venv/bin/improving evalplus-export \
  --tasks data/humanevalplus/tasks.jsonl \
  --samples runs/example/eval_raw.jsonl \
  --output runs/example/evalplus_samples.jsonl

scripts/evalplus_docker.sh evaluate humaneval \
  runs/example/evalplus_samples.jsonl runs/example/evalplus_result

.venv/bin/improving evalplus-import \
  --tasks data/humanevalplus/tasks.jsonl \
  --samples runs/example/eval_raw.jsonl \
  --results runs/example/evalplus_result/samples_eval_results.json \
  --manifest runs/example/evalplus_samples.jsonl.manifest.jsonl \
  --output runs/example/eval_verified.jsonl
```

Export keeps empty, incorrect, and syntactically invalid samples. It writes
complete `solution` strings and a manifest mapping arbitrary original sample
IDs to their per-task encounter positions. The official result format drops
sample IDs; import therefore checks the manifest, exact solution text, task
sets, and sample counts. Correctness requires both base and extended tests to
pass. No sanitizer, algorithm repair, best-of selection, or host candidate
execution is part of this workflow.

Every output directory must be new or empty. Outputs include
`samples_eval_results.json`, `evaluation_metadata.json`, `dataset_metadata.json`,
and `environment.txt`. The metadata includes sample-file SHA-256, dataset
release/hash, sampling counts, and evaluation timing parameters.

## Isolation and budgets

The wrapper binds only the selected sample file read-only and one dedicated
output directory writable. Runtime uses a nonroot UID, disabled networking,
read-only root filesystem, dropped capabilities, no new privileges, and bounded
CPU, memory, process count, temporary storage, and whole-container wall time.
It forwards no host cache, home directory, Docker socket, credentials, or
arbitrary host environment. On exit or timeout it force-removes the container.

Defaults are 2 CPU cores, 4 GiB container RAM, 256 processes, two evaluation
workers, 2 GiB maximum address space per sample, and a two-hour total wall limit.
The official evaluator uses `min_time_limit=1.0` and
`gt_time_limit_factor=4.0` for its per-test timing protocol. Override container
budgets with the `IMPROVING_EVALPLUS_*` variables shown by
`scripts/evalplus_docker.sh --help`; record the same settings for every arm.
Increase total memory when increasing parallelism. The whole-container timeout
is a failed evaluation run, not a set of fabricated incorrect sample labels.

This isolates execution from host files and networking. EvalPlus's Python
harness is not an adversarial anti-cheating system; treat intentionally
harness-tampering programs separately from ordinary model correctness failures.

## MBPP+ is a different task protocol

The same commands accept `mbpp`, but the repository's official **full MBPP test
split** and the **MBPP+ task set** are not identical. MBPP+ can also include IDs
assigned to training by a different MBPP partition. Do not pass the existing
full-MBPP run to this evaluator and silently report the surviving subset.

The wrapper requires exact coverage of the baked dataset before execution and
rejects extra or missing task IDs. To conduct a separate MBPP+ experiment,
prepare its tasks with `prepare mbpp`, explicitly redesign and record disjoint
train/calibration/validation/evaluation partitions, and run the repository's
ID and normalized-prompt leakage checks. Use identical tasks and sample
budgets across all compared arms. HumanEval+ is the straightforward external
evaluation route for an experiment trained on full MBPP.

The official format and entrypoint were checked against the published
[EvalPlus 0.3.1 package](https://pypi.org/project/evalplus/0.3.1/) and its
[`evaluate.py` implementation](https://github.com/evalplus/evalplus/blob/v0.3.1/evalplus/evaluate.py).
