# Self-contained figure source data

These two JSON files are lossless selections of the aggregate fields actually
used by `../make_figures.py`. They support rebuilding the four included vector
figures after extracting the Overleaf ZIP, without access to the full repository
or any model checkpoint. They contain no generated or estimated measurements.

## Provenance

Upstream repository: <https://github.com/yuhanlydia/improving>

Source checkout commit: `ff2a669b205bef774cff4abcf3d970ce2d0008d8`

| Bundled file | Original repository file | Selection |
|---|---|---|
| `report.compact.json` | `results/retention_5round_train16_eval16_seed43/report.json` | Initial / Plain / SPECTRUM evaluation-stage pass@1, correct AST richness@16, correct-conditioned AST richness@4; Plain and SPECTRUM paired differences from the initial model for each round |
| `eval64.compact.json` | `results/retention_5round_train16_eval16_seed43/eval64/metrics_compact.json` | Initial / Plain / SPECTRUM final-evaluation pass@k and correct AST richness@k for the reported budgets |

Each retained metric preserves the original JSON numbers for `mean`, `ci95`,
`eligible_tasks`, and `total_tasks` without recalculation or rounding. Unused
metrics, method arms, task-ID lists, training statistics and paths were removed.
The original per-round report is approximately 14 MB; these field selections
avoid shipping that unrelated content in the paper archive.

Original-file SHA-256 digests:

```
a671a8eb905dec67e9a36e929b73db8ac587fa5163b29ad91d2cec7fd67c0941  results/retention_5round_train16_eval16_seed43/report.json
f4e535aa7dc78a0a618da21ff2d2da8bf20120a528de1d66b803a5a684c6e63f  results/retention_5round_train16_eval16_seed43/eval64/metrics_compact.json
```

## Rebuild

From the extracted paper directory:

```bash
python -m pip install -r requirements-figures.txt
python make_figures.py
```

The script first uses the original repository result files when both are
available; otherwise it uses these bundled JSON files. Outputs are four PDFs,
four PNG previews, and `figures/figure_data.json`. No GPU, model inference,
training, statistical resampling or network access is required after Python
dependencies are installed. `main.tex` uses the included PDFs directly; rebuilding
figures is optional and is not needed to compile the Overleaf document.

## Interpretation

All experimental means and intervals come from the recorded MBPP experiment.
Intervals are pointwise 95% task-bootstrap confidence intervals from 2,000
resamples, conditional on a single training seed. Correct-conditioned richness
uses the recorded eligible task cohort; paired changes from the initial model
use their own common eligible task subsets. The files do not provide raw program
samples, empirical class histograms or seed-to-seed uncertainty.

Figure 1's equal-correctness probability example and Figure 2's gain curve are
explicit analytic illustrations defined in the plotting script, not measured
outputs. They are also labeled separately in `figures/figure_data.json`.
