# SPECTRUM — complete ICLR 2027 manuscript

**Title:** SPECTRUM: Looped Self-Distillation through Proximal Spectral Modulation

`main.tex` contains the entire manuscript, including the appendix after the
references. `main.pdf` is the compiled preview. Upload this folder's contents to
Overleaf and set `main.tex` as the main document, with pdfLaTeX as the compiler.

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

This is a complete, editable manuscript with explicitly pending experiments,
not a claim that every experiment has finished. Gray `x` entries are missing
measurements. Replace them only with results from the stated protocol. The
completed results are the 500-task MBPP seed-43 study: five learning rounds with
16-sample intermediate evaluation and a separate 64-sample final evaluation.

## What is included

- One `main.tex`: abstract, introduction, probability analysis, loop framework,
  method, experiments, related work, discussion, reproducibility and AI-use
  statements, references, and complete mathematical/experimental appendices.
- Official ICLR 2027 style and bibliography files, plus their bundled support
  styles. These are unchanged venue files, downloaded from
  [the official template](https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip).
- `references.bib`: all citations needed by the manuscript.
- `figures/`: four publication figures as vector PDFs and PNG previews, numeric
  figure data and captions. Their PDFs are already present; compiling the paper
  does not require Python.
- `make_figures.py` and `source-data/`: reproducible plots from committed reports,
  without model inference. The analytical distribution example is explicitly
  distinguished from measured outcomes.
- `FIGURE_PROMPTS.md` and `figure-prompts/`: editable figure specifications and
  three layout options per figure. Exact experimental charts use numerical
  plotting, not image-generation output.
- `PAPER_AUDIT.md`: claim-to-evidence map, missing experiments and terminology.

## Experimental continuation

The runnable suite is in
[`experiments/iclr2027`](../../experiments/iclr2027/README.md) in the repository.
The independent Overleaf package contains the manuscript rather than the whole
training repository. In a repository checkout, start from:

```bash
python scripts/run_iclr2027.py plan --stage core --profile 24gb --seeds 43
```

The command prints the exact manifest and run command. It does not train a
model. SSD and SPECTRUM share the SFT protocol with Plain. UA-RL is a separately
configured adapted RL comparator with a semantic judge and its own dependency
environment. Rank truncation is a design ablation, not a main prior-method arm.

## Before submission

Fill and discuss only experiments actually completed. Update the abstract and
tables together if new runs change the reported result. Confirm the author and
AI-use statements, remove pending-result tables or complete them, and review
the official venue submission instructions. The current anonymous PDF does not
link to the identifying development repository.
