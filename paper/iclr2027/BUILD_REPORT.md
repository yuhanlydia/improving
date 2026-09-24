# Build and evidence checks — 2026-09-24

- Rebuilt all four figure PDFs/PNGs from archived measurements and exact vector instructions.
- Recomputed only CPU summaries of saved data: paired transfer task bootstrap, resource totals, and deterministic class-count examples. No training, sampling, or code verification ran.
- Checked source SHA-256 values against the committed files at the recorded input snapshot.
- Checked the finite-sample class-count formulas against saved transfer per-task metrics.
- Cross-checked main MBPP and transfer table values against the source snapshot, and checked the separate n16 projection/SSD rows and eligibility counts.
- Compiled the manuscript with `latexmk -pdf -interaction=nonstopmode -halt-on-error`.
- Final LaTeX log has no undefined references/citations, missing figures, overfull boxes, or compilation errors.
- Final PDF: 20 pages. Main text occupies exactly pages 1–9, including independent Limitations and Conclusion and future work sections. Excluded statements/references begin on page 10; appendices begin on page 13. No template margins, font sizes, or line spacing were modified.
- Rendered and visually inspected all pages; inspected the title, main results, method diagram, tables and figures at readable size. Tables/figures use monochrome styling.
- All 23 used bibliography keys resolve. Citation-entailment notes are in `CITATION_AUDIT.md`.
- Four figure design records each contain exactly three standalone English alternatives. Prompt lengths range from 2,571 to 3,094 characters, all below 5,000.
- No pending-result placeholders remain in the manuscript. Explicit protocol-template placeholders designate variable prompt fields only.

Scientific boundaries remain as reported in the paper: one main training seed/backbone, AST structural proxies, fixed external reference information, unmatched realized token costs, and dataset-dependent correctness trade-offs. Artifact checks do not turn those boundaries into additional experimental evidence.

## Nine-page revision

- Expanded the method with the gradient quadratic-form interpretation, rationale for recalibration, an algebraic gain example, the exact per-example student objective, and the respective roles of K/V modulation and native-student learning.
- Expanded Related Work into four themes, with primary-source checks for SSD, CRISP, sampled-demonstration diversity, and reference-gradient spectral generation.
- Split the former combined discussion into Limitations and Conclusion and future work, both within the nine-page body.
- Preserved all result tables, figure files, source snapshots, bibliography entries, and experimental settings. No analysis, model, training, sampling, or verifier run was added in this revision.
- The final log contains no unresolved references or citations and no overfull boxes. Standard underfull-box diagnostics were reviewed visually; no text or graphics are clipped.

## Introduction definition and references

- Moved the fixed-information-budget definition into the second Introduction paragraph; aligned the formal loop description in Section 3.
- Distributed 15 cited works across 10 Introduction citation groups. Activated the already-present AlphaCode bibliography entry and verified its code-search attribution.
- Distinguished fixed reference supervision from ongoing external assessment of generated samples, and distinguished the 16-sample trajectory from the final 64-sample evaluation.
- Recompiled after bibliography resolution and visually inspected the updated PDF, including both Introduction pages. Exactly nine main pages and twenty total pages remain; all nine result tables are unchanged.
