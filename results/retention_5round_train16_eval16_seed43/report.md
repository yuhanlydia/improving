# Coding self-distillation report

Result status: **complete**.

Numbers show task means with pointwise 95% task-bootstrap intervals and explicit eligible-task denominators. Partial means describe the eligible subset; they do not establish gains across all tasks. Pending measurements are not zeros.

## Correctness and evaluation stages

| Method | Round | Stage | Status | Pass@1 | Samples |
| --- | ---: | --- | --- | --- | ---: |
| base | 0 | evaluation | available | 0.379 [0.347, 0.414]; 500/500 tasks, full | 8000 |
| plain | 1 | generation_policy | not_requested | pending | pending |
| plain | 1 | evaluation | available | 0.384 [0.351, 0.419]; 500/500 tasks, full | 8000 |
| plain | 2 | generation_policy | not_requested | pending | pending |
| plain | 2 | evaluation | available | 0.392 [0.360, 0.426]; 500/500 tasks, full | 8000 |
| plain | 3 | generation_policy | not_requested | pending | pending |
| plain | 3 | evaluation | available | 0.397 [0.365, 0.432]; 500/500 tasks, full | 8000 |
| plain | 4 | generation_policy | not_requested | pending | pending |
| plain | 4 | evaluation | available | 0.408 [0.374, 0.444]; 500/500 tasks, full | 8000 |
| plain | 5 | generation_policy | not_requested | pending | pending |
| plain | 5 | evaluation | available | 0.413 [0.379, 0.450]; 500/500 tasks, full | 8000 |
| spd_hard | 1 | generation_policy | not_requested | pending | pending |
| spd_hard | 1 | evaluation | available | 0.379 [0.347, 0.413]; 500/500 tasks, full | 8000 |
| spd_hard | 2 | generation_policy | not_requested | pending | pending |
| spd_hard | 2 | evaluation | available | 0.392 [0.360, 0.426]; 500/500 tasks, full | 8000 |
| spd_hard | 3 | generation_policy | not_requested | pending | pending |
| spd_hard | 3 | evaluation | available | 0.394 [0.362, 0.430]; 500/500 tasks, full | 8000 |
| spd_hard | 4 | generation_policy | not_requested | pending | pending |
| spd_hard | 4 | evaluation | available | 0.411 [0.377, 0.449]; 500/500 tasks, full | 8000 |
| spd_hard | 5 | generation_policy | not_requested | pending | pending |
| spd_hard | 5 | evaluation | available | 0.413 [0.379, 0.451]; 500/500 tasks, full | 8000 |
| spectral_soft | 1 | generation_policy | not_requested | pending | pending |
| spectral_soft | 1 | evaluation | available | 0.378 [0.347, 0.413]; 500/500 tasks, full | 8000 |
| spectral_soft | 2 | generation_policy | not_requested | pending | pending |
| spectral_soft | 2 | evaluation | available | 0.384 [0.352, 0.418]; 500/500 tasks, full | 8000 |
| spectral_soft | 3 | generation_policy | not_requested | pending | pending |
| spectral_soft | 3 | evaluation | available | 0.391 [0.360, 0.425]; 500/500 tasks, full | 8000 |
| spectral_soft | 4 | generation_policy | not_requested | pending | pending |
| spectral_soft | 4 | evaluation | available | 0.398 [0.365, 0.433]; 500/500 tasks, full | 8000 |
| spectral_soft | 5 | generation_policy | not_requested | pending | pending |
| spectral_soft | 5 | evaluation | available | 0.402 [0.368, 0.438]; 500/500 tasks, full | 8000 |

## Correct implementation and annotated strategy coverage

Implementation coverage uses conservative Python AST fingerprints. These are implementation proxies, not algorithm identities. Strategy coverage uses supplied independent labels only; incomplete annotations remain unavailable. Wrong completions remain in the draw population.

