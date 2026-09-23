# Final SPECTRUM study — finish training, then write

This is the bounded final experiment. Run the fixed manifest to completion and
then stop training, whether the result is positive, mixed, or negative. It does
not search for a winning test-set configuration, extend an unsuccessful run, or
replace the original method with a favorable ablation.

The original SPECTRUM remains **tau=1, all-token SFT, one merged LoRA per round**.
All raw synthetic completions enter training. The spectral operator, training
sample-selection policy and official MBPP split are unchanged.

## What runs

| Block | Methods | Seeds | Rounds | Method-seed-rounds |
|---|---|---|---:|---:|
| Main | Plain / SSD / SPECTRUM | 43, 44, 45 | 5 | 45 |
| Strength diagnostic | SPECTRUM, tau=0.5 | 43 | 1 | 1 |
| Geometry diagnostic | Matched isotropic attenuation | 43 | 1 | 1 |
| Loss diagnostic | Plain / SPECTRUM, completion-only SFT | 43 | 1 | 2 |
| **Training total** | | | | **49** |

The four diagnostic arms are compared with the matching main round-1 results,
not with round-5 students. The completion-only intervention includes its own
Plain baseline. The isotropic control matches the Frobenius distance from the
identity, not activation displacement, output KL or realized compute.

All jobs use `Qwen/Qwen2.5-Coder-1.5B-Instruct` at revision
`2e1fd397ee46e1388853d2af2c993145b0f1098a`. Training has 291 MBPP tasks, 16
unfiltered completions per task per round, and one LoRA epoch. Calibration uses
the same 50 reference tasks, re-estimating geometry for the current model every
round. The 30 validation tasks remain held out of training and test-based
selection is not performed.

Every round evaluates the native student on all 500 MBPP test tasks with 64
samples each. Generation-policy diagnostics use a fixed 128-task subset with
16 samples per task. All checkpoints, operator diagnostics, raw completions,
verified programs, task snapshots and provenance are retained.

The nine main round-5 checkpoints and their initial models are evaluated on:

| Dataset | Tasks | Samples per task | Protocol |
|---|---:|---:|---|
| HumanEval+ | 164 | 16 | Official EvalPlus base and plus tests |
| APPS Intro | 200 | 16 | Existing recorded function / `solve(stdin: str) -> str` adaptation |

Transfer never trains or calibrates on target tasks. The APPS scores are not
official leaderboard scores. All three methods use the same native evaluation
decoder. SSD uses its higher-temperature recipe only for synthesis; its
generation-policy diagnostic therefore has a different decoder and must not
be described as a same-decoder causal teacher/student contrast.

## Prepare once

From the repository root, update and install the existing dependencies:

```bash
git pull --ff-only origin main
python -m pip install -e '.[train,analysis,evalplus]'
```

Reuse the four existing `data/mbpp/{train,calibration,validation,eval}.jsonl`
files if present. If they are missing:

```bash
python -m improving prepare --dataset mbpp --output-dir data/mbpp --seed 42
```

Reuse the prepared HumanEval+ and 200-task APPS snapshots if present. Otherwise:

```bash
python scripts/prepare_iclr_benchmarks.py \
  --datasets humanevalplus apps_intro \
  --exclude-training data/mbpp/train.jsonl data/mbpp/calibration.jsonl data/mbpp/validation.jsonl
```

For the default Docker evaluation backend, prepare both images before running:

```bash
docker pull python:3.11-slim
docker build -f docker/EvalPlus.Dockerfile -t improving-evalplus:0.3.1 .
```

## Plan and execute

Planning reads and freezes prepared input files; it does not load a model,
download weights, run tests, or start training.

```bash
python scripts/run_final_study.py plan --profile 24gb
python scripts/run_final_study.py run \
  --manifest runs/final_study_v1/plan/manifest.json --block all
```

`24gb` uses conservative existing batch settings; `80gb` increases generation
batch size. These are memory targets, not measured guarantees. Do not edit a
started config to change hardware settings: create a new plan and output root.

If your machine already uses the explicitly enabled local verifier, select it
when creating a **new** plan:

```bash
python scripts/run_final_study.py plan --profile 24gb \
  --backend local --allow-unsafe-local --run-root runs/final_study_local_v1
python scripts/run_final_study.py run \
  --manifest runs/final_study_local_v1/plan/manifest.json --block all
```

