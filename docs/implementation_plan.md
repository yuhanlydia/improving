# Coding diversity implementation plan

Goal: deliver a runnable, tested coding self-distillation repository at yuhanlydia/improving. Architecture and interfaces: [design.md](design.md).

- [x] Data and verification: deterministic train/calibration/validation/heldout preparation; preserve all completions; controlled execution and EvalPlus import/export. Tests cover split overlaps, incorrect/timeout code, malformed inputs. Real MBPP preparation also passed after deterministic overlap removal.
- [x] Metrics: exact finite-sample pass and coverage formulas; conditional correct coverage and stable-label retention. Compared against exhaustive small enumerations and known examples.
- [x] Spectral intervention: CPU covariance eigensystem; identity/hard/random/blend/proximal operators; reversible folding; explicit-module gradient capture. Tests check bias transformation, orthonormality, all-token gradients and full-model equivalence.
- [x] Integration: same prompt serialization, complete generation records, raw-completion LoRA SFT, checkpoint lifecycle, CLI, multi-round manifest/resume and stage-separated diagnostics. Tiny random-model smoke checks the real paths.
- [x] Experiment handoff: 16/24 GB profiles, official-source audit, mathematical assumptions, first-round experiment and expansion gates, exact commands, CI.
- [x] Independent review and targeted fixes; validated changes prepared for GitHub publication. See validation.md for evidence and untested execution environments.

Constraints: no benchmark results fabricated; no claim of exact SPD/SSD reproduction where source details differ; no hook in candidate path; no training correctness filtering; no unsafe silent host execution; no full benchmark or GPU training launched here.
