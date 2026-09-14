# Formal Spectral-soft experiment

## Question and primary claim

Can a generation policy retain more **different correct implementations of the same coding task** during self-distillation, while keeping accuracy within a fixed tolerance?

The experiment maximizes correct-implementation diversity subject to an accuracy constraint. An increase in pass@1 is not required. The primary diversity endpoint is expected AST coverage in four draws without replacement from correct samples; AST classes are implementation proxies. An independent algorithm annotation study is needed before calling them distinct algorithms.

Spectral-soft is the current candidate. The 64-task, seed-42 pilot is exploratory evidence and is not pooled into the formal confirmation. The five formal training seeds are new: 43–47. Seed 42 stays exploratory; `data_seed: 42` fixes data selection and does not make a run a seed-42 training replication.

## Run commands

On a BF16-capable CUDA machine with Python 3.10+ and Docker:

```bash
git pull origin main
python -m pip install -e '.[train,test,analysis]'
bash scripts/run_formal.sh configs/formal_16gb.yaml
```

The default is **confirm**: five seeds, one self-distillation round, four methods, full prepared MBPP. It prepares MBPP only if all four standard split files are absent, retrieves the ordinary verifier image if needed, validates configuration/data, runs confirmation, and writes report plus compact evidence archive.

Use `configs/formal_24gb.yaml` for the 3B target profile. These memory profiles have not established measured peak memory or runtime. Both use generation batch 4; LoRA uses microbatch 1 and gradient accumulation 16. If changing batch size or any experimental setting, choose a fresh output directory because the sampling stream changes.

The remaining phases can run individually after confirmation:

```bash
bash scripts/run_formal.sh configs/formal_16gb.yaml mechanism
bash scripts/run_formal.sh configs/formal_16gb.yaml retention
bash scripts/run_formal.sh configs/formal_16gb.yaml transfer
```

Or execute the entire suite in sequence:

```bash
bash scripts/run_formal.sh configs/formal_16gb.yaml all
```

For `transfer` or `all`, the script builds `docker/EvalPlus.Dockerfile` if the configured image is absent, and prepares official HumanEval+ tasks if the default transfer path is absent. Candidate execution occurs in isolated containers without network. The container image may need network access during its dependency/data build.

```bash
# Split/config validation and candidate-budget estimates; no model execution.
bash scripts/run_formal.sh configs/formal_16gb.yaml validate

# Regenerate reports or evidence without running a model or requiring Docker.
bash scripts/run_formal.sh configs/formal_16gb.yaml report
bash scripts/run_formal.sh configs/formal_16gb.yaml export

# Optional evidence archive containing programs for independent annotation.
python -m improving formal --config configs/formal_16gb.yaml \
  --stage export --resume --include-programs
```

The Python `formal --stage validate` command itself only reads prepared data. The shell wrapper may download/prepare MBPP when its standard data directory is wholly absent. Existing partial data are an error, not an invitation to replace files.

## Fixed data and model settings

| Item | Formal setting |
|---|---|
| 16GB target | Qwen2.5-Coder-1.5B-Instruct, BF16, SDPA |
| 24GB target | Qwen2.5-Coder-3B-Instruct, BF16, SDPA |
| MBPP train | Full prepared train split: 291 tasks in the checked snapshot |
| Calibration | 50 disjoint training references |
| Validation | 30 disjoint tasks; reserved, not used in the fixed-tau formal pipeline |
| MBPP test | All 500 official full-MBPP test tasks |
| Transfer | All 164 HumanEval+ tasks, official EvalPlus 0.3.1 base-and-plus checks |
| Data selection seed | 42 for every training seed |
| Confirmation seeds | 43, 44, 45, 46, 47 |
| Mechanism / retention seeds | 43, 44, 45 |
| Common evaluation decoding | temperature 0.8, top-p 0.95, top-k 0, 64 samples/task |
| Completion/prompt cap | 512 / 1024 tokens |
| Training data per round | 1 raw completion per train task, including incorrect or empty completions |
| LoRA per round | rank 8, alpha 8, dropout 0.05, 5 epochs, learning rate 1e-5 |
| LoRA loss | Raw-sequence SFT (`loss_scope: all`) for every method |
| Calibration loss | Mean completion-token NLL; prompt positions masked from the loss |
| Gradient coordinates | Native K/V linear outputs; all nonpadding token gradient rows |
| Selected layers | Middle and last decoder layers, mechanically from layer count |
| Spectrum parameters | tau = 1.0; hard retained rank = floor(0.5 × native output dimension) |
| Code extraction | `first_fence`, identical across arms and included in verifier provenance |