| Stage | Draw budget K | Implementation proxy coverage | Annotated strategy coverage |
| --- | ---: | --- | --- |
| base/evaluation | 1 | 0.379 [0.347, 0.414]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 167/500 tasks, partial |
| base/evaluation | 8 | 2.253 [2.057, 2.453]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 167/500 tasks, partial |
| base/evaluation | 16 | 4.016 [3.664, 4.374]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 167/500 tasks, partial |
| plain/round_1/generation_policy | pending | pending | pending |
| plain/round_1/evaluation | 1 | 0.384 [0.351, 0.419]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 166/500 tasks, partial |
| plain/round_1/evaluation | 8 | 2.161 [1.978, 2.353]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 166/500 tasks, partial |
| plain/round_1/evaluation | 16 | 3.808 [3.472, 4.158]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 166/500 tasks, partial |
| plain/round_2/generation_policy | pending | pending | pending |
| plain/round_2/evaluation | 1 | 0.392 [0.360, 0.426]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 167/500 tasks, partial |
| plain/round_2/evaluation | 8 | 2.109 [1.922, 2.296]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 167/500 tasks, partial |
| plain/round_2/evaluation | 16 | 3.634 [3.302, 3.966]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 167/500 tasks, partial |
| plain/round_3/generation_policy | pending | pending | pending |
| plain/round_3/evaluation | 1 | 0.397 [0.365, 0.432]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 169/500 tasks, partial |
| plain/round_3/evaluation | 8 | 2.000 [1.830, 2.184]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 169/500 tasks, partial |
| plain/round_3/evaluation | 16 | 3.372 [3.068, 3.690]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 169/500 tasks, partial |
| plain/round_4/generation_policy | pending | pending | pending |
| plain/round_4/evaluation | 1 | 0.408 [0.374, 0.444]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 167/500 tasks, partial |
| plain/round_4/evaluation | 8 | 1.934 [1.762, 2.113]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 167/500 tasks, partial |
| plain/round_4/evaluation | 16 | 3.190 [2.886, 3.506]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 167/500 tasks, partial |
| plain/round_5/generation_policy | pending | pending | pending |
| plain/round_5/evaluation | 1 | 0.413 [0.379, 0.450]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 170/500 tasks, partial |
| plain/round_5/evaluation | 8 | 1.902 [1.738, 2.079]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 170/500 tasks, partial |
| plain/round_5/evaluation | 16 | 3.090 [2.804, 3.398]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 170/500 tasks, partial |
| spd_hard/round_1/generation_policy | pending | pending | pending |
| spd_hard/round_1/evaluation | 1 | 0.379 [0.347, 0.413]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 166/500 tasks, partial |
| spd_hard/round_1/evaluation | 8 | 2.104 [1.922, 2.293]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 166/500 tasks, partial |
| spd_hard/round_1/evaluation | 16 | 3.692 [3.360, 4.036]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 166/500 tasks, partial |
| spd_hard/round_2/generation_policy | pending | pending | pending |
| spd_hard/round_2/evaluation | 1 | 0.392 [0.360, 0.426]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 164/500 tasks, partial |
| spd_hard/round_2/evaluation | 8 | 2.091 [1.910, 2.277]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 164/500 tasks, partial |
| spd_hard/round_2/evaluation | 16 | 3.592 [3.266, 3.928]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 164/500 tasks, partial |
| spd_hard/round_3/generation_policy | pending | pending | pending |
| spd_hard/round_3/evaluation | 1 | 0.394 [0.362, 0.430]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 171/500 tasks, partial |
| spd_hard/round_3/evaluation | 8 | 1.967 [1.795, 2.149]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 171/500 tasks, partial |
| spd_hard/round_3/evaluation | 16 | 3.314 [3.012, 3.630]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 171/500 tasks, partial |
| spd_hard/round_4/generation_policy | pending | pending | pending |
| spd_hard/round_4/evaluation | 1 | 0.411 [0.377, 0.449]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 171/500 tasks, partial |
| spd_hard/round_4/evaluation | 8 | 1.908 [1.745, 2.085]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 171/500 tasks, partial |
| spd_hard/round_4/evaluation | 16 | 3.162 [2.874, 3.476]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 171/500 tasks, partial |
| spd_hard/round_5/generation_policy | pending | pending | pending |
| spd_hard/round_5/evaluation | 1 | 0.413 [0.379, 0.451]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 172/500 tasks, partial |
| spd_hard/round_5/evaluation | 8 | 1.876 [1.713, 2.054]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 172/500 tasks, partial |
| spd_hard/round_5/evaluation | 16 | 3.066 [2.774, 3.380]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 172/500 tasks, partial |
| spectral_soft/round_1/generation_policy | pending | pending | pending |
| spectral_soft/round_1/evaluation | 1 | 0.378 [0.347, 0.413]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 168/500 tasks, partial |
| spectral_soft/round_1/evaluation | 8 | 2.173 [1.989, 2.367]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 168/500 tasks, partial |
| spectral_soft/round_1/evaluation | 16 | 3.848 [3.504, 4.202]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 168/500 tasks, partial |
| spectral_soft/round_2/generation_policy | pending | pending | pending |
| spectral_soft/round_2/evaluation | 1 | 0.384 [0.352, 0.418]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 170/500 tasks, partial |
| spectral_soft/round_2/evaluation | 8 | 2.152 [1.971, 2.340]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 170/500 tasks, partial |
| spectral_soft/round_2/evaluation | 16 | 3.768 [3.436, 4.104]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 170/500 tasks, partial |
| spectral_soft/round_3/generation_policy | pending | pending | pending |
| spectral_soft/round_3/evaluation | 1 | 0.391 [0.360, 0.425]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 168/500 tasks, partial |
| spectral_soft/round_3/evaluation | 8 | 2.109 [1.928, 2.295]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 168/500 tasks, partial |
| spectral_soft/round_3/evaluation | 16 | 3.662 [3.330, 4.000]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 168/500 tasks, partial |
| spectral_soft/round_4/generation_policy | pending | pending | pending |
| spectral_soft/round_4/evaluation | 1 | 0.398 [0.365, 0.433]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 170/500 tasks, partial |
| spectral_soft/round_4/evaluation | 8 | 2.083 [1.907, 2.270]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 170/500 tasks, partial |
| spectral_soft/round_4/evaluation | 16 | 3.588 [3.268, 3.930]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 170/500 tasks, partial |
| spectral_soft/round_5/generation_policy | pending | pending | pending |
| spectral_soft/round_5/evaluation | 1 | 0.402 [0.368, 0.438]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 164/500 tasks, partial |
| spectral_soft/round_5/evaluation | 8 | 2.091 [1.907, 2.277]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 164/500 tasks, partial |
| spectral_soft/round_5/evaluation | 16 | 3.606 [3.274, 3.954]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 164/500 tasks, partial |

