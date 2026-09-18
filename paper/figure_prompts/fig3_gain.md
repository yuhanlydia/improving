# SPECTRUM — Figure 3: Analytic Gain Design

## A. Evidence Inventory

### Principal scientific question
How does the confirmed soft transform act on each eigen-direction of the normalized gradient second moment?

### Source-supported answer
`DERIVED`: for normalized second-moment eigenvalue μ∈[0,1] and τ≥0, s_τ(μ)=1/[1+τ(1−μ)]. For finite τ the transform is full rank; at the default τ=1, the gain spans [1/2,1]. This is an analytic statement, not a measurement of a model spectrum or evidence of a behavioral mechanism.

### Measurements and comparisons
`MEASURED`: none in this figure. `DERIVED`: the gain curves at τ=0.5,1,2, plus identity τ=0, directly from T=[I+τ(I−C̄)]⁻¹ and C̄=C/λ_max(C). The gradient second moment is from native K/V output gradients. `CONCEPTUAL`: explanatory annotations about attenuation and preservation of directions. Larger μ receives larger gain; the highest eigenvalue has unit gain. No arbitrary top-r hard threshold may be shown on the continuous μ axis as a measured quantity.

### Statistics and uncertainty
No sampling, aggregation, seeds, confidence intervals, significance tests, or statistical units apply to deterministic formula evaluation. Do not add empirical uncertainty. Default τ=1 is confirmed. The other τ values are illustrative analytic comparisons, not experimental settings with reported outcomes.

### Derived quantities
s_τ(0)=1/(1+τ); s_τ(1)=1; ∂s_τ/∂μ=τ/[1+τ(1−μ)]²≥0; ∂s_τ/∂τ=−(1−μ)/[1+τ(1−μ)]²≤0. Plotting uses no fit, empirical normalization, or extrapolation. Normalization presumes λ_max(C)>0; implementation behavior for a zero second-moment matrix is `MISSING` and should not be depicted.

### Missing information
`MISSING`: observed layer-wise second-moment spectra, intervention effects on outputs, τ ablation outcomes, retention outcomes, or semantic-algorithm assignments. The figure establishes none of these.

## B. Three Candidate Visualizations

| Option | Evidence narrative | Dominant panel | Supporting evidence | Data requirements | Main risk |
|---|---|---|---|---|---|
| 1 | Gain across normalized eigenvalues | Analytic gain curves, 65% | Formula and default range, 35% | Confirmed formula; available | Curves could be mistaken for observed spectra |
| 2 | Joint parameter response | Analytic μ-by-τ heatmap, 70% | Exact endpoint values, 30% | Formula on declared grid; available | Decorative heatmap without numeric mapping |
| 3 | Sensitivity to intervention strength | Gain-versus-τ family, 65% | Default-τ cross section, 35% | Formula only; available | τ sweep could be mistaken for an empirical ablation |

**Recommendation:** Option 1 is the embedded figure. It displays the mechanism's mathematical gain with the fewest interpretive steps. Every alternative must be visibly labeled analytic.

## C. Option 1 — Gain versus normalized second-moment eigenvalue

### Design rationale
Make the continuous gain response the visual center, with the identity line exposing attenuation and the default curve emphasized. Compress derivative algebra into the caption.

### Standalone generation prompt
Produce Figure 3 as a mathematically exact vector scientific plot for a full-width ICLR paper, 7 × 2.2 inches, on white. Its three-second claim is “Analytic soft gain preserves every direction”. Give the gain plot 65% of usable width and an equation/default-note column 35%. Plot x “Normalized second-moment eigenvalue μ”, with the definition “μ=λ/λ_max” in the equation column, from 0 to 1, and y “Directional gain s_τ(μ)”, from 0 to 1.045 with labeled ticks at 0,0.25,0.5,0.75,1. Draw the deterministic function s_τ(μ)=1/[1+τ(1−μ)] continuously for τ=0.5 as dotted desaturated blue, τ=1 as thicker solid teal, and τ=2 as dash-dot ochre; draw identity s=1 as dashed gray. Use a direct legend “Identity”, “τ=0.5”, “τ=1”, “τ=2”. The right note column shows the exact formula, “Default: τ=1”, “Gain range: [½,1]”, “Full-rank transform”, and “Analytic illustration”. Put beneath the title “Larger second-moment eigenvalues receive larger gain; no direction is zeroed.” The footer must say “Native K/V gradient second moment; curves are not measured model spectra.” Curves are deterministic formula evaluations with no seeds, statistical uncertainty, fitting, or measured points; alternative τ values are analytic comparisons only. Use 8-point horizontal axis labels, 10-point title, thin gray grids, no top/right spines, and redundant line styles. Required text is every quoted label and the exact formula above. Do not draw an arbitrary hard top-r threshold on μ, a measured eigenvalue histogram, empirical ablation results, confidence bands, algorithm labels, 3D effects, gradients, or invented performance data. Preserve the exact function, normalization, default τ, analytic status, and absence of empirical uncertainty.

### Caption and statistical disclosure
Analytic directional gain induced by the soft transform. Since s_τ(μ)=1/[1+τ(1−μ)], gains increase monotonically with normalized gradient second-moment eigenvalue; all directions retain positive gain for finite τ≥0. At the default τ=1, gains range from 1/2 to 1. The curves are formula evaluations, not measured spectra or empirical evidence of a behavioral mechanism.

