# Evidence used by the current manuscript

`rewrite_sources.json` is an exact, selected-field snapshot of committed results at the recorded source commit. Its `provenance` entries include paths and SHA-256 hashes for every input. It includes the historical n16 MBPP trajectory, final n64 supplement, separate SSD continuation, training budgets, and compact per-task HumanEval+/APPS records.

`derived_analysis.json` contains calculations from this evidence only: paired transfer task bootstraps, sums of training-generation resources, and deterministic equal-correct-count examples. Bootstrap seed is 20260924, with 2,000 resamples. No new model generation or program execution is needed.

Use `../analyze_existing.py` to reproduce these calculations. The `--refresh-sources` flag reads the original archived files from a full repository checkout. Default execution reads the bundled snapshot.

Earlier `report.compact.json` and `eval64.compact.json` remain historical source selections, but the current figures use `rewrite_sources.json`. Intermediate-round n64 outputs, unrun geometry controls, further training seeds, and larger model results are not reconstructed or imputed.
