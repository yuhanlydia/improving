# Ten-round retention smoke run (seed 43)

This directory publishes the completed functional smoke run for
`configs/retention_smoke_10round_32gb_local.yaml`. It ran Qwen2.5-Coder-1.5B-Instruct
for ten sequential rounds with `plain`, `spd_hard`, and `spectral_soft`. Each
round used 8 training tasks, 8 calibration tasks, 4 evaluation tasks, 4 samples
per evaluation task, and one SFT epoch. All 30 method-rounds completed and local
verification completed.

This is a pipeline and retention-mechanics check, not benchmark evidence. Four
evaluation tasks and four samples per task are too small for research claims or
pass@8/32/64 reporting.

## Published artifacts

- `summary.csv`: compact per-round accuracy and diversity metrics.
- `artifacts/report.md` and `artifacts/report.json`: full generated report.
- `artifacts/<method>/round_<n>/`: final generated samples, verified outcomes,
  metrics, operator diagnostics, calibration tensors, budgets, and resource logs.
- `artifacts/tasks/`, `manifest.json`, and `run_status.json`: frozen task and run
  provenance.
- `artifacts/run.log`: execution log including the recovered disk-full event.
- `ARTIFACTS.sha256`: hashes for every published file.

Model weights and atomic `.parts` generation caches are excluded. Intermediate
weights for plain rounds 1–9 and SPD-hard rounds 1–5 were deleted during the run
to recover disk space; retained runtime `complete.json` files therefore contain
model hash entries whose weight files are intentionally absent from this Git
archive. Generated programs, verified outcomes, metrics, and resource records
for every round are retained.
