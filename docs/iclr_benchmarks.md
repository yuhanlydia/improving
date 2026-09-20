# Five coding benchmarks for the ICLR extension

This extension evaluates **one MBPP-trained loop** on five coding task sets. It
does not claim five independent in-domain training experiments. Calibration,
validation, model selection, and all synthetic-data training use the MBPP
training pool only. HumanEval+, APPS, CodeContests, and LiveCodeBench are frozen
checkpoint transfer evaluations. No transfer-test solution enters calibration.

## Prepare once before starting a model run

```bash
pip install -e '.[train,evalplus,analysis]'
python scripts/prepare_iclr_benchmarks.py \
  --datasets mbpp humanevalplus apps_intro codecontests livecodebench \
  --output-dir data/iclr2027 --seed 42 --limit 200 --lcb-release release_v5
```

The command downloads **dataset files only**. It never downloads model weights,
trains a model, or executes a reference/candidate program. HF dataset names are
resolved to immutable commits before downloading. APPS and LiveCodeBench JSONL
files are downloaded directly, without running their remote dataset scripts.
MBPP and CodeContests use the installed `datasets` reader. HumanEval+ requires
EvalPlus 0.3.1 with HumanEvalPlus v0.1.10 and records the complete fixture hash.

For identical preparation on another machine, provide a JSON file via
`--revisions revisions.json` with the immutable `revision` values in the saved
manifests. The explicit LiveCodeBench release and actual file SHA-256 values are
also retained. A rerun verifies existing hashes and reuses the existing snapshot;
it never silently advances to a new upstream revision. Changed settings require
a different output directory. A failed preparation leaves its files for
inspection; rerun to a fresh directory rather than mixing partial snapshots.

The output is `data/iclr2027/<name>/eval.jsonl`, `manifest.json`, and a top-level
`benchmark_registry.json`. MBPP additionally writes `train.jsonl`,
`calibration.jsonl`, `validation.jsonl`, and its original preparation manifest.
If preparing all five datasets with the command above, point the training planner
at this MBPP directory:

```bash
python scripts/run_iclr2027.py plan --stage core --data-root data/iclr2027/mbpp
```

If continuing an existing `data/mbpp` training snapshot, keep that snapshot and
prepare only the other four datasets with `--exclude-training
data/mbpp/train.jsonl data/mbpp/calibration.jsonl data/mbpp/validation.jsonl`.

| Name in configuration | Source / evaluation set | Selection | Verification label |
|---|---|---|---|
| `mbpp` | Official MBPP full/test | All 500 official tasks; existing train-pool decontamination | MBPP original tests, existing repository protocol |
| `humanevalplus` | Official HumanEvalPlus v0.1.10 | All 164 tasks | Official EvalPlus base **and** plus tests |
| `apps_intro` | APPS official test split, introductory difficulty | Seeded 200-task subset, or all with `--limit 0` | Adapted all-test functional / standard-I/O protocol |
| `codecontests` | DeepMind CodeContests official test split | Seeded limit 200; if fewer, all available tasks | Adapted all public, private, and generated tests |
| `livecodebench` | LiveCodeBench lite, explicit `release_v5` | Seeded 200-task subset, or all with `--limit 0` | Adapted all public and private release tests |

The actual count is authoritative in the manifest. CodeContests' official test
split can have fewer than 200 tasks; it is never padded or resampled. All
selection is completed before model generation and does not use correctness.

## What the adapted protocols mean

Standard-input problems are presented as `solve(stdin: str) -> str`. The argument
is the complete input for one program execution; the returned string is the
complete standard output. The verifier compares whitespace-separated output
tokens, preserving token order and case. It does not add numeric tolerance,
accept alternative witnesses, or invoke problem-specific special judges. File
input/output in the original problem is represented by this same string API.
Every available input/output fixture is retained, including duplicate tests.

Callable problems retain the function name and the published `Solution` class
interface where present. APPS stores an argument list for each case; LiveCodeBench
functional fixtures store one JSON argument per input line. Returned structures
are compared after JSON round-trip normalization, which treats tuples as lists
but does not sort outputs or infer unordered semantics. A new `Solution` object
is constructed for each callable test case.

