# Figure 3 — Sampling budget exposes retained breadth

## A. Evidence inventory / scientific ground truth

**Principal question.** How do total sampling budget and success probability change the breadth advantage?

**Source-supported answer.** At higher budgets, SPECTRUM exposes more correct AST classes than Plain while final pass@64 is also higher.

**Source.** `results/retention_5round_train16_eval16_seed43/eval64/metrics_compact.json`; exact data also appear in `figures/figure_data.json`.

MEASURED: task means and pointwise 95% task-bootstrap CIs for k in {1,4,8,16,64}; Initial, Plain, SPECTRUM; 500 MBPP tasks, 64 samples per task, one training seed. DERIVED: only unit conversion of pass fractions to percent. MISSING: k=32 estimates, per-task raw samples, seed-to-seed uncertainty, any fitted asymptotic coverage curve. No AUC or extrapolation is available.

## B. Three candidates

| Option | Evidence organization / topology | Emphasis and main risk |
|---|---|---|
| 1 | Dominant richness curve with success side panel | This is the implemented recommendation. It highlights breadth and retains the correctness control. Risk: readers may mistake connecting segments for unmeasured budgets; caption must define them as guides. |
| 2 | Budget-by-budget paired interval ladder | Whiskers make uncertainty and individual budgets explicit. It compresses continuity. Risk: shared native scale makes k=1 small but preserves truthful scale. |
| 3 | Richness-first split with aligned value table | The main pattern remains visual while the success probability can be read precisely. It compresses the visual pass curve. Risk: numeric text must remain readable at full paper width. |

**Recommendation:** Option 1, which is supplied as the completed vector PDF. Every option preserves the same evidence and uses a dominant region of at least half the usable area.

## C. Option 1 — Dominant richness curve with success side panel

### Design rationale
This is the implemented recommendation. It highlights breadth and retains the correctness control. Risk: readers may mistake connecting segments for unmeasured budgets; caption must define them as guides.

### Standalone production prompt

Create Figure 3 for an ICLR research paper at 6.7 × 2.25 inches, full text width, as a precise vector scientific figure. Scientific question: How do total sampling budget and success probability change the breadth advantage? The three-second takeaway is: At higher budgets, SPECTRUM exposes more correct AST classes than Plain while final pass@64 is also higher.

Use 65% of the canvas for Correct AST richness@k versus k, with a log2 x axis labeled only 1,4,8,16,64 and y starting at zero. Use 35% for pass@k (%) on an independently labeled y axis and the same budget ticks. Draw exact point estimates and reported pointwise CI bands, not new resampling. Connect adjacent reported points by straight segments. Label final richness values 12.802, 8.506, 11.510 at k=64; place the legend once in the main panel.

Exact evidence and mathematical inputs to preserve:
Initial model, Correct AST richness@k: k=1: 0.37943750 [0.34740547, 0.41365703]; k=4: 1.26656412 [1.15941525, 1.37364708]; k=8: 2.26701320 [2.07380042, 2.45909174]; k=16: 4.03963783 [3.69290328, 4.39086368]; k=64: 12.80200000 [11.69585000, 13.96810000].
Initial model, pass@k (%): k=1: 37.94375000 [34.74054687, 41.36570312]; k=4: 55.07654491 [51.32311306, 58.90580618]; k=8: 61.09743277 [57.24928416, 64.97163629]; k=16: 65.69243831 [61.84579346, 69.52451294]; k=64: 72.00000000 [68.19500000, 75.80000000].
Plain, Correct AST richness@k: k=1: 0.41446875 [0.38040547, 0.45168984]; k=4: 1.16613830 [1.07090341, 1.26727310]; k=8: 1.92287379 [1.75710562, 2.10157406]; k=16: 3.15921554 [2.86730684, 3.47591124]; k=64: 8.50600000 [7.60195000, 9.46405000].
Plain, pass@k (%): k=1: 41.44687500 [38.04054687, 45.16898438]; k=4: 56.54111550 [52.68074897, 60.45970198]; k=8: 61.85723087 [57.93926136, 65.81580562]; k=16: 65.63636761 [61.66121006, 69.60772760]; k=64: 70.40000000 [66.40000000, 74.40000000].
SPECTRUM, Correct AST richness@k: k=1: 0.40331250 [0.37115313, 0.43831797]; k=4: 1.24374904 [1.14310835, 1.34875512]; k=8: 2.16108051 [1.97638390, 2.34680530]; k=16: 3.75825577 [3.42517823, 4.10308652]; k=64: 11.51000000 [10.42400000, 12.65240000].
SPECTRUM, pass@k (%): k=1: 40.33125000 [37.11531250, 43.83179687]; k=4: 56.21481611 [52.39757779, 60.09773592]; k=8: 61.89282396 [57.99531765, 65.81920368]; k=16: 66.22507815 [62.33787417, 70.18316379]; k=64: 72.60000000 [68.80000000, 76.60000000].

