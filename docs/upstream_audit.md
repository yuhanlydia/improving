# Upstream implementation audit

Audited on 2026-09-14. This document separates paper specifications, inspected
upstream code, and choices made by this repository. It does not report a
benchmark reproduction or a measured improvement.

## SPD: the comparison target

The target is [Self-Policy Distillation via Capability-Selective Subspace
Projection](https://arxiv.org/abs/2605.22675), abbreviated **SPD**, rather than a
generic external-teacher on-policy distillation algorithm.

The [version 1 paper](https://arxiv.org/html/2605.22675v1) describes the following
procedure:

1. Use a small labeled prompt–answer calibration set and mask the loss to
   correctness-defining target spans.
2. Differentiate that loss with respect to K/V activations. Concatenate gradient
   rows from **all token positions**, rather than only the supervised positions.
3. Extract top right-singular vectors from each gradient matrix and form a hard
   orthogonal projector.
4. Project K/V during generation and sample one raw completion per training
   prompt. Generated completions may be incorrect and are not execution-filtered.
5. Remove the intervention and LoRA-fine-tune the original model on the generated
   corpus. Final inference has no projection hook.

This is SVD of **activation-gradient matrices**, not SVD of the original K/V
weight matrices. The paper does not establish that a singular direction is an
algorithm, or that orthogonal directions yield different correct algorithms.

### Published settings and unresolved details

| Item | Published specification | Reproduction limitation |
|---|---|---|
| Code calibration | 50 examples; assertion-relevant target spans, typically 5–20 tokens | Exact assertion-to-token span construction and serialization are not specified |
| Code training size | 464 prompts | Exact example IDs and split construction are not supplied in the paper |
| Gradient matrix | All token-position gradients connected to the masked loss | Exact feature layout across KV heads is not specified |
| Projection rank | Half of full rank | The implementation-level feature dimension needs to be stated explicitly |
| Layers | Last and middle | A reconstruction must specify zero-based indices |
| Projection mode | Both K and V; hard projection in Eq. 12 | No residual blending parameter is described |
| Projection position | K/V activations | Position relative to key normalization, RoPE, head reshaping, and KV repetition is unspecified |
| Generation | One raw completion per prompt | Temperature, top-p, maximum length, and batch size are not stated sufficiently for exact reproduction |
| SFT | LoRA Q/K/V/O, rank 8, alpha 8, dropout 0.05 | Paper Eq. 14 sums over the concatenated prompt and completion |
| Optimizer | AdamW, LR 1e-5, weight decay 0.01, cosine schedule, gradient checkpointing | Some batching and scheduling details remain unspecified |
| Training duration | Five epochs, seed 42 | Five epochs are **not** five generate–train rounds |
| Hardware | Four A100 80 GB GPUs | Does not establish single-GPU memory use |
| Code evaluation | MBPP sanitized test: 257; CodeAlpaca held-out: 100 | CodeAlpaca NLL does not measure executable correctness or algorithm diversity |

The paper contains no official code link that we could identify. A GitHub
repository search for the exact method title did not identify an official
repository. This is a bounded search result, not proof that no private or
unindexed implementation exists. No SPD source code was available for inspection
in this audit.

### Reconstruction choices in this repository

`spd_hard` is a **documented SPD-style reconstruction** under this repository's
common protocol. It must not be reported as verified bit-for-bit official SPD.

- The intervention is defined on the output of the native K/V linear module,
  before any subsequent key normalization, RoPE, or head reshaping. The collected
  gradients use the same coordinate system as the intervention.
- The feature dimension is the flattened native KV linear output dimension.
  The implementation records actual module paths, dimensions, rank, and layer
  indices in calibration metadata.
- Calibration defaults to completion-token NLL on held-out-from-evaluation
  training references. Optional explicit reference-character intervals can
  express a supplied span protocol. Full completion supervision differs from
  SPD's assertion-relevant supervision and is an acknowledged reconstruction
  choice, not an automatic substitute for the published span definition.
- Generation settings and SFT loss masking are explicit in the experiment
  configuration. Budget-matched comparisons use the same SFT convention across
  interventions. A completion-only loss differs from SPD's written Eq. 14.
- Multi-round experiments extend the published setting. They are not reported as
  an experiment already performed by SPD.

### What folding proves, and what it does not

For PyTorch's linear convention

\[
z=xW^\top+b,\qquad z'=zT,
\]

the equivalent linear parameters are

\[
W'=T^\top W,\qquad b'=T^\top b.
\]

All operators here are symmetric, so the transpose can be omitted when applying
them. Folding changes a **temporary generation model**. SFT starts from the
unintervened current-round student.

This equality is exact in real arithmetic for our defined linear-output
intervention. Floating-point implementations need a tolerance-based test,
including the bias. A post-RoPE projector generally cannot be folded this way
because the projector and position-dependent rotations need not commute. A
post-key-normalization projector also generally cannot be moved before a
nonlinear normalization. In particular, Qwen3 key normalization makes that
distinction material.

Therefore, a successful folded-versus-explicit intervention test validates our
implementation boundary. It does **not** resolve the insertion-point ambiguity
in the SPD paper. The candidate does not need runtime hook registration. An
optional reference hook used in an equivalence test is a test instrument, not a
method contribution.

## SSD: inspected official repository

Paper: [Embarrassingly Simple Self-Distillation Improves Code
Generation](https://arxiv.org/abs/2604.01193).

The paper links `apple/ml-ssd`, which redirects to
[apple-aiml-research/ml-ssd](https://github.com/apple-aiml-research/ml-ssd).
The inspected repository commit was
[`2637d2021f1bc523385b48a1f88ea9aa4812b0a9`](https://github.com/apple-aiml-research/ml-ssd/commit/2637d2021f1bc523385b48a1f88ea9aa4812b0a9),
dated 2026-09-11. The following files and the complete repository tree were read:

- [README.md](https://github.com/apple-aiml-research/ml-ssd/blob/2637d2021f1bc523385b48a1f88ea9aa4812b0a9/README.md)
- [data_generation/generate.py](https://github.com/apple-aiml-research/ml-ssd/blob/2637d2021f1bc523385b48a1f88ea9aa4812b0a9/data_generation/generate.py)
- [data_generation/config.yaml](https://github.com/apple-aiml-research/ml-ssd/blob/2637d2021f1bc523385b48a1f88ea9aa4812b0a9/data_generation/config.yaml)
- [data_generation/templates/self_distillation_prompt_function.j2](https://github.com/apple-aiml-research/ml-ssd/blob/2637d2021f1bc523385b48a1f88ea9aa4812b0a9/data_generation/templates/self_distillation_prompt_function.j2)
- [data_generation/templates/self_distillation_prompt_stdin.j2](https://github.com/apple-aiml-research/ml-ssd/blob/2637d2021f1bc523385b48a1f88ea9aa4812b0a9/data_generation/templates/self_distillation_prompt_stdin.j2)
- [evaluation/eval.py](https://github.com/apple-aiml-research/ml-ssd/blob/2637d2021f1bc523385b48a1f88ea9aa4812b0a9/evaluation/eval.py)
- [evaluation/benchmark.py](https://github.com/apple-aiml-research/ml-ssd/blob/2637d2021f1bc523385b48a1f88ea9aa4812b0a9/evaluation/benchmark.py)
- [LICENSE](https://github.com/apple-aiml-research/ml-ssd/blob/2637d2021f1bc523385b48a1f88ea9aa4812b0a9/LICENSE)

### Code and paper differences that affect replication

| Item | Inspected release | Paper description / consequence |
|---|---|---|
| Default model | Qwen/Qwen3-4B-Instruct-2507 | Use the exact model ID, not an ambiguous Qwen3-4B label |
| Prompt dataset | microsoft/rStar-Coder, `seed_sft`, train | Competitive-programming prompts; this is a larger setting than small MBPP LoRA experiments |
| Generation temperature | YAML: 1.5; Python fallback: 1.6 | Paper Qwen3-4B-Instruct table: 1.6 |
| Other generation settings | top-k 20, top-p 0.8, max tokens 65536 | Context and output budgets must be explicit |
| Filtering | Removes empty outputs and bottom 10% shortest responses by default | More aggressive than paper's stated minimal empty/stub filtering; not used by our no-filter training protocol |
| Generation formatting | Passes plain template strings directly to `vLLM.generate` | Paper describes official chat templates; evaluation code does call `apply_chat_template` |
| Deduplication | No problem deduplication in the released generation script | Paper describes whitespace-normalized exact deduplication to about 10,168 prompts |
| Generation seed | No seed CLI/config argument passed in released generator | Our outputs must record reproducible sampling seeds |
| SFT | No training implementation in the inspected tree | Our trainer is an independent implementation |
| Evaluation persistence | Per-example `examples` contains the last repeat only | Our diversity analysis requires every completion from every repeat |

The [paper's full experimental setup](https://arxiv.org/html/2604.01193v1)
uses Megatron-LM on eight B200 GPUs, global batch 32, sequence length 65536,
AdamW with peak LR 5e-6, and 2500 instruct-model iterations. A 1.5B/3B LoRA pilot
with a smaller corpus is a **budget-matched SSD-style recipe adaptation**, not a
reproduction of those headline results. Report both training-time and
evaluation-time decoding settings; a gain caused by changing only the evaluation
decoder must remain visible.

### Attribution and source-code handling

The inspected SSD release has a custom Apple license, not MIT or Apache-2.0.
This repository's implementation was written independently from the documented
algorithms and interfaces; no SSD source files or prompt templates were copied
into the implementation. “Independent implementation” is the intended meaning
of clean-room implementation here: upstream code was inspected for understanding,
so this is not a claim of a formal legally isolated clean-room process.

Any future vendoring must retain the applicable source notices and license
rather than relabeling the copied source under this repository's license.

## Interpretation limits

Neither paper directly establishes repeated-round loss of distinct correct
algorithms for the same coding question. SSD reports pass@k improvements, which
must be treated as counterevidence to a blanket claim that self-distillation
necessarily damages coding performance. Pass@k does not count algorithm types.

The proposed spectral operator and the experimental claims are specified in
[experiment_protocol.md](experiment_protocol.md). No upstream code or theorem
supports claiming that it already outperforms SPD, or guarantees semantic
diversity.
