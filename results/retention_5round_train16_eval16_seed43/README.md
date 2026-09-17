# Five-round MBPP self-evolution results (seed 43)

This is the compact evidence bundle for the completed full-task run. Each round generated 16 candidates for each of 291 training tasks, trained one LoRA epoch on all 4,656 raw candidates, and evaluated 16 samples on all 500 held-out MBPP tasks. Three methods ran for five rounds. Verification completed with exit code 0.

| Method | Round-5 pass@1 | 95% CI | Correct-matched AST coverage (4 correct draws) | Eligible tasks |
| --- | ---: | --- | ---: | ---: |
| base | 0.3792 | [0.3469, 0.4140] | 3.310 | 262/500 |
| plain | 0.4130 | [0.3794, 0.4498] | 2.747 | 268/500 |
| spd_hard | 0.4135 | [0.3794, 0.4514] | 2.690 | 262/500 |
| spectral_soft | 0.4017 | [0.3685, 0.4375] | 2.997 | 263/500 |

## Interpretation

At round 5, spectral-soft retained more correct-program AST coverage than plain and SPD-hard in point estimates. This is the conditional expected coverage in four draws from the correct samples, not coverage from four total generations. Its paired coverage advantage over SPD-hard was +0.293 [0.233, 0.353] on 251 shared eligible tasks. Pass@1 was 0.402 versus 0.413 for both controls. The paired pass@1 delta versus SPD-hard was -0.0118 [-0.0190, -0.0048], so the declared 1% noninferiority criterion was not met. Spectral-soft remained above the base model in pass@1 (+0.0225 [0.0120, 0.0335]) while all methods lost diversity relative to base across five rounds.

This is a single-seed run. The original round reports use 16 evaluation
samples per task; the completed final-checkpoint supplement uses 64 samples per
task and is reported in [`eval64/`](eval64/REPORT.md). AST fingerprints are
implementation proxies rather than independently annotated algorithms.
Correct-matched coverage is conditional on tasks with enough correct samples
for the stated budget. Generation-policy diagnostics were intentionally
disabled for the runtime-constrained profile. Generated programs and
intermediate 2.9 GB checkpoints are omitted from GitHub; the final checkpoints
are published on Hugging Face.

- `metrics.csv`: compact per-round metrics
- `round5_comparisons.json`: paired final-round comparisons
- `report.md` / `report.json`: complete generated report and per-task statistics
- `MODEL_FILES.sha256`: final checkpoint checksums
- `config.yaml`, `manifest.json`, `run_status.json`: frozen provenance
- `eval64/`: final-checkpoint 500-task x 64-sample report, compact aggregates,
  paired comparisons, and source checksums
