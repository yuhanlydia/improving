# Figure 4 — Longitudinal preservation on reported task cohorts

## A. Evidence inventory / scientific ground truth

**Principal question.** How does breadth loss evolve after subsequent student learning?

**Source-supported answer.** Reported paired changes from the initial model become more negative for Plain; SPECTRUM shows smaller later-round losses and higher all-task richness.

**Source.** `results/retention_5round_train16_eval16_seed43/report.json`; exact data also appear in `figures/figure_data.json`.

MEASURED: five per-method paired changes from Initial model with pointwise 95% CIs and exact eligible counts, plus all-task C16 trajectories and CIs over rounds 0–5. Task-bootstrap unit is paired tasks for changes and tasks for absolute levels; 2,000 resamples; one training seed; 16 samples per task. MISSING: paired SPECTRUM-minus-Plain per-round CIs and fixed-intersection raw task values. They must not be inferred by subtracting endpoints or intervals. Correct-conditioned cohorts vary by round and arm.

## B. Three candidates

| Option | Evidence organization / topology | Emphasis and main risk |
|---|---|---|
| 1 | Paired change as the dominant trajectory | This is the implemented recommendation. It centers inference on actual reported paired quantities, while absolute levels anchor scale. Risk: the two per-method paired subsets differ and their gap is not a paired between-method CI. |
| 2 | Round-wise paired forest with an absolute-scale footer | Exact round-specific eligible counts are easy to audit. It compresses the temporal line pattern. Risk: do not rank rounds by effect; preserve their chronological order. |
| 3 | Raw trajectory dominant with paired evidence strip | The absolute breadth is immediately readable, while the paired strip resolves sample-count conditioning. It compresses the richer paired trajectory. Risk: avoid interpreting marginal band overlap as a test of method difference. |

**Recommendation:** Option 1, which is supplied as the completed vector PDF. Every option preserves the same evidence and uses a dominant region of at least half the usable area.

## C. Option 1 — Paired change as the dominant trajectory

### Design rationale
This is the implemented recommendation. It centers inference on actual reported paired quantities, while absolute levels anchor scale. Risk: the two per-method paired subsets differ and their gap is not a paired between-method CI.

### Standalone production prompt

Create Figure 4 for an ICLR research paper at 6.7 × 2.25 inches, full text width, as a precise vector scientific figure. Scientific question: How does breadth loss evolve after subsequent student learning? The three-second takeaway is: Reported paired changes from the initial model become more negative for Plain; SPECTRUM shows smaller later-round losses and higher all-task richness.

Use 65% of the canvas for changes in Correct-conditioned AST richness@4 relative to the Initial model, with learning round 1–5 on x, two line-and-whisker series, and a zero reference line. Whiskers are the provided paired-task 95% intervals. Use 35% for absolute Correct AST richness@16 over rounds0–5 on all500tasks, with provided marginal CI bands. State n=236–246 in the first panel and put the exact per-round counts in the caption.

Exact evidence and mathematical inputs to preserve:
Plain, paired correct-conditioned AST richness@4 change relative to Initial model, rounds 1–5: r=1: -0.13825759 [-0.20797811, -0.06804864], n=245; r=2: -0.22024800 [-0.29347575, -0.14517954], n=246; r=3: -0.37609344 [-0.45267750, -0.29874511], n=240; r=4: -0.50030750 [-0.57363409, -0.42959306], n=244; r=5: -0.57416180 [-0.65371073, -0.49874934], n=241.
Plain, all-task Correct AST richness@16, rounds 0–5: r=0: 4.01600000 [3.66400000, 4.37405000]; r=1: 3.80800000 [3.47200000, 4.15810000]; r=2: 3.63400000 [3.30195000, 3.96620000]; r=3: 3.37200000 [3.06795000, 3.69010000]; r=4: 3.19000000 [2.88595000, 3.50600000]; r=5: 3.09000000 [2.80395000, 3.39800000].
SPECTRUM, paired correct-conditioned AST richness@4 change relative to Initial model, rounds 1–5: r=1: -0.09967773 [-0.16600567, -0.03543752], n=242; r=2: -0.13999219 [-0.21132327, -0.06972499], n=236; r=3: -0.22102294 [-0.30475451, -0.14572165], n=244; r=4: -0.31629952 [-0.39198348, -0.24394556], n=242; r=5: -0.31529659 [-0.39445073, -0.23957211], n=245.
SPECTRUM, all-task Correct AST richness@16, rounds 0–5: r=0: 4.01600000 [3.66400000, 4.37405000]; r=1: 3.84800000 [3.50395000, 4.20200000]; r=2: 3.76800000 [3.43600000, 4.10405000]; r=3: 3.66200000 [3.32995000, 4.00000000]; r=4: 3.58800000 [3.26800000, 3.93005000]; r=5: 3.60600000 [3.27395000, 3.95400000].

