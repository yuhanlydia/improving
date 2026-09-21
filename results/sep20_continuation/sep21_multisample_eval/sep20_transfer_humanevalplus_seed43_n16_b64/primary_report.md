# Coding self-distillation report

Result status: **pending**.

Numbers show task means with pointwise 95% task-bootstrap intervals and explicit eligible-task denominators. Partial means describe the eligible subset; they do not establish gains across all tasks. Pending measurements are not zeros.

## Correctness and evaluation stages

| Method | Round | Stage | Status | Pass@16 | Pass@64 | Samples |
| --- | ---: | --- | --- | --- | --- | ---: |
| base | 0 | evaluation | available | 0.854 [0.799, 0.902]; 164/164 tasks, full | pending | 2624 |
| plain | 1 | generation_policy | not_requested | pending | pending | pending |
| plain | 1 | evaluation | pending_metrics | pending | pending | pending |
| plain | 2 | generation_policy | not_requested | pending | pending | pending |
| plain | 2 | evaluation | pending_metrics | pending | pending | pending |
| plain | 3 | generation_policy | not_requested | pending | pending | pending |
| plain | 3 | evaluation | pending_metrics | pending | pending | pending |
| plain | 4 | generation_policy | not_requested | pending | pending | pending |
| plain | 4 | evaluation | pending_metrics | pending | pending | pending |
| plain | 5 | generation_policy | not_requested | pending | pending | pending |
| plain | 5 | evaluation | available | 0.866 [0.811, 0.915]; 164/164 tasks, full | pending | 2624 |
| spd_hard | 1 | generation_policy | not_requested | pending | pending | pending |
| spd_hard | 1 | evaluation | pending_metrics | pending | pending | pending |
| spd_hard | 2 | generation_policy | not_requested | pending | pending | pending |
| spd_hard | 2 | evaluation | pending_metrics | pending | pending | pending |
| spd_hard | 3 | generation_policy | not_requested | pending | pending | pending |
| spd_hard | 3 | evaluation | pending_metrics | pending | pending | pending |
| spd_hard | 4 | generation_policy | not_requested | pending | pending | pending |
| spd_hard | 4 | evaluation | pending_metrics | pending | pending | pending |
| spd_hard | 5 | generation_policy | not_requested | pending | pending | pending |
| spd_hard | 5 | evaluation | available | 0.848 [0.793, 0.896]; 164/164 tasks, full | pending | 2624 |
| spectral_soft | 1 | generation_policy | not_requested | pending | pending | pending |
| spectral_soft | 1 | evaluation | pending_metrics | pending | pending | pending |
| spectral_soft | 2 | generation_policy | not_requested | pending | pending | pending |
| spectral_soft | 2 | evaluation | pending_metrics | pending | pending | pending |
| spectral_soft | 3 | generation_policy | not_requested | pending | pending | pending |
| spectral_soft | 3 | evaluation | pending_metrics | pending | pending | pending |
| spectral_soft | 4 | generation_policy | not_requested | pending | pending | pending |
| spectral_soft | 4 | evaluation | pending_metrics | pending | pending | pending |
| spectral_soft | 5 | generation_policy | not_requested | pending | pending | pending |
| spectral_soft | 5 | evaluation | available | 0.866 [0.811, 0.915]; 164/164 tasks, full | pending | 2624 |

## Correct implementation richness and annotated strategy coverage

Implementation coverage uses conservative Python AST fingerprints. These are implementation proxies, not algorithm identities. Strategy coverage uses supplied independent labels only; incomplete annotations remain unavailable. Wrong completions remain in the draw population.

