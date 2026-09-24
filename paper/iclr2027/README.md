# SPECTRUM — manuscript based on completed results

**Current revision: 2026-09-24, nine-page main text.** The full paper is in `main.tex`, with references in `references.bib` and all appendices in the same main file. `main.pdf` is the compiled anonymous ICLR 2027 version: main text on pages 1–9, statements/references from page 10, and appendices from page 13 (20 pages total).

The latest revision expands SPECTRUM's calibration interpretation, numerical gain example, explicit student objective, and generation-to-learning mechanism. Related Work now has four substantive themes. Independent **Limitations** and **Conclusion and future work** sections close the main text. Figures, experimental values, and the official template remain unchanged.

The Introduction now defines the fixed information budget in its second paragraph: no new annotation or external assessment of generated rollouts enters training, while a reference anchor fixed before the loop can be reused for calibration. Fifteen cited works support the Introduction's specific background and attribution claims; the full paper uses 23 references.

The positioning is **Looped Self-Distillation with a fixed reference anchor**. The same calibration examples are reused each round; geometry is re-estimated on the current model. SPECTRUM retains every raw generated completion for single-LoRA learning. It uses fixed external reference supervision, without scoring or filtering generated samples.

The rewrite uses only completed MBPP, SSD, HumanEval+, and APPS Intro records. It starts no new training, sampling, or code-verification experiment. Planned scale/seed/control matrices are not numerical evidence and have been removed from result tables.

## Files

- `main.tex`, `main.pdf`, `references.bib`: manuscript, compiled paper, bibliography.
- `PAPER_AUDIT.md`: Chinese narrative guide, claim–evidence ledger, source/change map, scope and venue notes.
- `CITATION_AUDIT.md`: sources and the exact distinctions each citation supports.
- `FIGURE_PROMPTS.md`: four complete figure design packs, each with three standalone English prompts under 5,000 characters.
- `figure-prompts/figure_N_option_M.txt`: individually copyable prompts. Option 1 matches the manuscript.
- `source-data/rewrite_sources.json`: exact selected fields from existing results and source hashes.
- `source-data/derived_analysis.json`: new CPU-only reanalyses of those saved records.
- `analyze_existing.py`, `make_paper_figures.py`, `make_design_specs.py`: reproducible analysis, figures, and design prompts.

## Rebuild without any model run

```bash
python -m pip install -r requirements-figures.txt
python analyze_existing.py
python make_paper_figures.py
python make_design_specs.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

These commands use bundled data. To re-extract exact selected fields from the repository's original archived result files, run `python analyze_existing.py --refresh-sources` first. It checks saved metric consistency and computes task bootstraps; it does not import or execute a model, a code verifier, or the experiment runner.

The original `make_figures.py` entry point forwards to the updated renderer. The package uses the official ICLR 2027 style unchanged; ordinary TeX-distribution packages supply the remaining dependencies.

## How to read the results

The main n64 table compares initial/Plain/SPECTRUM after five MBPP rounds. Every historical round has n16 evaluation, and the SSD continuation is also n16; these pools are kept separate. Frozen-student HumanEval+ and adapted APPS Intro each use n16. Conditional richness gains and correctness costs are both retained. Confidence intervals describe evaluation-task variation for saved checkpoints, not variation across independently trained seeds.
