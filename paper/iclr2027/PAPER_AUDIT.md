# Evidence and writing decisions — 2026-09-20

## Central argument

Correctness determines how much probability reaches valid outputs; it does not
determine the distribution of implementations within those outputs. Repeated
self-distillation makes this distinction consequential because each student's
outputs supply the next synthetic corpus. The paper formalizes that loop and
uses SPECTRUM to improve the richness retained by the final native student.

The main contribution is the measured longitudinal question and its spectral
generation intervention. We do not claim the first iterative self-training
algorithm, the first recognition of solution diversity, or a semantic guarantee
from an invertible local operator.

## Claim-to-evidence map

| Claim | Evidence | Scope |
|---|---|---|
| Equal correctness can coexist with different correct-solution richness | Probability factorization and occupancy identities, Proposition 1 | Analytical statement under independent sampling; not a new empirical histogram |
| Accuracy can rise as richness contracts | Five-round MBPP trajectories and final evaluation | Completed seed 43, Qwen2.5-Coder-1.5B-Instruct |
| SPECTRUM retains more richness than Plain | Final C64 11.510 vs 8.506; retention 89.9% vs 66.4% | Same 500 tasks, 64 draws each |
| The gain is not explained solely by correct-sample count | Paired correct-conditioned richness at 4/8/16 correct draws | Common eligible tasks per contrast; not a token-length matched study |
| Larger budgets reveal retained breadth | Recorded budget points from the final 64-draw pool | No extrapolated pass@32 point in the historical figure |
| The learned student retains a benefit | All reported endpoints evaluate native students after restoring generation weights | No intervention needed in final inference |
| The proximal operator has positive bounded gains | Closed-form solution and appendix proofs | Local linear map, not preservation of semantic classes through the whole network |
| Random/isotropic/fixed geometry clarify the mechanism | Runnable controls and pending tables | Unmeasured: `x`, no positive result asserted |
| Robustness across seeds, scale and benchmarks | Extension matrices and runnable suite | Unmeasured except explicitly identified historical MBPP cells |

## Data provenance

The source is `results/retention_5round_train16_eval16_seed43/` in the repository.
Its `report.json` contains the 16-sample round summaries and available paired
contrasts. `eval64/metrics_compact.json` and the final comparison files supply
the final evaluation. The figure package includes the exact compact JSONs it
uses. Original generation/configuration/resource summaries supply token counts.

These results are not pooled with the earlier seed-42 64-task pilot or the
ten-round smoke run. Task bootstrap intervals express evaluation-task
uncertainty, not uncertainty over independent training seeds. Missing historic
task-level records or pruned checkpoints cannot be recovered from compact
means, and the continuation tools do not fabricate them.

## Terminology and methodological choices

- **Correct AST richness @k** is the expected number of distinct verified AST
  classes under a total sample budget. **Correct-conditioned AST richness @b**
  fixes the number of correct draws. C_k and D_b are symbols for these defined
  quantities, not proposed community-standard metric names.
- Richness retention compares class counts; it does not track identity overlap
  with the original model's classes. AST equivalence is an implementation
  proxy, not a claim of distinct algorithms.
- The completed pipeline trains on raw generated outputs, not only correct
  outputs. Calibration uses a fixed completion-masked reference loss. SFT uses
  the recorded full nonpadding-token loss.
- Rank truncation is a simple operator replacement in the ablation table.
  The loss-sensitive K/V calibration predecessor still receives proper credit.
- UA-RL is an adapted RL comparison with semantic strategy judging. It is not
  renamed self-distillation. Its public repository did not contain a training
  implementation at the reviewed revision, so the new implementation and its
  adaptations are documented separately.
- Five-round candidate counts match, but SPECTRUM generated 9.9% more tokens
  than Plain. Wall time and peak memory missing from the original archive stay
  `x`; the new suite records them explicitly.

## Literature positioning

STaR, ReST, ReST-EM and SD-Zero already establish iterative generation and
learning. UA-RL and program-diversity studies motivate diversity beyond
correctness. Recursive model-collapse studies and data-accumulation results
concern broader recursive-data distributions and should not be presented as
already answering conditional correct-implementation retention. Looped
Transformers repeat computation inside inference; our loop updates parameters
using synthetic corpora between rounds.

The present framing defines an explicit modular experimental regime and a
particular method inside it. It avoids claiming ownership of all recursive
self-improvement or all diversity evaluation.

## Required completion cells

Main: common-protocol SSD and adapted UA-RL. Confirmation: independent seeds
42/43/44 with every round evaluated at 64 samples. Mechanism: random spectrum,
isotropic displacement, fixed geometry and tau sensitivity; matched blend is
optional. Scope: HumanEval+, APPS Intro, CodeContests, LiveCodeBench, Qwen3B,
Qwen7B and DeepSeek6.7B. Resources: stage time/memory and UA-RL judge costs.

The transfer benchmarks use frozen MBPP-trained students. Adapted stdin/stdout
benchmarks are labeled as such and do not claim official leaderboard scores.
Mathematics motivates the general question but has no claimed experimental
result in this version.

## Artifact checks

The manuscript uses the official ICLR 2027 anonymous template. All material is
in one main.tex, with references followed by appendices. The PDF was compiled
and visually inspected. Code changes received static inspection and CLI/syntax
checks only; no new GPU experiment or training run was executed in this update.
