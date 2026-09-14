# Seed-42 code-centric pilot

This is an exploratory sensitivity analysis of the artifacts generated from
commit `7dc18f9` with Qwen2.5-Coder-1.5B-Instruct, 64 held-out MBPP tasks and 64
samples per task. It preserves the original strict results and re-verifies the
first Python/`py`/untagged fenced block using the task tests.

The strict extractor accepted a fenced answer only when the whole completion
was exactly one fence. Although 4093--4096 of 4096 completions per stage had a
code fence, only 194--299 were standalone fences. This made roughly 95% of the
original outcomes `compile_error`. First-fence extraction reduces final-stage
compile errors to 28--34 of 4096.

## Final checkpoints

| Metric | Plain | SSD | SPD-hard | Spectral-soft |
|---|---:|---:|---:|---:|
| correct / 4096 | 1508 | **1511** | 1510 | 1501 |
| pass@1 | 36.82% | **36.89%** | 36.87% | 36.65% |
| pass@8 | 56.49% | **56.79%** | 55.78% | 56.18% |
| pass@32 | 61.61% | 61.66% | 60.84% | **63.11%** |
| pass@64 | 62.50% | 62.50% | 60.94% | **65.63%** |
| tasks with a correct sample | 40 | 40 | 39 | **42** |
| mean exact-program unique fraction | 0.802 | 0.797 | 0.796 | **0.814** |
| mean AST unique fraction | 0.622 | 0.622 | 0.616 | **0.649** |
| AST Simpson diversity | 0.864 | 0.863 | 0.869 | **0.872** |
| expected AST coverage in four correct draws | 3.393 | 3.391 | 3.409 | **3.422** |

Using one percentage point as a candidate margin for the confirmatory run,
spectral-soft is correctness-noninferior to all three controls. Against SSD,
its paired final-checkpoint deltas are:

- fixed-four-correct AST coverage: +0.0312, 95% CI [0.0095, 0.0550];
- exact-program unique fraction: +0.0083, 95% CI [0.0009, 0.0171];
- AST Simpson diversity: +0.0094, 95% CI [0.0034, 0.0162];
- pass@1: -0.244 percentage points, 95% CI [-0.854, 0.342] points;
- pass@64: +3.125 percentage points, 95% CI [0, 7.813] points.

Against SPD-hard at intervention time, spectral-soft has positive paired 95%
intervals for fixed-four-correct AST coverage, AST entropy, AST and exact-code
unique fractions, AST Simpson diversity, and lexical Jaccard distance.

## Interpretation

The pilot signal is a distributional trade-off: nearly unchanged single-draw
correctness, broader task coverage at larger sample budgets, and modestly more
distinct/balanced correct implementations. It is not yet evidence of distinct
semantic algorithms or an ICLR-level result.

This analysis is post hoc, uses one seed, uses local rather than Docker
execution, and reports pointwise intervals without multiple-comparison
correction. The first-fence rule, one-point noninferiority margin, and correct
budgets `[2, 4, 8]` must be frozen before multi-seed confirmation. Raw programs,
model weights and logs are intentionally not committed; `ARTIFACTS.sha256`
records the retained local artifact identities.