All bracketed intervals are the source-reported pointwise 95% confidence intervals from 2,000 task bootstrap resamples, not SD across seeds. Do not generate new tests, stars, uncertainty, or pseudo-replicates. Measurements derive from one training seed. No simultaneous interval guarantee is claimed. The exact sample unit, conditional eligibility and compared quantity must appear in the caption.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Correct AST richness@k”, “pass@k (%)”, “Sampling budget k”, “Initial model”, “Plain”, “SPECTRUM”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Sampling budget separates correctness from implementation breadth. The final students and the initial model are evaluated with 64 samples on each of 500 MBPP tasks. Correct AST richness@k is the expected number of distinct correct normalized-AST classes within k draws without replacement from the observed pool; pass@k is the corresponding probability of at least one passing program. Only k=1,4,8,16,64 were reported. The lines join these measured budget points, and shaded bands are pointwise 95% task-bootstrap confidence intervals from 2,000 resamples; they quantify task uncertainty for one training seed, not training-seed uncertainty.

## D. Option 2 — Budget-by-budget paired interval ladder

### Design rationale
Whiskers make uncertainty and individual budgets explicit. It compresses continuity. Risk: shared native scale makes k=1 small but preserves truthful scale.

### Standalone production prompt

Create Figure 3 for an ICLR research paper at 6.7 × 2.25 inches, full text width, as a precise vector scientific figure. Scientific question: How do total sampling budget and success probability change the breadth advantage? The three-second takeaway is: At higher budgets, SPECTRUM exposes more correct AST classes than Plain while final pass@64 is also higher.

Use a dominant 65% left panel with one horizontal row per k in ascending order. Within each row, plot Initial, Plain and SPECTRUM as offset dot-whiskers for native Correct AST richness@k; every row shares the same richness scale starting at zero. On the right, allocate 35% to the exact pass@k curves. State that the richer row values naturally grow with sampling budget. Keep all exact CIs and show no paired-difference intervals, because the listed intervals are marginal task-bootstrap intervals.

Exact evidence and mathematical inputs to preserve:
Initial model, Correct AST richness@k: k=1: 0.37943750 [0.34740547, 0.41365703]; k=4: 1.26656412 [1.15941525, 1.37364708]; k=8: 2.26701320 [2.07380042, 2.45909174]; k=16: 4.03963783 [3.69290328, 4.39086368]; k=64: 12.80200000 [11.69585000, 13.96810000].
Initial model, pass@k (%): k=1: 37.94375000 [34.74054687, 41.36570312]; k=4: 55.07654491 [51.32311306, 58.90580618]; k=8: 61.09743277 [57.24928416, 64.97163629]; k=16: 65.69243831 [61.84579346, 69.52451294]; k=64: 72.00000000 [68.19500000, 75.80000000].
Plain, Correct AST richness@k: k=1: 0.41446875 [0.38040547, 0.45168984]; k=4: 1.16613830 [1.07090341, 1.26727310]; k=8: 1.92287379 [1.75710562, 2.10157406]; k=16: 3.15921554 [2.86730684, 3.47591124]; k=64: 8.50600000 [7.60195000, 9.46405000].
Plain, pass@k (%): k=1: 41.44687500 [38.04054687, 45.16898438]; k=4: 56.54111550 [52.68074897, 60.45970198]; k=8: 61.85723087 [57.93926136, 65.81580562]; k=16: 65.63636761 [61.66121006, 69.60772760]; k=64: 70.40000000 [66.40000000, 74.40000000].
SPECTRUM, Correct AST richness@k: k=1: 0.40331250 [0.37115313, 0.43831797]; k=4: 1.24374904 [1.14310835, 1.34875512]; k=8: 2.16108051 [1.97638390, 2.34680530]; k=16: 3.75825577 [3.42517823, 4.10308652]; k=64: 11.51000000 [10.42400000, 12.65240000].
SPECTRUM, pass@k (%): k=1: 40.33125000 [37.11531250, 43.83179687]; k=4: 56.21481611 [52.39757779, 60.09773592]; k=8: 61.89282396 [57.99531765, 65.81920368]; k=16: 66.22507815 [62.33787417, 70.18316379]; k=64: 72.60000000 [68.80000000, 76.60000000].

All bracketed intervals are the source-reported pointwise 95% confidence intervals from 2,000 task bootstrap resamples, not SD across seeds. Do not generate new tests, stars, uncertainty, or pseudo-replicates. Measurements derive from one training seed. No simultaneous interval guarantee is claimed. The exact sample unit, conditional eligibility and compared quantity must appear in the caption.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Correct AST richness@k”, “pass@k (%)”, “Sampling budget k”, “Initial model”, “Plain”, “SPECTRUM”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Sampling budget separates correctness from implementation breadth. The final students and the initial model are evaluated with 64 samples on each of 500 MBPP tasks. Correct AST richness@k is the expected number of distinct correct normalized-AST classes within k draws without replacement from the observed pool; pass@k is the corresponding probability of at least one passing program. Only k=1,4,8,16,64 were reported. The lines join these measured budget points, and shaded bands are pointwise 95% task-bootstrap confidence intervals from 2,000 resamples; they quantify task uncertainty for one training seed, not training-seed uncertainty.