Preparation removes exact normalized prompt overlap between training and held-out splits while preserving all test tasks. On the checked snapshot, excluded training IDs are 602, 704 and 872. The preparation manifest records actual counts and exclusions; the runner uses those actual counts, not the table as a substitute for checking files. These are full MBPP scores, not sanitized MBPP or MBPP+ scores.

HumanEval+ supplies an external test set; no HumanEval+ reference, correctness label or generated program enters calibration or SFT. Prepared continuation prompts preserve the official function specification. Additional extended tests are evaluated only by official EvalPlus in the bounded container.

Tau, rank fraction, selected layers, correctness margin and evaluation budgets are fixed before the next run. This suite does not select them on the test set. A later validation sweep must be declared separately and use a fresh output directory and independent confirmation protocol.

## Phases and what they establish

| Phase | Runs | Main question |
|---|---|---|
| `confirm` | 5 seeds × 4 methods × 1 round, plus base model per seed | Does the post-LoRA candidate improve same-task correct diversity while maintaining accuracy? |
| `mechanism` | 3 seeds × 3 additional controls × 1 round, plus base | Do the covariance directions and continuous spectral gains matter beyond a mild perturbation? |
| `retention` | 3 seeds × 3 methods × 3 rounds, plus base | Is the diversity advantage retained over repeated generate–train cycles? |
| `transfer` | 5 seeds × base and 4 confirmation checkpoints on HumanEval+ | Does the learned model retain diversity under a second task/test protocol? |

`plain`, `ssd`, `spd_hard`, and `spectral_soft` are the confirmation methods. The base model is an additional reference and is not the `plain` self-trained checkpoint.

`matched_blend`, `random_soft`, and `isotropic_soft` are the additional mechanism methods. They use the same raw-corpus size, calibration access where needed, LoRA recipe and common post-LoRA decoding. Their round-one summaries can be compared to the corresponding seeds from confirmation.

Retention uses `plain`, `spd_hard`, and `spectral_soft`. Each trajectory is an independent sealed three-round run starting at the base model; round 1 is repeated within that trajectory. It does not mutate or append to a previously sealed one-round confirmation directory. Each round begins from that method's previous merged checkpoint and recomputes calibration.

Every round also measures the **intervened generating policy before LoRA** on a fixed 128-task test subset with 32 samples/task. This smaller diagnostic set is the same across seeds/methods and is never training data or a selection criterion. It explains where a change arises, but its estimates must not be substituted for 500-task post-LoRA results. A 32-sample diagnostic cannot supply pass@64. SSD uses its own decoding recipe during generation, so an SSD generation-policy comparison has a decoding confound; all post-LoRA evaluations use the common decoder.

Five SFT epochs are within one round. Three retention rounds are three complete generation-and-SFT cycles. No adapter pool, heuristic strategy filter, prompt ensemble or new coevolution algorithm is added here. The separate frozen-model geometry study remains available as an optional diagnostic, not a dependency of this suite.

## Spectral hypothesis and controls

For one native K/V output module, completion-loss gradients define

\[
C=\frac{1}{M}\sum_t g_tg_t^\top,
\qquad C=U\operatorname{diag}(\lambda_i)U^\top,
\qquad s_i=\frac{1}{1+\tau(1-\lambda_i/\lambda_{\max})}.
\]

The candidate operator is

