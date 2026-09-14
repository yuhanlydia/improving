# ICLR validation roadmap

The seed-42 pilot motivates a confirmatory study; it does not establish the
paper claim by itself. The candidate claim is:

> Under a pre-registered correctness-noninferiority constraint, full-spectrum
> proximal attenuation improves the breadth and within-task diversity of
> correct code generations relative to ordinary self-training and hard
> projection controls.

## Freeze before the next run

- Code extraction: `first_fence`.
- Primary correctness endpoint: task-macro pass@1 with an absolute 1 percentage
  point noninferiority margin selected on validation data.
- Primary diversity endpoint: AST coverage in four draws from correct samples.
- Secondary endpoints: pass@8/32/64, solved-task breadth, exact-program and AST
  unique fractions, effective label count, Simpson diversity, control-flow
  proxy diversity and lexical token-set distance.
- Confirmatory comparisons: spectral-soft versus SPD-hard and plain. SSD is a
  decoding control; its intervention-time result is not directly attributable
  to representation geometry because its decoder differs.
- Statistical unit: paired evaluation task; report simultaneous or FDR-adjusted
  intervals for the declared secondary family.

## Required evidence

1. Run at least five training seeds with fixed task IDs and three independently
   selected task subsets; do not select seeds after seeing evaluation outcomes.
2. Re-run with Docker or official EvalPlus execution and preserve explicit
   verifier, prompt, decoding, model and task-test provenance.
3. Add HumanEval+ and a frozen harder benchmark whose tasks admit meaningful
   algorithmic alternatives.
4. Label a blinded, pre-specified subset of correct programs with audited
   semantic algorithm classes; AST and control-flow fingerprints remain proxy
   outcomes.
5. Tune `tau` only on validation tasks, then freeze it. Include tau=0 identity,
   residual-blend, random rank-matched, rank/tau sweeps and equal-compute
   controls.
6. Test whether the intervention-time diversity shift survives 1, 3 and 5
   generate-train rounds, reporting token/FLOP budgets and calibration cost.

## Decision rule

Call the central result supported only if spectral-soft passes the frozen
correctness-noninferiority test and improves the primary fixed-correct diversity
endpoint against SPD-hard on the confirmatory aggregate. Treat all current
single-seed findings and newly introduced proxy metrics as exploratory.