All bracketed intervals are the source-reported pointwise 95% confidence intervals from 2,000 task bootstrap resamples, not SD across seeds. Do not generate new tests, stars, uncertainty, or pseudo-replicates. Measurements derive from one training seed. No simultaneous interval guarantee is claimed. The exact sample unit, conditional eligibility and compared quantity must appear in the caption.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Change in correct-conditioned AST richness@4”, “Correct AST richness@16”, “Learning round”, “Plain”, “SPECTRUM”, “Initial model”, “95% task-bootstrap CIs”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Breadth retention across repeated learning. The dominant panel shows paired changes in correct-conditioned AST richness@4 from the initial model; each estimate uses only tasks with at least four correct samples in both the current and initial evaluation. Plain has n=(245,246,240,244,241) eligible pairs and SPECTRUM has n=(242,236,244,242,245) across rounds 1–5. These are changing paired subsets, not a fixed longitudinal cohort. The supporting panel reports correct AST richness@16 on all 500 tasks. Every round uses 16 samples per task. Whiskers and bands are the reported pointwise 95% task-bootstrap confidence intervals, based on 2,000 resamples and one training seed. Differences between the two paired-to-initial curves are descriptive and are not themselves paired SPECTRUM-minus-Plain confidence intervals.

## D. Option 2 — Round-wise paired forest with an absolute-scale footer

### Design rationale
Exact round-specific eligible counts are easy to audit. It compresses the temporal line pattern. Risk: do not rank rounds by effect; preserve their chronological order.

### Standalone production prompt

Create Figure 4 for an ICLR research paper at 6.7 × 2.25 inches, full text width, as a precise vector scientific figure. Scientific question: How does breadth loss evolve after subsequent student learning? The three-second takeaway is: Reported paired changes from the initial model become more negative for Plain; SPECTRUM shows smaller later-round losses and higher all-task richness.

Use a dominant 65% forest plot with five rows for learning rounds and a horizontal x axis of paired Correct-conditioned AST richness@4 change vs Initial. Draw paired method offsets with exact whiskers and n labels for every row. Use the remaining 35% as an absolute-richness trajectory strip on the common 500-task cohort. Use a zero vertical line in the forest plot, never a truncated quantitative bar.

Exact evidence and mathematical inputs to preserve:
Plain, paired correct-conditioned AST richness@4 change relative to Initial model, rounds 1–5: r=1: -0.13825759 [-0.20797811, -0.06804864], n=245; r=2: -0.22024800 [-0.29347575, -0.14517954], n=246; r=3: -0.37609344 [-0.45267750, -0.29874511], n=240; r=4: -0.50030750 [-0.57363409, -0.42959306], n=244; r=5: -0.57416180 [-0.65371073, -0.49874934], n=241.
Plain, all-task Correct AST richness@16, rounds 0–5: r=0: 4.01600000 [3.66400000, 4.37405000]; r=1: 3.80800000 [3.47200000, 4.15810000]; r=2: 3.63400000 [3.30195000, 3.96620000]; r=3: 3.37200000 [3.06795000, 3.69010000]; r=4: 3.19000000 [2.88595000, 3.50600000]; r=5: 3.09000000 [2.80395000, 3.39800000].
SPECTRUM, paired correct-conditioned AST richness@4 change relative to Initial model, rounds 1–5: r=1: -0.09967773 [-0.16600567, -0.03543752], n=242; r=2: -0.13999219 [-0.21132327, -0.06972499], n=236; r=3: -0.22102294 [-0.30475451, -0.14572165], n=244; r=4: -0.31629952 [-0.39198348, -0.24394556], n=242; r=5: -0.31529659 [-0.39445073, -0.23957211], n=245.
SPECTRUM, all-task Correct AST richness@16, rounds 0–5: r=0: 4.01600000 [3.66400000, 4.37405000]; r=1: 3.84800000 [3.50395000, 4.20200000]; r=2: 3.76800000 [3.43600000, 4.10405000]; r=3: 3.66200000 [3.32995000, 4.00000000]; r=4: 3.58800000 [3.26800000, 3.93005000]; r=5: 3.60600000 [3.27395000, 3.95400000].

All bracketed intervals are the source-reported pointwise 95% confidence intervals from 2,000 task bootstrap resamples, not SD across seeds. Do not generate new tests, stars, uncertainty, or pseudo-replicates. Measurements derive from one training seed. No simultaneous interval guarantee is claimed. The exact sample unit, conditional eligibility and compared quantity must appear in the caption.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Change in correct-conditioned AST richness@4”, “Correct AST richness@16”, “Learning round”, “Plain”, “SPECTRUM”, “Initial model”, “95% task-bootstrap CIs”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Breadth retention across repeated learning. The dominant panel shows paired changes in correct-conditioned AST richness@4 from the initial model; each estimate uses only tasks with at least four correct samples in both the current and initial evaluation. Plain has n=(245,246,240,244,241) eligible pairs and SPECTRUM has n=(242,236,244,242,245) across rounds 1–5. These are changing paired subsets, not a fixed longitudinal cohort. The supporting panel reports correct AST richness@16 on all 500 tasks. Every round uses 16 samples per task. Whiskers and bands are the reported pointwise 95% task-bootstrap confidence intervals, based on 2,000 resamples and one training seed. Differences between the two paired-to-initial curves are descriptive and are not themselves paired SPECTRUM-minus-Plain confidence intervals.

