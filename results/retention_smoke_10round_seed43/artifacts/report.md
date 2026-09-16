# Coding self-distillation report

Result status: **complete**.

Numbers show task means with pointwise 95% task-bootstrap intervals and explicit eligible-task denominators. Partial means describe the eligible subset; they do not establish gains across all tasks. Pending measurements are not zeros.

## Correctness and evaluation stages

| Method | Round | Stage | Status | Pass@1 | Samples |
| --- | ---: | --- | --- | --- | ---: |
| base | 0 | evaluation | available | 0.312 [0.000, 0.750]; 4/4 tasks, full | 16 |
| plain | 1 | generation_policy | not_requested | pending | pending |
| plain | 1 | evaluation | available | 0.250 [0.000, 0.750]; 4/4 tasks, full | 16 |
| plain | 2 | generation_policy | not_requested | pending | pending |
| plain | 2 | evaluation | available | 0.438 [0.000, 0.875]; 4/4 tasks, full | 16 |
| plain | 3 | generation_policy | not_requested | pending | pending |
| plain | 3 | evaluation | available | 0.500 [0.125, 0.875]; 4/4 tasks, full | 16 |
| plain | 4 | generation_policy | not_requested | pending | pending |
| plain | 4 | evaluation | available | 0.312 [0.000, 0.750]; 4/4 tasks, full | 16 |
| plain | 5 | generation_policy | not_requested | pending | pending |
| plain | 5 | evaluation | available | 0.375 [0.000, 0.750]; 4/4 tasks, full | 16 |
| plain | 6 | generation_policy | not_requested | pending | pending |
| plain | 6 | evaluation | available | 0.438 [0.000, 0.875]; 4/4 tasks, full | 16 |
| plain | 7 | generation_policy | not_requested | pending | pending |
| plain | 7 | evaluation | available | 0.375 [0.000, 0.750]; 4/4 tasks, full | 16 |
| plain | 8 | generation_policy | not_requested | pending | pending |
| plain | 8 | evaluation | available | 0.562 [0.125, 1.000]; 4/4 tasks, full | 16 |
| plain | 9 | generation_policy | not_requested | pending | pending |
| plain | 9 | evaluation | available | 0.438 [0.125, 0.812]; 4/4 tasks, full | 16 |
| plain | 10 | generation_policy | not_requested | pending | pending |
| plain | 10 | evaluation | available | 0.375 [0.000, 0.750]; 4/4 tasks, full | 16 |
| spd_hard | 1 | generation_policy | not_requested | pending | pending |
| spd_hard | 1 | evaluation | available | 0.375 [0.062, 0.812]; 4/4 tasks, full | 16 |
| spd_hard | 2 | generation_policy | not_requested | pending | pending |
| spd_hard | 2 | evaluation | available | 0.500 [0.125, 0.875]; 4/4 tasks, full | 16 |
| spd_hard | 3 | generation_policy | not_requested | pending | pending |
| spd_hard | 3 | evaluation | available | 0.500 [0.125, 0.875]; 4/4 tasks, full | 16 |
| spd_hard | 4 | generation_policy | not_requested | pending | pending |
| spd_hard | 4 | evaluation | available | 0.375 [0.000, 0.750]; 4/4 tasks, full | 16 |
| spd_hard | 5 | generation_policy | not_requested | pending | pending |
| spd_hard | 5 | evaluation | available | 0.375 [0.062, 0.812]; 4/4 tasks, full | 16 |
| spd_hard | 6 | generation_policy | not_requested | pending | pending |
| spd_hard | 6 | evaluation | available | 0.438 [0.000, 0.875]; 4/4 tasks, full | 16 |
| spd_hard | 7 | generation_policy | not_requested | pending | pending |
| spd_hard | 7 | evaluation | available | 0.312 [0.000, 0.750]; 4/4 tasks, full | 16 |
| spd_hard | 8 | generation_policy | not_requested | pending | pending |
| spd_hard | 8 | evaluation | available | 0.500 [0.125, 0.875]; 4/4 tasks, full | 16 |
| spd_hard | 9 | generation_policy | not_requested | pending | pending |
| spd_hard | 9 | evaluation | available | 0.438 [0.125, 0.812]; 4/4 tasks, full | 16 |
| spd_hard | 10 | generation_policy | not_requested | pending | pending |
| spd_hard | 10 | evaluation | available | 0.438 [0.000, 0.875]; 4/4 tasks, full | 16 |
| spectral_soft | 1 | generation_policy | not_requested | pending | pending |
| spectral_soft | 1 | evaluation | available | 0.312 [0.000, 0.750]; 4/4 tasks, full | 16 |
| spectral_soft | 2 | generation_policy | not_requested | pending | pending |
| spectral_soft | 2 | evaluation | available | 0.438 [0.000, 0.875]; 4/4 tasks, full | 16 |
| spectral_soft | 3 | generation_policy | not_requested | pending | pending |
| spectral_soft | 3 | evaluation | available | 0.500 [0.125, 0.875]; 4/4 tasks, full | 16 |
| spectral_soft | 4 | generation_policy | not_requested | pending | pending |
| spectral_soft | 4 | evaluation | available | 0.312 [0.000, 0.750]; 4/4 tasks, full | 16 |
| spectral_soft | 5 | generation_policy | not_requested | pending | pending |
| spectral_soft | 5 | evaluation | available | 0.375 [0.000, 0.750]; 4/4 tasks, full | 16 |
| spectral_soft | 6 | generation_policy | not_requested | pending | pending |
| spectral_soft | 6 | evaluation | available | 0.438 [0.000, 0.875]; 4/4 tasks, full | 16 |
| spectral_soft | 7 | generation_policy | not_requested | pending | pending |
| spectral_soft | 7 | evaluation | available | 0.375 [0.000, 0.750]; 4/4 tasks, full | 16 |
| spectral_soft | 8 | generation_policy | not_requested | pending | pending |
| spectral_soft | 8 | evaluation | available | 0.375 [0.000, 0.750]; 4/4 tasks, full | 16 |
| spectral_soft | 9 | generation_policy | not_requested | pending | pending |
| spectral_soft | 9 | evaluation | available | 0.375 [0.000, 0.750]; 4/4 tasks, full | 16 |
| spectral_soft | 10 | generation_policy | not_requested | pending | pending |
| spectral_soft | 10 | evaluation | available | 0.312 [0.000, 0.750]; 4/4 tasks, full | 16 |

