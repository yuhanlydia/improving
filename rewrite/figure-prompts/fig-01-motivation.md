# Figure 1 — Experiment Figure Design

Figure number: **1** · Role: motivation/hero · Section: Introduction · Intended width: full text width (7.0 in), height ≈ 2.6–2.9 in.

## A. Evidence Inventory

### Principal scientific question

Does ordinary self-distillation preserve the set of correct implementations a code model can produce, and does a selection-based intervention (hard spectral projection) preserve more or less of it than a continuous one?

### Source-supported answer

Self-distillation erodes correctness-matched implementation coverage over rounds, and it does so in every arm tested. After five rounds the two comparator arms that the literature establishes as effective (plain raw-output self-distillation, SSD-style sampling, and hard spectral projection, SPD-style) sit furthest below the undilstilled base. The continuous-gain arm sits closest to it. On the same tasks, all arms are *more* accurate single-shot than the base.

This is a tension, not a win: the field's current self-distillation recipes buy single-sample accuracy with implementation coverage, and the coverage loss is not currently measured or reported.

### Measurements and comparisons

| Quantity | Value | Status |
|---|---|---|
| Setting | Qwen2.5-Coder-1.5B-Instruct, MBPP, 291 synthesis tasks, 500 held-out test tasks, seed 43, five generate→LoRA rounds, 16 raw candidates/task/round | `MEASURED` |
| Final evaluation | 500 tasks × 64 samples, first-fence extraction | `MEASURED` |
| Base (undistilled) pass@1 | 0.3792, 95% CI [0.3469, 0.4140] | `MEASURED` |
| Plain pass@1 | 0.4130 [0.3794, 0.4498] | `MEASURED` |
| SPD-hard pass@1 | 0.4135 [0.3794, 0.4514] | `MEASURED` |
| SPECTRUM pass@1 | 0.4017 [0.3685, 0.4375] | `MEASURED` |
| Base D₄^AST (4 correct draws) | 3.310, eligible 262/500 | `MEASURED` |
| Plain D₄^AST | 2.747, eligible 268/500 | `MEASURED` |
| SPD-hard D₄^AST | 2.690, eligible 262/500 | `MEASURED` |
| SPECTRUM D₄^AST | 2.997, eligible 263/500 | `MEASURED` |
| Per-round trajectories r1…r5, all arms | `[INSERT VERIFIED VALUE from metrics.csv]` | `MISSING` until read |
| Paired D₄ vs SPD-hard | +0.293, [0.233, 0.353], 251 shared eligible tasks | `MEASURED` |
| Paired pass@1 vs SPD-hard (pp) | −0.0118, [−0.0190, −0.0048] | `MEASURED` |
| SPECTRUM pass@1 vs base | +0.0225, [+0.0120, +0.0335] | `MEASURED` |

**Unit warning.** Two different coverage endpoints exist in this repository and must never be conflated on one axis:
- `D₄^AST` — expected number of distinct AST classes in **four correct** draws. Unit: AST classes. Range [1, 4] in practice.
- `coverage@64` — total correct-implementation coverage at a 64-sample budget. Unit: AST classes. Range [0, 64].
The paired SPD-hard comparisons are **+0.293 [0.233, 0.353] (D₄)** and **+3.122 [2.686, 3.596] (coverage@64)**. These are different endpoints, not a unit conversion.

### Statistics and uncertainty

- Intervals are task-bootstrap 95%, **paired** on shared eligible tasks (a task must supply ≥ 4 correct samples in both compared arms), seed 43 only.
- Accuracy uses **all** 500 tasks; coverage uses only eligible tasks, so accuracy and coverage denominators differ.
- Single training seed. No seed-level variation is available. The five rounds are not independent replicates.
- No multiple-comparison correction is applied to these intervals.

### Derived quantities