\[
T_{\mathrm{soft}}=U\operatorname{diag}(s_i)U^\top.
\]

The research hypothesis is that hard removal of weak covariance directions can suppress low-frequency correct implementations, while graded attenuation may retain them. This is a hypothesis to test: gradient covariance alone does not identify algorithm identity. The proximal operator is classical; the research contribution would be the coding diversity phenomenon, controlled intervention and evidence across distillation.

Let \(P_r\) project onto the top-r covariance directions, \(d\) be module output dimension and \(\delta=\|T_{\mathrm{soft}}-I\|_F\).

| Method | Operator / policy | Question |
|---|---|---|
| `plain` | Identity, common sampling | Ordinary raw-output self-training |
| `ssd` | Identity, temperature 1.5 / top-p 0.8 / top-k 20 for synthesis | Whether a decoding recipe is sufficient |
| `spd_hard` | \(P_r\) | Hard spectrum cutoff |
| `spectral_soft` | \(U\operatorname{diag}(s_i)U^\top\) | Learned graded spectral attenuation |
| `matched_blend` | \(P_r+\rho(I-P_r)\), \(\rho=1-\delta/\sqrt{d-r}\) | Simple two-level softness at matched distance from identity |
| `random_soft` | \(Q\operatorname{diag}(s_i)Q^\top\), independent seeded Haar \(Q\) | Same full spectrum, without learned eigenvectors |
| `isotropic_soft` | \((1-\delta/\sqrt d)I\) | Uniform shrinkage at matched distance from identity |

Matching is **per module in operator Frobenius distance from identity**. It does not match activation RMS, folded-weight change, attention scores or output KL. The same gains in `random_soft` additionally match the full eigenvalue spectrum. If a chosen rank/tau makes the matched blend infeasible, the operator rejects it instead of silently using an unmatched setting.

Temporary operators are folded into native K/V linear weights before RoPE and key normalization, then removed before LoRA training. This realizes the chosen linear intervention without activation hooks. The hard baseline uses the same execution route. Hook removal is an implementation property, not evidence of a new mathematical method. The hard baseline is a declared paper reconstruction; default completion masks and insertion point must be reported when comparing to SPD.

## Statistical decision and interpretation

The two primary comparisons are Spectral-soft minus SPD-hard and Spectral-soft minus plain, after round-one LoRA on full MBPP. There are two primary endpoints for each comparison:

1. **Correctness noninferiority:** paired task-macro pass@1 delta has lower confidence bound at least -0.01. All test tasks enter this endpoint. A confidence interval containing zero alone does not prove noninferiority.
2. **Correct implementation diversity:** paired AST coverage at a fixed budget of 4 correct samples has lower confidence bound above zero. A task enters a seed's comparison only when both arms have at least 4 correct samples. Report that common eligible-task count, not the separate arm denominators as if they were identical.

The primary family therefore has four tests. The suite uses Bonferroni-adjusted intervals for that declared family (family-wise confidence at least 95%; individual two-sided confidence 98.75%). Bootstrap sampling preserves arm pairing, resamples training seeds and task IDs as crossed units, and recomputes each seed's shared eligibility. Per-seed results remain visible. With only five seeds, intervals still have limited information about training randomness; do not present thousands of generated samples as thousands of independent training replications.

AST coverage budgets 8 and 16, pass@8/32/64, exact-program coverage, unique fractions, Simpson diversity and control-flow proxies are secondary. Their reported pointwise intervals are descriptive unless explicitly included in a separately declared correction family. SSD is a secondary comparison. A pass@64 improvement measures solved-task breadth and cannot establish multiple algorithms for one question.

For correct implementation-class counts \(c_j\), total correct samples \(c\), and budget \(b\), expected coverage is

\[
\widehat D_b=\sum_j\left(1-\frac{\binom{c-c_j}{b}}{\binom cb}\right),\qquad c\ge b.
\]

This conditions on correctness. Report eligibility alongside every budget because the eligible subset changes as b increases. A unique fraction can increase merely because fewer correct samples were collected, so it is not the primary endpoint. Higher coverage at equal total sampling and fixed correct budget is more direct evidence, while still remaining conditional on the shared eligible subset.