## Coverage at a fixed correct-sample budget

These conditional estimates use only correct samples and require at least the displayed number of correct samples per task. Different eligible-task populations must not be interpreted as whole-task improvements.

| Stage | Correct-sample budget | Implementation proxy coverage | Annotated strategy coverage |
| --- | ---: | --- | --- |
| base/evaluation | 4 | 3.310 [3.221, 3.400]; 262/500 tasks, partial | unavailable (0/500 tasks) |
| plain/round_1/generation_policy | pending | pending | pending |
| plain/round_1/evaluation | 4 | 3.173 [3.067, 3.281]; 261/500 tasks, partial | unavailable (0/500 tasks) |
| plain/round_2/generation_policy | pending | pending | pending |
| plain/round_2/evaluation | 4 | 3.080 [2.974, 3.192]; 269/500 tasks, partial | unavailable (0/500 tasks) |
| plain/round_3/generation_policy | pending | pending | pending |
| plain/round_3/evaluation | 4 | 2.895 [2.777, 3.018]; 257/500 tasks, partial | unavailable (0/500 tasks) |
| plain/round_4/generation_policy | pending | pending | pending |
| plain/round_4/evaluation | 4 | 2.803 [2.686, 2.918]; 270/500 tasks, partial | unavailable (0/500 tasks) |
| plain/round_5/generation_policy | pending | pending | pending |
| plain/round_5/evaluation | 4 | 2.747 [2.629, 2.862]; 268/500 tasks, partial | unavailable (0/500 tasks) |
| spd_hard/round_1/generation_policy | pending | pending | pending |
| spd_hard/round_1/evaluation | 4 | 3.144 [3.035, 3.253]; 257/500 tasks, partial | unavailable (0/500 tasks) |
| spd_hard/round_2/generation_policy | pending | pending | pending |
| spd_hard/round_2/evaluation | 4 | 3.059 [2.945, 3.171]; 267/500 tasks, partial | unavailable (0/500 tasks) |
| spd_hard/round_3/generation_policy | pending | pending | pending |
| spd_hard/round_3/evaluation | 4 | 2.889 [2.768, 3.010]; 256/500 tasks, partial | unavailable (0/500 tasks) |
| spd_hard/round_4/generation_policy | pending | pending | pending |
| spd_hard/round_4/evaluation | 4 | 2.774 [2.656, 2.888]; 266/500 tasks, partial | unavailable (0/500 tasks) |
| spd_hard/round_5/generation_policy | pending | pending | pending |
| spd_hard/round_5/evaluation | 4 | 2.690 [2.574, 2.811]; 262/500 tasks, partial | unavailable (0/500 tasks) |
| spectral_soft/round_1/generation_policy | pending | pending | pending |
| spectral_soft/round_1/evaluation | 4 | 3.222 [3.122, 3.326]; 261/500 tasks, partial | unavailable (0/500 tasks) |
| spectral_soft/round_2/generation_policy | pending | pending | pending |
| spectral_soft/round_2/evaluation | 4 | 3.159 [3.054, 3.267]; 259/500 tasks, partial | unavailable (0/500 tasks) |
| spectral_soft/round_3/generation_policy | pending | pending | pending |
| spectral_soft/round_3/evaluation | 4 | 3.063 [2.952, 3.174]; 262/500 tasks, partial | unavailable (0/500 tasks) |
| spectral_soft/round_4/generation_policy | pending | pending | pending |
| spectral_soft/round_4/evaluation | 4 | 2.991 [2.880, 3.102]; 263/500 tasks, partial | unavailable (0/500 tasks) |
| spectral_soft/round_5/generation_policy | pending | pending | pending |
| spectral_soft/round_5/evaluation | 4 | 2.997 [2.888, 3.106]; 263/500 tasks, partial | unavailable (0/500 tasks) |