`ΔD₄^AST` = SPECTRUM minus comparator, paired, mean over shared eligible tasks. Sign convention: **positive = more correct-implementation coverage.**
`retention ratio` = D₄^AST(round t) / D₄^AST(base), per arm. `DERIVED`; formula stated on the axis label.

### Missing information

- Per-round D₄^AST and pass@1 for rounds 1–4 (`MISSING` — must be read from `metrics.csv` before this panel is drawn).
- Base-arm per-round values (base is only measured once; it is a horizontal rule, not a trajectory).
- Any seed other than 43. Any model other than 1.5B. Any benchmark other than MBPP.

## B. Three Candidate Visualizations

| Option | Evidence narrative | Dominant panel | Supporting evidence | Data requirements | Main risk |
|---|---|---|---|---|---|
| 1 | **Headline-first**: five-round coverage trajectories, base as a reference rule | Retention trajectories (≥ 50% width) | Final-checkpoint accuracy dot-strip | per-round D₄ for 3 arms + base rule | traces may overlap; needs direct end-labels |
| 2 | **Two-objective**: each arm as one point in the (accuracy, coverage) plane, arrows from base | Scatter with base-to-final arrows (≥ 50%) | small inset: the two objectives defined | base + final checkpoint per arm only | with 4 points it can read as thin; arrows carry the message |
| 3 | **Diagnostic**: per-round *change* in coverage relative to each arm's own round-1, small multiples | Δ-from-round-1 small multiples (≥ 50%) | paired final deltas vs SPD-hard with intervals | per-round D₄ for all arms | normalization hides absolute level; needs an absolute reference |

**Recommendation: Option 1.** The paper's problem statement is *erosion over repeated rounds*. Only Option 1 shows the erosion mechanism directly, and it degrades gracefully: even if rounds 1–4 are unavailable, rounds 1 and 5 still carry the trajectory claim. Option 2 compresses five rounds into two points and drops the temporal claim; Option 3's within-arm normalization invites the misreading that a flat line means "no loss."

## C. Option 1 — Retention trajectories with an undistilled reference rule

### Design rationale

One dominant panel owns the reading: x = distillation round (base, 1, 2, 3, 4, 5), y = D₄^AST. The base value is drawn as a **horizontal reference rule in muted ink, annotated "undistilled base"** — it is a level, not a series, so it does not get a categorical hue. Three colored traces descend from it. The visual center is the *gap between the base rule and each trace*, which is the quantity the paper is about. Direct labels at every line end name the arm, so color is redundant identity.

The supporting panel is a horizontal dot-strip of final pass@1 for the same four arms, sharing the y-category order, so the reader can check that the coverage ranking is not an accuracy ranking.

### Standalone generation prompt