## Correct implementation and annotated strategy coverage

Implementation coverage uses conservative Python AST fingerprints. These are implementation proxies, not algorithm identities. Strategy coverage uses supplied independent labels only; incomplete annotations remain unavailable. Wrong completions remain in the draw population.

| Stage | Draw budget K | Implementation proxy coverage | Annotated strategy coverage |
| --- | ---: | --- | --- |
| base/evaluation | 1 | 0.312 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| base/evaluation | 4 | 0.500 [0.000, 1.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_1/generation_policy | pending | pending | pending |
| plain/round_1/evaluation | 1 | 0.250 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 3/4 tasks, partial |
| plain/round_1/evaluation | 4 | 0.500 [0.000, 1.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 3/4 tasks, partial |
| plain/round_2/generation_policy | pending | pending | pending |
| plain/round_2/evaluation | 1 | 0.438 [0.000, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_2/evaluation | 4 | 1.000 [0.000, 2.250]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_3/generation_policy | pending | pending | pending |
| plain/round_3/evaluation | 1 | 0.500 [0.125, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| plain/round_3/evaluation | 4 | 1.250 [0.250, 2.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| plain/round_4/generation_policy | pending | pending | pending |
| plain/round_4/evaluation | 1 | 0.312 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_4/evaluation | 4 | 0.750 [0.000, 1.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_5/generation_policy | pending | pending | pending |
| plain/round_5/evaluation | 1 | 0.375 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_5/evaluation | 4 | 1.000 [0.000, 2.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_6/generation_policy | pending | pending | pending |
| plain/round_6/evaluation | 1 | 0.438 [0.000, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_6/evaluation | 4 | 1.000 [0.000, 2.250]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_7/generation_policy | pending | pending | pending |
| plain/round_7/evaluation | 1 | 0.375 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_7/evaluation | 4 | 0.750 [0.000, 1.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_8/generation_policy | pending | pending | pending |
| plain/round_8/evaluation | 1 | 0.562 [0.125, 1.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| plain/round_8/evaluation | 4 | 1.750 [0.500, 3.250]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| plain/round_9/generation_policy | pending | pending | pending |
| plain/round_9/evaluation | 1 | 0.438 [0.125, 0.812]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| plain/round_9/evaluation | 4 | 1.500 [0.500, 2.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| plain/round_10/generation_policy | pending | pending | pending |
| plain/round_10/evaluation | 1 | 0.375 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| plain/round_10/evaluation | 4 | 0.750 [0.000, 1.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spd_hard/round_1/generation_policy | pending | pending | pending |
| spd_hard/round_1/evaluation | 1 | 0.375 [0.062, 0.812]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_1/evaluation | 4 | 1.000 [0.250, 1.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_2/generation_policy | pending | pending | pending |
| spd_hard/round_2/evaluation | 1 | 0.500 [0.125, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_2/evaluation | 4 | 1.250 [0.250, 2.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_3/generation_policy | pending | pending | pending |
| spd_hard/round_3/evaluation | 1 | 0.500 [0.125, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_3/evaluation | 4 | 1.250 [0.250, 2.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_4/generation_policy | pending | pending | pending |
| spd_hard/round_4/evaluation | 1 | 0.375 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spd_hard/round_4/evaluation | 4 | 1.000 [0.000, 2.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spd_hard/round_5/generation_policy | pending | pending | pending |
| spd_hard/round_5/evaluation | 1 | 0.375 [0.062, 0.812]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_5/evaluation | 4 | 1.000 [0.250, 1.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_6/generation_policy | pending | pending | pending |
| spd_hard/round_6/evaluation | 1 | 0.438 [0.000, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spd_hard/round_6/evaluation | 4 | 1.000 [0.000, 2.250]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spd_hard/round_7/generation_policy | pending | pending | pending |
| spd_hard/round_7/evaluation | 1 | 0.312 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spd_hard/round_7/evaluation | 4 | 0.500 [0.000, 1.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spd_hard/round_8/generation_policy | pending | pending | pending |
| spd_hard/round_8/evaluation | 1 | 0.500 [0.125, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_8/evaluation | 4 | 1.500 [0.500, 2.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_9/generation_policy | pending | pending | pending |
| spd_hard/round_9/evaluation | 1 | 0.438 [0.125, 0.812]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_9/evaluation | 4 | 1.250 [0.500, 2.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spd_hard/round_10/generation_policy | pending | pending | pending |
| spd_hard/round_10/evaluation | 1 | 0.438 [0.000, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spd_hard/round_10/evaluation | 4 | 1.000 [0.000, 2.250]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_1/generation_policy | pending | pending | pending |
| spectral_soft/round_1/evaluation | 1 | 0.312 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_1/evaluation | 4 | 0.750 [0.000, 1.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_2/generation_policy | pending | pending | pending |
| spectral_soft/round_2/evaluation | 1 | 0.438 [0.000, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_2/evaluation | 4 | 1.000 [0.000, 2.250]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_3/generation_policy | pending | pending | pending |
| spectral_soft/round_3/evaluation | 1 | 0.500 [0.125, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spectral_soft/round_3/evaluation | 4 | 1.250 [0.250, 2.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 1/4 tasks, partial |
| spectral_soft/round_4/generation_policy | pending | pending | pending |
| spectral_soft/round_4/evaluation | 1 | 0.312 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_4/evaluation | 4 | 0.750 [0.000, 1.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_5/generation_policy | pending | pending | pending |
| spectral_soft/round_5/evaluation | 1 | 0.375 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_5/evaluation | 4 | 1.000 [0.000, 2.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_6/generation_policy | pending | pending | pending |
| spectral_soft/round_6/evaluation | 1 | 0.438 [0.000, 0.875]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_6/evaluation | 4 | 1.000 [0.000, 2.250]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_7/generation_policy | pending | pending | pending |
| spectral_soft/round_7/evaluation | 1 | 0.375 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_7/evaluation | 4 | 0.750 [0.000, 1.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_8/generation_policy | pending | pending | pending |
| spectral_soft/round_8/evaluation | 1 | 0.375 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_8/evaluation | 4 | 0.750 [0.000, 1.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_9/generation_policy | pending | pending | pending |
| spectral_soft/round_9/evaluation | 1 | 0.375 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_9/evaluation | 4 | 1.250 [0.000, 2.500]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_10/generation_policy | pending | pending | pending |
| spectral_soft/round_10/evaluation | 1 | 0.312 [0.000, 0.750]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |
| spectral_soft/round_10/evaluation | 4 | 0.500 [0.000, 1.000]; 4/4 tasks, full | 0.000 [0.000, 0.000]; 2/4 tasks, partial |

## Coverage at a fixed correct-sample budget

These conditional estimates use only correct samples and require at least the displayed number of correct samples per task. Different eligible-task populations must not be interpreted as whole-task improvements.

| Stage | Correct-sample budget | Implementation proxy coverage | Annotated strategy coverage |
| --- | ---: | --- | --- |
| base/evaluation | 2 | 1.000 [1.000, 1.000]; 1/4 tasks, partial | unavailable (0/4 tasks) |
| plain/round_1/generation_policy | pending | pending | pending |
| plain/round_1/evaluation | 2 | 1.500 [1.500, 1.500]; 1/4 tasks, partial | unavailable (0/4 tasks) |
| plain/round_2/generation_policy | pending | pending | pending |
| plain/round_2/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| plain/round_3/generation_policy | pending | pending | pending |
| plain/round_3/evaluation | 2 | 1.667 [1.000, 2.000]; 3/4 tasks, partial | unavailable (0/4 tasks) |
| plain/round_4/generation_policy | pending | pending | pending |
| plain/round_4/evaluation | 2 | 1.500 [1.500, 1.500]; 1/4 tasks, partial | unavailable (0/4 tasks) |
| plain/round_5/generation_policy | pending | pending | pending |
| plain/round_5/evaluation | 2 | 1.750 [1.500, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| plain/round_6/generation_policy | pending | pending | pending |
| plain/round_6/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| plain/round_7/generation_policy | pending | pending | pending |
| plain/round_7/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| plain/round_8/generation_policy | pending | pending | pending |
| plain/round_8/evaluation | 2 | 1.750 [1.500, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| plain/round_9/generation_policy | pending | pending | pending |
| plain/round_9/evaluation | 2 | 1.917 [1.833, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| plain/round_10/generation_policy | pending | pending | pending |
| plain/round_10/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spd_hard/round_1/generation_policy | pending | pending | pending |
| spd_hard/round_1/evaluation | 2 | 1.500 [1.500, 1.500]; 1/4 tasks, partial | unavailable (0/4 tasks) |
| spd_hard/round_2/generation_policy | pending | pending | pending |
| spd_hard/round_2/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spd_hard/round_3/generation_policy | pending | pending | pending |
| spd_hard/round_3/evaluation | 2 | 1.667 [1.000, 2.000]; 3/4 tasks, partial | unavailable (0/4 tasks) |
| spd_hard/round_4/generation_policy | pending | pending | pending |
| spd_hard/round_4/evaluation | 2 | 1.750 [1.500, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spd_hard/round_5/generation_policy | pending | pending | pending |
| spd_hard/round_5/evaluation | 2 | 1.500 [1.500, 1.500]; 1/4 tasks, partial | unavailable (0/4 tasks) |
| spd_hard/round_6/generation_policy | pending | pending | pending |
| spd_hard/round_6/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spd_hard/round_7/generation_policy | pending | pending | pending |
| spd_hard/round_7/evaluation | 2 | 1.000 [1.000, 1.000]; 1/4 tasks, partial | unavailable (0/4 tasks) |
| spd_hard/round_8/generation_policy | pending | pending | pending |
| spd_hard/round_8/evaluation | 2 | 1.750 [1.500, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spd_hard/round_9/generation_policy | pending | pending | pending |
| spd_hard/round_9/evaluation | 2 | 1.750 [1.500, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spd_hard/round_10/generation_policy | pending | pending | pending |
| spd_hard/round_10/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spectral_soft/round_1/generation_policy | pending | pending | pending |
| spectral_soft/round_1/evaluation | 2 | 1.500 [1.500, 1.500]; 1/4 tasks, partial | unavailable (0/4 tasks) |
| spectral_soft/round_2/generation_policy | pending | pending | pending |
| spectral_soft/round_2/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spectral_soft/round_3/generation_policy | pending | pending | pending |
| spectral_soft/round_3/evaluation | 2 | 1.667 [1.000, 2.000]; 3/4 tasks, partial | unavailable (0/4 tasks) |
| spectral_soft/round_4/generation_policy | pending | pending | pending |
| spectral_soft/round_4/evaluation | 2 | 1.500 [1.500, 1.500]; 1/4 tasks, partial | unavailable (0/4 tasks) |
| spectral_soft/round_5/generation_policy | pending | pending | pending |
| spectral_soft/round_5/evaluation | 2 | 1.750 [1.500, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spectral_soft/round_6/generation_policy | pending | pending | pending |
| spectral_soft/round_6/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spectral_soft/round_7/generation_policy | pending | pending | pending |
| spectral_soft/round_7/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spectral_soft/round_8/generation_policy | pending | pending | pending |
| spectral_soft/round_8/evaluation | 2 | 1.500 [1.000, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spectral_soft/round_9/generation_policy | pending | pending | pending |
| spectral_soft/round_9/evaluation | 2 | 1.917 [1.833, 2.000]; 2/4 tasks, partial | unavailable (0/4 tasks) |
| spectral_soft/round_10/generation_policy | pending | pending | pending |
| spectral_soft/round_10/evaluation | 2 | 1.000 [1.000, 1.000]; 1/4 tasks, partial | unavailable (0/4 tasks) |

## Paired comparisons

Deltas are candidate minus reference. Correctness noninferiority uses an absolute margin of 0.010 and the lower endpoint of a two-sided 95% paired task-bootstrap interval. It requires all tasks. These are descriptive statistical outputs, not automatic claims of algorithm diversity or a successful research result.

| Candidate | Reference | Status | Correctness delta | Noninferiority | Reason |
| --- | --- | --- | --- | --- | --- |
| plain/round_1/evaluation | base/evaluation | available | -0.062 [-0.188, 0.000]; 4/4 tasks, paired | criterion not met | — |
| plain/round_1/evaluation | spd_hard/round_1/evaluation | available | -0.125 [-0.250, 0.000]; 4/4 tasks, paired | criterion not met | — |
| plain/round_2/evaluation | base/evaluation | available | 0.125 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| plain/round_2/evaluation | spd_hard/round_2/evaluation | available | -0.062 [-0.188, 0.000]; 4/4 tasks, paired | criterion not met | — |
| plain/round_3/evaluation | base/evaluation | available | 0.188 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| plain/round_3/evaluation | spd_hard/round_3/evaluation | available | 0.000 [0.000, 0.000]; 4/4 tasks, paired | criterion met | — |
| plain/round_4/evaluation | base/evaluation | available | 0.000 [0.000, 0.000]; 4/4 tasks, paired | criterion met | — |
| plain/round_4/evaluation | spd_hard/round_4/evaluation | available | -0.062 [-0.188, 0.000]; 4/4 tasks, paired | criterion not met | — |
| plain/round_5/evaluation | base/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| plain/round_5/evaluation | spd_hard/round_5/evaluation | available | 0.000 [-0.188, 0.188]; 4/4 tasks, paired | criterion not met | — |
| plain/round_6/evaluation | base/evaluation | available | 0.125 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| plain/round_6/evaluation | spd_hard/round_6/evaluation | available | 0.000 [0.000, 0.000]; 4/4 tasks, paired | criterion met | — |
| plain/round_7/evaluation | base/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| plain/round_7/evaluation | spd_hard/round_7/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| plain/round_8/evaluation | base/evaluation | available | 0.250 [0.000, 0.562]; 4/4 tasks, paired | criterion met | — |
| plain/round_8/evaluation | spd_hard/round_8/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| plain/round_9/evaluation | base/evaluation | available | 0.125 [0.000, 0.250]; 4/4 tasks, paired | criterion met | — |
| plain/round_9/evaluation | spd_hard/round_9/evaluation | available | 0.000 [0.000, 0.000]; 4/4 tasks, paired | criterion met | — |
| plain/round_10/evaluation | base/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| plain/round_10/evaluation | spd_hard/round_10/evaluation | available | -0.062 [-0.188, 0.000]; 4/4 tasks, paired | criterion not met | — |
| spd_hard/round_1/evaluation | base/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| spd_hard/round_2/evaluation | base/evaluation | available | 0.188 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| spd_hard/round_3/evaluation | base/evaluation | available | 0.188 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| spd_hard/round_4/evaluation | base/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| spd_hard/round_5/evaluation | base/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| spd_hard/round_6/evaluation | base/evaluation | available | 0.125 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| spd_hard/round_7/evaluation | base/evaluation | available | 0.000 [0.000, 0.000]; 4/4 tasks, paired | criterion met | — |
| spd_hard/round_8/evaluation | base/evaluation | available | 0.188 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| spd_hard/round_9/evaluation | base/evaluation | available | 0.125 [0.000, 0.250]; 4/4 tasks, paired | criterion met | — |
| spd_hard/round_10/evaluation | base/evaluation | available | 0.125 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_1/evaluation | base/evaluation | available | 0.000 [0.000, 0.000]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_1/evaluation | spd_hard/round_1/evaluation | available | -0.062 [-0.188, 0.000]; 4/4 tasks, paired | criterion not met | — |
| spectral_soft/round_2/evaluation | base/evaluation | available | 0.125 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_2/evaluation | spd_hard/round_2/evaluation | available | -0.062 [-0.188, 0.000]; 4/4 tasks, paired | criterion not met | — |
| spectral_soft/round_3/evaluation | base/evaluation | available | 0.188 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_3/evaluation | spd_hard/round_3/evaluation | available | 0.000 [0.000, 0.000]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_4/evaluation | base/evaluation | available | 0.000 [0.000, 0.000]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_4/evaluation | spd_hard/round_4/evaluation | available | -0.062 [-0.188, 0.000]; 4/4 tasks, paired | criterion not met | — |
| spectral_soft/round_5/evaluation | base/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_5/evaluation | spd_hard/round_5/evaluation | available | 0.000 [-0.188, 0.188]; 4/4 tasks, paired | criterion not met | — |
| spectral_soft/round_6/evaluation | base/evaluation | available | 0.125 [0.000, 0.375]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_6/evaluation | spd_hard/round_6/evaluation | available | 0.000 [0.000, 0.000]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_7/evaluation | base/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_7/evaluation | spd_hard/round_7/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_8/evaluation | base/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_8/evaluation | spd_hard/round_8/evaluation | available | -0.125 [-0.250, 0.000]; 4/4 tasks, paired | criterion not met | — |
| spectral_soft/round_9/evaluation | base/evaluation | available | 0.062 [0.000, 0.188]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_9/evaluation | spd_hard/round_9/evaluation | available | -0.062 [-0.188, 0.000]; 4/4 tasks, paired | criterion not met | — |
| spectral_soft/round_10/evaluation | base/evaluation | available | 0.000 [0.000, 0.000]; 4/4 tasks, paired | criterion met | — |
| spectral_soft/round_10/evaluation | spd_hard/round_10/evaluation | available | -0.125 [-0.375, 0.000]; 4/4 tasks, paired | criterion not met | — |

Coverage and entropy deltas, including their intervals and paired eligibility, are included in the JSON report. Comparisons require matching explicit sampling and evaluation protocols, task IDs, metric budgets, and per-task sample counts.

## Budgets and training

| Stage | Generated samples | Generation tokens | Prompt tokens |
| --- | ---: | ---: | ---: |
| base/evaluation | 16 | 3440 | 1092 |
| plain/round_1/generation_policy | unavailable | unavailable | unavailable |
| plain/round_1/evaluation | 16 | 3105 | 1092 |
| plain/round_2/generation_policy | unavailable | unavailable | unavailable |
| plain/round_2/evaluation | 16 | 3362 | 1092 |
| plain/round_3/generation_policy | unavailable | unavailable | unavailable |
| plain/round_3/evaluation | 16 | 3174 | 1092 |
| plain/round_4/generation_policy | unavailable | unavailable | unavailable |
| plain/round_4/evaluation | 16 | 3470 | 1092 |
| plain/round_5/generation_policy | unavailable | unavailable | unavailable |
| plain/round_5/evaluation | 16 | 3424 | 1092 |
| plain/round_6/generation_policy | unavailable | unavailable | unavailable |
| plain/round_6/evaluation | 16 | 3050 | 1092 |
| plain/round_7/generation_policy | unavailable | unavailable | unavailable |
| plain/round_7/evaluation | 16 | 3313 | 1092 |
| plain/round_8/generation_policy | unavailable | unavailable | unavailable |
| plain/round_8/evaluation | 16 | 3513 | 1092 |
| plain/round_9/generation_policy | unavailable | unavailable | unavailable |
| plain/round_9/evaluation | 16 | 3454 | 1092 |
| plain/round_10/generation_policy | unavailable | unavailable | unavailable |
| plain/round_10/evaluation | 16 | 3097 | 1092 |
| spd_hard/round_1/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_1/evaluation | 16 | 3140 | 1092 |
| spd_hard/round_2/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_2/evaluation | 16 | 3365 | 1092 |
| spd_hard/round_3/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_3/evaluation | 16 | 3177 | 1092 |
| spd_hard/round_4/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_4/evaluation | 16 | 3346 | 1092 |
| spd_hard/round_5/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_5/evaluation | 16 | 3444 | 1092 |
| spd_hard/round_6/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_6/evaluation | 16 | 3104 | 1092 |
| spd_hard/round_7/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_7/evaluation | 16 | 3253 | 1092 |
| spd_hard/round_8/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_8/evaluation | 16 | 3488 | 1092 |
| spd_hard/round_9/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_9/evaluation | 16 | 3386 | 1092 |
| spd_hard/round_10/generation_policy | unavailable | unavailable | unavailable |
| spd_hard/round_10/evaluation | 16 | 3043 | 1092 |
| spectral_soft/round_1/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_1/evaluation | 16 | 3059 | 1092 |
| spectral_soft/round_2/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_2/evaluation | 16 | 3345 | 1092 |
| spectral_soft/round_3/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_3/evaluation | 16 | 3113 | 1092 |
| spectral_soft/round_4/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_4/evaluation | 16 | 3410 | 1092 |
| spectral_soft/round_5/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_5/evaluation | 16 | 3438 | 1092 |
| spectral_soft/round_6/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_6/evaluation | 16 | 3036 | 1092 |
| spectral_soft/round_7/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_7/evaluation | 16 | 3304 | 1092 |
| spectral_soft/round_8/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_8/evaluation | 16 | 3266 | 1092 |
| spectral_soft/round_9/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_9/evaluation | 16 | 3470 | 1092 |
| spectral_soft/round_10/generation_policy | unavailable | unavailable | unavailable |
| spectral_soft/round_10/evaluation | 16 | 3199 | 1092 |

**plain/round_1**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1498, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**plain/round_2**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1447, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**plain/round_3**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1447, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**plain/round_4**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1488, "length_capped_samples": 1, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**plain/round_5**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1564, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**plain/round_6**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1323, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**plain/round_7**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1410, "length_capped_samples": 4, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**plain/round_8**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1860, "length_capped_samples": 6, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**plain/round_9**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1298, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**plain/round_10**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.7908135950565338, "optimizer_steps": 1, "seed": 53, "supervised_tokens_per_epoch": 1899, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1405, "length_capped_samples": 2, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spd_hard/round_1**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1655, "length_capped_samples": 4, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spd_hard/round_2**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1481, "length_capped_samples": 2, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spd_hard/round_3**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1357, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spd_hard/round_4**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1480, "length_capped_samples": 1, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spd_hard/round_5**

Training statistics: unavailable

Training generation budget: `{"generation_tokens": 1522, "length_capped_samples": 2, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spd_hard/round_6**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.9606694728136063, "optimizer_steps": 1, "seed": 49, "supervised_tokens_per_epoch": 1771, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1277, "length_capped_samples": 2, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spd_hard/round_7**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.876946046948433, "optimizer_steps": 1, "seed": 50, "supervised_tokens_per_epoch": 1807, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1313, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spd_hard/round_8**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.6422794163227081, "optimizer_steps": 1, "seed": 51, "supervised_tokens_per_epoch": 2032, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1538, "length_capped_samples": 4, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spd_hard/round_9**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 2.11173178255558, "optimizer_steps": 1, "seed": 52, "supervised_tokens_per_epoch": 1678, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1184, "length_capped_samples": 2, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spd_hard/round_10**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.762989267706871, "optimizer_steps": 1, "seed": 53, "supervised_tokens_per_epoch": 2056, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1562, "length_capped_samples": 5, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spectral_soft/round_1**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.5961434096097946, "optimizer_steps": 1, "seed": 44, "supervised_tokens_per_epoch": 2094, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1600, "length_capped_samples": 4, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spectral_soft/round_2**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.7381977289915085, "optimizer_steps": 1, "seed": 45, "supervised_tokens_per_epoch": 1974, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1480, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spectral_soft/round_3**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.7794398814439774, "optimizer_steps": 1, "seed": 46, "supervised_tokens_per_epoch": 1862, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1368, "length_capped_samples": 1, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spectral_soft/round_4**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.5773076564073563, "optimizer_steps": 1, "seed": 47, "supervised_tokens_per_epoch": 2060, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1566, "length_capped_samples": 2, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spectral_soft/round_5**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.5670710504055023, "optimizer_steps": 1, "seed": 48, "supervised_tokens_per_epoch": 2074, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1580, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spectral_soft/round_6**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.9828344881534576, "optimizer_steps": 1, "seed": 49, "supervised_tokens_per_epoch": 1765, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1271, "length_capped_samples": 2, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spectral_soft/round_7**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.6892479062080383, "optimizer_steps": 1, "seed": 50, "supervised_tokens_per_epoch": 2092, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1598, "length_capped_samples": 4, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spectral_soft/round_8**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.5677783489227295, "optimizer_steps": 1, "seed": 51, "supervised_tokens_per_epoch": 2128, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1634, "length_capped_samples": 5, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spectral_soft/round_9**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 2.0528967827558517, "optimizer_steps": 1, "seed": 52, "supervised_tokens_per_epoch": 1832, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1338, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

**spectral_soft/round_10**

Training statistics: `{"epochs": 1, "examples": 8, "loss_scope": "all", "mean_loss": 1.679800033569336, "optimizer_steps": 1, "seed": 53, "supervised_tokens_per_epoch": 2100, "trainable_parameter_count": 2179072, "truncated_examples": 0, "truncated_tokens": 0}`

Training generation budget: `{"generation_tokens": 1606, "length_capped_samples": 3, "prompt_tokens": 502, "samples": 8, "tasks": 8}`

The JSON report preserves generation budgets, training statistics, full sampling metadata, evaluation provenance, and eligibility details. Sampling budget and correctness can change observed diversity; no model-performance claim follows from a report being complete.
