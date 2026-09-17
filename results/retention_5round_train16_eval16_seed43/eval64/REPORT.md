# Five-round self-evolution: final 64-sample evaluation

This is the supplemental final-checkpoint evaluation for the single-seed five-round run. It evaluates the base model and round-5 `plain`, `spd_hard`, and `spectral_soft` checkpoints on all 500 held-out MBPP tasks with 64 common-policy samples per task (32,000 samples per model).

## Results

| Model | pass@1 | pass@4 | pass@8 | pass@16 | pass@64 | total coverage@4 | total coverage@16 | total coverage@64 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base | 0.379 | 0.551 | 0.611 | 0.657 | 0.720 | 1.267 | 4.040 | 12.802 |
| plain | 0.414 | 0.565 | 0.619 | 0.656 | 0.704 | 1.166 | 3.159 | 8.506 |
| spd_hard | 0.418 | 0.566 | 0.619 | 0.656 | 0.702 | 1.153 | 3.103 | 8.388 |
| spectral_soft | 0.403 | 0.562 | 0.619 | 0.662 | 0.726 | 1.244 | 3.758 | 11.510 |

Correct-matched implementation coverage conditions on drawing the stated number of correct samples:

| Model | correct coverage@4 (eligible) | @8 (eligible) | @16 (eligible) | @64 (eligible) |
| --- | ---: | ---: | ---: | ---: |
| base | 3.358 (322/500) | 5.987 (294/500) | 10.423 (251/500) | 19.875 (24/500) |
| plain | 2.856 (321/500) | 4.690 (305/500) | 7.324 (263/500) | 8.686 (51/500) |
| spd_hard | 2.810 (321/500) | 4.590 (303/500) | 7.136 (264/500) | 7.981 (53/500) |
| spectral_soft | 3.143 (323/500) | 5.451 (302/500) | 9.091 (259/500) | 12.176 (34/500) |

## Main findings

- Relative to the intended hard-projection control (`spd_hard`), `spectral_soft` restores implementation coverage: total coverage improves by +0.091 [+0.066, +0.116] at draw budget 4 and +3.122 [+2.686, +3.596] at budget 64. Correct-matched coverage improves by +0.334 [+0.290, +0.379] at four correct draws.
- `spectral_soft` also improves pass@64 over `spd_hard` by +0.024 [+0.006, +0.044]. Its pass@1 is lower by -0.014 [-0.019, -0.010]. The correctness delta fails the preregistered absolute 0.01 noninferiority margin (`noninferior=false`).
- Relative to `plain`, `spectral_soft` gains +3.004 [+2.568, +3.494] total coverage@64 and +0.295 [+0.249, +0.343] correct-matched coverage@4, with pass@1 -0.011 [-0.016, -0.006].
- Relative to the base model, `spectral_soft` improves pass@1 by +0.024 [+0.016, +0.032] and has an inconclusive pass@64 difference of +0.006 [-0.018, +0.030]. It does not fully retain base diversity: total coverage@64 differs by -1.292 [-1.786, -0.780].

## Interpretation and limits

- The result supports the mechanism claim that soft spectral attenuation preserves substantially more implementation diversity than the hard projection after five rounds. It does not meet the stated correctness noninferiority gate against `plain` or `spd_hard` at the 0.01 margin.
- `spd_hard` is an aggressive hard-projection control; its lower coverage is expected and is evidence about the cost of hard removal, rather than an optimization failure.
- Correct-matched coverage@64 has small and model-dependent eligibility (24–53 tasks; only 30 paired tasks for `spectral_soft` versus `spd_hard`). Treat it as a sparse conditional diagnostic. Budgets 4, 8, and 16 are more stable.
- This run uses one training seed (43). Bootstrap intervals resample the 500 evaluation tasks and do not measure training-seed variation.
- AST fingerprints are implementation proxies, not audited semantic algorithm labels. Local execution used the recorded Python 3.11 task-test harness; all four models have identical recorded evaluator and task-harness provenance.

## Reproducibility

- Training: 291 MBPP training tasks × 16 raw completions per task × 5 self-evolution rounds; one LoRA epoch per round.
- Evaluation: seed 43, temperature 0.8, top-p 0.95, 64 samples per each of 500 held-out tasks.
- Exact aggregate values and task-bootstrap intervals are in `summary.csv`; compact paired results are in `comparisons_compact.json`; source-file hashes are in `manifest.json`.
