# Publication tables: committed measurements and pending experiments

`x` means not measured in the committed experiment snapshot. Fill it only from
the exported artifacts of a completed run. Do not infer it from another budget,
round, seed, model, or evaluator. Historical values below are the five-round
seed-43 MBPP experiment; SSD and UA-RL require new runs.

## Main comparison: fifth-round MBPP, 500 tasks × 64 candidates

| Metric | Initial model | Plain | SSD | UA-RL (adapted) | SPECTRUM |
|---|---:|---:|---:|---:|---:|
| pass@1 (%) | 37.94 | 41.45 | x | x | 40.33 |
| pass@8 (%) | 61.10 | 61.86 | x | x | 61.89 |
| pass@16 (%) | 65.69 | 65.64 | x | x | 66.23 |
| pass@64 (%) | 72.00 | 70.40 | x | x | 72.60 |
| Correct AST richness @64 | 12.802 | 8.506 | x | x | 11.510 |
| AST richness retention relative to initial (%) | 100.0 | 66.4 | x | x | 89.9 |
| Correct-conditioned AST richness @4 | 3.358 | 2.856 | x | x | 3.143 |
| Eligible tasks for the matched metric | 322 | 321 | x | x | 323 |
| Solved tasks / 500 | 360 | 352 | x | x | 363 |

The marginal correct-conditioned richness means use each arm's eligible tasks. Paired
contrasts instead use the intersection of eligible tasks; these are different
estimands and need their own sample count and task-bootstrap interval.

## Design ablations (fifth round; historical values where present)

| Design | pass@1 (%) | pass@64 (%) | Correct AST richness @64 | Correct-conditioned AST richness @4 | Paired richness change vs SPECTRUM |
|---|---:|---:|---:|---:|---:|
| SPECTRUM | 40.33 | 72.60 | 11.510 | 3.143 | — |
| Projection | 41.77 | 70.20 | 8.388 | 2.810 | x |
| Random eigenbasis, identical gains | x | x | x | x | x |
| Isotropic gain, matched displacement | x | x | x | x | x |
| Fixed first-round geometry | x | x | x | x | x |
| Matched residual blend (optional) | x | x | x | x | x |

The projection row is an internal design comparison. Newly run controls should
use the same configuration, seed and verifier as the SPECTRUM row they compare.

## Strength sensitivity (appendix)

| tau | pass@1 | pass@64 | Correct AST richness @64 | Correct-conditioned AST richness @4 | Generated tokens |
|---:|---:|---:|---:|---:|---:|
| 0.25 | x | x | x | x | x |
| 0.5 | x | x | x | x | x |
| 1 | x | x | x | x | x |
| 2 | x | x | x | x | x |
| 4 | x | x | x | x | x |

Fill this entire table from the new mechanism manifest, including its tau=1
reference, to preserve a common protocol. Do not select the headline strength
using this test-set table.

## Resources and synthetic sample lengths

| Method | Raw training candidates (five rounds) | Generated training tokens | Mean / median / p95 tokens | Generation hours | Calibration hours | Student-training hours | Evaluation hours | Peak allocated GPU GB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Plain | 23,280 | 4,859,928 | x | x | x | x | x | x |
| SSD | x | x | x | x | x | x | x | x |
| UA-RL (adapted) | x | x | x | x | x | x | x | x |
| SPECTRUM | 23,280 | 5,342,368 | x | x | x | x | x | x |
| Projection design | 23,280 | 4,727,089 | x | x | x | x | x | x |

Historical token totals are recorded five-round seed-43 generation totals.
Raw candidates equal 291 × 16 × 5, including incorrect/duplicate samples.
Obtain length quantiles from raw generated records; no quantile is derivable
from the total alone. Peak GPU allocation is the maximum over stages, not a sum.

## Benchmark transfer (all students trained on MBPP)

| Evaluation set | Verifier/protocol | Initial | Plain | SSD | UA-RL (adapted) | SPECTRUM |
|---|---|---:|---:|---:|---:|---:|
| MBPP (500) | Recorded native Python tests | 12.802 | 8.506 | x | x | 11.510 |
| HumanEval+ (164) | Official EvalPlus 0.3.1, base + plus | x | x | x | x | x |
| APPS introductory (up to 200) | Recorded function / stdin adapter | x | x | x | x | x |
| CodeContests (up to 200) | Recorded stdin adapter | x | x | x | x | x |
| LiveCodeBench (up to 200) | Pinned release and recorded adapter | x | x | x | x | x |

Endpoint shown: mean distinct correct AST classes at 64 candidates. Accompany
with pass@1, pass@64, correct-conditioned AST richness and eligibility in a
separate panel or appendix table. Report actual prepared task counts and release
identities, not only the requested maximum. This is transfer, not target training.

## Model-size and architecture replication (MBPP)

| Backbone | Parameters | Method | pass@1 | pass@64 | Correct AST richness @64 | Richness retention | Correct-conditioned AST richness @4 |
|---|---:|---|---:|---:|---:|---:|---:|
| Qwen2.5-Coder-Instruct | 1.5B | Plain / SSD / SPECTRUM | x | x | x | x | x |
| Qwen2.5-Coder-Instruct | 3B | Plain / SSD / SPECTRUM | x | x | x | x | x |
| Qwen2.5-Coder-Instruct | 7B | Plain / SSD / SPECTRUM | x | x | x | x | x |
| DeepSeek-Coder-Instruct | 6.7B | Plain / SSD / SPECTRUM | x | x | x | x | x |

Expand each model into separate method rows when results arrive. The 1.5B row
here means the new common-protocol replication, not an average invented from
the existing single-seed result.
