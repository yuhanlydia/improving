# Coding self-distillation report

Result status: **complete**.

Numbers show task means with pointwise 95% task-bootstrap intervals and explicit eligible-task denominators. Partial means describe the eligible subset; they do not establish gains across all tasks. Pending measurements are not zeros.

## Correctness and evaluation stages

| Method | Round | Stage | Status | Pass@16 | Pass@64 | Samples |
| --- | ---: | --- | --- | --- | --- | ---: |
| base | 0 | evaluation | available | 0.668 [0.628, 0.710]; 500/500 tasks, full | pending | 8000 |
| ssd | 1 | generation_policy | not_requested | pending | pending | pending |
| ssd | 1 | evaluation | available | 0.666 [0.626, 0.706]; 500/500 tasks, full | pending | 8000 |
| ssd | 2 | generation_policy | not_requested | pending | pending | pending |
| ssd | 2 | evaluation | available | 0.658 [0.616, 0.700]; 500/500 tasks, full | pending | 8000 |
| ssd | 3 | generation_policy | not_requested | pending | pending | pending |
| ssd | 3 | evaluation | available | 0.660 [0.620, 0.702]; 500/500 tasks, full | pending | 8000 |
| ssd | 4 | generation_policy | not_requested | pending | pending | pending |
| ssd | 4 | evaluation | available | 0.664 [0.624, 0.706]; 500/500 tasks, full | pending | 8000 |
| ssd | 5 | generation_policy | not_requested | pending | pending | pending |
| ssd | 5 | evaluation | available | 0.656 [0.616, 0.700]; 500/500 tasks, full | pending | 8000 |

## Correct implementation richness and annotated strategy coverage

Implementation coverage uses conservative Python AST fingerprints. These are implementation proxies, not algorithm identities. Strategy coverage uses supplied independent labels only; incomplete annotations remain unavailable. Wrong completions remain in the draw population.

| Stage | Draw budget K | Correct AST richness @K | Annotated strategy coverage |
| --- | ---: | --- | --- |
| base/evaluation | 16 | 3.992 [3.644, 4.350]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 166/500 tasks, partial |
| base/evaluation | 64 | pending | pending |
| ssd/round_1/generation_policy | 16 | pending | pending |
| ssd/round_1/generation_policy | 64 | pending | pending |
| ssd/round_1/evaluation | 16 | 3.846 [3.514, 4.192]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 167/500 tasks, partial |
| ssd/round_1/evaluation | 64 | pending | pending |
| ssd/round_2/generation_policy | 16 | pending | pending |
| ssd/round_2/generation_policy | 64 | pending | pending |
| ssd/round_2/evaluation | 16 | 3.710 [3.380, 4.052]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 171/500 tasks, partial |
| ssd/round_2/evaluation | 64 | pending | pending |
| ssd/round_3/generation_policy | 16 | pending | pending |
| ssd/round_3/generation_policy | 64 | pending | pending |
| ssd/round_3/evaluation | 16 | 3.724 [3.396, 4.078]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 170/500 tasks, partial |
| ssd/round_3/evaluation | 64 | pending | pending |
| ssd/round_4/generation_policy | 16 | pending | pending |
| ssd/round_4/generation_policy | 64 | pending | pending |
| ssd/round_4/evaluation | 16 | 3.752 [3.418, 4.102]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 168/500 tasks, partial |
| ssd/round_4/evaluation | 64 | pending | pending |
| ssd/round_5/generation_policy | 16 | pending | pending |
| ssd/round_5/generation_policy | 64 | pending | pending |
| ssd/round_5/evaluation | 16 | 3.710 [3.380, 4.060]; 500/500 tasks, full | 0.000 [0.000, 0.000]; 172/500 tasks, partial |
| ssd/round_5/evaluation | 64 | pending | pending |

## Coverage at a fixed correct-sample budget

These conditional estimates use only correct samples and require at least the displayed number of correct samples per task. Different eligible-task populations must not be interpreted as whole-task improvements.

