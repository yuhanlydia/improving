# SPECTRUM — Paper Brief

**State:** submission-ready draft. Main text 8.911 pages counted (8.994 strict; limit 9.0), style
files byte-identical to the official ICLR 2027 archive, anonymity sweep clean, three independent
numeric audit passes closed plus a figure-geometry pass.
See `LONGGOAL.md` for the goal-by-goal verification record and `COMPLIANCE.md` for the compliance
note. The one declared deviation from the template default is documented there in §3.
**Operation:** `restructure` + `revise` (structure re-ordered to problem-first; prose and evidence alignment rewritten).
**Profile:** AI-conference mode (ICLR 2027, double-blind, submission stage).
**Language:** English manuscript; planning artifacts in the working language.

---

## 1. One-sentence thesis

> In **repeated raw-output self-distillation of a code LLM** (S), we address the fact that **the field's evaluation — single-sample correctness — is blind to the collapse of the set of correct implementations that distillation causes, and current recipes accelerate it** (P), with **SPECTRUM, a full-rank continuous proximal gain on correctness-gradient K/V directions used only during data generation** (I), producing **higher correctness-matched implementation coverage than plain self-distillation and than hard rank-truncated projection after five rounds, while staying closest to the undistilled model's coverage** (O), supported by **a five-round, 500-task, 64-sample MBPP experiment with paired task-bootstrap intervals on shared eligible tasks** (E).

## 2. Argumentative spine

| # | Link | Content | Evidence duty |
|---|---|---|---|
| 1 | Importance | Self-distillation on raw model outputs is a cheap, effective, widely adopted way to improve code models. | `zhang2026ssd` (SSD), `wang2023selfinstruct` |
| 2 | Gap | It is evaluated by correctness alone. Two models with identical pass@1 can expose completely different sets of correct implementations, and correctness statistics leave that distribution *unidentified*. | Exact distributional construction (§2 of manuscript) — no citation needed, it is arithmetic |
| 3 | Failure | Under repeated rounds the second property **erodes**, in every arm we tested — including the undistilled base as the reference level. The erosion is invisible in pass@k. | Five-round run, Figure 1 |
| 4 | Worse | The existing intervention on this axis — hard top-$r$ projection of correctness-gradient directions (SPD) — is the **worst** arm on coverage. Hard selection discards directions that a small reference set merely under-exercises. | Figure 1, Table 1, Table 2 |
| 5 | Response | Keep SPD's pipeline; replace zeroing with a continuous gain. A quadratic proximal map gives a closed-form, full-rank, bounded-contraction operator with no exact nullspace at finite strength. | §3, Proposition 1 |
| 6 | Evidence | Five rounds, 291 synthesis tasks, all 500 test tasks, 64 samples/task, paired task-bootstrap CIs on shared eligible tasks. | Tables 1–2, Figures 1, 3 |
| 7 | Implication | Report correctness-conditioned coverage alongside accuracy; intervention strength becomes a dial rather than a cutoff. | §5, §6 |

## 3. Intended reader and assumed knowledge

An ICLR reviewer who knows LoRA, pass@k estimation, and the SSD/SPD line of self-distillation. No prior knowledge of spectral methods assumed; the proximal map is introduced from the optimization problem, not by name.

## 4. Scope boundary — what this paper does NOT establish

- **Not** semantic algorithm diversity. AST fingerprints are implementation-*structure* proxies. Blinded algorithm annotation is designed but not performed.
- **Not** multi-seed. Everything reported is training seed 43 (pilot: 42). No seed-level uncertainty exists.
- **Not** multi-model. Qwen2.5-Coder-1.5B-Instruct only; the 3B configuration exists and is unrun.
- **Not** transfer. No HumanEval+/EvalPlus result. No second benchmark.
- **Not** a mechanism proof. Matched-blend / random-eigenvector / isotropic controls are implemented but unrun.
- **Not** a claim that accuracy improves relative to the strong comparators. It does not, by 1.18 pp against SPD-hard.
- **Not** execution in the official EvalPlus container. Verification used local execution.

## 5. Smallest coherent defensible contribution set