> **Figure 1, ICLR camera-ready style.** Scientific question: does self-distillation preserve correctness-matched implementation coverage across repeated rounds, and does a continuous-gain intervention preserve more of it than hard projection or plain self-distillation? Source-supported answer: every arm loses coverage relative to the undistilled base across five rounds; the continuous-gain arm (SPECTRUM) loses least.
>
> **Canvas.** Full text width 7.0 in × 2.7 in, white background. Two panels, reading order left→right. Panel (a) occupies 62% of width and is the dominant panel. Panel (b) occupies 34%; a 4% gutter separates them. 8 pt sans-serif throughout (match the manuscript body), horizontal text only.
>
> **Panel (a) — dominant, retention trajectories.** x axis: "Self-distillation round", categorical ticks `base, 1, 2, 3, 4, 5`. y axis: "AST implementation coverage, $D_4$ (↑)", linear. Data: per-round mean $D_4^{AST}$ for `plain`, `spd_hard`, `spectral_soft` from `[INSERT VERIFIED VALUE: metrics.csv per-round D4 for rounds 1-4]`. The `base` value 3.310 is drawn as a **horizontal dashed rule in muted gray `#898781` spanning the full x range, directly labelled "undistilled base (3.31)"** at its right end; it is NOT a fourth line. Each arm is one solid 2 px line with a distinct marker at every round: `spectral_soft` `#2a78d6` diamond ◆, `spd_hard` `#eb6834` triangle ▲, `plain` `#898781` circle ●. Each line carries a **direct end-label** with the arm name, placed to the right of round 5, no legend box. The vertical distance from the base rule down to each trace is the message; annotate it once with a light vertical double-arrow beside round 5 and the text "coverage lost". Shade the region between the base rule and the SPECTRUM trace at 12% opacity in `#2a78d6` only, to make the retained fraction legible.
>
> **Panel (b) — supporting, accuracy.** Horizontal dot-strip, y categories in this order top→bottom: `base`, `plain`, `spd_hard`, `spectral_soft`. x axis: "pass@1 (%) (↑)", linear, spanning 34–46. One dot per arm with a horizontal 95% interval whisker, cap height 3 px: base 37.92 [34.69, 41.40], plain 41.30 [37.94, 44.98], spd_hard 41.35 [37.94, 45.14], spectral_soft 40.17 [36.85, 43.75] (values in percent). Markers and colors identical to panel (a). Direct-label each dot with its value to two decimals. Panel title: "Single-sample accuracy after five rounds".
>
> **Statistical semantics.** D₄ = expected number of distinct AST implementation classes in four *correct* draws, $\sum_j[1-\binom{c-c_j}{4}/\binom{c}{4}]$, macro-averaged over tasks with ≥ 4 correct samples; higher is better. Panel (b) intervals are task-bootstrap 95% over all 500 tasks, seed 43. The two panels use different denominators (eligible tasks vs all tasks) — state this in the caption, not on the axes. Single training seed: do not draw seed-level error bars.
>
> **Negative constraints.** Do not fabricate rounds 1–4 values; if unavailable, draw only the measured round-5 endpoint and label the trace as a direct base→round-5 segment. Do not connect points with a curve or spline — straight segments only. Do not add a trendline or fit. Do not put accuracy and coverage on one panel or use dual y-axes. Do not truncate the y axis in panel (b) to exaggerate differences; start the x range at a stated value and label it. Do not add significance stars. Do not use a legend box when direct labels exist. No 3-D, no gradients, no shadows, no commercial logos.

### Caption and statistical disclosure

> **Figure 1: Self-distillation erodes correct-implementation coverage, in every arm.** Five generate→LoRA rounds of Qwen2.5-Coder-1.5B-Instruct on MBPP (291 synthesis tasks, seed 43), evaluated on all 500 held-out test tasks with 64 samples per task; a 64-sample final-checkpoint supplement supplies the round-5 evaluation. **(a)** Correct-implementation coverage $D_4^{AST}$ — the expected number of distinct AST implementation classes in four correct samples — falls below the undistilled base (dashed rule, 3.31) in all three arms. The continuous-gain arm (SPECTRUM) retains the most; plain self-distillation and hard projection retain least. **(b)** The same arms are all *more* accurate single-shot than the base, so coverage loss is not visible in the field's usual reported metric. Intervals are task-bootstrap 95%. Coverage is computed on tasks with at least four correct samples in the compared arm (262–268 of 500), accuracy on all 500; the two panels therefore have different denominators. One training seed; rounds are sequential, not independent replicates. AST fingerprints are implementation-structure proxies, not audited semantic algorithm labels. `[INSERT VERIFIED VALUE: per-round trajectories]`

### Alt text

Line chart plus dot plot. Top-left: three lines descend over five distillation rounds from a dashed horizontal "undistilled base" rule at 3.31; the blue diamond line labelled SPECTRUM ends highest at 2.997, the orange triangle line labelled SPD-hard ends lowest at 2.690, a gray circle line labelled plain ends at 2.747. Bottom-right: the same four arms as dots with intervals on pass@1, ordered base 37.92%, plain 41.30%, SPD-hard 41.35%, SPECTRUM 40.17% — all distilled arms exceed the base. Main contrast: coverage falls while accuracy rises.