| Stage | Draw budget K | Correct AST richness @K | Annotated strategy coverage |
| --- | ---: | --- | --- |
| base/evaluation | 16 | 5.768 [5.152, 6.439]; 164/164 tasks, full | 0.000 [0.000, 0.000]; 24/164 tasks, partial |
| base/evaluation | 64 | pending | pending |
| plain/round_1/generation_policy | 16 | pending | pending |
| plain/round_1/generation_policy | 64 | pending | pending |
| plain/round_1/evaluation | 16 | pending | pending |
| plain/round_1/evaluation | 64 | pending | pending |
| plain/round_2/generation_policy | 16 | pending | pending |
| plain/round_2/generation_policy | 64 | pending | pending |
| plain/round_2/evaluation | 16 | pending | pending |
| plain/round_2/evaluation | 64 | pending | pending |
| plain/round_3/generation_policy | 16 | pending | pending |
| plain/round_3/generation_policy | 64 | pending | pending |
| plain/round_3/evaluation | 16 | pending | pending |
| plain/round_3/evaluation | 64 | pending | pending |
| plain/round_4/generation_policy | 16 | pending | pending |
| plain/round_4/generation_policy | 64 | pending | pending |
| plain/round_4/evaluation | 16 | pending | pending |
| plain/round_4/evaluation | 64 | pending | pending |
| plain/round_5/generation_policy | 16 | pending | pending |
| plain/round_5/generation_policy | 64 | pending | pending |
| plain/round_5/evaluation | 16 | 5.848 [5.207, 6.482]; 164/164 tasks, full | 0.000 [0.000, 0.000]; 22/164 tasks, partial |
| plain/round_5/evaluation | 64 | pending | pending |
| spd_hard/round_1/generation_policy | 16 | pending | pending |
| spd_hard/round_1/generation_policy | 64 | pending | pending |
| spd_hard/round_1/evaluation | 16 | pending | pending |
| spd_hard/round_1/evaluation | 64 | pending | pending |
| spd_hard/round_2/generation_policy | 16 | pending | pending |
| spd_hard/round_2/generation_policy | 64 | pending | pending |
| spd_hard/round_2/evaluation | 16 | pending | pending |
| spd_hard/round_2/evaluation | 64 | pending | pending |
| spd_hard/round_3/generation_policy | 16 | pending | pending |
| spd_hard/round_3/generation_policy | 64 | pending | pending |
| spd_hard/round_3/evaluation | 16 | pending | pending |
| spd_hard/round_3/evaluation | 64 | pending | pending |
| spd_hard/round_4/generation_policy | 16 | pending | pending |
| spd_hard/round_4/generation_policy | 64 | pending | pending |
| spd_hard/round_4/evaluation | 16 | pending | pending |
| spd_hard/round_4/evaluation | 64 | pending | pending |
| spd_hard/round_5/generation_policy | 16 | pending | pending |
| spd_hard/round_5/generation_policy | 64 | pending | pending |
| spd_hard/round_5/evaluation | 16 | 5.921 [5.287, 6.573]; 164/164 tasks, full | 0.000 [0.000, 0.000]; 25/164 tasks, partial |
| spd_hard/round_5/evaluation | 64 | pending | pending |
| spectral_soft/round_1/generation_policy | 16 | pending | pending |
| spectral_soft/round_1/generation_policy | 64 | pending | pending |
| spectral_soft/round_1/evaluation | 16 | pending | pending |
| spectral_soft/round_1/evaluation | 64 | pending | pending |
| spectral_soft/round_2/generation_policy | 16 | pending | pending |
| spectral_soft/round_2/generation_policy | 64 | pending | pending |
| spectral_soft/round_2/evaluation | 16 | pending | pending |
| spectral_soft/round_2/evaluation | 64 | pending | pending |
| spectral_soft/round_3/generation_policy | 16 | pending | pending |
| spectral_soft/round_3/generation_policy | 64 | pending | pending |
| spectral_soft/round_3/evaluation | 16 | pending | pending |
| spectral_soft/round_3/evaluation | 64 | pending | pending |
| spectral_soft/round_4/generation_policy | 16 | pending | pending |
| spectral_soft/round_4/generation_policy | 64 | pending | pending |
| spectral_soft/round_4/evaluation | 16 | pending | pending |
| spectral_soft/round_4/evaluation | 64 | pending | pending |
| spectral_soft/round_5/generation_policy | 16 | pending | pending |
| spectral_soft/round_5/generation_policy | 64 | pending | pending |
| spectral_soft/round_5/evaluation | 16 | 6.000 [5.348, 6.665]; 164/164 tasks, full | 0.000 [0.000, 0.000]; 22/164 tasks, partial |
| spectral_soft/round_5/evaluation | 64 | pending | pending |

