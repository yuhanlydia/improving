# Sources and preparation of this manuscript

Prepared 2026-09-15. This file accompanies the editable paper package; it is not part of the nine-page main text.

## Research evidence

- Research repository: [yuhanlydia/improving](https://github.com/yuhanlydia/improving).
- Repository state inspected: [`d8a50903de671cdb7e5c23a28ff43de1c32c16b5`](https://github.com/yuhanlydia/improving/commit/d8a50903de671cdb7e5c23a28ff43de1c32c16b5).
- Completed measurements are the retained seed-42, 64-task MBPP pilot summary reproduced in `support/pilot_README.md`. Its reported artifact hashes are preserved in `support/pilot_ARTIFACTS.sha256`; retaining hashes does not supply the absent raw programs or establish an independent numerical reproduction.
- Later repository additions include formal and extended-round execution configurations. Their presence is not evidence that those experiments have completed.
- `spectral_soft` is the existing implementation identifier. SPECTRUM is its manuscript name, with no change to the underlying algorithm in this writing task.
- Final-checkpoint paired intervals supplied numerically are against SSD-style sampling. Positive intervention-stage intervals against SPD-hard do not substitute for final-checkpoint paired comparisons against SPD-hard.
- All currently missing outcomes are marked Pending in the manuscript and described in `PENDING_EXPERIMENTS.md`. No research training, generation, or benchmark execution was performed while preparing this package.

## Writing approach

The requested ARIS workflow was read from [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep), pinned at [`f1bd907b58f653131ebe6807c482e2554e07f9b9`](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/f1bd907b58f653131ebe6807c482e2554e07f9b9):

- `skills/paper-write/SKILL.md`;
- `skills/skills-codex/paper-write/SKILL.md`, the GPT/Codex adaptation;
- shared writing principles, citation discipline, and venue guidance.

The draft follows one narrative: observed accuracy–diversity ranking disagreement → correctness-conditioned coverage → soft spectral generation → ordinary LoRA → measured pilot effects → prospective mechanism and retention tests. Claims use direct language tied to the available evidence. Specific uncertainties are collected in Discussion and limitations. Novelty is positioned against SPD, spectral editing, conceptors, and correctness-aware diversity optimization; it is not asserted from the absence of an exact keyword match.

The user's request for one `main.tex` overrides the workflow's preference for separate section files. No unrun experiment is converted into a completed result to make the paper read like a finished study.

An independent GPT-6 Astra manuscript review checked the full text, notation, estimators, local spectral proof, loss masks, and evidence attribution. The final draft incorporates corrections to total-budget coverage, row/bias conventions, paired-task eligibility disclosure, retention language, and the interpretation of matched controls. This editorial review is not an experimental replication.

## Figures

The pipeline and experimental-figure design skills were used to write six figure specifications with three self-contained alternatives each. Figure 1 uses the reported pilot means; Figure 2 depicts the implemented data/training flow; Figure 3 evaluates the exact gain formula. Figures 4–6 are future-result specifications with explicit data requirements and no invented points or uncertainty bands.

The three included figures are programmatic vector PDFs, accompanied by PNG previews and `support/make_figures.py`. Analytical gain curves are labelled analytical and are not empirical spectra or ablation results.

## Template and bibliography

The official ICLR 2027 conference style and bibliography style are unchanged. See `support/TEMPLATE_PROVENANCE.md`, `support/UPSTREAM_MANIFEST.json`, and `licenses/lppl.txt` for source and licensing details. Standard TeX Live / Overleaf packages supply the remaining dependencies.

The bibliography contains 15 source-checked references. `source-notes.md` records primary-source URLs and positioning decisions. The anonymous main text has nine pages; its AI-use statement and references follow on two additional pages. The package is an editable research draft whose future-result slots must be completed before a final submission.
