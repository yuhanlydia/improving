# Formal Diversity Implementation Plan

> **For agentic workers:** Use subagent-driven implementation with independent module ownership and integrated review.

**Goal:** Deliver runnable formal diversity experiments to the authorized GitHub repository.

**Architecture:** A frozen suite manifest compiles ordinary pipeline jobs. Pure crossed-bootstrap statistics consume saved per-question summaries. An independent transfer worker uses official EvalPlus in Docker. Reporting and archive export are model-free.

**Tech Stack:** Python, PyTorch, Transformers, PEFT, Docker, YAML, NumPy.

**Spec:** docs/superpowers/specs/2026-09-14-formal-diversity.md

## Global constraints

- Diversity is primary; correctness margin is 0.01, fixed before confirmation.
- No GPU experiment is executed during implementation.
- All training outputs enter ordinary LoRA. Strategy labels are evaluation-only.
- No test-based tau/seed/round selection. No hooks.
- Full task membership and all expected seeds are checked before a decision.

## Tasks

- [x] Fix verification and geometry protocol composition. Two individually
  verified tasks must aggregate identically to a joint call; changing one task
  harness must still fail comparison. A prose-plus-fence correct program must
  pass `first_fence` through geometry and EvalPlus export/import.
- [x] Implement spectral controls and budgeted policy diagnostics. Verify gains,
  random orientation, Frobenius matching and infeasible blend rejection.
- [x] Implement `compare_seed_summaries(previous,current,...)` with crossed
  resampling, paired eligibility, simultaneous intervals and seed completeness.
- [x] Implement suite compilation and `improving formal` stages. Validate all
  jobs before model execution, seal identities, reject changed resume inputs,
  and report partial runs without treating them as complete evidence.
- [x] Implement official held-out HumanEval+ transfer. Preserve every sample,
  source identity, evaluator metadata and failed attempt; reuse only intact
  results. Test orchestration with mocks and trusted fixtures.
- [x] Write profiles, direct-run script and protocol; generate comparable
  per-seed tables, pointwise and simultaneous intervals, and evidence archives.
- [ ] Publish the integrated code to GitHub main without force.

## Validation status

Component regression checks were run during implementation. The user then
explicitly requested code delivery without further testing. No additional
tests or GPU experiments were run after that instruction; the full integrated
formal workflow has not been executed here. Test files are provided for later
execution by the user.
