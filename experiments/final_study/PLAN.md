# Final SPECTRUM study: implementation and stopping contract

The user requested one final executable study followed by paper writing. This
extension keeps the existing SPECTRUM definition fixed. It does not choose a new
method or checkpoint using MBPP, HumanEval+, or APPS test outcomes.

## Fixed experiment

- Qwen2.5-Coder-1.5B-Instruct, pinned revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Main: Plain, SSD decoding-recipe adaptation, SPECTRUM (tau=1, all-token SFT),
  seeds 43/44/45, five rounds each: 45 method-seed-rounds.
- Diagnostics: seed 43, one round each of SPECTRUM tau=0.5, matched isotropic
  attenuation, and a matched Plain/SPECTRUM completion-only pair: four more
  method-seed-rounds. These are diagnostic ablations, never automatically
  promoted to the main result.
- All rounds: 291 training tasks x 16 unfiltered completions, one LoRA epoch;
  MBPP 500 tasks x 64 native-student samples; generation-policy diagnostic on
  a fixed 128-task subset x 16 samples. Retain all checkpoints and diagnostics.
- Final main checkpoints: HumanEval+ 164 and APPS Intro 200 tasks, n=16, frozen
  transfer without target training or calibration. Use official EvalPlus for
  HumanEval+ and clearly label the existing adapted APPS protocol.
- Stop after all requested artifacts are complete, regardless of effect size,
  significance, or sign. No automatic extra seed, round, model, or parameter.

## Implementation ownership

1. `scripts/run_final_study.py`: immutable planning, input/code provenance,
   finite execution, dependency checks, per-job locks, resume and status.
2. `scripts/report_final_study.py`: all planned endpoints, task-paired effects,
   seed summaries, aligned pre-generation/post-generation/post-SFT diagnostics,
   resource/error summaries and explicit missing cells.
3. `src/improving/reporting.py` and `longitudinal.py`: honor explicitly requested
   post-hoc evaluation rounds; do not label an evaluated round-5-only study
   incomplete because rounds 1-4 were not requested.
4. `src/improving/verification.py`: bounded exception metadata without changing
   correctness decisions, candidate code, or the number of executions.
5. `experiments/final_study/README.md`: runnable commands, budget and paper scope.

## Verification boundary

The user has asked for code without running experiments or tests. No training,
model loading, generated-code execution, pytest or benchmark is run during this
implementation. Review changes independently, inspect call signatures and
parse Python syntax. Regression-test source may be provided for later use; it
must not be described as executed or passing. Push only after static review.

Historical results remain immutable. Changed configurations and verifier
provenance use new output directories. Repository-backed files stay in Git.
