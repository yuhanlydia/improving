# ICLR evidence plan: diversity with accuracy maintained

The candidate paper asks whether self-distillation can preserve more correct implementations for the same coding task while maintaining accuracy. Pass@1 improvement is not required. The seed-42, 64-task MBPP pilot motivates the next experiment; it is exploratory, and the new formal results are pending.

Use [the formal protocol](formal_protocol.md) as the executable specification. Start with:

```bash
bash scripts/run_formal.sh configs/formal_16gb.yaml
```

## E1 — Confirm the diversity result

**Implemented, formal GPU results pending.** Five new seeds 43–47, full 500-task MBPP test split, 64 samples per task, one raw-output LoRA round. Compare plain, SSD, SPD-hard and Spectral-soft, plus the original base model.

Two primary comparisons are Spectral-soft versus SPD-hard and versus plain. Require both correctness noninferiority within the fixed absolute 1 percentage point margin and higher AST coverage at four correct samples. Use paired shared eligible tasks for diversity, all tasks for accuracy, crossed seed/task bootstrap and a declared four-endpoint family. Show each seed alongside the aggregate. AST coverage at 8/16 correct samples and other structure proxies are secondary, with their eligible task counts.

This replaces the old proposal to use several cherry-pickable task subsets: the formal run uses the full test set, a fixed data selection seed and five new training seeds. Tau is fixed at 1; no test-set selection or automatic validation tuning occurs.

## E2 — Test the spectrum explanation

**Implemented, formal GPU results pending.** On seeds 43–45 add matched-blend, random-soft and isotropic-soft controls. They distinguish continuous eigenvalue gains, learned directions and a uniformly weaker intervention. Operator distance from identity is matched where declared; activation RMS and output KL are not automatically matched.

Compare the intervened generating policy and the distilled native model separately. Generation diagnostics use 128 fixed tasks × 32 samples, while main final-checkpoint evaluation uses 500 × 64. The smaller diagnostic does not establish the full benchmark result. SSD's generation decoder differs and must be treated separately.

The operator itself is a classical proximal map. A meaningful research contribution requires evidence that its particular use preserves correct implementation diversity, not just naming a new transform or avoiding activation hooks. The hard SPD arm is a reconstruction with declared completion-mask and insertion-point assumptions.

## E3 — Measure retention across cycles

**Implemented, formal GPU results pending.** Three seeds, plain / SPD-hard / Spectral-soft, three complete generate–LoRA cycles. Every cycle recomputes calibration and starts from that method's previous merged model. Save generation-policy and post-LoRA scores for each round.

Show accuracy and correct coverage curves. Interpret decay only with explicit task cohorts and shared eligibility; a changing eligible subset is not within-task evidence of collapse. Independent three-round directories intentionally repeat round 1 to preserve immutable provenance. Three rounds test that finite horizon, not indefinite protection.

## E4 — External correctness and transfer

**Implemented, official container execution pending.** Evaluate the base model and all four one-round confirmation checkpoints, for five seeds, on all 164 HumanEval+ tasks with 64 samples per task. Use official EvalPlus 0.3.1 extended checks in isolated Docker execution. No HumanEval+ data are used in calibration or SFT.

Treat this as a second benchmark and a new verifier protocol, not as another seed of MBPP. Full MBPP and MBPP+ contain different task sets; their scores cannot be substituted. LiveCodeBench is not part of this implemented formal suite.

## E5 — Check actual algorithm differences

**Independent annotation work remains.** AST differences and program uniqueness are structural proxies. Before claiming algorithm diversity, select a fixed evaluation subset prospectively, export programs, hide methods/seeds from annotators, apply a fixed algorithm rubric, use two independent annotators and adjudicate disagreements. Keep the sampling rule and eligible denominators visible.

The repository exports program artifacts and provides `annotate` / `metrics` interfaces. It does not supply fictitious ground-truth strategy labels. Annotations are evaluation-only and never filter training data, select calibration examples or route adapters.

## Evidence to retain and share

The runner writes aggregate Markdown/JSON, per-seed CSV, comparison CSV, per-task JSONL, configuration/data/model/code provenance and resource logs. `evidence/compact.tar.gz` omits weights and programs; optional program export supports independent verification and annotation. Keep incomplete phases pending rather than assigning zeros or reporting them as finished.

Resource reporting includes actual generated tokens, calibration cost, stage time and CUDA memory. Equal numbers of candidates and equal LoRA settings do not imply equal actual FLOPs. The entire configured suite is substantially larger than the pilot; phase budgets are in the formal protocol, and the default command runs E1 first.

## Decision rule

Continue toward an ICLR methods paper if the new full-benchmark evidence supports higher correct-implementation diversity under the frozen accuracy constraint, survives meaningful spectral controls and LoRA distillation, and is supported by a second benchmark and independent semantic checks. Do not require an accuracy improvement that is outside the paper's primary objective.

If the controls explain the effect by generic mild perturbation, narrow the mechanism claim. If only proxy metrics improve while independently labeled algorithm coverage does not, state that scope. If the primary confirmation fails, report the failure and reassess the method before expanding it with an adapter pool, prompts or heuristic filtering.