| Stage | Correct-sample budget b | Correct-conditioned AST richness @b | Annotated strategy coverage |
| --- | ---: | --- | --- |
| base/evaluation | 4 | 3.311 [3.217, 3.402]; 260/500 tasks, partial | unavailable (0/500 tasks) |
| base/evaluation | 8 | 5.646 [5.387, 5.929]; 193/500 tasks, partial | unavailable (0/500 tasks) |
| base/evaluation | 16 | 7.387 [6.549, 8.290]; 62/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_1/generation_policy | pending | pending | pending |
| ssd/round_1/evaluation | 4 | 3.232 [3.133, 3.333]; 260/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_1/evaluation | 8 | 5.328 [5.050, 5.614]; 193/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_1/evaluation | 16 | 7.509 [6.463, 8.549]; 53/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_2/generation_policy | pending | pending | pending |
| ssd/round_2/evaluation | 4 | 3.200 [3.095, 3.305]; 250/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_2/evaluation | 8 | 5.292 [5.021, 5.590]; 189/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_2/evaluation | 16 | 6.325 [5.181, 7.526]; 40/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_3/generation_policy | pending | pending | pending |
| ssd/round_3/evaluation | 4 | 3.196 [3.090, 3.299]; 256/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_3/evaluation | 8 | 5.422 [5.121, 5.725]; 185/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_3/evaluation | 16 | 6.404 [5.378, 7.436]; 47/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_4/generation_policy | pending | pending | pending |
| ssd/round_4/evaluation | 4 | 3.181 [3.080, 3.288]; 257/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_4/evaluation | 8 | 5.375 [5.096, 5.678]; 192/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_4/evaluation | 16 | 6.947 [5.718, 8.185]; 38/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_5/generation_policy | pending | pending | pending |
| ssd/round_5/evaluation | 4 | 3.268 [3.178, 3.360]; 255/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_5/evaluation | 8 | 5.386 [5.118, 5.650]; 187/500 tasks, partial | unavailable (0/500 tasks) |
| ssd/round_5/evaluation | 16 | 6.800 [5.636, 8.022]; 40/500 tasks, partial | unavailable (0/500 tasks) |

## Paired comparisons

Deltas are candidate minus reference at draw budgets 16 and 64. Missing budgets remain pending. These descriptive estimates do not establish algorithm diversity or an automatic research conclusion.

| Candidate | Reference | Status | ΔPass@16 | ΔPass@64 | Reason |
| --- | --- | --- | --- | --- | --- |
| ssd/round_1/evaluation | base/evaluation | available | -0.002 [-0.026, 0.020]; 500/500 tasks, paired | pending | — |
| ssd/round_2/evaluation | base/evaluation | available | -0.010 [-0.032, 0.010]; 500/500 tasks, paired | pending | — |
| ssd/round_3/evaluation | base/evaluation | available | -0.008 [-0.034, 0.018]; 500/500 tasks, paired | pending | — |
| ssd/round_4/evaluation | base/evaluation | available | -0.004 [-0.032, 0.022]; 500/500 tasks, paired | pending | — |
| ssd/round_5/evaluation | base/evaluation | available | -0.012 [-0.040, 0.016]; 500/500 tasks, paired | pending | — |

Coverage and entropy deltas, including their intervals and paired eligibility, are included in the JSON report. Comparisons require matching explicit sampling and evaluation protocols, task IDs, metric budgets, and per-task sample counts.

## Budgets and training

| Stage | Generated samples | Generation tokens | Prompt tokens |
| --- | ---: | ---: | ---: |
| base/evaluation | 8000 | 1956808 | 526192 |
| ssd/round_1/generation_policy | unavailable | unavailable | unavailable |
| ssd/round_1/evaluation | 8000 | 1755723 | 526192 |
| ssd/round_2/generation_policy | unavailable | unavailable | unavailable |
| ssd/round_2/evaluation | 8000 | 1635816 | 526192 |
| ssd/round_3/generation_policy | unavailable | unavailable | unavailable |
| ssd/round_3/evaluation | 8000 | 1485364 | 526192 |
| ssd/round_4/generation_policy | unavailable | unavailable | unavailable |
| ssd/round_4/evaluation | 8000 | 1425795 | 526192 |
| ssd/round_5/generation_policy | unavailable | unavailable | unavailable |
| ssd/round_5/evaluation | 8000 | 1501593 | 526192 |

**ssd/round_1**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.3872394959515928, "optimizer_steps": 291, "seed": 44, "supervised_tokens_per_epoch": 1614418, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1311746, "length_capped_samples": 354, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**ssd/round_2**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.3669333655476774, "optimizer_steps": 291, "seed": 45, "supervised_tokens_per_epoch": 1522834, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1220162, "length_capped_samples": 321, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**ssd/round_3**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.3296882664893603, "optimizer_steps": 291, "seed": 46, "supervised_tokens_per_epoch": 1455221, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1152549, "length_capped_samples": 315, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**ssd/round_4**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.3016503546066915, "optimizer_steps": 291, "seed": 47, "supervised_tokens_per_epoch": 1378369, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1075697, "length_capped_samples": 278, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

**ssd/round_5**

Training statistics: `{"epochs": 1, "examples": 4656, "loss_scope": "all", "mean_loss": 1.2608390893479906, "optimizer_steps": 291, "seed": 48, "supervised_tokens_per_epoch": 1354918, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1052246, "length_capped_samples": 230, "prompt_tokens": 307328, "samples": 4656, "tasks": 291}`

## Wall time and memory

Elapsed time includes recorded attempts. CUDA peaks are recorded per stage; stage peaks must not be added as if they occurred simultaneously. Unrecorded costs remain unavailable.