## Coverage at a fixed correct-sample budget

These conditional estimates use only correct samples and require at least the displayed number of correct samples per task. Different eligible-task populations must not be interpreted as whole-task improvements.

| Stage | Correct-sample budget b | Correct-conditioned AST richness @b | Annotated strategy coverage |
| --- | ---: | --- | --- |
| base/evaluation | 4 | 3.410 [3.280, 3.537]; 116/164 tasks, partial | unavailable (0/164 tasks) |
| base/evaluation | 8 | 5.840 [5.441, 6.250]; 88/164 tasks, partial | unavailable (0/164 tasks) |
| base/evaluation | 16 | 8.080 [6.308, 9.840]; 25/164 tasks, partial | unavailable (0/164 tasks) |
| plain/round_1/generation_policy | pending | pending | pending |
| plain/round_1/evaluation | pending | pending | pending |
| plain/round_2/generation_policy | pending | pending | pending |
| plain/round_2/evaluation | pending | pending | pending |
| plain/round_3/generation_policy | pending | pending | pending |
| plain/round_3/evaluation | pending | pending | pending |
| plain/round_4/generation_policy | pending | pending | pending |
| plain/round_4/evaluation | pending | pending | pending |
| plain/round_5/generation_policy | pending | pending | pending |
| plain/round_5/evaluation | 4 | 3.422 [3.300, 3.533]; 120/164 tasks, partial | unavailable (0/164 tasks) |
| plain/round_5/evaluation | 8 | 5.968 [5.599, 6.316]; 93/164 tasks, partial | unavailable (0/164 tasks) |
| plain/round_5/evaluation | 16 | 8.368 [6.588, 10.191]; 19/164 tasks, partial | unavailable (0/164 tasks) |
| spd_hard/round_1/generation_policy | pending | pending | pending |
| spd_hard/round_1/evaluation | pending | pending | pending |
| spd_hard/round_2/generation_policy | pending | pending | pending |
| spd_hard/round_2/evaluation | pending | pending | pending |
| spd_hard/round_3/generation_policy | pending | pending | pending |
| spd_hard/round_3/evaluation | pending | pending | pending |
| spd_hard/round_4/generation_policy | pending | pending | pending |
| spd_hard/round_4/evaluation | pending | pending | pending |
| spd_hard/round_5/generation_policy | pending | pending | pending |
| spd_hard/round_5/evaluation | 4 | 3.473 [3.358, 3.587]; 115/164 tasks, partial | unavailable (0/164 tasks) |
| spd_hard/round_5/evaluation | 8 | 6.027 [5.668, 6.373]; 93/164 tasks, partial | unavailable (0/164 tasks) |
| spd_hard/round_5/evaluation | 16 | 8.682 [6.920, 10.579]; 22/164 tasks, partial | unavailable (0/164 tasks) |
| spectral_soft/round_1/generation_policy | pending | pending | pending |
| spectral_soft/round_1/evaluation | pending | pending | pending |
| spectral_soft/round_2/generation_policy | pending | pending | pending |
| spectral_soft/round_2/evaluation | pending | pending | pending |
| spectral_soft/round_3/generation_policy | pending | pending | pending |
| spectral_soft/round_3/evaluation | pending | pending | pending |
| spectral_soft/round_4/generation_policy | pending | pending | pending |
| spectral_soft/round_4/evaluation | pending | pending | pending |
| spectral_soft/round_5/generation_policy | pending | pending | pending |
| spectral_soft/round_5/evaluation | 4 | 3.497 [3.386, 3.602]; 114/164 tasks, partial | unavailable (0/164 tasks) |
| spectral_soft/round_5/evaluation | 8 | 6.139 [5.773, 6.476]; 89/164 tasks, partial | unavailable (0/164 tasks) |
| spectral_soft/round_5/evaluation | 16 | 8.667 [6.889, 10.647]; 18/164 tasks, partial | unavailable (0/164 tasks) |

## Paired comparisons

Deltas are candidate minus reference at draw budgets 16 and 64. Missing budgets remain pending. These descriptive estimates do not establish algorithm diversity or an automatic research conclusion.

