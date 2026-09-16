# Post-run effect audit

This audit separates implementation failures from weak or inconclusive
experimental effects.

## What worked

- All 30 method-rounds completed and all 480 evaluation samples were verified.
- The `plain`, `spd_hard`, and `spectral_soft` training and evaluation JSONL
  hashes differ in every round. The intervention paths did not collapse to an
  accidental no-op or reuse another method's samples.
- Spectral-soft operator diagnostics report eigenvalues from approximately
  0.5 to 1.0 and relative folded-weight changes of approximately 0.50 in the
  selected K/V projections. SPD-hard reports the expected rank-128 projector
  and larger relative changes. These records support that both interventions
  were applied.

## Weak result

Across the ten rounds, mean pass@1 was 0.406 for plain, 0.425 for SPD-hard and
0.381 for Spectral-soft. At round 10 it was 0.375, 0.438 and 0.312,
respectively. Mean AST coverage at four draws was 1.025, 1.075 and 0.900.
Spectral-soft therefore did not outperform either control in this smoke run.

These values are descriptive diagnostics, not an efficacy comparison. Each
round contains only four tasks and sixteen samples. The same four tasks recur
across rounds, correct-count-matched AST coverage often has only one or two
eligible tasks, intervals are very wide, and rounds are not independent
replicates. No parameter or method selection should use this smoke outcome.

## Limitations

- There are no independent semantic algorithm labels, so strategy coverage is
  unavailable. AST fingerprints remain implementation-structure proxies.
- Generation-policy diagnostics were deliberately disabled in the smoke
  profile. The run cannot separate intervention-time effects from effects after
  LoRA distillation.
- The run uses local generated-code execution and a tiny fixed task subset.
- Intermediate model weights were pruned to fit the machine. Samples, metrics,
  resource records and operator diagnostics remain, but old checkpoints cannot
  be reloaded from this archive. Training statistics were recovered for the 16
  retained checkpoints; statistics for the 14 deleted checkpoints are
  unavailable.

## Engineering issue and fix

The original multi-round runner retained a roughly 2.9 GB merged checkpoint
for every round and exhausted the 100 GB filesystem halfway through this run.
The pipeline now supports `checkpoint_retention: latest`. It seals the next
round before pruning the superseded model, retains the newest resumable
checkpoint for each method, records the pruned hashes in `complete.json`, and
saves `training_stats.json` outside the model directory so reports remain
complete after pruning. The retention profiles enable this policy.

The research limitation remains: deciding whether Spectral-soft helps requires
the preregistered larger task/seed experiment or a smaller prospective run with
enough tasks and samples for stable paired estimates. The smoke result provides
no basis for claiming a gain.