### Accessibility

Identity is carried by direct text labels, not color. Each series has a distinct marker shape. Grayscale survival: blue/orange/gray separate by lightness; the dashed base rule is distinguishable by line style. Minimum 8 pt at final size; no rotated text.

### Negative constraints (restated)

No invented rounds, no fitted curve, no dual axis, no significance stars, no truncated accuracy axis, no legend duplicating direct labels.

## D. Option 2 — Accuracy–coverage plane with base-to-final displacement

### Design rationale

Reframes the same evidence as a two-objective displacement: each arm is one arrow from the base point to its round-5 point. The visual center is the *direction* of every arrow — right (more accurate) and down (less coverage) — which states the paper's problem as a single geometric fact. Emphasizes that the field optimizes the horizontal axis and ignores the vertical one. Compresses the round-by-round story into endpoints.

### Standalone generation prompt

> **Figure 1, ICLR camera-ready style.** Scientific question: when self-distillation raises single-sample accuracy, what happens to correctness-matched implementation coverage? Answer: every arm moves right and down; the continuous-gain arm moves down least.
>
> **Canvas.** Full width 7.0 in × 2.9 in, white. Panel (a) 60% width, dominant. Panel (b) 36%, a compact definition inset. 8 pt sans.
>
> **Panel (a) — dominant, the (accuracy, coverage) plane.** x: "pass@1 (%) (↑)" 34–46. y: "$D_4^{AST}$, coverage in four correct draws (↑)" 2.5–3.5. Draw the undistilled base as a single filled black square at (37.92, 3.310) labelled "base (undistilled)". Draw one 2 px arrow from the base point to each arm's round-5 point: SPECTRUM (40.17, 2.997) `#2a78d6` diamond head; SPD-hard (41.35, 2.690) `#eb6834` triangle head; plain (41.30, 2.747) `#898781` circle head. Arrow heads are marker-shaped, not generic triangles, and match panel (a) of Figure 1's identity. Direct-label each arrow head with the arm name and its (Δacc, Δcov) pair, e.g. "+2.25 pp, −0.31". Draw a light horizontal guide at the base coverage level (dotted `#e1e0d9`) and a light vertical guide at the base accuracy level, so the four quadrants are legible; label the lower-right quadrant "faster, less varied" in muted ink. Add thin 95% interval whiskers on the accuracy axis only (coverage has its own paired interval shown in Figure 3, not here — do not duplicate it).
>
> **Panel (b) — inset.** A small schematic of the two objectives on shared axes: two mini-distributions over implementation classes with equal correct mass and different class spread, annotated "$a_\theta$ equal" and "$D_4$ unequal". Purely `CONCEPTUAL`; no numbers, no axis ticks.
>
> **Statistical semantics.** Point coordinates are means over all 500 tasks (accuracy) and over each arm's eligible tasks (coverage); arrow lengths are therefore not a like-for-like difference and the caption must say so. Intervals: task-bootstrap 95% on accuracy. Single seed.
>
> **Negative constraints.** No fitted frontier, no pareto-front line, no connecting the arm points to each other. No invented quadrant labels beyond the one stated. No third axis. Do not imply causality between the two movements. Inset carries no numbers.

### Caption and statistical disclosure

> **Figure 1: Self-distillation moves every arm right and down.** ... Coordinates are the round-5 checkpoint means; accuracy is macro-averaged over all 500 held-out tasks, coverage over tasks with at least four correct samples (262–268 per arm), so the two coordinates have different denominators and the displacement is descriptive. ... `[INSERT VERIFIED VALUE: per-round trajectories are not shown in this option]`

### Alt text

Scatter plot. One black square labelled base sits at 37.92% pass@1 and 3.31 coverage. Three arrows leave it to the right and downward: SPECTRUM to 40.17%, 3.997; plain to 41.30%, 2.747; SPD-hard to 41.35%, 2.690. All arms gain accuracy and lose coverage; SPECTRUM loses least.

