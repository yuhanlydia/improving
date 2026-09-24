# Build and evidence checks — 2026-09-24

- Rebuilt all four figure PDFs/PNGs from archived measurements and exact vector instructions.
- Recomputed only CPU summaries of saved data: paired transfer task bootstrap, resource totals, and deterministic class-count examples. No training, sampling, or code verification ran.
- Checked source SHA-256 values against the committed files at the recorded input snapshot.
- Checked the finite-sample class-count formulas against saved transfer per-task metrics.
- Cross-checked main MBPP and transfer table values against the source snapshot, and checked the separate n16 projection/SSD rows and eligibility counts.
- Compiled the manuscript with `latexmk -pdf -interaction=nonstopmode -halt-on-error`.
- Final LaTeX log has no undefined references/citations, missing figures, overfull boxes, or compilation errors.
- Final PDF: 19 pages. Main text occupies pages 1–8; excluded statements/references begin on page 9; appendices begin on page 12. It is within the official nine-page main-text limit. No template margins or font sizes were modified.
- Rendered and visually inspected all pages; inspected the title, main results, method diagram, tables and figures at readable size. Tables/figures use monochrome styling.
- All 22 used bibliography keys resolve. Citation-entailment notes are in `CITATION_AUDIT.md`.
- Four figure design records each contain exactly three standalone English alternatives. Prompt lengths range from 2,571 to 3,094 characters, all below 5,000.
- No pending-result placeholders remain in the manuscript. Explicit protocol-template placeholders designate variable prompt fields only.

Scientific boundaries remain as reported in the paper: one main training seed/backbone, AST structural proxies, fixed external reference information, unmatched realized token costs, and dataset-dependent correctness trade-offs. Artifact checks do not turn those boundaries into additional experimental evidence.
