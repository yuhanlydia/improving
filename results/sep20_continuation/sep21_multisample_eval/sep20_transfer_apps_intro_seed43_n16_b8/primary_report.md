# Coding self-distillation report

Result status: **pending**.

Numbers show task means with pointwise 95% task-bootstrap intervals and explicit eligible-task denominators. Partial means describe the eligible subset; they do not establish gains across all tasks. Pending measurements are not zeros.

## Correctness and evaluation stages

| Method | Round | Stage | Status | Pass@16 | Pass@64 | Samples |
| --- | ---: | --- | --- | --- | --- | ---: |
| base | 0 | evaluation | available | 0.415 [0.345, 0.485]; 200/200 tasks, full | pending | 3200 |
| plain | 1 | generation_policy | not_requested | pending | pending | pending |
| plain | 1 | evaluation | pending_metrics | pending | pending | pending |
| plain | 2 | generation_policy | not_requested | pending | pending | pending |
| plain | 2 | evaluation | pending_metrics | pending | pending | pending |
| plain | 3 | generation_policy | not_requested | pending | pending | pending |
| plain | 3 | evaluation | pending_metrics | pending | pending | pending |
| plain | 4 | generation_policy | not_requested | pending | pending | pending |
| plain | 4 | evaluation | pending_metrics | pending | pending | pending |
| plain | 5 | generation_policy | not_requested | pending | pending | pending |
| plain | 5 | evaluation | available | 0.355 [0.290, 0.425]; 200/200 tasks, full | pending | 3200 |
| spd_hard | 1 | generation_policy | not_requested | pending | pending | pending |
| spd_hard | 1 | evaluation | pending_metrics | pending | pending | pending |
| spd_hard | 2 | generation_policy | not_requested | pending | pending | pending |
| spd_hard | 2 | evaluation | pending_metrics | pending | pending | pending |
| spd_hard | 3 | generation_policy | not_requested | pending | pending | pending |
| spd_hard | 3 | evaluation | pending_metrics | pending | pending | pending |
| spd_hard | 4 | generation_policy | not_requested | pending | pending | pending |
| spd_hard | 4 | evaluation | pending_metrics | pending | pending | pending |
| spd_hard | 5 | generation_policy | not_requested | pending | pending | pending |
| spd_hard | 5 | evaluation | available | 0.345 [0.280, 0.410]; 200/200 tasks, full | pending | 3200 |
| spectral_soft | 1 | generation_policy | not_requested | pending | pending | pending |
| spectral_soft | 1 | evaluation | pending_metrics | pending | pending | pending |
| spectral_soft | 2 | generation_policy | not_requested | pending | pending | pending |
| spectral_soft | 2 | evaluation | pending_metrics | pending | pending | pending |
| spectral_soft | 3 | generation_policy | not_requested | pending | pending | pending |
| spectral_soft | 3 | evaluation | pending_metrics | pending | pending | pending |
| spectral_soft | 4 | generation_policy | not_requested | pending | pending | pending |
| spectral_soft | 4 | evaluation | pending_metrics | pending | pending | pending |
| spectral_soft | 5 | generation_policy | not_requested | pending | pending | pending |
| spectral_soft | 5 | evaluation | available | 0.340 [0.280, 0.405]; 200/200 tasks, full | pending | 3200 |

## Correct implementation richness and annotated strategy coverage

Implementation coverage uses conservative Python AST fingerprints. These are implementation proxies, not algorithm identities. Strategy coverage uses supplied independent labels only; incomplete annotations remain unavailable. Wrong completions remain in the draw population.

| Stage | Draw budget K | Correct AST richness @K | Annotated strategy coverage |
| --- | ---: | --- | --- |
| base/evaluation | 16 | 2.070 [1.620, 2.545]; 200/200 tasks, full | 0.000 [0.000, 0.000]; 117/200 tasks, partial |
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
| plain/round_5/evaluation | 16 | 1.930 [1.480, 2.420]; 200/200 tasks, full | 0.000 [0.000, 0.000]; 129/200 tasks, partial |
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
| spd_hard/round_5/evaluation | 16 | 1.880 [1.435, 2.355]; 200/200 tasks, full | 0.000 [0.000, 0.000]; 131/200 tasks, partial |
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
| spectral_soft/round_5/evaluation | 16 | 1.845 [1.405, 2.325]; 200/200 tasks, full | 0.000 [0.000, 0.000]; 132/200 tasks, partial |
| spectral_soft/round_5/evaluation | 64 | pending | pending |