| Candidate | Reference | Status | ΔPass@16 | ΔPass@64 | Reason |
| --- | --- | --- | --- | --- | --- |
| plain/round_1/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| plain/round_1/evaluation | spd_hard/round_1/evaluation | pending | pending | pending | candidate metrics are pending |
| plain/round_2/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| plain/round_2/evaluation | spd_hard/round_2/evaluation | pending | pending | pending | candidate metrics are pending |
| plain/round_3/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| plain/round_3/evaluation | spd_hard/round_3/evaluation | pending | pending | pending | candidate metrics are pending |
| plain/round_4/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| plain/round_4/evaluation | spd_hard/round_4/evaluation | pending | pending | pending | candidate metrics are pending |
| plain/round_5/evaluation | base/evaluation | available | 0.012 [-0.030, 0.055]; 164/164 tasks, paired | pending | — |
| plain/round_5/evaluation | spd_hard/round_5/evaluation | available | 0.018 [-0.006, 0.049]; 164/164 tasks, paired | pending | — |
| spd_hard/round_1/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_1/evaluation | plain/round_1/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_2/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_2/evaluation | plain/round_2/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_3/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_3/evaluation | plain/round_3/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_4/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_4/evaluation | plain/round_4/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_5/evaluation | base/evaluation | available | -0.006 [-0.049, 0.030]; 164/164 tasks, paired | pending | — |
| spd_hard/round_5/evaluation | plain/round_5/evaluation | available | -0.018 [-0.049, 0.006]; 164/164 tasks, paired | pending | — |
| spectral_soft/round_1/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_1/evaluation | plain/round_1/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_1/evaluation | spd_hard/round_1/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_2/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_2/evaluation | plain/round_2/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_2/evaluation | spd_hard/round_2/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_3/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_3/evaluation | plain/round_3/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_3/evaluation | spd_hard/round_3/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_4/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_4/evaluation | plain/round_4/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_4/evaluation | spd_hard/round_4/evaluation | pending | pending | pending | candidate metrics are pending |
| spectral_soft/round_5/evaluation | base/evaluation | available | 0.012 [-0.018, 0.049]; 164/164 tasks, paired | pending | — |
| spectral_soft/round_5/evaluation | plain/round_5/evaluation | available | 0.000 [-0.030, 0.030]; 164/164 tasks, paired | pending | — |
| spectral_soft/round_5/evaluation | spd_hard/round_5/evaluation | available | 0.018 [-0.012, 0.049]; 164/164 tasks, paired | pending | — |

Coverage and entropy deltas, including their intervals and paired eligibility, are included in the JSON report. Comparisons require matching explicit sampling and evaluation protocols, task IDs, metric budgets, and per-task sample counts.

## Budgets and training

| Stage | Generated samples | Generation tokens | Prompt tokens |
| --- | ---: | ---: | ---: |
| base/evaluation | 2624 | 1031104 | 425664 |
| plain/round_1/generation_policy | unavailable | unavailable | unavailable |
| plain/round_1/evaluation | unavailable | unavailable | unavailable |
| plain/round_2/generation_policy | unavailable | unavailable | unavailable |
| plain/round_2/evaluation | unavailable | unavailable | unavailable |
| plain/round_3/generation_policy | unavailable | unavailable | unavailable |
| plain/round_3/evaluation | unavailable | unavailable | unavailable |
| plain/round_4/generation_policy | unavailable | unavailable | unavailable |
| plain/round_4/evaluation | unavailable | unavailable | unavailable |
| plain/round_5/generation_policy | unavailable | unavailable | unavailable |
| plain/round_5/evaluation | 2624 | 1152774 | 425664 |
| spd_hard/round_1/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_1/evaluation | unavailable | unavailable | unavailable |
| spd_hard/round_2/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_2/evaluation | unavailable | unavailable | unavailable |
| spd_hard/round_3/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_3/evaluation | unavailable | unavailable | unavailable |
| spd_hard/round_4/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_4/evaluation | unavailable | unavailable | unavailable |
| spd_hard/round_5/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_5/evaluation | 2624 | 1138798 | 425664 |
| spectral_soft/round_1/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_1/evaluation | unavailable | unavailable | unavailable |
| spectral_soft/round_2/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_2/evaluation | unavailable | unavailable | unavailable |
| spectral_soft/round_3/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_3/evaluation | unavailable | unavailable | unavailable |
| spectral_soft/round_4/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_4/evaluation | unavailable | unavailable | unavailable |
| spectral_soft/round_5/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_5/evaluation | 2624 | 1155318 | 425664 |