| Run stage | Operation | Elapsed seconds | Peak allocated bytes | Peak reserved bytes |
| --- | --- | ---: | ---: | ---: |
| base/round_0 | evaluation | 2654.27518206893 | 6304199680 | 8430551040 |
| base/round_0 | model_loading | 5.848486725939438 | 3088346624 | 3286237184 |
| ssd/round_1 | model_loading | 1.2321206741034985 | 3097259520 | 3307208704 |
| ssd/round_1 | post_training_evaluation | 3384.7638026430504 | 6312784896 | 7539261440 |
| ssd/round_1 | sft | 1268.201509646955 | 4320449024 | 10525605888 |
| ssd/round_1 | training_generation | 2115.309274193016 | 6318401536 | 8606711808 |
| ssd/round_2 | model_loading | 1.1036821720190346 | 3105779200 | 3307208704 |
| ssd/round_2 | post_training_evaluation | 2748.7119781449437 | 6301773824 | 15814623232 |
| ssd/round_2 | sft | 1254.9343612419907 | 4320920064 | 15814623232 |
| ssd/round_2 | training_generation | 1781.2269305629889 | 6327216128 | 8579448832 |
| ssd/round_3 | model_loading | 1.030997694004327 | 3105779200 | 3307208704 |
| ssd/round_3 | post_training_evaluation | 2936.4503774029436 | 6302027776 | 14929625088 |
| ssd/round_3 | sft | 1274.6769531379687 | 4320920064 | 14929625088 |
| ssd/round_3 | training_generation | 1834.5565974490019 | 6327216128 | 8579448832 |
| ssd/round_4 | model_loading | 1.0421923340763897 | 3105779200 | 3307208704 |
| ssd/round_4 | post_training_evaluation | 3042.8353078759974 | 6301773824 | 14852030464 |
| ssd/round_4 | sft | 1277.7264816479292 | 4320920064 | 14852030464 |
| ssd/round_4 | training_generation | 1834.717230431037 | 6327216128 | 8579448832 |
| ssd/round_5 | model_loading | 1.0321697120089084 | 3105779200 | 3307208704 |
| ssd/round_5 | post_training_evaluation | 3042.156086345087 | 6301773824 | 15808331776 |
| ssd/round_5 | sft | 1269.9517815719591 | 4320920064 | 15808331776 |
| ssd/round_5 | training_generation | 1824.9651086620288 | 6327216128 | 8579448832 |

## Appendix: Pass@1 and correctness noninferiority

Pass@1 and the original correctness criterion are retained as supplementary diagnostics. They do not determine the main Pass@16/Pass@64 and diversity conclusions.

| Stage | Pass@1 |
| --- | --- |
| base/evaluation | 0.378 [0.346, 0.413]; 500/500 tasks, full |
| ssd/round_1/generation_policy | pending |
| ssd/round_1/evaluation | 0.378 [0.346, 0.412]; 500/500 tasks, full |
| ssd/round_2/generation_policy | pending |
| ssd/round_2/evaluation | 0.368 [0.336, 0.402]; 500/500 tasks, full |
| ssd/round_3/generation_policy | pending |
| ssd/round_3/evaluation | 0.366 [0.335, 0.399]; 500/500 tasks, full |
| ssd/round_4/generation_policy | pending |
| ssd/round_4/evaluation | 0.371 [0.339, 0.405]; 500/500 tasks, full |
| ssd/round_5/generation_policy | pending |
| ssd/round_5/evaluation | 0.360 [0.330, 0.394]; 500/500 tasks, full |

Correctness noninferiority uses the task-macro correct fraction (Pass@1), an absolute margin of 0.010, and the lower endpoint of a two-sided 95% paired task-bootstrap interval. It requires all tasks.

| Candidate | Reference | Status | Pass@1 delta | Noninferiority | Reason |
| --- | --- | --- | --- | --- | --- |
| ssd/round_1/evaluation | base/evaluation | available | -0.000 [-0.010, 0.011]; 500/500 tasks, paired | criterion not met | — |
| ssd/round_2/evaluation | base/evaluation | available | -0.010 [-0.021, 0.001]; 500/500 tasks, paired | criterion not met | — |
| ssd/round_3/evaluation | base/evaluation | available | -0.012 [-0.024, -0.000]; 500/500 tasks, paired | criterion not met | — |
| ssd/round_4/evaluation | base/evaluation | available | -0.007 [-0.020, 0.006]; 500/500 tasks, paired | criterion not met | — |
| ssd/round_5/evaluation | base/evaluation | available | -0.018 [-0.032, -0.005]; 500/500 tasks, paired | criterion not met | — |

The JSON report preserves all metric budgets, Pass@1 and correctness comparisons, generation budgets, training statistics, full sampling metadata, evaluation provenance, and eligibility details. Sampling budget and correctness can change observed diversity; no model-performance claim follows from a report being complete.
