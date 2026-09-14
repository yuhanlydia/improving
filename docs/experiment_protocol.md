# Coding-only experimental protocol

## Question and current status

Can self-distillation improve executable correctness while retaining different
correct implementations and algorithms for the **same programming problem**?
The scope excludes cross-domain forgetting and popular-versus-rare industries.

The repository implements an experiment, not a validated new method. The first
decision is whether a reproducible correctness–diversity problem exists under a
controlled coding setup. An implementation test, a tiny-model smoke test, or a
promising single seed does not establish research success.

中文说明：我们比较同一道代码题在生成干预前、干预时以及蒸馏后的正确解法分布。
首先检验问题是否存在，再检验平滑谱变换能否改善正确率与解法保留之间的关系。
不通过增加 prompt、人工挑选训练样本或增加策略 adapter 数量取得优势。

## Candidate: a proximal spectral transformation

Let C be the positive semidefinite second-moment matrix of gradients with respect
to a selected K/V linear module's output. Gradients come from calibration loss,
and every nonpadding token-position gradient contributes. C is an uncentered
gradient second moment; “covariance” in informal descriptions refers to this
quantity rather than mean-centered covariance.

For positive maximum eigenvalue, define

\[
\bar C=C/\lambda_{\max}(C),\qquad
T_\tau=\left[I+\tau(I-\bar C)\right]^{-1},\quad\tau\geq0.
\]

For a column activation h, the transformed activation is the solution of

\[
\operatorname*{argmin}_z
\frac12\lVert z-h\rVert_2^2+
\frac\tau2 z^\top(I-\bar C)z.
\]

With normalized eigenvalues \(\mu_i\in[0,1]\), the attenuation on eigenvector i is

\[
t_i=\frac{1}{1+\tau(1-\mu_i)}\in
\left[\frac1{1+\tau},1\right].
\]

At tau=0 this is identity. For finite nonnegative tau it has no exact nullspace
in real arithmetic. This is a property of the local linear transformation, **not
a guarantee that the whole language model retains algorithms**. Finite precision,
normalization, nonlinear attention, sampling, and SFT can all change the final
distribution. Zero calibration energy is an invalid capability signal: the
implementation must report it explicitly rather than treating a numerical
normalization constant as evidence of a useful subspace.

This is classical proximal spectral shrinkage used as an unvalidated experimental
candidate. We do not claim a new mathematical operator or establish superiority
by giving it a name. It differs from the residual blend control because it uses
the complete normalized spectrum rather than assigning only two attenuation
levels.

The operator is folded into temporary native K/V linear weights for generation.
Calibration uses explicit temporary modules and autograd, not activation-hook
registration. The student is fine-tuned from its unintervened checkpoint with one
LoRA adapter; there is no strategy adapter pool. The exact intervention boundary
and SPD reconstruction limitations are in [upstream_audit.md](upstream_audit.md).

## Methods and what each controls

| Method | Data-generation policy | Purpose |
|---|---|---|
| `plain` | Unmodified current model with common sampling settings | Raw self-training reference |
| `ssd` | Unmodified current model with declared SSD-style temperature/truncation | Existing hook-free decoding-and-SFT recipe, adapted to the common budget |
| `spd_hard` | Top-r hard projector from calibration gradients | SPD-style reconstruction with declared insertion point and loss spans |
| `spectral_soft` | Full-spectrum proximal operator T_tau | Main unvalidated candidate |
| Residual blend control | P + rho(I-P) | Does a two-level softening explain any gain? |
| Random projection control | Random orthogonal rank-r projector | Does selecting capability-related directions matter? |
| Identity / tau=0 | Unmodified activations | Numerical and pipeline control; must agree with plain when settings match |

Use the common decoder for plain, spd_hard, spectral_soft, and structural
controls. The SSD arm explicitly varies decoding, so include a frozen-model
decode-only comparison with that decoder. Do not infer a training gain from
changing the test-time temperature alone.

Random controls must match intervention module paths and rank. If perturbation
magnitude is used as an additional matching criterion, fit the scale using
calibration/development data, report the resulting magnitude, and preserve it
for the evaluation run. Random directions are not presumed to encode strategies.

## Data, information access, and task choice

Use deterministic, namespaced task IDs and save a manifest containing dataset
name, configuration, revision or downloaded file hash, split, selected IDs, and
normalized prompt fingerprints. Store manifests before training. Hash overlap
checks catch exact or formatting-level contamination; they do not establish the
absence of semantic near-duplicates or pretraining contamination.

Use separate sets for:

1. Calibration references, used only to compute the intervention.
2. Unlabeled self-generation training prompts.
3. Development tasks, used to choose tau/rank/decoding and the noninferiority
   margin before final evaluation.
4. Final held-out evaluation tasks and their correctness tests.

The calibration and generation sets are disjoint in the main protocol. All four
sets are disjoint by task ID and checked prompt fingerprint. Do not use held-out
references, private tests, or evaluation strategy labels for calibration,
training, model selection, or choosing favorable seeds. Public examples already
present in a benchmark's standard problem statement remain part of the fixed
prompt; hidden tests must never be added to the generation prompt.