**plain/round_1**

Training statistics: unavailable

Training generation budget: unavailable

**plain/round_2**

Training statistics: unavailable

Training generation budget: unavailable

**plain/round_3**

Training statistics: unavailable

Training generation budget: unavailable

**plain/round_4**

Training statistics: unavailable

Training generation budget: unavailable

**plain/round_5**

Training statistics: unavailable

Training generation budget: unavailable

**spd_hard/round_1**

Training statistics: unavailable

Training generation budget: unavailable

**spd_hard/round_2**

Training statistics: unavailable

Training generation budget: unavailable

**spd_hard/round_3**

Training statistics: unavailable

Training generation budget: unavailable

**spd_hard/round_4**

Training statistics: unavailable

Training generation budget: unavailable

**spd_hard/round_5**

Training statistics: unavailable

Training generation budget: unavailable

**spectral_soft/round_1**

Training statistics: unavailable

Training generation budget: unavailable

**spectral_soft/round_2**

Training statistics: unavailable

Training generation budget: unavailable

**spectral_soft/round_3**

Training statistics: unavailable

Training generation budget: unavailable

**spectral_soft/round_4**

Training statistics: unavailable

Training generation budget: unavailable

**spectral_soft/round_5**

Training statistics: unavailable

Training generation budget: unavailable

## Wall time and memory

Elapsed time includes recorded attempts. CUDA peaks are recorded per stage; stage peaks must not be added as if they occurred simultaneously. Unrecorded costs remain unavailable.

| Run stage | Operation | Elapsed seconds | Peak allocated bytes | Peak reserved bytes |
| --- | --- | ---: | ---: | ---: |
| base/round_0 | evaluation_generation | 2643.9403774100356 | 6229723136 | 11836325888 |
| base/round_0 | model_loading | 4.979612536961213 | 3088346624 | 3286237184 |
| base/round_0 | verification_and_metrics | 183.5081168799661 | 3096866304 | 11836325888 |
| plain/round_5 | evaluation_generation | 2626.496298920014 | 6272896512 | 14015266816 |
| plain/round_5 | model_loading | 1.3205553039442748 | 3097629184 | 3307208704 |
| plain/round_5 | verification_and_metrics | 165.3004659949802 | 3097629184 | 14015266816 |
| spd_hard/round_5 | evaluation_generation | 2736.512540473952 | 6431325184 | 11454644224 |
| spd_hard/round_5 | model_loading | 2.457188030006364 | 3097629184 | 3307208704 |
| spd_hard/round_5 | verification_and_metrics | 145.26516672910657 | 3097629184 | 11454644224 |
| spectral_soft/round_5 | evaluation_generation | 2601.732270266046 | 6052150784 | 11563696128 |
| spectral_soft/round_5 | model_loading | 2.2999666759278625 | 3097629184 | 3307208704 |
| spectral_soft/round_5 | verification_and_metrics | 225.32990736002102 | 3097629184 | 11563696128 |

## Appendix: Pass@1 and correctness noninferiority

Pass@1 and the original correctness criterion are retained as supplementary diagnostics. They do not determine the main Pass@16/Pass@64 and diversity conclusions.

