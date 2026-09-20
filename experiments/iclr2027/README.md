# SPECTRUM ICLR 2027: runnable continuation

This folder extends the completed five-round MBPP experiment. It does not
replace the committed seed-43 results or fill unmeasured cells with estimates.
The paper-facing primary methods are **Plain, SSD, SPECTRUM**, with **UA-RL
(adapted)** evaluated as a separate reinforcement-learning comparator. Projection
is a simple design ablation; its internal compatibility key remains `spd_hard`.

## Run today

Run commands from the repository root in a CUDA environment. The plan command is
stdlib-only: it does not import PyTorch, download weights, or start training.

```bash
python -m pip install -e '.[train,evalplus,analysis]'
python -m improving prepare --dataset mbpp --output-dir data/mbpp --seed 42
docker pull python:3.11-slim
python scripts/run_iclr2027.py plan --stage core --profile 24gb --seeds 43
```

If the four `data/mbpp/*.jsonl` splits already exist, keep them and skip the
`prepare` command. The launcher checks their existence before loading a model;
the pipeline checks their disjointness and records their hashes.

The plan command prints a manifest path, one job ID and the exact `run` command.
Copy that printed command. Repeating it resumes the same experiment. All three
methods are run sequentially; use one such process per GPU. To target a device:

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/run_iclr2027.py run --manifest MANIFEST --job JOB_ID
```

`MANIFEST` and `JOB_ID` above mean the exact values printed by `plan`, not literal
paths. For the three-seed confirmation plan:

```bash
python scripts/run_iclr2027.py plan --stage core --profile 24gb --seeds 42,43,44
python scripts/run_iclr2027.py run --manifest MANIFEST --all
```

`--all` is explicit and sequential. Planning a multi-job grid never runs it.
To run one seed on each GPU, use its separate `--job` entry. Each job keeps all
five student checkpoints and all evaluation programs; allow substantial disk
space (especially for 7B models). Interruptions preserve existing artifacts.

The default verifier executes generated programs in Docker. If a machine cannot
run Docker, the explicit alternative is:

```bash
python scripts/run_iclr2027.py plan --stage core --profile 24gb --seeds 43 \
  --backend local --allow-unsafe-local