## Coverage at a fixed correct-sample budget

These conditional estimates use only correct samples and require at least the displayed number of correct samples per task. Different eligible-task populations must not be interpreted as whole-task improvements.

| Stage | Correct-sample budget b | Correct-conditioned AST richness @b | Annotated strategy coverage |
| --- | ---: | --- | --- |
| base/evaluation | 4 | 3.772 [3.674, 3.864]; 50/200 tasks, partial | unavailable (0/200 tasks) |
| base/evaluation | 8 | 6.825 [6.427, 7.210]; 28/200 tasks, partial | unavailable (0/200 tasks) |
| base/evaluation | 16 | 14.000 [14.000, 14.000]; 1/200 tasks, partial | unavailable (0/200 tasks) |
| plain/round_1/generation_policy | pending | pending | pending |
| plain/round_1/evaluation | pending | pending | pending |
| plain/round_2/generation_policy | pending | pending | pending |
| plain/round_2/evaluation | pending | pending | pending |
| plain/round_3/generation_policy | pending | pending | pending |
| plain/round_3/evaluation | pending | pending | pending |
| plain/round_4/generation_policy | pending | pending | pending |
| plain/round_4/evaluation | pending | pending | pending |
| plain/round_5/generation_policy | pending | pending | pending |
| plain/round_5/evaluation | 4 | 3.632 [3.487, 3.755]; 46/200 tasks, partial | unavailable (0/200 tasks) |
| plain/round_5/evaluation | 8 | 6.293 [5.744, 6.831]; 27/200 tasks, partial | unavailable (0/200 tasks) |
| plain/round_5/evaluation | 16 | 9.000 [8.000, 10.000]; 2/200 tasks, partial | unavailable (0/200 tasks) |
| spd_hard/round_1/generation_policy | pending | pending | pending |
| spd_hard/round_1/evaluation | pending | pending | pending |
| spd_hard/round_2/generation_policy | pending | pending | pending |
| spd_hard/round_2/evaluation | pending | pending | pending |
| spd_hard/round_3/generation_policy | pending | pending | pending |
| spd_hard/round_3/evaluation | pending | pending | pending |
| spd_hard/round_4/generation_policy | pending | pending | pending |
| spd_hard/round_4/evaluation | pending | pending | pending |
| spd_hard/round_5/generation_policy | pending | pending | pending |
| spd_hard/round_5/evaluation | 4 | 3.685 [3.564, 3.795]; 47/200 tasks, partial | unavailable (0/200 tasks) |
| spd_hard/round_5/evaluation | 8 | 6.410 [5.966, 6.865]; 29/200 tasks, partial | unavailable (0/200 tasks) |
| spd_hard/round_5/evaluation | 16 | 8.667 [8.000, 10.000]; 3/200 tasks, partial | unavailable (0/200 tasks) |
| spectral_soft/round_1/generation_policy | pending | pending | pending |
| spectral_soft/round_1/evaluation | pending | pending | pending |
| spectral_soft/round_2/generation_policy | pending | pending | pending |
| spectral_soft/round_2/evaluation | pending | pending | pending |
| spectral_soft/round_3/generation_policy | pending | pending | pending |
| spectral_soft/round_3/evaluation | pending | pending | pending |
| spectral_soft/round_4/generation_policy | pending | pending | pending |
| spectral_soft/round_4/evaluation | pending | pending | pending |
| spectral_soft/round_5/generation_policy | pending | pending | pending |
| spectral_soft/round_5/evaluation | 4 | 3.721 [3.605, 3.823]; 43/200 tasks, partial | unavailable (0/200 tasks) |
| spectral_soft/round_5/evaluation | 8 | 6.679 [6.188, 7.121]; 25/200 tasks, partial | unavailable (0/200 tasks) |
| spectral_soft/round_5/evaluation | 16 | 9.000 [9.000, 9.000]; 1/200 tasks, partial | unavailable (0/200 tasks) |

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
| plain/round_5/evaluation | base/evaluation | available | -0.060 [-0.105, -0.015]; 200/200 tasks, paired | pending | — |
| plain/round_5/evaluation | spd_hard/round_5/evaluation | available | 0.010 [-0.020, 0.040]; 200/200 tasks, paired | pending | — |
| spd_hard/round_1/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_1/evaluation | plain/round_1/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_2/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_2/evaluation | plain/round_2/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_3/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_3/evaluation | plain/round_3/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_4/evaluation | base/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_4/evaluation | plain/round_4/evaluation | pending | pending | pending | candidate metrics are pending |
| spd_hard/round_5/evaluation | base/evaluation | available | -0.070 [-0.120, -0.020]; 200/200 tasks, paired | pending | — |
| spd_hard/round_5/evaluation | plain/round_5/evaluation | available | -0.010 [-0.040, 0.020]; 200/200 tasks, paired | pending | — |
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
| spectral_soft/round_5/evaluation | base/evaluation | available | -0.075 [-0.125, -0.025]; 200/200 tasks, paired | pending | — |
| spectral_soft/round_5/evaluation | plain/round_5/evaluation | available | -0.015 [-0.045, 0.015]; 200/200 tasks, paired | pending | — |
| spectral_soft/round_5/evaluation | spd_hard/round_5/evaluation | available | -0.005 [-0.035, 0.025]; 200/200 tasks, paired | pending | — |