## E. Option 3 — Raw trajectory dominant with paired evidence strip

### Design rationale
The absolute breadth is immediately readable, while the paired strip resolves sample-count conditioning. It compresses the richer paired trajectory. Risk: avoid interpreting marginal band overlap as a test of method difference.

### Standalone production prompt

Create Figure 4 for an ICLR research paper at 6.7 × 2.25 inches, full text width, as a precise vector scientific figure. Scientific question: How does breadth loss evolve after subsequent student learning? The three-second takeaway is: Reported paired changes from the initial model become more negative for Plain; SPECTRUM shows smaller later-round losses and higher all-task richness.

Use 60% for full-cohort Correct AST richness@16 trajectories of Plain and SPECTRUM with the common Initial point and exact task-bootstrap bands over rounds0–5. Below or to the right, use 40% for a compact paired-change interval matrix with rounds1–5 and the two methods. Include exact per-round eligible counts beside each interval. Both panels answer how much breadth survives student updates.

Exact evidence and mathematical inputs to preserve:
Plain, paired correct-conditioned AST richness@4 change relative to Initial model, rounds 1–5: r=1: -0.13825759 [-0.20797811, -0.06804864], n=245; r=2: -0.22024800 [-0.29347575, -0.14517954], n=246; r=3: -0.37609344 [-0.45267750, -0.29874511], n=240; r=4: -0.50030750 [-0.57363409, -0.42959306], n=244; r=5: -0.57416180 [-0.65371073, -0.49874934], n=241.
Plain, all-task Correct AST richness@16, rounds 0–5: r=0: 4.01600000 [3.66400000, 4.37405000]; r=1: 3.80800000 [3.47200000, 4.15810000]; r=2: 3.63400000 [3.30195000, 3.96620000]; r=3: 3.37200000 [3.06795000, 3.69010000]; r=4: 3.19000000 [2.88595000, 3.50600000]; r=5: 3.09000000 [2.80395000, 3.39800000].
SPECTRUM, paired correct-conditioned AST richness@4 change relative to Initial model, rounds 1–5: r=1: -0.09967773 [-0.16600567, -0.03543752], n=242; r=2: -0.13999219 [-0.21132327, -0.06972499], n=236; r=3: -0.22102294 [-0.30475451, -0.14572165], n=244; r=4: -0.31629952 [-0.39198348, -0.24394556], n=242; r=5: -0.31529659 [-0.39445073, -0.23957211], n=245.
SPECTRUM, all-task Correct AST richness@16, rounds 0–5: r=0: 4.01600000 [3.66400000, 4.37405000]; r=1: 3.84800000 [3.50395000, 4.20200000]; r=2: 3.76800000 [3.43600000, 4.10405000]; r=3: 3.66200000 [3.32995000, 4.00000000]; r=4: 3.58800000 [3.26800000, 3.93005000]; r=5: 3.60600000 [3.27395000, 3.95400000].

All bracketed intervals are the source-reported pointwise 95% confidence intervals from 2,000 task bootstrap resamples, not SD across seeds. Do not generate new tests, stars, uncertainty, or pseudo-replicates. Measurements derive from one training seed. No simultaneous interval guarantee is claimed. The exact sample unit, conditional eligibility and compared quantity must appear in the caption.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Change in correct-conditioned AST richness@4”, “Correct AST richness@16”, “Learning round”, “Plain”, “SPECTRUM”, “Initial model”, “95% task-bootstrap CIs”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Breadth retention across repeated learning. The dominant panel shows paired changes in correct-conditioned AST richness@4 from the initial model; each estimate uses only tasks with at least four correct samples in both the current and initial evaluation. Plain has n=(245,246,240,244,241) eligible pairs and SPECTRUM has n=(242,236,244,242,245) across rounds 1–5. These are changing paired subsets, not a fixed longitudinal cohort. The supporting panel reports correct AST richness@16 on all 500 tasks. Every round uses 16 samples per task. Whiskers and bands are the reported pointwise 95% task-bootstrap confidence intervals, based on 2,000 resamples and one training seed. Differences between the two paired-to-initial curves are descriptive and are not themselves paired SPECTRUM-minus-Plain confidence intervals.

## F. Cross-option fidelity checklist

- Exactly three distinct evidence organizations or topologies, with the same source-supported content.
- One dominant region occupies at least half the usable area.
- Every numerical mark comes from the printed ledger or a labeled analytic example.
- Reported uncertainty is task uncertainty, not training-seed uncertainty.
- Measured aggregates are never reconstructed as fabricated empirical histograms.
- No projection comparator appears before the ablation experiment.
- Correct AST richness counts normalized syntax classes, not proven semantic strategies.
- Native student evaluation, raw-data learning and temporary generation modulation remain distinct.
