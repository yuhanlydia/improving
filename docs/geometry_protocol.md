# Correct-solution subspace study: executable protocol

This experiment answers a question that must precede the proposed coevolution
method: do different correct implementations of the same coding task produce
distinct, reproducible K/V gradient subspaces, and does their geometry predict
useful changes in generated programs? The model is frozen throughout this study.
It does **not** train a new LoRA or demonstrate that coevolution works. The earlier
self-distillation/LoRA pipeline remains a separate experiment.

## Run commands

From the repository root, install the declared environment and make the program
executor available:

```bash
python -m pip install -e '.[train,test,analysis]'
docker pull python:3.11-slim
python -m improving doctor
```

The machine needs working Docker access, network access for the initial model
and dataset downloads, and a GPU for practical model execution. The script never
installs packages or replaces Docker with unsandboxed execution automatically.

For the 100-question diagnostic on the smaller model:

```bash
bash scripts/run_geometry.sh configs/geometry_100_16gb.yaml
```

For all prepared MBPP tasks on the smaller model:

```bash
bash scripts/run_geometry.sh configs/geometry_full_16gb.yaml
```

For the 3B model, use the corresponding 24 GB configuration:

```bash
bash scripts/run_geometry.sh configs/geometry_100_24gb.yaml
bash scripts/run_geometry.sh configs/geometry_full_24gb.yaml
```

Choose one run at a time on a single GPU. The 16 GB / 24 GB labels are target
hardware profiles, not measured peak-memory guarantees. Both profiles generate
in batches of four; extraction processes complete solutions independently. If
memory is insufficient, reduce `generation.batch_size` in a copied configuration
and give that configuration a new `output_dir`. Do not change a configuration
inside an existing resumable run. `IMPROVING_PYTHON` may select a virtualenv's
Python executable when invoking the shell script.

The script resolves relative configuration paths from the repository root. It
prepares the documented MBPP dataset only if all four default split files are
absent. Partial preparations and missing custom datasets produce an error instead
of being overwritten. To prepare explicitly:

```bash
python -m improving prepare --dataset mbpp --output-dir data/mbpp --seed 42
```

The same pipeline is exposed as individual stages:

```bash
python -m improving geometry --config configs/geometry_100_16gb.yaml --stage validate
python -m improving geometry --config configs/geometry_100_16gb.yaml --stage discover --resume
python -m improving geometry --config configs/geometry_100_16gb.yaml --stage extract --resume
python -m improving geometry --config configs/geometry_100_16gb.yaml --stage analyze --resume
python -m improving geometry --config configs/geometry_100_16gb.yaml --stage relations --resume
python -m improving geometry --config configs/geometry_100_16gb.yaml --stage select --resume
python -m improving geometry --config configs/geometry_100_16gb.yaml --stage evaluate --resume
python -m improving geometry --config configs/geometry_100_16gb.yaml --stage report --resume
```

`--stage all --resume` runs these stages in their dependency order. Resume checks
the saved identities and completed artifacts; it is not permission to change
data, configuration, or completed outputs halfway through a run.

## Split by question, then generate implementations

| Profile | Discovery questions | Validation questions | Final test questions | Initial candidates/question |
| --- | ---: | ---: | ---: | ---: |
| `geometry_100_*` | 64 | 16 | 20 | 10 |
| `geometry_full_*` | All prepared train + calibration | All prepared validation | All prepared official test | 32 |

The existing MBPP preparation uses official source partitions and removes exact
prompt overlap before splitting its training pool. With the currently prepared
snapshot, the full profile has 341 discovery, 30 validation, and 500 final test
questions. Read the saved manifest for actual counts. Discovery combines the
prepared training and calibration partitions; validation and final evaluation
remain disjoint.

The 100-question profile is the proposed "80 questions for development, 20 for
evaluation" with the 80 split again into **64 discovery + 16 validation**. This
allows rank and bank size to be selected without consulting the 20 final
questions. All implementations of a question stay in the same split. We do not
randomly split 1,000 programs from 100 questions into train/test programs.

Ten rollout candidates do not mean ten correct programs, and ten correct
programs do not mean ten algorithms. Some questions will have zero or one correct
candidate. Those questions remain in the reported denominators; they cannot
supply a within-question pair. Up to ten verified correct candidates per
discovery question enter extraction, even in the 32-candidate full profile.
This cap is an extraction budget, not an assertion that a question has ten modes.

The 20-question final partition is a pilot. Formal benchmark reporting uses the
full held-out partition and the saved uncertainty estimates. A single configured
seed provides one run, not a claim of seed robustness. Replicates use a fresh
`output_dir`; keep `data_seed` fixed when varying stochastic model seeds so that
the question split is unchanged.

## What loss and subspace are actually measured?