## Paired comparisons

Deltas are candidate minus reference. Correctness noninferiority uses an absolute margin of 0.010 and the lower endpoint of a two-sided 95% paired task-bootstrap interval. It requires all tasks. These are descriptive statistical outputs, not automatic claims of algorithm diversity or a successful research result.

| Candidate | Reference | Status | Correctness delta | Noninferiority | Reason |
| --- | --- | --- | --- | --- | --- |
| plain/round_1/evaluation | base/evaluation | available | 0.005 [-0.004, 0.014]; 500/500 tasks, paired | criterion met | — |
| plain/round_1/evaluation | spd_hard/round_1/evaluation | available | 0.005 [0.001, 0.009]; 500/500 tasks, paired | criterion met | — |
| plain/round_2/evaluation | base/evaluation | available | 0.012 [0.002, 0.023]; 500/500 tasks, paired | criterion met | — |
| plain/round_2/evaluation | spd_hard/round_2/evaluation | available | -0.001 [-0.005, 0.004]; 500/500 tasks, paired | criterion met | — |
| plain/round_3/evaluation | base/evaluation | available | 0.017 [0.007, 0.028]; 500/500 tasks, paired | criterion met | — |
| plain/round_3/evaluation | spd_hard/round_3/evaluation | available | 0.003 [-0.003, 0.008]; 500/500 tasks, paired | criterion met | — |
| plain/round_4/evaluation | base/evaluation | available | 0.029 [0.016, 0.040]; 500/500 tasks, paired | criterion met | — |
| plain/round_4/evaluation | spd_hard/round_4/evaluation | available | -0.003 [-0.009, 0.003]; 500/500 tasks, paired | criterion met | — |
| plain/round_5/evaluation | base/evaluation | available | 0.034 [0.022, 0.046]; 500/500 tasks, paired | criterion met | — |
| plain/round_5/evaluation | spd_hard/round_5/evaluation | available | -0.001 [-0.006, 0.005]; 500/500 tasks, paired | criterion met | — |
| spd_hard/round_1/evaluation | base/evaluation | available | 0.000 [-0.009, 0.010]; 500/500 tasks, paired | criterion met | — |
| spd_hard/round_2/evaluation | base/evaluation | available | 0.013 [0.002, 0.024]; 500/500 tasks, paired | criterion met | — |
| spd_hard/round_3/evaluation | base/evaluation | available | 0.015 [0.003, 0.026]; 500/500 tasks, paired | criterion met | — |
| spd_hard/round_4/evaluation | base/evaluation | available | 0.032 [0.020, 0.044]; 500/500 tasks, paired | criterion met | — |
| spd_hard/round_5/evaluation | base/evaluation | available | 0.034 [0.023, 0.047]; 500/500 tasks, paired | criterion met | — |
| spectral_soft/round_1/evaluation | base/evaluation | available | -0.001 [-0.010, 0.009]; 500/500 tasks, paired | criterion met | — |
| spectral_soft/round_1/evaluation | spd_hard/round_1/evaluation | available | -0.001 [-0.006, 0.004]; 500/500 tasks, paired | criterion met | — |
| spectral_soft/round_2/evaluation | base/evaluation | available | 0.004 [-0.006, 0.015]; 500/500 tasks, paired | criterion met | — |
| spectral_soft/round_2/evaluation | spd_hard/round_2/evaluation | available | -0.008 [-0.014, -0.002]; 500/500 tasks, paired | criterion not met | — |
| spectral_soft/round_3/evaluation | base/evaluation | available | 0.011 [0.001, 0.022]; 500/500 tasks, paired | criterion met | — |
| spectral_soft/round_3/evaluation | spd_hard/round_3/evaluation | available | -0.004 [-0.009, 0.003]; 500/500 tasks, paired | criterion met | — |
| spectral_soft/round_4/evaluation | base/evaluation | available | 0.018 [0.009, 0.029]; 500/500 tasks, paired | criterion met | — |
| spectral_soft/round_4/evaluation | spd_hard/round_4/evaluation | available | -0.013 [-0.020, -0.007]; 500/500 tasks, paired | criterion not met | — |
| spectral_soft/round_5/evaluation | base/evaluation | available | 0.022 [0.012, 0.034]; 500/500 tasks, paired | criterion met | — |
| spectral_soft/round_5/evaluation | spd_hard/round_5/evaluation | available | -0.012 [-0.019, -0.005]; 500/500 tasks, paired | criterion not met | — |

