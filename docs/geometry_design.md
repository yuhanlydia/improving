# Correct-solution subspace geometry study

This study freezes the model before testing the proposed coevolution mechanism.
It measures whether K/V gradient subspaces from different correct implementations
have reproducible overlap, directional containment, useful interpolation, or
useful joint spans. Geometry alone is not an algorithm label.

## Protocol

Use official prepared MBPP partitions. Combine training and calibration only for
discovery; keep validation for rank/bank-size selection and the official test
partition for a single locked evaluation. The 100-task profile selects 64/16/20
tasks; the full profile retains all prepared tasks. All implementations of one
task stay together. Ten rollouts mean ten candidates, not ten correct algorithms.

For each verified discovery implementation, compute the mean completion-token
cross entropy, masking the prompt. Preserve generated token IDs and reject
truncation. Explicit implementation-specific character spans are an optional
protocol; reference spans must never be reused on different generated programs.
This default is not SPD's underspecified assertion-relevant span extractor.

Capture gradients at each selected native K/V Linear output before RoPE or key
normalization with explicit temporary modules, never hooks. Per-implementation
G has rows for nonpadding token positions and columns for native feature
channels. Compute compact leading right singular vectors, storing spectral
energy and approximation diagnostics, not dense covariance archives.

Compare bases only within the same checkpoint, module and feature coordinates.
Use principal angles and directional captured energy, including unequal-rank
comparisons and the random-subspace containment expectation. Joint span means
orth([U,V]), not set union or projector addition. Interpolation follows an
equal-rank Grassmann path; basis signs/rotations cannot change projector results
away from nonunique orthogonal/cut-locus cases.

Per-task relation experiments regenerate fresh candidates under endpoint,
interpolated, pooled, joint-span and matched random operators. Residual operators
I + strength*P/sqrt(rank) have matched Frobenius residual norm; this does not imply
equal activation perturbation or output KL. Report actual folded parameter
perturbations and ranks. Use a separate native baseline and fixed candidate
budgets for all arms. No correct test programs enter fitting or routing.

Discovery-only farthest-first representatives form experimental banks. These
are geometric representatives, not manually assigned algorithm specialists.
Validation chooses rank and count from a preregistered grid using a declared
implementation-diversity proxy subject to a correctness tolerance. It must be
called proxy selection; audited algorithm labels are evaluation-only. Lock the
selection before evaluating native, learned-bank, random-bank and pooled controls
on test prompts. Failed or insufficient-rank cases remain explicit.

The first run does not train LoRA or claim coevolution. Existing LoRA experiments
remain available separately. Only after generated-program diversity is supported
should LoRA absorption and online subspace refresh become the next experiment.

## Verification and reproducibility

Docker is the default program executor. Failed infrastructure is not a wrong
program. All candidate outputs are retained, including failures. Archive data,
model, source-code, configuration and stage identities; checkpoints are atomic.
Resume must reject changed inputs/configuration and modified completed artifacts.
Report question-level uncertainty and denominators. Twenty test tasks constitute
a pilot, not a full benchmark claim.