These adapters measure **within-study transfer with a shared generation and
verification protocol**. Their scores are not official APPS, CodeContests, or
LiveCodeBench leaderboard scores. In particular, exact output comparison may
reject a valid alternative witness or a numerically equivalent floating-point
answer. Report the adapted-protocol label alongside each dataset result. Do not
state that LiveCodeBench guarantees an absence of pretraining contamination;
the release and contest dates are retained to define the evaluated time window.

HumanEval+ does not use these adapters. Its task JSONL deliberately omits local
`tests`: sending it to the builtin verifier fails instead of quietly evaluating
only original HumanEval examples. Use the official bridge below.

## Leakage and schema accounting

The command automatically compares each transfer question against prepared MBPP
train, calibration, and validation questions using NFKC normalization and
whitespace collapse. `--exclude-training` adds other training files to the same
check. Exact overlaps with adapted transfer sets are excluded and recorded with
their matching source IDs. For full MBPP/HumanEval+ evaluation sets an overlap
raises an error: remove the overlap from training and refit rather than altering
the official test set after training.

This is an exact-text overlap check, not a claim that semantic duplicates or
pretraining contamination have been ruled out. The manifest records every
difficulty exclusion, overlap exclusion, and deterministic subset exclusion.
Malformed or missing tests, unsupported mixed test styles, invalid IDs, and
empty resulting datasets raise errors. There is no catch-and-skip path for
conversion failures. Private LiveCodeBench fixtures are decoded by a restricted
unpickler that forbids global/class loading; no reference solution is executed.

## Official HumanEval+ callback

The experiment transfer runner obtains the callback using:

```python
from improving.benchmarks import make_humanevalplus_evaluator
from improving.longitudinal import evaluate_checkpoints

evaluate, evaluator_identity = make_humanevalplus_evaluator(
    'data/iclr2027/humanevalplus/eval.jsonl',
    {'backend': 'docker', 'image': 'improving-evalplus:0.3.1'},
)
evaluate_checkpoints(
    'runs/my_mbpp_run', 'runs/my_mbpp_transfer/humanevalplus',
    samples=64, rounds=[5], methods=['plain', 'spectral_soft'],
    eval_tasks_path='data/iclr2027/humanevalplus/eval.jsonl',
    evaluator=evaluate, evaluator_identity=evaluator_identity,
    resume=True,
)
```

Build the image first using the existing `docker/EvalPlus.Dockerfile`. The bridge
pins the local Docker image ID, checks fixture hashes and release metadata,
exports every sample with its mapping manifest, and imports both original and
extended correctness. It retains evaluator output, errors, and environment
metadata. It returns the same per-task metrics required by the longitudinal
bootstrap report. Local fallback is available only with explicit
`{'backend': 'local', 'allow_unsafe_local': True}` and is labelled accordingly.

## Reporting and comparisons

Run all methods for a dataset on the **same prepared eval.jsonl**, same decoding
budget, same code extraction, same timeout, and same selected round. Publish the
task count, dataset revision/release, verification protocol, and `manifest.json`
alongside each aggregate. Use paired task bootstrap within each dataset. Keep
training seeds separate from bootstrap replicates; the latter quantify sampling
of evaluation tasks, not training reproducibility. Correct-sample-matched
coverage needs enough correct samples for each task and its eligible count must
be reported, especially on harder competitive programming tasks.

Generation limits should be declared before evaluation. Long competitive tasks
may require more than the MBPP limit of 512 new tokens. If a longer limit is
used, apply it to every method in that dataset comparison and report generated
tokens and resource use; this is a different decoding protocol from the original
MBPP pilot. Mathematics and writing need separately justified correctness and
solution-equivalence definitions, so they are not silently relabelled as coding
AST diversity benchmarks in this extension.

## Primary source schemas

- [APPS dataset and fields](https://huggingface.co/datasets/codeparrot/apps)
- [CodeContests dataset](https://huggingface.co/datasets/deepmind/code_contests)
- [LiveCodeBench release definitions](https://huggingface.co/datasets/livecodebench/code_generation_lite)
- [LiveCodeBench official task parsing](https://github.com/LiveCodeBench/LiveCodeBench/blob/main/lcb_runner/benchmarks/code_generation.py)
- [EvalPlus v0.3.1 HumanEval+ data module](https://github.com/evalplus/evalplus/blob/v0.3.1/evalplus/data/humaneval.py)