Coverage and entropy deltas, including their intervals and paired eligibility, are included in the JSON report. Comparisons require matching explicit sampling and evaluation protocols, task IDs, metric budgets, and per-task sample counts.

## Budgets and training

| Stage | Generated samples | Generation tokens | Prompt tokens |
| --- | ---: | ---: | ---: |
| base/evaluation | 3200 | 851860 | 1518352 |
| plain/round_1/generation_policy | unavailable | unavailable | unavailable |
| plain/round_1/evaluation | unavailable | unavailable | unavailable |
| plain/round_2/generation_policy | unavailable | unavailable | unavailable |
| plain/round_2/evaluation | unavailable | unavailable | unavailable |
| plain/round_3/generation_policy | unavailable | unavailable | unavailable |
| plain/round_3/evaluation | unavailable | unavailable | unavailable |
| plain/round_4/generation_policy | unavailable | unavailable | unavailable |
| plain/round_4/evaluation | unavailable | unavailable | unavailable |
| plain/round_5/generation_policy | unavailable | unavailable | unavailable |
| plain/round_5/evaluation | 3200 | 824973 | 1518352 |
| spd_hard/round_1/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_1/evaluation | unavailable | unavailable | unavailable |
| spd_hard/round_2/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_2/evaluation | unavailable | unavailable | unavailable |
| spd_hard/round_3/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_3/evaluation | unavailable | unavailable | unavailable |
| spd_hard/round_4/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_4/evaluation | unavailable | unavailable | unavailable |
| spd_hard/round_5/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_5/evaluation | 3200 | 826614 | 1518352 |
| spectral_soft/round_1/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_1/evaluation | unavailable | unavailable | unavailable |
| spectral_soft/round_2/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_2/evaluation | unavailable | unavailable | unavailable |
| spectral_soft/round_3/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_3/evaluation | unavailable | unavailable | unavailable |
| spectral_soft/round_4/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_4/evaluation | unavailable | unavailable | unavailable |
| spectral_soft/round_5/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_5/evaluation | 3200 | 884832 | 1518352 |

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
| base/round_0 | evaluation_generation | 5690.0317990919575 | 4130455552 | 4710203392 |
| base/round_0 | model_loading | 3.415693075978197 | 3088346624 | 3286237184 |
| base/round_0 | verification_and_metrics | 195.08948686299846 | 3096866304 | 4607442944 |
| plain/round_5 | evaluation_generation | 5100.362694742042 | 4130445824 | 4672454656 |
| plain/round_5 | model_loading | 1.3028196269879118 | 3096866304 | 3307208704 |
| plain/round_5 | verification_and_metrics | 140.27555010700598 | 3096866304 | 4569694208 |
| spd_hard/round_5 | evaluation_generation | 5119.448006187915 | 4130445824 | 4672454656 |
| spd_hard/round_5 | model_loading | 1.0819347810465842 | 3096866304 | 3307208704 |
| spd_hard/round_5 | verification_and_metrics | 174.2148492950946 | 3096866304 | 4569694208 |
| spectral_soft/round_5 | evaluation_generation | 5510.913375256932 | 4130452992 | 4672454656 |
| spectral_soft/round_5 | model_loading | 1.0447804920841008 | 3096866304 | 3307208704 |
| spectral_soft/round_5 | verification_and_metrics | 170.10149706690572 | 3096866304 | 4569694208 |