| Stage | Pass@1 |
| --- | --- |
| base/evaluation | 0.531 [0.477, 0.587]; 164/164 tasks, full |
| plain/round_1/generation_policy | pending |
| plain/round_1/evaluation | pending |
| plain/round_2/generation_policy | pending |
| plain/round_2/evaluation | pending |
| plain/round_3/generation_policy | pending |
| plain/round_3/evaluation | pending |
| plain/round_4/generation_policy | pending |
| plain/round_4/evaluation | pending |
| plain/round_5/generation_policy | pending |
| plain/round_5/evaluation | 0.535 [0.481, 0.588]; 164/164 tasks, full |
| spd_hard/round_1/generation_policy | pending |
| spd_hard/round_1/evaluation | pending |
| spd_hard/round_2/generation_policy | pending |
| spd_hard/round_2/evaluation | pending |
| spd_hard/round_3/generation_policy | pending |
| spd_hard/round_3/evaluation | pending |
| spd_hard/round_4/generation_policy | pending |
| spd_hard/round_4/evaluation | pending |
| spd_hard/round_5/generation_policy | pending |
| spd_hard/round_5/evaluation | 0.527 [0.473, 0.582]; 164/164 tasks, full |
| spectral_soft/round_1/generation_policy | pending |
| spectral_soft/round_1/evaluation | pending |
| spectral_soft/round_2/generation_policy | pending |
| spectral_soft/round_2/evaluation | pending |
| spectral_soft/round_3/generation_policy | pending |
| spectral_soft/round_3/evaluation | pending |
| spectral_soft/round_4/generation_policy | pending |
| spectral_soft/round_4/evaluation | pending |
| spectral_soft/round_5/generation_policy | pending |
| spectral_soft/round_5/evaluation | 0.519 [0.467, 0.573]; 164/164 tasks, full |

Correctness noninferiority uses the task-macro correct fraction (Pass@1), an absolute margin of 0.010, and the lower endpoint of a two-sided 95% paired task-bootstrap interval. It requires all tasks.

| Candidate | Reference | Status | Pass@1 delta | Noninferiority | Reason |
| --- | --- | --- | --- | --- | --- |
| plain/round_1/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| plain/round_1/evaluation | spd_hard/round_1/evaluation | pending | pending | unavailable | candidate metrics are pending |
| plain/round_2/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| plain/round_2/evaluation | spd_hard/round_2/evaluation | pending | pending | unavailable | candidate metrics are pending |
| plain/round_3/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| plain/round_3/evaluation | spd_hard/round_3/evaluation | pending | pending | unavailable | candidate metrics are pending |
| plain/round_4/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| plain/round_4/evaluation | spd_hard/round_4/evaluation | pending | pending | unavailable | candidate metrics are pending |
| plain/round_5/evaluation | base/evaluation | available | 0.004 [-0.018, 0.026]; 164/164 tasks, paired | criterion not met | — |
| plain/round_5/evaluation | spd_hard/round_5/evaluation | available | 0.007 [-0.006, 0.020]; 164/164 tasks, paired | criterion met | — |
| spd_hard/round_1/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_1/evaluation | plain/round_1/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_2/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_2/evaluation | plain/round_2/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_3/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_3/evaluation | plain/round_3/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_4/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_4/evaluation | plain/round_4/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_5/evaluation | base/evaluation | available | -0.003 [-0.025, 0.017]; 164/164 tasks, paired | criterion not met | — |
| spd_hard/round_5/evaluation | plain/round_5/evaluation | available | -0.007 [-0.020, 0.006]; 164/164 tasks, paired | criterion not met | — |
| spectral_soft/round_1/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_1/evaluation | plain/round_1/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_1/evaluation | spd_hard/round_1/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_2/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_2/evaluation | plain/round_2/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_2/evaluation | spd_hard/round_2/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_3/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_3/evaluation | plain/round_3/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_3/evaluation | spd_hard/round_3/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_4/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_4/evaluation | plain/round_4/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_4/evaluation | spd_hard/round_4/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spectral_soft/round_5/evaluation | base/evaluation | available | -0.011 [-0.033, 0.011]; 164/164 tasks, paired | criterion not met | — |
| spectral_soft/round_5/evaluation | plain/round_5/evaluation | available | -0.015 [-0.031, 0.001]; 164/164 tasks, paired | criterion not met | — |
| spectral_soft/round_5/evaluation | spd_hard/round_5/evaluation | available | -0.008 [-0.024, 0.008]; 164/164 tasks, paired | criterion not met | — |

The JSON report preserves all metric budgets, Pass@1 and correctness comparisons, generation budgets, training statistics, full sampling metadata, evaluation provenance, and eligibility details. Sampling budget and correctness can change observed diversity; no model-performance claim follows from a report being complete.
