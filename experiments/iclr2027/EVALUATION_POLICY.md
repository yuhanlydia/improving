# Multi-answer evaluation policy — September 21, 2026

The user approved this policy after reviewing preliminary n16 results. It is a
post-hoc reporting change, not a preregistered endpoint selection.

## Main endpoints

- pass@16 and pass@64: probability of at least one correct answer in the draw budget.
- Correct implementation coverage@16 and @64, using the recorded AST fingerprint.
- Correct-sample-matched implementation diversity, with explicit eligible-task
  counts and a shared eligible population for comparisons.

AST differences are implementation proxies, not independently established
algorithm strategies. Strategy coverage requires complete independent labels.
Report all methods and benchmarks, including negative differences. Report paired
uncertainty where the sampling and verifier protocols are comparable.

## Audit and incomplete measurements

Keep pass@1 and other computed k values in raw JSON and an appendix; do not use
pass@1 as the main table or sole basis for the study conclusion. Keep any existing
pass@1 noninferiority calculation as a diagnostic, not a new primary endpoint.

An n16 run supports pass@16, but its pass@64 must remain unavailable. Never
extrapolate, duplicate samples, or mix changed generation protocols to fill it.
Existing running/frozen protocols and historical outputs remain unchanged.
New independent n64 evaluation runs provide the full main-endpoint budget.
Unstarted expansion runs use 64 evaluation samples after configuration validation;
training candidate count remains 16, seed 43, and five training rounds.

## Execution

Evaluate saved samples on CPU where possible. New candidate generation needs GPU
admission. Use the same sample budget and evaluation harness across comparison
arms. Archive/delete weights only after every dependent evaluation is complete.