## Appendix: Pass@1 and correctness noninferiority

Pass@1 and the original correctness criterion are retained as supplementary diagnostics. They do not determine the main Pass@16/Pass@64 and diversity conclusions.

| Stage | Pass@1 |
| --- | --- |
| base/evaluation | 0.155 [0.119, 0.193]; 200/200 tasks, full |
| plain/round_1/generation_policy | pending |
| plain/round_1/evaluation | pending |
| plain/round_2/generation_policy | pending |
| plain/round_2/evaluation | pending |
| plain/round_3/generation_policy | pending |
| plain/round_3/evaluation | pending |
| plain/round_4/generation_policy | pending |
| plain/round_4/evaluation | pending |
| plain/round_5/generation_policy | pending |
| plain/round_5/evaluation | 0.152 [0.116, 0.191]; 200/200 tasks, full |
| spd_hard/round_1/generation_policy | pending |
| spd_hard/round_1/evaluation | pending |
| spd_hard/round_2/generation_policy | pending |
| spd_hard/round_2/evaluation | pending |
| spd_hard/round_3/generation_policy | pending |
| spd_hard/round_3/evaluation | pending |
| spd_hard/round_4/generation_policy | pending |
| spd_hard/round_4/evaluation | pending |
| spd_hard/round_5/generation_policy | pending |
| spd_hard/round_5/evaluation | 0.149 [0.113, 0.189]; 200/200 tasks, full |
| spectral_soft/round_1/generation_policy | pending |
| spectral_soft/round_1/evaluation | pending |
| spectral_soft/round_2/generation_policy | pending |
| spectral_soft/round_2/evaluation | pending |
| spectral_soft/round_3/generation_policy | pending |
| spectral_soft/round_3/evaluation | pending |
| spectral_soft/round_4/generation_policy | pending |
| spectral_soft/round_4/evaluation | pending |
| spectral_soft/round_5/generation_policy | pending |
| spectral_soft/round_5/evaluation | 0.140 [0.105, 0.179]; 200/200 tasks, full |

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
| plain/round_5/evaluation | base/evaluation | available | -0.003 [-0.016, 0.011]; 200/200 tasks, paired | criterion not met | — |
| plain/round_5/evaluation | spd_hard/round_5/evaluation | available | 0.003 [-0.003, 0.010]; 200/200 tasks, paired | criterion met | — |
| spd_hard/round_1/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_1/evaluation | plain/round_1/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_2/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_2/evaluation | plain/round_2/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_3/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_3/evaluation | plain/round_3/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_4/evaluation | base/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_4/evaluation | plain/round_4/evaluation | pending | pending | unavailable | candidate metrics are pending |
| spd_hard/round_5/evaluation | base/evaluation | available | -0.006 [-0.019, 0.008]; 200/200 tasks, paired | criterion not met | — |
| spd_hard/round_5/evaluation | plain/round_5/evaluation | available | -0.003 [-0.010, 0.003]; 200/200 tasks, paired | criterion met | — |
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
| spectral_soft/round_5/evaluation | base/evaluation | available | -0.015 [-0.029, -0.001]; 200/200 tasks, paired | criterion not met | — |
| spectral_soft/round_5/evaluation | plain/round_5/evaluation | available | -0.012 [-0.019, -0.005]; 200/200 tasks, paired | criterion not met | — |
| spectral_soft/round_5/evaluation | spd_hard/round_5/evaluation | available | -0.009 [-0.016, -0.002]; 200/200 tasks, paired | criterion not met | — |

The JSON report preserves all metric budgets, Pass@1 and correctness comparisons, generation budgets, training statistics, full sampling metadata, evaluation provenance, and eligibility details. Sampling budget and correctness can change observed diversity; no model-performance claim follows from a report being complete.