```

This executes generated Python on the host under subprocess resource limits;
it is not a security sandbox. This option is never enabled implicitly.

## What is fixed across the training arms

| Component | Protocol |
|---|---|
| Main model | Qwen2.5-Coder-1.5B-Instruct |
| Main data | MBPP train 291, calibration 50, validation 30, test 500; data seed 42 |
| Learning | Five rounds; 16 raw candidates per training prompt each round |
| Student | One LoRA, rank 8/alpha 8, Q/K/V/O, dropout 0.05; one epoch per round |
| Loss | All nonpadding SFT tokens; completion-masked reference loss for geometry |
| Optimizer | LR 1e-5; microbatch 1; accumulation 16; gradient checkpointing |
| Evaluation | Initial model and every student round; 64 candidates per test task |
| Evaluation sampling | Temperature 0.8, top-p 0.95, top-k 0, 512 new tokens |
| Metrics | pass@1/4/8/16/32/64; correct AST richness at each budget; correct-conditioned AST richness at 4/8/16 |
| Uncertainty | 2,000 evaluation-task bootstrap resamples; paired comparisons where appropriate |
| Geometry | Recomputed each round except the explicit fixed-geometry ablation |
| Provenance | Immutable configurations, data hashes, checkpoint hashes, per-task outcomes, stage resources |

Candidate counts, prompts, and update schedules are matched. Generated token
counts, realized token lengths, wall time, and FLOPs are **not assumed equal**;
stage resource files and length summaries must be reported. Confidence intervals
over tasks quantify evaluation-task uncertainty, not variation across training
seeds. Report the three independent seeds separately and their aggregate.

Plain and SPECTRUM synthesize training samples with the common 0.8/0.95/0
decoder. SSD uses its decoding-recipe adaptation (temperature 1.5, top-p 0.8,
top-k 20) during synthesis. All resulting students use the same evaluation
decoder shown above. The implementation is an SSD recipe adaptation under this
study's data and update budget, not a full reproduction of its original scale.

`C_k` and `D_b` are notation defined in the paper, not standardized metric names.
Use **Correct AST richness @k** and **Correct-conditioned AST richness @b**
as table labels, with AST equivalence and budgets specified in the caption. These are standard occupancy/rarefaction class-count estimators, not reference-strategy recall.

## Priorities and required tables

| Priority | Command stage | Jobs / default seed | Scientific question |
|---|---|---:|---|
| 1 | `core` | 1 grouped three-method job / 43 | Five-round retention with 64-sample evaluation at every round |
| 2 | `core --seeds 42,43,44` | 3 grouped jobs | Replication across training seeds |
| 3 | `mechanism` | 6 / 43 | Geometry, directionality, fixed geometry, and strength |
| 4 | `transfer --source-run RUN` | 4 evaluations | Frozen MBPP-trained students on four additional benchmarks |
| 5 | `scale` | 3 grouped jobs / 43 | 3B, 7B and a second architecture family |
| separate | `scripts/run_ua_rl.py` | Explicit judge configuration | Published uniqueness-aware RL comparator adapted to the common task/candidate setting |

Missing measurements stay `x` in manuscript tables. See
[`table_skeletons.md`](table_skeletons.md) for the complete pending cells.

### Mechanism and parameter sensitivity

```bash
python scripts/run_iclr2027.py plan --stage mechanism --profile 24gb --seeds 43
```

The first job groups SPECTRUM, projection, random eigenbasis with identical
eigenvalues, and isotropic gain with matched Frobenius displacement. The next
holds first-round calibration geometry fixed. Four further jobs evaluate
tau = 0.25, 0.5, 2, 4; tau = 1 is the SPECTRUM arm of the first job. This avoids
duplicating tau = 1. `--include-matched-blend` adds the optional matched residual
blend control. The primary setting tau = 1 is prespecified; do not choose a
replacement using held-out test outcomes. All sensitivity settings are reported.

### Five benchmarks, with a consistent scientific question

MBPP supplies the training and main test task. HumanEval+, APPS introductory,
CodeContests and LiveCodeBench are **evaluation-only transfer**, not five
independently trained benchmark winners. The latter three use the recorded
function/`solve(stdin: str) -> str` adaptation and their benchmark test cases;
their scores must carry that protocol label rather than claim official
leaderboard equivalence. Keep all five tasks in the coding domain because
correct program structure and execution checks give the same diversity endpoint.
Mathematical reasoning or free-form writing require a separate equivalence
definition and do not belong in this code-AST table.

Prepare the evaluation snapshots with
`python scripts/prepare_iclr_benchmarks.py --help` and the benchmark protocol
in [`docs/iclr_benchmarks.md`](../../docs/iclr_benchmarks.md).
Then:

```bash
python scripts/prepare_iclr_benchmarks.py \
  --datasets humanevalplus apps_intro codecontests livecodebench \
  --exclude-training data/mbpp/train.jsonl data/mbpp/calibration.jsonl data/mbpp/validation.jsonl