Calibration uses the same examples and supervision convention for all spectral
methods. Plain and SSD receive no calibration update because their algorithms do
not use one; report this difference in information access and include a
reference-SFT control on the same calibration examples if attributing a gain
specifically to the geometry. Neither generated correctness outcomes nor
algorithm annotations enter the training loop.

Start with a small development pilot on Python function-generation tasks.
HumanEval+ and MBPP+ are suitable held-out functional-correctness checks. A fixed
LiveCodeBench release/date slice can later test more substantial algorithmic
choices; it must have a frozen task manifest and a compatible, validated
execution adapter. Preparing or naming a dataset is not evidence that its full
evaluation path has been run.

Do not assume every problem admits 64 meaningfully different algorithms. Sampling
64 programs is a measurement budget, not a target algorithm count. Some short
utility tasks have little algorithmic freedom. Select benchmarks for the research
question before seeing method outcomes; report all selected tasks, including
those with zero correct outputs or only one observed strategy. Complexity and
problem type may be reported as predefined evaluation descriptors, never used
as a manual training hierarchy.

## Generation and training controls

- Main evaluation: 64 independent samples per problem, with the same task IDs,
  temperature, top-p/top-k, token limits, stop conditions, and prompt format for
  paired comparisons. Save every raw sample, even empty, invalid, wrong, or
  truncated outputs.
- Use a single fixed task prompt through the model's chat template. No prompt
  ensemble, per-strategy instruction, or manual rewrite per method.
- Give every method the same generation-prompt count and samples per prompt for
  training. The initial protocol uses one completion per training prompt, as in
  the published SPD/SSD setup. Additional samples are a separate common-budget
  experiment for every method.
- Do not filter training samples by execution, correctness, AST, cluster,
  estimated strategy, response length, or a human judgment. Serialization errors
  should fail loudly. Zero-token records that cannot define an SFT loss remain
  in the generation audit with an explicit nontrainable count; they must not be
  silently relabeled successful or replaced until the data looks favorable.
- Use equal LoRA rank, target modules, loss convention, optimizer, optimizer-step
  cap, and context cap. Report realized supervised tokens, padding, truncation,
  generated tokens, and wall time. Equal epochs do not imply equal token budgets
  when responses have different lengths. If enforcing an exact supervised-token
  budget, document the scheduling rule before running and use it for every arm.
- Record base checkpoint, model and tokenizer revision, seed, configuration hash,
  dataset manifest hash, dependency versions, calibration statistics, and all
  generation/train/evaluation counts.
- Checkpoint before and after every SFT stage. A resume must verify matching
  configurations and manifests. Do not reuse a partial output file from a
  different method or overwrite earlier round evidence.

Calibration is an additional cost. Report its backward passes, wall time, and
peak memory separately from generation and SFT. Comparing only optimizer steps
would conceal this cost.

## Rounds and mechanism measurements

First run rounds 0 and 1. At a fixed evaluation protocol, distinguish:

| Checkpoint or policy | Measurement |
|---|---|
| Unmodified round-t model | Which correct implementations are observable before intervention? |
| Temporary intervened generation model | Does the intervention change correctness or correct-implementation coverage immediately? |
| Unintervened model after SFT | Does fitting generated data preserve or amplify that change? |

Only extend to rounds 3 and 5 after resolving numerical/pipeline errors and
observing an interpretable pilot signal. If the experiment is designed to reach
round 5, retain rounds 2 and 4 checkpoints and logs as well. Never substitute five
epochs for five generate–train cycles.

The main multi-round intervention recomputes its gradient statistics on the same
fixed calibration examples using the current-round student. A frozen
round-0-spectrum experiment is a separate ablation. Mixing these policies within
one curve would make the trajectory uninterpretable.

At each round, train from the current unintervened student. Restore the original
generation weights before SFT, or load a separate original checkpoint. Do not
accidentally accumulate folded projectors across rounds. If LoRA updates are
merged between rounds, record that operation explicitly; it does not prove that
intruder dimensions accumulate or explain a diversity outcome.

## Correctness and diversity measurements

For a task with n samples and c correct samples, the usual finite-sample
pass@k estimator is

\[
\widehat{\operatorname{pass@k}}=
1-\frac{\binom{n-c}{k}}{\binom nk},\qquad k\leq n.
\]

Missing samples, duplicate sample IDs, and k>n are protocol errors or explicitly
unavailable metrics. They are not grounds for manufacturing a favorable value.
Execution outcomes must distinguish incorrect programs from infrastructure
failures, and preserve timeouts and parse errors in the audit.

Let n_j be the number of correct programs assigned label j. The finite-sample
expected distinct-label coverage in k draws without replacement is

\[
\widehat D_k=\sum_j
\left[1-\frac{\binom{n-n_j}{k}}{\binom nk}\right].
\]