## E. Option 3 — Richness-first split with aligned value table

### Design rationale
The main pattern remains visual while the success probability can be read precisely. It compresses the visual pass curve. Risk: numeric text must remain readable at full paper width.

### Standalone production prompt

Create Figure 3 for an ICLR research paper at 6.7 × 2.25 inches, full text width, as a precise vector scientific figure. Scientific question: How do total sampling budget and success probability change the breadth advantage? The three-second takeaway is: At higher budgets, SPECTRUM exposes more correct AST classes than Plain while final pass@64 is also higher.

Use a dominant 60% top richness plot with all three methods and exact CIs on logarithmic budget ticks. Use the lower 40% as a compact aligned matrix of pass@k values and their 95% intervals, with rows Initial model / Plain / SPECTRUM and columns 1 / 4 / 8 / 16 / 64. Render actual numeric data; light table rules only, no heatmap unless a true numeric color legend is supplied.

Exact evidence and mathematical inputs to preserve:
Initial model, Correct AST richness@k: k=1: 0.37943750 [0.34740547, 0.41365703]; k=4: 1.26656412 [1.15941525, 1.37364708]; k=8: 2.26701320 [2.07380042, 2.45909174]; k=16: 4.03963783 [3.69290328, 4.39086368]; k=64: 12.80200000 [11.69585000, 13.96810000].
Initial model, pass@k (%): k=1: 37.94375000 [34.74054687, 41.36570312]; k=4: 55.07654491 [51.32311306, 58.90580618]; k=8: 61.09743277 [57.24928416, 64.97163629]; k=16: 65.69243831 [61.84579346, 69.52451294]; k=64: 72.00000000 [68.19500000, 75.80000000].
Plain, Correct AST richness@k: k=1: 0.41446875 [0.38040547, 0.45168984]; k=4: 1.16613830 [1.07090341, 1.26727310]; k=8: 1.92287379 [1.75710562, 2.10157406]; k=16: 3.15921554 [2.86730684, 3.47591124]; k=64: 8.50600000 [7.60195000, 9.46405000].
Plain, pass@k (%): k=1: 41.44687500 [38.04054687, 45.16898438]; k=4: 56.54111550 [52.68074897, 60.45970198]; k=8: 61.85723087 [57.93926136, 65.81580562]; k=16: 65.63636761 [61.66121006, 69.60772760]; k=64: 70.40000000 [66.40000000, 74.40000000].
SPECTRUM, Correct AST richness@k: k=1: 0.40331250 [0.37115313, 0.43831797]; k=4: 1.24374904 [1.14310835, 1.34875512]; k=8: 2.16108051 [1.97638390, 2.34680530]; k=16: 3.75825577 [3.42517823, 4.10308652]; k=64: 11.51000000 [10.42400000, 12.65240000].
SPECTRUM, pass@k (%): k=1: 40.33125000 [37.11531250, 43.83179687]; k=4: 56.21481611 [52.39757779, 60.09773592]; k=8: 61.89282396 [57.99531765, 65.81920368]; k=16: 66.22507815 [62.33787417, 70.18316379]; k=64: 72.60000000 [68.80000000, 76.60000000].

All bracketed intervals are the source-reported pointwise 95% confidence intervals from 2,000 task bootstrap resamples, not SD across seeds. Do not generate new tests, stars, uncertainty, or pseudo-replicates. Measurements derive from one training seed. No simultaneous interval guarantee is claimed. The exact sample unit, conditional eligibility and compared quantity must appear in the caption.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Correct AST richness@k”, “pass@k (%)”, “Sampling budget k”, “Initial model”, “Plain”, “SPECTRUM”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Sampling budget separates correctness from implementation breadth. The final students and the initial model are evaluated with 64 samples on each of 500 MBPP tasks. Correct AST richness@k is the expected number of distinct correct normalized-AST classes within k draws without replacement from the observed pool; pass@k is the corresponding probability of at least one passing program. Only k=1,4,8,16,64 were reported. The lines join these measured budget points, and shaded bands are pointwise 95% task-bootstrap confidence intervals from 2,000 resamples; they quantify task uncertainty for one training seed, not training-seed uncertainty.

## F. Cross-option fidelity checklist

- Exactly three distinct evidence organizations or topologies, with the same source-supported content.
- One dominant region occupies at least half the usable area.
- Every numerical mark comes from the printed ledger or a labeled analytic example.
- Reported uncertainty is task uncertainty, not training-seed uncertainty.
- Measured aggregates are never reconstructed as fabricated empirical histograms.
- No projection comparator appears before the ablation experiment.
- Correct AST richness counts normalized syntax classes, not proven semantic strategies.
- Native student evaluation, raw-data learning and temporary generation modulation remain distinct.