Coverage and entropy deltas, including their intervals and paired eligibility, are included in the JSON report. Comparisons require matching explicit sampling and evaluation protocols, task IDs, metric budgets, and per-task sample counts.

## Budgets and training

| Stage | Generated samples | Generation tokens | Prompt tokens |
| --- | ---: | ---: | ---: |
| base/evaluation | 8000 | 1958119 | 526192 |
| plain/round_1/generation_policy | unavailable | unavailable | unavailable |
| plain/round_1/evaluation | 8000 | 1751347 | 526192 |
| plain/round_2/generation_policy | unavailable | unavailable | unavailable |
| plain/round_2/evaluation | 8000 | 1635736 | 526192 |
| plain/round_3/generation_policy | unavailable | unavailable | unavailable |
| plain/round_3/evaluation | 8000 | 1502777 | 526192 |
| plain/round_4/generation_policy | unavailable | unavailable | unavailable |
| plain/round_4/evaluation | 8000 | 1520412 | 526192 |
| plain/round_5/generation_policy | unavailable | unavailable | unavailable |
| plain/round_5/evaluation | 8000 | 1517357 | 526192 |
| spd_hard/round_1/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_1/evaluation | 8000 | 1718795 | 526192 |
| spd_hard/round_2/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_2/evaluation | 8000 | 1587806 | 526192 |
| spd_hard/round_3/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_3/evaluation | 8000 | 1443502 | 526192 |
| spd_hard/round_4/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_4/evaluation | 8000 | 1436204 | 526192 |
| spd_hard/round_5/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_5/evaluation | 8000 | 1429188 | 526192 |
| spectral_soft/round_1/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_1/evaluation | 8000 | 1770155 | 526192 |
| spectral_soft/round_2/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_2/evaluation | 8000 | 1680539 | 526192 |
| spectral_soft/round_3/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_3/evaluation | 8000 | 1570145 | 526192 |
| spectral_soft/round_4/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_4/evaluation | 8000 | 1582746 | 526192 |
| spectral_soft/round_5/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_5/evaluation | 8000 | 1597418 | 526192 |