For a verified program, the default loss is the mean next-token cross entropy
over its complete generated completion. Prompt targets are masked out. The
generated token IDs are preserved; silent sequence truncation is rejected.
Optional character spans must belong to that particular generated program.
Reference-answer offsets must never be applied to another implementation.

This default is explicitly **not** a reproduction of SPD's assertion-relevant
span extraction. It makes the mask definition identical across different
implementations without inventing an automatic assertion mask. See the
[SPD paper](https://arxiv.org/abs/2605.22675) for the original method.

For a selected native K or V projection, let its activation output have feature
dimension `d`. Different programs have different sequence lengths, but the same
feature coordinates. Temporary native modules collect the gradient of the masked
loss at each nonpadding activation row, including prompt rows whose activations
influence completion targets. There are no forward/backward hooks. The resulting
matrix is

```math
G_i\in\mathbb R^{T_i\times d},\qquad
G_i = L_i\Sigma_i U_i^\top.
```

The leading right singular vectors form a feature-space basis. The loss is an
NLL sensitivity probe, not a differentiable test-execution reward. A gradient
mean, gradient sum, and weight gradient have different meanings and are not
interchangeable.

Extraction records spectra, available numerical rank, captured energy, and the
decomposition diagnostics. The default requests at most 32 directions and reports
whether the 95% energy target is reached; a rank cap cannot guarantee that target.
The randomized decomposition is a computational approximation. A task/module
without sufficient numerical rank is reported explicitly, not padded with random
columns and called a learned subspace.

`layers: null` uses the package's declared default target layers. Comparisons are
always between the same checkpoint, layer, projection, and native feature
coordinates, before RoPE and any key normalization. K and V bases, different
layers, and different checkpoints are never directly compared as though their
coordinates were identical.

## Interpolation, joint span, and directional containment

For orthonormal bases `U` and `V`, singular values of `U.T @ V` give the cosines of
their principal angles. Angles measure orientation; they do not identify an
algorithm. Same-implementation formatting controls help estimate how much the
measurement can change without changing the underlying program behavior.

Directional containment is asymmetric when ranks differ:

```math
c(U\rightarrow V)=\frac{\|V^\top U\|_F^2}{r_U}.
```

A value of one means that `span(U)` is contained in `span(V)` up to numerical
tolerance. For an independent uniformly random rank-`r_V` destination subspace in
`d` dimensions, the expected value is `r_V / d`. Consequently a large destination
rank can create apparent containment by chance. Report ranks, both directions,
principal angles, and matched random controls together.

The geometric operation corresponding to combining directions is the **joint
linear span** `orth([U, V])`. A set-theoretic union of two subspaces generally is
not a subspace, and `P_U + P_V` generally is not its orthogonal projector. The joint
rank can range from `max(r_U, r_V)` to `r_U + r_V`, capped by `d`.

Interpolation uses an equal-rank Grassmann path at `t = 0.25, 0.5, 0.75`. Arbitrary
basis signs and rotations must not change the subspace comparison. Orthogonal
endpoints can have nonunique shortest paths; the chosen path is a specified
construction, not evidence of a unique semantic midpoint.

The `relations` stage uses discovery questions only. Fresh programs are generated
under ten arms per eligible question: native, each of two endpoints, their joint
span, matched random joint-span rank, random single-subspace rank, pooled
subspace, and the three interpolated subspaces. This tests whether geometry has a
behavioral effect; a pleasing angle plot alone is insufficient.

All projection arms use a declared residual operator of the form

```math
T_P=I+\alpha\,P/\sqrt{r_P}.
```

This matches the Frobenius norm of the residual operator across different ranks.
It does **not** match activation perturbation, token-distribution KL, or the norm
of the folded weight perturbation; those quantities must not be inferred from
the normalization. The operator is folded into native projection weights before
RoPE/normalization. A rollout uses a fixed operator and its own recomputed cache.

## How many subspaces should be used?

There is no rule that ten candidates require ten subspaces. The experiment
separates per-solution rank `r` from generator-bank size `m`:

| Quantity | Preregistered values | Selection data |
| --- | --- | --- |
| Per-subspace rank `r` | 4, 8, 16, 32 | Validation only |
| Bank size `m` | 1, 2, 4, 8 | Validation only |
| Relation-study rank | 8 | Fixed before relation experiments |
| Interpolation positions | 0.25, 0.5, 0.75 | Fixed before relation experiments |

Bank candidates come exclusively from discovery implementations. Farthest-first
selection in geometric distance provides reproducible representatives. This is
an experimental construction, not a manually defined taxonomy or a claim that
each representative is an algorithm specialist. A pool with too few usable
candidates cannot support the requested bank size and is marked ineligible.

The `select` stage generates a native baseline and the valid rank/count grid on
validation questions. It selects using the declared `ast_proxy_coverage` metric
subject to the configured absolute correctness tolerance (`0.05` means five
percentage points). This is a validation rule, not a statistical guarantee of
noninferiority. Selection and the chosen bank are saved before final evaluation.
No final-test solution, label, or test result can enter the bank or selection.

The locked final comparison has four arms: `plain`, `learned_bank`, `random_bank`,
and `pooled`. Each gets the same number of completions per held-out question; bank
size does not multiply the total completion budget. The bank transfers from
discovery questions to new questions. We do not extract a subspace from a correct
test solution and then call generation on that question held-out evaluation.
If no valid configuration is selected, the pipeline reports `no_eligible_bank` and retains
the native baseline instead of inventing a learned result.

## Candidate and extraction budget

Let `D`, `V`, and `E` denote discovery, validation, and final question counts.
Let `n_D` be discovery samples, `T <= relations.max_tasks` the eligible relation
question count, and `G <= 16` the number of eligible rank/bank combinations.
Configured generation has the following upper bounds:

```text
Discovery:       D * n_D
Relations:       T * 10 * 16
Selection:       V * (G + 1) * 16
Final:           E * 4 * 32
Total:           sum of the four rows
```

The formulas count candidate completions, not accepted programs. Native baselines
are included. They assume all arms are eligible; `no_eligible_bank` and unavailable ranks
can reduce the realized total.

| Profile | Discovery | Relations, at most | Selection, at most | Final, at most | Total, at most |
| --- | ---: | ---: | ---: | ---: | ---: |
| 100 questions | 640 | 1,280 | 4,352 | 2,560 | 8,832 |
| Full MBPP at 341/30/500 | 10,912 | 2,560 | 8,160 | 64,000 | 85,632 |

At the 512-token generation cap these are at most 4,521,984 and 43,843,584 generated
tokens, respectively. Prefill, gradient extraction, formatting controls,
decomposition, verification, and model scoring are additional work. These counts
are not runtime or FLOP estimates. In particular the full profile is materially
larger than the 100-question diagnostic.

There are at most `D * min(n_D, 10)` original-solution gradient extractions, plus
the enabled same-implementation formatting controls. `max_pairs_per_task: 20`
caps the within-task geometry comparison work. All candidates, including failed
programs, remain in the saved discovery records. Report actual task eligibility,
generated tokens, runtime, and peak memory alongside the nominal budget.

## Reports and interpretation

Outputs below `output_dir` include:

| Artifact | Purpose |
| --- | --- |
| `manifest.json`, `tasks/*.jsonl` | Run identity and exact split membership |
| `discovery/<taskhash>/samples.jsonl`, `verified.jsonl` | Original candidates and execution outcomes |
| `subspaces/<taskhash>/<sampleid>.pt`, `subspaces/index.json` | Per-implementation bases and extraction metadata |
| `analysis/geometry.json`, `analysis/format_controls.json` | Pair geometry and surface-variation controls |
| `relations/<taskhash>/<arm>/summary.json` | Fresh generation under relation operators |
| `selection/grid.json`, `locked.json`, `bank.pt` | Validation results and the locked selection record and bank |
| `final/<arm>/summary.json` | Held-out comparison for each final arm |
| `final/comparisons.json` | Paired task-bootstrap differences versus native and direct learned-bank comparisons versus random/pooled controls |
| `report/summary.json`, `summary.md` | Machine-readable and readable outcome |
| `report/geometry_pairs.csv`, `bank_selection.csv`, `generation_metrics.csv` | Plot and analysis source tables |
| `report/geometry_overlap.png`, `generation_metrics.png` | Geometry and behavior figures |

The default diversity score is an **AST implementation proxy**, not a certified
algorithm count. Renaming robustness and formatting controls reduce obvious
surface confounds; they cannot prove that two implementations use different
algorithms. Independently audited strategy labels may be used for evaluation,
never to fit or select the train bank in this protocol. Pass@k remains a success
metric and cannot by itself establish same-question algorithm diversity.

Inspect these three outcomes separately:

1. **Geometry:** between-implementation variation compared with the
   same-implementation controls and matched random subspaces; containment in both
   directions at stated ranks.
2. **Generation:** whether endpoint, interpolation, and joint-span interventions
   produce more distinct correct implementations without an unacceptable
   correctness loss; denominator and intervention rank remain visible.
3. **Transfer:** whether a bank constructed on discovery tasks improves the
   locked held-out comparison over native, pooled, and random controls.

Question-level uncertainty is reported; completions from one question must not
be treated as independent benchmark questions. Execution infrastructure failures
are errors, not ordinary wrong programs. A run can complete successfully while
the research outcome is negative.

If these stages support useful generation diversity, the next experiment can
test ordinary LoRA absorption and repeated subspace refresh. That later study
must distinguish generation allocation `q_j` from student-training weights
`w_j`: after retaining correct programs, the source proportions are proportional
to `q_j s_j`, where `s_j` is the source success rate. It is not implemented or
validated by the frozen-model geometry results.