1. **A measurement claim.** Correctness and correctness-conditioned implementation coverage are different objectives; the second is unidentified by any pass@k and is not reported by current self-distillation work. (Supported by arithmetic + the measured disagreement in Table 1.)
2. **An empirical finding.** Repeated self-distillation reduces correctness-matched implementation coverage below the undistilled base in every arm tested; the hard-projection intervention reduces it most. (Supported by the five-round run.)
3. **A method.** A full-rank continuous spectral gain derived from correctness gradients, with a proximal interpretation, a local contraction bound, and exact temporary weight folding. (Supported by closed-form derivation + Proposition 1.)
4. **A measured effect.** Under a frozen protocol, the continuous gain retains more coverage than both plain self-distillation and hard projection after five rounds. (Supported by paired CIs.)

Contribution 4 is the one with a **known counter-evidence**: the accuracy side of the declared noninferiority criterion fails. This is handled in §6 and named in the main text once, plainly.

## 6. Handling of the adverse result (decision record)

The frozen protocol declares success as *both* a positive paired $\Delta D_4$ **and** a pass@1 difference whose interval lower bound is $\ge -0.01$ against **both** comparators. Measured against SPD-hard: $\Delta D_4 = +0.293\ [0.233, 0.353]$ (**met**) and $\Delta$pass@1 $= -0.0118\ [-0.0190, -0.0048]$ (**not met**).

Disposition, per the writing skill's rule that a materially adverse result stays visible:

- **Main text:** one plainly-worded sentence in the results, plus one sentence in the limitations. No hedging cascade, no rhetorical minimization, no relocation to the appendix.
- **Appendix:** the full per-comparison table and the protocol's original success criterion, for readers who want to check it.
- **Not permitted:** describing the accuracy change as a "trade-off" (only one direction of the trade-off was measured against the same comparator under the same conditions as the coverage gain — the other direction is the coverage gain itself, which is a different endpoint), or as "noninferior" (the interval excludes zero on the wrong side).

The reframing that makes this honest rather than fatal: **the relevant comparison for a practitioner is against the undistilled base, and there SPECTRUM is strictly better on accuracy (+2.25 pp [1.20, 3.35]) while losing the least coverage.** Against SPD-hard it buys coverage at a real accuracy cost. Both statements go in the abstract.

## 7. Terminology and notation to fix early

| Term | Fix |
|---|---|
| SPECTRUM | manuscript name; implementation id is `spectral_soft`; never mix in prose |
| SPD-hard | the reconstructed hard-projection baseline; "SPD" alone refers to the prior work |
| SSD | the raw-output self-distillation baseline; the arm's decoding recipe differs by design |
| `D_b^AST` | expected number of distinct AST classes in **b correct** draws |
| `coverage@k` | total correct-implementation coverage at a **k-sample** budget — a **different endpoint**; never on the same axis as `D_b` |
| eligible task | a task with $\ge b$ correct samples in **both** compared arms |
| base | the undistilled checkpoint; a *level*, drawn as a rule, never a categorical series |

## 8. Blocking gaps before submission

All three original gaps are now **resolved**:

1. ~~Per-round trajectories must be read from `metrics.csv` and reconciled with the two conflicting
   pass@1 deltas against SPD-hard.~~ **Resolved, and it was not a conflict.** `-0.01434` is the
   64-sample tier, `-0.01175` the 16-sample tier. Both are correct; both are now labelled by tier
   wherever they appear.
2. ~~Confirmation that `eval64/` and the run-level `metrics.csv` use the same extraction rule and
   eligible-task denominators.~~ **Resolved.** Both are exact count fractions
   (`correct_count / total_samples`), which equals the task-macro mean when all tasks carry equal
   sample counts. Verified: every 64-tier pass@1 × 32000 is an exact integer matching
   `correct_count`. The tiers differ only in sample budget (16 vs 64), never in estimator.
3. ~~Every claim touching "algorithm diversity" must stay at the *structural* level.~~
   **Held, and enforced.** `strategy_annotation_status` is empty in every record, so no
   algorithm-level claim appears anywhere; §2 and the Figure 1 caption say so explicitly.

**Remaining named gaps** (stated, not hidden — see `CLAIM_EVIDENCE.md` §5):

- The paired bootstrap was **not re-run**; the shipped bundle holds hashes only, no per-task jsonl.
  Intervals are reported as stored.
- Mechanism controls (matched blend / random eigenvectors / isotropic) are implemented but **unrun**.
- Single training seed (43): no seed-level uncertainty exists.
- Single model and single benchmark (Qwen2.5-Coder-1.5B-Instruct, MBPP). No transfer result.