**plain/round_1**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.2624597945906657, "optimizer_steps": 291, "seed": 44, "supervised_tokens_per_epoch": 1447502, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1144830, "length_capped_samples": 197, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**plain/round_2**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.11890587999239, "optimizer_steps": 291, "seed": 45, "supervised_tokens_per_epoch": 1320878, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1018206, "length_capped_samples": 153, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**plain/round_3**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 0.9364572664229935, "optimizer_steps": 291, "seed": 46, "supervised_tokens_per_epoch": 1237824, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 935152, "length_capped_samples": 127, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**plain/round_4**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 0.7720478443985748, "optimizer_steps": 291, "seed": 47, "supervised_tokens_per_epoch": 1177665, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 874993, "length_capped_samples": 96, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**plain/round_5**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 0.6136689797856707, "optimizer_steps": 291, "seed": 48, "supervised_tokens_per_epoch": 1189419, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 886747, "length_capped_samples": 44, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**spd_hard/round_1**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.301723701437724, "optimizer_steps": 291, "seed": 44, "supervised_tokens_per_epoch": 1426835, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1124163, "length_capped_samples": 207, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**spd_hard/round_2**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.1594782830616044, "optimizer_steps": 291, "seed": 45, "supervised_tokens_per_epoch": 1294566, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 991894, "length_capped_samples": 144, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**spd_hard/round_3**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 0.9674526236925748, "optimizer_steps": 291, "seed": 46, "supervised_tokens_per_epoch": 1214457, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 911785, "length_capped_samples": 129, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**spd_hard/round_4**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 0.8018581939611545, "optimizer_steps": 291, "seed": 47, "supervised_tokens_per_epoch": 1154793, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 852121, "length_capped_samples": 99, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**spd_hard/round_5**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 0.6396646224301552, "optimizer_steps": 291, "seed": 48, "supervised_tokens_per_epoch": 1149798, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 847126, "length_capped_samples": 40, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**spectral_soft/round_1**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.2695576966551365, "optimizer_steps": 291, "seed": 44, "supervised_tokens_per_epoch": 1512424, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1209752, "length_capped_samples": 257, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**spectral_soft/round_2**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.12982993904514, "optimizer_steps": 291, "seed": 45, "supervised_tokens_per_epoch": 1408721, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1106049, "length_capped_samples": 195, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**spectral_soft/round_3**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 0.954183371916823, "optimizer_steps": 291, "seed": 46, "supervised_tokens_per_epoch": 1362678, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1060006, "length_capped_samples": 171, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**spectral_soft/round_4**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 0.8206671065366042, "optimizer_steps": 291, "seed": 47, "supervised_tokens_per_epoch": 1278225, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 975553, "length_capped_samples": 112, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**spectral_soft/round_5**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 0.6789387929736543, "optimizer_steps": 291, "seed": 48, "supervised_tokens_per_epoch": 1293680, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 991008, "length_capped_samples": 98, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

The JSON report preserves generation budgets, training statistics, full sampling metadata, evaluation provenance, and eligibility details. Sampling budget and correctness can change observed diversity; no model-performance claim follows from a report being complete.
