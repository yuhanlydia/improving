# Solution Subspace Geometry Implementation Plan

> **For agentic workers:** Use subagent-driven implementation with independent mathematical and integration review.

**Goal:** A runnable, resumable coding experiment for solution subspace relationships and held-out generation.

**Architecture:** Keep the existing self-distillation runner intact. Add compact geometry extraction, pure subspace algebra, discovery-bank analysis, and a separate staged runner with validation-only selection.

**Tech Stack:** Python, PyTorch, pinned Transformers, Docker verifier, YAML, optional Matplotlib.

**Spec:** docs/geometry_design.md

## Global Constraints

- Native pre-RoPE K/V coordinates; no activation hooks.
- Frozen model throughout this diagnostic, one question per data partition.
- Verification labels only from task tests; no strategy labels in fitting.
- No silent truncation, fabricated subspace rank or fabricated zero-correct results.
- Preserve raw outputs and all immutable artifact identities.

## Tasks

- [x] Implement `geometry.py`: compact SVD, principal angles, containment, span and Grassmann interpolation. Test known nested/orthogonal spaces, gauge changes and endpoints.
- [x] Implement `geometry_extraction.py`: real per-implementation native K/V gradients and completion scoring. Test tiny Qwen gradients, prompt masks, state restoration and absence of hooks.
- [x] Implement `geometry_analysis.py`: within-question summaries, deterministic discovery-only representative banks and equal-norm operator controls. Test rank failures, source isolation and controls.
- [x] Implement `geometry_study.py`: split checks, resumable generation/verification/extraction, relation experiments, validation selection and locked held-out controls. Test an end-to-end tiny-model fixture and interrupted resume identities.
- [x] Expose `improving geometry --config ... --stage all --resume`, full and 100-task 16/24 GB profiles, and a direct-run shell script. Document actual budgets, labels, selection criteria and limits.
- [x] Run meaningful CPU integration and mathematical tests, review the final patch, prepare the verified patch for publication to the authorized GitHub repository.