The existing local backend executes generated code on the host; the flag keeps
that choice explicit. HumanEval+ still uses official EvalPlus.

Use `--block core`, `--block diagnostic`, or `--block transfer` to run the fixed
blocks separately. Transfer requires its corresponding core job to be
complete. The same command resumes sealed work after interruption; it does not
overwrite historical runs. An interrupted SFT round restarts that round's
training, as in the existing pipeline; optimizer-step resume is not added.

For multiple GPUs, assign different job IDs to different processes, for example:

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/run_final_study.py run \
  --manifest runs/final_study_v1/plan/manifest.json --job core-s43
CUDA_VISIBLE_DEVICES=1 python scripts/run_final_study.py run \
  --manifest runs/final_study_v1/plan/manifest.json --job core-s44
CUDA_VISIBLE_DEVICES=2 python scripts/run_final_study.py run \
  --manifest runs/final_study_v1/plan/manifest.json --job core-s45
```

Launch those commands in separate terminals or your scheduler. Per-job locks
prevent two processes from writing the same job. Afterwards run the diagnostic
and transfer blocks once. Keep the code and input snapshots fixed throughout.

## Bounded budget

| Candidate source | Maximum new candidates |
|---|---:|
| Synthetic training data | 228,144 |
| Native MBPP student evaluation, all rounds | 1,568,000 |
| Initial MBPP evaluations, six grouped jobs | 192,000 |
| Generation-policy diagnostics | 100,352 |
| Final HumanEval+ and APPS transfer, including initial models | 69,888 |
| **Total** | **2,158,384** |

These are candidate counts, not GPU-hour estimates. Completed stages are
reused on resume. Length, actual token count, memory and elapsed time remain
measured outputs; matching examples and optimizer steps does not match FLOPs.
Keeping every checkpoint requires substantially more storage than the old
`checkpoint_retention: latest` runs. No large-model or further dataset training
is added to this final study.

## Results and paper outputs

```bash
python scripts/run_final_study.py status \
  --manifest runs/final_study_v1/plan/manifest.json
python scripts/report_final_study.py \
  --manifest runs/final_study_v1/plan/manifest.json
```

The report directory is `runs/final_study_v1/paper_report/`. It contains the
planned endpoints, per-seed results and missing cells, round trajectories,
paired effects, seed summaries, teacher/student diagnostics, and recorded
errors/resources. No report command loads a model or reruns candidate code.

`REPORT.md` and `summary.json` index the results. Plotting tables are
`endpoints.csv`, `trajectories.csv`, `paired_differences.csv`, `seed_summary.csv`,
`teacher_student.csv`, `ablations.csv`, `errors.csv`, `resources.csv`, and
`operators.csv`. The last file records each layer's actual gain spectrum and
the nonuniform component of its operator, helping distinguish directional
modulation from nearly uniform attenuation.

Use these measurements in the paper:

1. Main table: round-5 pass@1/16/64, Correct AST richness@64, initial-relative
   richness retention, and Correct-conditioned AST richness@4 with eligibility.
2. Main figure: all five rounds, reporting task-bootstrap intervals and each
   independent seed; task intervals are not estimates of training-seed variation.
3. Mechanism figure: before modulation, after modulation and after SFT on the
   same diagnostic task/sample budgets; state the SSD decoder difference.
4. Ablation table: the four fixed single-round diagnostics and matched controls.
5. Transfer table: both datasets, all three main methods, including regressions.

Correct AST fingerprints measure implementation structure, not audited
algorithm identities. Correct-sample-matched comparisons use the intersection
of eligible tasks; do not subtract different eligible-population means and
call the result a paired effect. Seed summaries must not treat repeated
evaluations of the same 500 tasks as 1,500 independent tasks.

## End rule

Once every planned job is complete and the report has no missing planned
endpoint, **stop training and start writing**. Describe whichever result was
observed: preserved diversity, an accuracy/diversity trade-off, a limited
transfer effect, or a failed diagnostic hypothesis. A positive result, a
particular confidence interval, or beating SSD is not a condition for stopping.

The main method stays fixed. A favorable tau/loss ablation is reported as an
ablation, not selected retrospectively as an independently confirmed winner.
Existing archived results remain separate from this newly frozen study.

## Code verification note

This update was prepared under the user's instruction not to run tests or
training. Source review and syntax checks are distinct from executed test or
benchmark results. Added regression-test source is available for later use;
no new model-performance result is claimed by this code release.