Retention plots should show accuracy and coverage at every round, with explicit round-matched eligible tasks. A claim about within-task decay needs a stable common eligible set across the compared rounds; a change of cohort must not be interpreted as individual-task loss or recovery. Three rounds establish behavior over that horizon, not indefinite prevention of collapse.

A blinded annotation follow-up uses only an exported, prospectively selected evaluation subset. Choose task IDs and program sampling rules before revealing method names; strip method/seed labels; use a fixed algorithm rubric and two independent annotators, adjudicating disagreements. Use the existing `annotate` and `metrics` interfaces to compute algorithm-label coverage. The suite exports programs on request but does not fabricate labels or run an automated classifier as ground truth. Annotated labels never alter calibration, sample inclusion for training or checkpoints.

## Compute budget and resumability

Let \(N=291\) train tasks, \(E=500\) test tasks, \(D=128\) diagnostic tasks, \(n=64\) final samples and \(q=32\) diagnostic samples. One method-round generates \(N+Dq+En=36{,}387\) candidates. Each seed/phase also generates \(En=32{,}000\) base candidates. These are maximum configured candidate counts; actual generated tokens depend on stop positions.

| Phase | Candidate formula | Candidates in the checked snapshot |
|---|---|---:|
| Confirmation | \(5[En+4(N+Dq+En)]\) | 887,740 |
| Mechanism | \(3[En+3(N+Dq+En)]\) | 423,483 |
| Retention | \(3[En+3\times3(N+Dq+En)]\) | 1,078,449 |
| HumanEval+ transfer | \(5\times5\times164\times64\) | 262,400 |
| Entire suite | Sum of phases | 2,652,072 |

At 512 new tokens per completion the entire suite has a **1,357,860,864-token upper bound** on generated new tokens. This excludes prompt prefill, calibration/backpropagation, SFT, code verification and report costs. It is not an estimate of elapsed time, token usage or FLOPs. Use `validate` for counts from the actual prepared dataset. The default shell command runs confirmation only; the `all` argument explicitly requests every phase.

Each phase/seed gets a compiled immutable pipeline configuration under `configs/<job_id>.yaml` inside the suite output directory and a separate run directory. The formal CLI supports `--job-id confirm_seed43` (with `--stage confirm`) for a single planned job. To distribute jobs across GPUs, run validation once, use a distinct job ID on each GPU and produce the aggregate report after jobs finish; do not launch the same job concurrently. Generation reuses complete atomic chunks and deterministic batch seeds. Interrupted SFT restarts the current incomplete round from the previous complete checkpoint; mid-optimizer resume is not implemented. Saved data/model/code/config fingerprints prevent silently combining different versions. Pulling changed implementation code while an experiment is incomplete can invalidate resume; keep the running checkout fixed and move changed protocols to new output directories.

Actual generated token totals, calibration cost, wall time, training statistics and CUDA peak allocation/reservation are saved. Candidate counts match by design; actual completion tokens and compute need not match because program lengths differ. Every raw output is retained, including failures, and is used for the common SFT protocol.

## Results to share

Outputs live beneath `runs/formal_spectral_16gb_v1/` or the configured output directory:

- `report/summary.md`, `report/summary.json`: phase status, comparisons and declared statistical settings.
- `report/per_seed.csv`, `report/comparisons.csv`, `report/per_task.jsonl`: auditable aggregate and paired-task results.
- `evidence/compact.tar.gz`: reports, configurations, manifests, resource summaries and per-task metrics, without model weights or full programs.
- `evidence/programs.tar.gz`: optional export with programs for independent reproduction/annotation.

Share the compact archive or commit its extracted evidence to the result directory on GitHub after the run. A table or hash alone is insufficient for independently recomputing paired intervals. Incomplete phases are explicitly pending; missing values are not zero performance. The formal suite is code prepared for execution, not a completed GPU experiment.
