# Formal Spectral-soft study

The user authorized a runnable confirmation study of correct-code diversity,
with accuracy treated as a noninferiority constraint, after inspecting the
seed-42 pilot. No new GPU experiment is run during implementation.

## Primary question

Does Spectral-soft increase within-question correct implementation diversity
after ordinary raw-corpus LoRA self-distillation while preserving correctness
within one absolute percentage point? The primary endpoint is expected AST
coverage in four draws from correct completions. AST is a structural proxy,
not an algorithm annotation. Main comparisons are against plain self-training
and SPD-hard, at the final checkpoint of round one.

## Fixed protocol

- Full prepared MBPP: 291 training, 50 calibration, 30 reserved validation and
  500 evaluation tasks in the inspected snapshot. Actual counts are recorded.
- Fixed data seed 42; five new confirmation seeds 43–47; pilot seed42 remains exploratory. No test-set model selection.
- Raw corpus: one completion per training prompt, all retained for ordinary
  LoRA, including incorrect outputs. Correctness labels are evaluation-only.
- Common final decoding: 64 completions/question. Generating-policy diagnostics
  use a fixed 128-question subset and 32 completions/question to limit cost.
- First Python code fence extraction for every arm; task tests in Docker.
- Fixed tau=1 and hard rank fraction=0.5. No retrospective tuning or selection
  of the best seed/round. Changed protocol requires a new output directory.
- Secondary diversity curves use correct budgets 4/8/16 and total budgets
  1/8/32/64 where supported; eligibility is reported per seed and comparison.

## Experiment groups

1. Confirmation: plain, SSD, SPD-hard and Spectral-soft, five seeds, one round.
2. Mechanism: three additional controls, seeds 43–45, one round; use the
   corresponding confirmation Spectral-soft checkpoint as reference. Controls
   are equal-operator-norm residual blending, identical gains with random
   eigenvectors, and isotropic attenuation with equal operator perturbation.
3. Retention: plain/SPD-hard/Spectral-soft for three rounds and seeds 43–45.
   These are separately sealed trajectories; round one is deliberately rerun.
4. Transfer: the five confirmation runs' base and four final checkpoints on
   all 164 official HumanEval+ tasks. No HumanEval training or tuning.

## Statistics and evidence

Crossed seed-by-task bootstrap resamples seeds and shared question IDs, with
paired comparisons and recomputed eligibility. Confirmation uses simultaneous
Bonferroni intervals for two endpoints times two baseline comparisons. Success
requires positive primary diversity difference and correctness noninferiority.
Generation-stage, final-checkpoint, retention and transfer conclusions remain
separate. All expected seeds must finish before a confirmatory decision.

Save raw programs, verifier outcomes, per-task metrics, source/config hashes,
model identities, exact question sets, resource costs and failure attempts.
Generate compact portable evidence archives by default; optionally include raw
and verified programs. No weights or credentials enter these archives.

## Execution

Add a staged `improving formal` orchestrator around the existing pipeline, with
immutable suite and per-job manifests. Default shell entry runs confirmation;
`all` additionally runs mechanisms, retention, HumanEval+, reporting and export.
Report/export work without loading a model. The 16/24 GB labels are target
hardware profiles, not measured memory guarantees.

## Known fixes included

Make verifier identities invariant to batching without losing task-harness
identity; pass code extraction through geometry; preserve extraction identity
through EvalPlus export/import. Add real two-question regressions. No hooks,
prompt ensembles, manual strategy filtering, or strategy adapter pool.