## D. Option 2 — Exact analytic response matrix

### Design rationale
Make dependence on both τ and eigenvalue simultaneously visible. Emphasize endpoints and bounded gains, compress continuity into a discrete matrix. This is a derived numeric matrix, never a decorative proxy for measured second-moment.

### Standalone generation prompt
Produce an alternate analytic Figure 3 in a full-width ICLR layout at 7 × 2.7 inches on white. Title “Analytic gain across eigenvalue and strength”. Allocate 70% of usable area to a numeric response matrix and 30% to the formula and endpoint notes. The dominant matrix has columns “μ=0”, “0.25”, “0.50”, “0.75”, “1.00”, and rows “Identity (τ=0)”, “τ=0.5”, “τ=1 (default)”, “τ=2”. Each cell is computed exactly from s_τ(μ)=1/[1+τ(1−μ)]; print three-decimal values, using rational endpoint text in the note column. Compute all values programmatically, not from visual inference. Color cells with a perceptually uniform white-to-teal sequential scale fixed from 0 to 1 and label its colorbar “Analytic directional gain”. Draw a stronger border around the τ=1 row. The right note column shows the formula, “s_τ(0)=1/(1+τ)”, “s_τ(1)=1”, “Default gain range: [½,1]”, and “Derived values; no empirical data”. This is an exact parameter response table, not the second-moment matrix C or an observed model spectrum. Required text is every stated title, row/column header, equation, note, colorbar label, and the footer “Native K/V gradient second moment; analytic illustration”. Use horizontal 8-point cell values and labels, 10-point title, subtle cell boundaries, no shadows or decorative motifs. No confidence intervals, sample counts, seed labels, or statistical tests apply. Do not invent a zero-second-moment fallback, experimental τ outcomes, rank-truncation thresholds, semantic algorithms, measured eigenvalue distributions, or behavioral conclusions. Preserve the confirmed analytic function, declared grid, default τ, exact numeric derivation, and missing empirical evidence.

### Caption and statistical disclosure
Formula-evaluated gains on a declared normalized-eigenvalue and τ grid. Color and printed numbers encode the same deterministic values, and the outlined row is the confirmed default τ=1. The table is not a measured second-moment heatmap; it has no statistical uncertainty or empirical ablation outcomes.

## E. Option 3 — Strength-response family with a default cross section

### Design rationale
Transpose the explanatory question: how does attenuation vary with τ for a fixed second-moment direction? Emphasize strength sensitivity, compress eigenvalue continuity into five analytically selected slices.

### Standalone generation prompt
Produce an alternate analytic Figure 3 as a 7 × 2.7 inch full-width ICLR vector chart on white, titled “Analytic attenuation as τ increases”. The dominant panel occupies 65% of usable area and plots x “Strength τ”, range 0–2, against y “Directional gain”, range 0–1.05. Plot s_τ(μ)=1/[1+τ(1−μ)] for the explicitly illustrative normalized eigenvalues μ=0,0.25,0.5,0.75,1.0. These are exact formula slices, not observed eigenvalues. Use direct right-end labels “μ=0”, “μ=0.25”, “μ=0.50”, “μ=0.75”, “μ=1.00”; use distinguishable line styles in a restrained gray/blue/teal palette, with μ=1 a dashed gray identity line. Draw a vertical dotted guide at τ=1 labeled “Default τ=1”. In the remaining 35%, show a separate five-dot cross section titled “At τ=1”, with μ values 0,0.25,0.5,0.75,1 and analytic gains 0.5,4/7,2/3,0.8,1, printed as 0.500,0.571,0.667,0.800,1.000. Do not connect the small-panel dots as empirical observations; label them “Formula values”. Include the formula and “Analytic illustration; no measured τ ablation”. Use 8-point horizontal labels, 10-point title, thin gray grids, no dual axes, and sufficient whitespace between the main panel and default slice. The footer is “Native K/V output-gradient second moment; all finite-τ gains are positive.” No aggregation, sampling, fit, significance test, CI, or empirical selected-point rule applies; τ=1 is a confirmed method default, not a fitted optimum. Required text is all quoted text, direct μ labels, formula, and numeric values. Do not depict any experimental outcome, invented measured spectrum, hard rank cutoff, semantic-algorithm meaning, or empirically optimal τ. Preserve the exact derived gain function, illustrative parameter slices, confirmed default, absence of measurements, and all missing-data distinctions.

### Caption and statistical disclosure
Deterministic gain as a function of intervention strength for five illustrative normalized second-moment eigenvalues. The dotted guide marks the confirmed method default, and the side panel reports its analytic gains. This is not an empirical τ ablation or evidence that any τ is optimal for correctness or diversity.

## F. Cross-option evidence-fidelity checklist

- Exactly three distinct organizations: eigenvalue curves, numeric response matrix, strength curves.
- Every mark is `DERIVED` from the exact formula; no mark is empirical.
- At least half of usable area belongs to one dominant panel.
- Axes, units, ranges, parameter grids, and default τ are explicit.
- All finite-τ gains are positive; τ=1 gain range is [1/2,1].
- No arbitrary top-r threshold is misrepresented as a normalized-eigenvalue cutoff.
- No observed spectrum, behavioral mechanism, semantic algorithm, or optimality result is fabricated.
- No uncertainty is attached to deterministic formula evaluations.