### Accessibility

Arrow heads use distinct marker shapes and direct labels. Quadrant guides are dotted and low-contrast but not load-bearing. Grayscale-safe.

### Negative constraints (restated)

No pareto frontier, no inter-arm connectors, no causal arrows, no numbers in the inset.

## E. Option 3 — Within-arm coverage change, small multiples

### Design rationale

Makes the *rate* of erosion the subject rather than the level: each arm gets its own small panel showing $D_4^{AST}$ relative to its own round 1, so arms with different starting points can be compared for slope. A shared absolute reference band (the base level, normalized the same way) keeps the reader from over-reading the flattening.

### Standalone generation prompt

> **Figure 1, ICLR camera-ready style.** Question: how fast does coverage erode across rounds in each arm, independent of each arm's starting level? Three equal small multiples, left→right: `plain`, `spd_hard`, `spectral_soft`. Each panel: x = round 1–5 (categorical), y = "$D_4^{AST}$ relative to that arm's round 1" 0.80–1.05, with a solid gray 1.0 rule labelled "arm's own round 1". A second dashed rule shows the undistilled base level expressed in the same normalization for that arm, labelled "undistilled base". Outer-shared y tick labels only on the leftmost panel; each panel repeats its arm's direct label as a title in the panel's own color. One 2 px line per panel in the arm's identity color with its identity marker. Annotate only the round-5 value numerically in each panel.
>
> **Statistical semantics.** Normalization is per-arm and destroys cross-arm level comparison — the shared base rule is what restores it. No uncertainty is available per round; state that all panels are single-seed descriptive trajectories.
>
> **Negative constraints.** Do not draw a trendline. Do not use a y axis that hides the absolute fall. Do not add a fourth panel. Do not compare panel heights as if they were effect sizes — the y range is shared.

### Caption and statistical disclosure

> **Figure 1: Erosion rate per arm.** ... Each panel is normalized to its own round 1, so panel *levels* are not comparable; the dashed rule places the undistilled base in the same normalization within each panel. Single seed, five sequential rounds, no per-round uncertainty available.

### Alt text

Three side-by-side line panels, one per method, each showing coverage relative to that method's own first round, all declining toward a dashed base-level rule. SPECTRUM's panel declines most slowly.

### Accessibility

Each panel is titled with its arm name in text, so color is redundant. Shared y range printed once.

### Negative constraints (restated)

No trendlines, no per-panel different y ranges, no fourth panel.

## F. Cross-option evidence-fidelity checklist

- [ ] Every plotted number traces to `metrics.csv` / `eval64/REPORT.md`; no round-1–4 value is invented.
- [ ] `D₄^AST` and `coverage@64` never share an axis.
- [ ] Base is encoded as a rule or a single distinguished point, never as a fourth categorical series.
- [ ] Coverage denominators (eligible tasks) and accuracy denominators (all 500) are disclosed in the caption.
- [ ] Single-seed status is stated; no seed-level error bars are drawn.
- [ ] Identity is carried by direct text labels and marker shape, not color alone.
- [ ] The dominant panel owns ≥ 50% of the canvas in every option.
- [ ] No fit, frontier, spline, or significance marker appears in any option.
- [ ] Bars are absent; if any bar is later introduced, it starts at zero.
- [ ] Rendered at 7.0 in and inspected at that size before sign-off.

## G. Unresolved items

1. **Per-round $D_4^{AST}$ for rounds 1–4** — required for Options 1 and 3; read from `results/retention_5round_train16_eval16_seed43/metrics.csv`. Blocks Options 1 and 3.
2. **Whether the base model was evaluated per round or once.** Base is measured once (an undistilled checkpoint cannot change); confirm and keep it a rule.
3. **Round-1 vs base gap.** If round 1 already sits at the round-5 level, the "erosion over rounds" framing weakens and the claim narrows to "distillation degrades coverage, and the choice of intervention determines how much."