Unconditional coverage can increase just because correctness increases. Also
report coverage conditional on a fixed number b of correct samples, replacing n
with c and k with b in the expression above. Choose b before final evaluation.
This measure is unavailable for c<b; report the eligible task count for every
arm and a paired common-eligible comparison. Explicitly discuss the selection
effect of restricting to tasks both models solve often enough. Do not hide
zero-correct tasks; their outcomes remain in unconditional coverage and accuracy.

Use two clearly separated label types:

- **AST implementation proxy:** a deterministic normalized structural
  fingerprint. It is useful for tracking syntactic/structural duplication but
  does not establish algorithmic novelty or semantic equivalence.
- **Audited algorithm labels:** stable within-task labels assigned through an
  independent evaluation procedure with a fixed rubric. An annotator must be
  able to distinguish algorithm/data-structure/control-flow choices from
  renaming, comments, and superficial reformatting. Hide method identity and
  training round during annotation. Use an audited subset, report disagreements
  and unavailable labels, and keep labels consistent across all compared rounds.

No universal hand-written strategy hierarchy is required. Labels are evaluation
metadata, not a training signal. If using an LLM to assist annotation, preserve
its prompt, version, decisions, and independent audit; the evaluator's output is
not an infallible strategy oracle. Do not treat different ASTs or embeddings as
proof of different algorithms.

Additional descriptive measures are entropy over correct labels, observed
cross-round retention using stable labels, and the distribution of observed
strategy counts across tasks. Observed retention is limited by finite sampling:
failure to resample a rare strategy does not prove that its true probability is
zero. Cross-round relative decay is undefined when baseline coverage is zero;
report it as unavailable rather than divide by an arbitrary epsilon.

## Statistical gates and decisions

Use at least three independently trained seeds for the pilot; expand to five
only when a specific remaining uncertainty justifies it. Pair comparisons by
task and keep sampling protocols identical. Report each training seed rather
than pooling every completion as an independent training replicate.

For each seed, task-bootstrap confidence intervals quantify uncertainty across
the selected task population. They do not by themselves quantify training-seed
uncertainty. Report seed variability separately; a combined interval requires a
declared hierarchical resampling procedure. Persist all raw records so these
choices are reviewable.

Before final evaluation, choose one primary correctness endpoint (pass@1), one
primary conditional-diversity endpoint and budget, and a practically acceptable
accuracy loss margin delta. Choose delta on scientific grounds and development
data, not after seeing held-out results. State all secondary metrics and avoid
selecting whichever k or seed yields a favorable result.

Progress gates:

1. **Implementation:** identity limit, PSD/eigenvalue checks, gradient masks,
   token shifting, folding equivalence, checkpoint reload, split separation,
   and metric calculations pass meaningful tests. These are software checks.
2. **Phenomenon:** paired pilot data show whether intervention or SFT changes
   correct-implementation diversity, after accounting for correctness and sample
   budget. No detected collapse is a legitimate result; do not fabricate the
   motivation from an AST fluctuation.
3. **Candidate:** candidate minus comparison pass@1 has a lower confidence bound
   above -delta, while the prespecified conditional-diversity endpoint improves
   with uncertainty reported and is reasonably consistent across seeds. AST-only
   improvement warrants an algorithm-label audit, not an algorithmic claim.
4. **Mechanism and scope:** compare the residual blend, random projection, and
   decoder controls. If ordinary softening or sampling explains the effect,
   report that outcome. A classical spectral operator plus a positive pilot does
   not alone justify a novelty claim.

Hyperparameters are selected on development tasks, frozen, and then evaluated on
the final held-out set. Do not repeatedly use the final test set to decide tau,
rank, prompt, dataset subset, training duration, or which seeds to retain.
Formal claims involving multiple arms/endpoints require a declared multiplicity
policy. The pilot is diagnostic and must be described as such.

If the candidate consistently loses correctness, adds no audited diversity, or
is explained by a simpler matched control, stop expanding that candidate. A
negative result can still locate where a hypothesis failed; it should not be
repackaged as successful protection against collapse.

## Hardware profiles and execution status

The initial profile targets Qwen2.5-Coder-1.5B-Instruct with a 16 GB-class GPU,
LoRA rank 8, microbatch 1, gradient accumulation, and bounded sequence lengths.
A 24 GB-class profile can target Qwen2.5-Coder-3B-Instruct. These are planning
targets, **not measured memory-fit guarantees**. Model weights alone do not
determine peak memory: activation gradients, attention implementation, optimizer
state, sequence length, generation KV cache, and temporary calibration tensors
all matter.

Use BF16 only on supported hardware. Record actual peak allocated/reserved
memory, throughput, and length distributions before increasing batch or context.
CPU float64 accumulation of gradient second moments avoids retaining all
calibration rows on GPU, but does not eliminate the GPU backward-pass cost.
Hold only the model instances required by the current stage; sequential stages
are preferable when testing a memory-constrained profile.

Development of this repository does not launch a GPU benchmark job. Tiny random
model tests validate tensor mechanics only. Report a run as complete only after
its manifest, expected sample counts, training checkpoint, verifier outputs, and
metrics are present and internally consistent. Unmeasured GPU memory and
unmeasured coding performance remain explicitly unmeasured.