python scripts/run_iclr2027.py plan --stage transfer --source-run COMPLETED_MBPP_RUN
```

Transfer planning defaults to Docker even if the source training run used local
execution. Pass `--backend local --allow-unsafe-local` explicitly to select the
local fallback for a new transfer manifest.

The converter records the exact snapshot, deterministic subset, prompt/test
adaptation and exclusions. Use the same frozen task files for every method and
seed. The default large-benchmark evaluation limit is 200 tasks; HumanEval+
uses all 164. A changed limit is a new protocol, not a continuation of a run.

HumanEval+ must use official EvalPlus base **and** plus tests. Build its pinned
evaluation image before the transfer run:

```bash
docker build -f docker/EvalPlus.Dockerfile -t improving-evalplus:0.3.1 .
```

Transfer uses a separate, fixed generation allowance of 4,096 prompt tokens and
1,024 new tokens, sequence batch one, across all methods. Native adapted-program
verification allows 30 seconds and 1,024 MB per program; HumanEval+ retains its
official EvalPlus timing policy. These settings are recorded in the transfer
manifest and differ from the 512-new-token MBPP protocol. No overlong statement
is silently truncated; a failure requires an explicit new protocol/output path.

### Model-size and architecture replication

```bash
python scripts/run_iclr2027.py plan --stage scale --profile 80gb --seeds 43
python scripts/run_iclr2027.py plan --stage scale --profile 24gb --models qwen3b --seeds 43
```

The scale stage includes Qwen2.5-Coder-3B-Instruct,
Qwen2.5-Coder-7B-Instruct and DeepSeek-Coder-6.7B-Instruct. Training remains on
MBPP; transfer can subsequently use each completed source run. The default
does not create a full model × benchmark × seed × ablation grid.

The DeepSeek 6.7B checkpoint declares the standard `LlamaForCausalLM` architecture
and `LlamaTokenizerFast`, including a native chat template. It therefore uses
the existing Transformers Llama implementation and `trust_remote_code=False`;
it is not a DeepSeek-V2/V3 MLA model. This compatibility is based on the
[published model configuration](https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct/blob/main/config.json)
and [tokenizer configuration](https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct/blob/main/tokenizer_config.json),
not a claimed completed model run.

| Profile | Generation batch for 1.5B / 3B / 7B / 6.7B | Student microbatch | Accumulation |
|---|---|---:|---:|
| 24gb | 8 / 4 / 1 / 1 | 1 | 16 |
| 80gb | 32 / 16 / 8 / 8 | 1 | 16 |

These are conservative target profiles, not measured memory guarantees.
Both use BF16 dense weights and gradient checkpointing. Weight folding does
not support NF4/INT8; the suite does not advertise quantization as a shortcut.
Use the 80GB profile for the large-model study where available. If a new
hardware/profile change is needed, regenerate a plan: editing a started job's
config invalidates its immutable identity.

### UA-RL comparator

Install its additional dependencies in a separate environment following
[`docs/ua_rl_baseline.md`](../../docs/ua_rl_baseline.md). Its pinned TRL and
Transformers versions differ from the core SFT environment.
The semantic judge must be explicitly configured; it is not replaced by AST
hashes. Example interface:

```bash
python scripts/run_ua_rl.py --config CORE_JOB_CONFIG.json \
  --judge-model YOUR_SERVED_JUDGE --judge-base-url http://localhost:8000/v1 \
  --output-dir runs/iclr2027/ua_rl_seed43 --rounds 5 --eval-samples 64
```

Report this as **UA-RL (adapted)**: it uses reinforcement-learning updates and
semantic judging, while the three main arms use student SFT. Match task sets,
candidate counts and evaluation budgets; report its own update/compute budget.
The existing seed-42 one-round pilot does not supply missing fifth-round SSD
or UA-RL numbers.

After UA-RL completes, its run directory can also be passed as `--source-run`
to the transfer planner. Its final merged student is saved in the common
`ua_rl/round_5/model` layout; earlier UA-RL rounds retain adapters and their
already-computed evaluation records.

## Export trajectories and resources

The run launcher invokes the longitudinal exporter automatically on completion.
It can also be invoked without GPU work:

```bash
python scripts/export_longitudinal.py export --run-dir COMPLETED_RUN --bootstrap-samples 2000
python scripts/run_iclr2027.py status --manifest MANIFEST
```

Keep `evaluation.verified.jsonl`, `evaluation.metrics.json`, generated-token
budget files, resource files, configuration and the exported per-task table.
They support pass@k and coverage trajectories, paired task intervals,
correct-sample eligibility counts and resource/length tables. The compact
historical GitHub bundle is not a substitute for missing raw task-level records.

To evaluate every **available** old checkpoint with 64 samples without training:

```bash
python scripts/export_longitudinal.py evaluate \
  --run-dir OLD_RUN --output-dir runs/iclr2027/old_run_all_rounds_eval64 \
  --samples 64 --bootstrap-samples 2000 --resume
```

If old checkpoints were pruned under `checkpoint_retention: latest`, a missing
round cannot be reconstructed from its metric JSON; the command reports that
round as missing. New runs retain all checkpoints. Do not synthesize old
64-sample curves by extrapolating their 16-sample measurements.
