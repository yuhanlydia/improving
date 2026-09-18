# SPECTRUM — Figure 4: Future Formal Comparison

**Production status: future experiment prompts only. No formal results are available. Do not render data marks until verified inputs replace the `MISSING` fields.**

## A. Evidence Inventory

### Principal scientific question

At matched, explicitly accounted budgets, how do Plain self-distillation, SSD, Hard spectral, and SPECTRUM compare in pass@1 and correct-code AST diversity across the eventually confirmed datasets and independent training seeds?

### Source-supported answer

`MISSING`: the formal experiment has no measured answer. The figure must expose the joint accuracy/diversity comparison without asserting a winner, noninferiority, robustness, or statistical significance. The paper title is **SPECTRUM: Preserving Correct-Code Diversity in Self-Distillation**; “preserving” in the title is not evidence that a formal result exists.

### Measurements and comparisons

| Status | Field | Meaning and required source |
|---|---|---|
| `MEASURED` | Formal observations | None supplied; exploratory pilot observations must not be relabeled formal. |
| `CONCEPTUAL` | Method labels | `Plain self-distillation`, `SSD`, `Hard spectral`, `SPECTRUM`; exact baseline configurations remain `[MISSING: baseline implementation and checkpoint manifest]`. |
| `MISSING` | Benchmark ledger | `[MISSING: confirmed dataset names, revisions, splits, task IDs, and task counts]`; do not turn candidate dataset names into completed evaluations. |
| `MISSING` | Replication | `[MISSING: confirmed independent training seeds and per-seed run IDs]`; do not assume a seed count from a candidate configuration. |
| `MISSING` | Native evaluation | Per-method, dataset, seed, checkpoint, task, sample ID, correctness, normalized-AST fingerprint, decoding settings, and verifier provenance. Evaluate restored/merged native checkpoints without inference adapters. |
| `DERIVED` | pass@1 ↑ | Per-task estimator `c/n`, where `c` is verified correct completions and `n` all evaluation completions; display as percent. All raw values are `[INSERT VERIFIED VALUE]`. |
| `DERIVED` | D4AST ↑ | Expected distinct normalized-AST fingerprints in four draws without replacement from the correct completion pool: `Σ_j [1 − choose(c−n_j,4)/choose(c,4)]`. Local `metrics.py` verifies this estimator. Require `c ≥ 4` and complete correct-sample AST labels; otherwise unavailable. Unit: expected distinct AST fingerprints, not percent or semantic algorithms. |
| `CONCEPTUAL` | Method scope | SPECTRUM uses native K/V output gradients from completion-masked reference CE at all nonpadding token positions: `C = (1/M) Σ_{i,u} g_{iu}g_{iu}ᵀ`, `C̄ = C/λmax(C)`, `T = [I + τ(I−C̄)]⁻¹`, default `τ = 1`. Temporarily fold `W′ = TᵀW`, `b′ = Tᵀb`; generate one raw completion per training prompt; restore; ordinary LoRA on all raw outputs with all-token loss; merge into native weights. Recompute calibration each round. |
| `MISSING` | Budget matching | `[MISSING: confirmed training-prompt count, calibration allocation, generation tokens, optimization tokens/steps, compute accounting, evaluation samples per task, and matching rule]`. One raw training completion per prompt is method specification, not the evaluation sample count. |

### Statistics and uncertainty

No formal aggregate, CI, SD, SE, test, or tie criterion exists in the supplied evidence. Require `[MISSING: aggregation across tasks and independent training seeds]`, `[MISSING: interval definition and level]`, `[MISSING: pairing key and paired analysis confirmation]`, `[MISSING: test and multiplicity family]`, and `[MISSING: tie or noninferiority rule]`. The possible hierarchy is completions within tasks within dataset/seed runs; completions are not independent training replicates. Report total and D4AST-eligible tasks for each method and the exact cohort for each contrast. Do not silently compare different eligible subsets or drop zero-correct tasks from pass@1. A task-bootstrap interval from one seed must not be presented as uncertainty across seeds.

### Derived quantities

After protocol confirmation, possible contrasts are `Δpass@1 = pass@1_method − pass@1_Plain` in percentage points and `ΔD4AST = D4AST_method − D4AST_Plain` in expected distinct fingerprints. They require matched analysis populations and actual inputs; all effects remain `[INSERT VERIFIED VALUE]`. Do not average native units together. No Pareto frontier, causal effect, inferred noninferiority threshold, or significance marker is authorized by the present evidence.

### Missing information

All result coordinates, counts, uncertainty, dataset/seed plans, exact matching tolerances, baseline details, eligibility rules across methods, and task aggregation are absent or unconfirmed. Required machine-readable input fields: `dataset_id`, `dataset_revision`, `split`, `method`, `training_seed`, `checkpoint_id`, `budget_id`, `task_id`, `sample_id`, `correct`, `ast_fingerprint`, `n`, `c`, `D4AST`, `eligible`, `aggregate`, `interval_low`, `interval_high`, `interval_type`, and protocol metadata. The figure-production stage must fail closed when a coordinate or its scientific meaning is missing.

## B. Three Candidate Visualizations

| Option | Evidence narrative | Dominant panel | Supporting evidence | Data requirements | Main risk |
|---|---|---|---|---|---|
| 1 | Native-metric benchmark audit | Aligned dataset-by-metric dot/interval facets, 66% | Budget and eligibility ledger, 34% | Exact native scores, task/seed aggregation, intervals, confirmed dataset order; all `MISSING` | Averages may conceal seed variability unless seed-level marks are retained. |
| 2 | Joint accuracy/diversity behavior | Dataset-faceted accuracy–diversity scatter, 65% | Raw-value and cohort strip, 35% | Both metrics for each same run/cohort, verified pairing and uncertainty; all `MISSING` | Position alone can imply a universal winner; different cohorts invalidate coordinates. |
| 3 | Reviewer contrast audit | Two-unit effect forest versus Plain, 62% | Native-value columns and budget/cohort ledger, 38% | Reproducible deltas and contrast intervals, confirmed comparator pairing; all `MISSING` | Baseline normalization can hide native magnitudes. |

**Recommendation:** Option 1 once formal data arrive. It shows both native metrics and incomplete replication clearly. Options 2 and 3 are conditional on verified joint observations and contrast construction; none is presently a result figure.

## C. Option 1 — Native-Metric Benchmark Audit

### Design rationale

Emphasize the complete comparison set and both outcomes without collapsing them to a scalar. Compress budget details into a readable ledger. The risk is excessive facets if many datasets are eventually confirmed; extend vertically instead of deleting datasets or shrinking labels.

### Standalone generation prompt

Create the planned Figure 4 for the research paper “SPECTRUM: Preserving Correct-Code Diversity in Self-Distillation,” in a restrained ICLR-style double-column layout, approximately 178 × 108 mm, white background, 4 mm gutters. This is a future-data production specification: no formal observations exist. The question is whether Plain self-distillation, SSD, Hard spectral, and SPECTRUM differ in pass@1 and D4AST under a confirmed matched-budget protocol. The three-second message must be the presence of two distinct outcomes and a complete four-method comparison, never an unsupported win. Allocate 66% of usable area to panel (a), a unified native-metric comparison field; allocate 34% to panel (b), a budget, replication, and eligibility ledger. Read left-to-right, then downward.

In (a), create one row per `[MISSING: confirmed dataset name and revision]`, ordered by the final evaluation protocol rather than performance. Within each row place two horizontally aligned facets titled `pass@1 (%) ↑` and `D4AST ↑`. Use methods in the exact order `Plain self-distillation`, `SSD`, `Hard spectral`, `SPECTRUM` on the categorical axis. Map verified per-seed run scores to small method-shaped points, verified aggregate scores to larger points, and only documented intervals to whiskers. Require fields dataset, method, training_seed, budget_id, checkpoint_id, per-task counts, aggregate, interval limits, and interval type. Before data exist, leave all data layers empty and place `[MISSING: formal results]` and `[INSERT VERIFIED VALUE]` in the specification or empty panel area; never place a placeholder at an invented numeric coordinate. Print exact aggregate values next to marks only after verification. Use percent for pass@1; D4AST is expected distinct normalized-AST fingerprints in four correct draws, not algorithms. Keep metric scales consistent across datasets when scientifically possible; pass@1 is bounded 0–100 and D4AST has theoretical range 1–4 when eligible, but these bounds are not observations. Use dots rather than bars; state any nonzero displayed axis limits explicitly. There is no baseline ranking highlight.

In (b), use text/table rows for `[MISSING: training seeds]`, `[MISSING: task counts and D4AST eligibility]`, `[MISSING: matched-budget definition]`, and `[MISSING: verifier and decoding protocol]`. The ledger must distinguish the evaluation draw count from the one raw training completion per training prompt. Require native merged checkpoint evaluation without filters, hooks, prompt ensembles, or inference adapters. For SPECTRUM, the reference-CE gradient second moment at all nonpadding positions of native K/V outputs defines `C̄ = C/λmax(C)` and `T = [I + τ(I−C̄)]⁻¹` with `τ = 1`; temporary weight/bias folding is restored before ordinary all-token LoRA on all raw generated outputs, followed by native merging. Do not diagram unverified baseline internals.

Do not choose mean, median, bootstrap, SD, SE, CI, test, correction, or tie rule by convention. Keep `[MISSING: task/seed aggregation]`, `[MISSING: interval definition]`, `[MISSING: pairing and eligible cohort]`, and `[MISSING: test, correction, and tie rule]` visible until the protocol supplies them. Correctness includes all tasks; unavailable D4AST values remain missing. Seed points represent independent training seeds, not completion replicates. Use SPECTRUM blue #0072B2 diamond, Plain dark-gray circle, SSD medium-gray square, and Hard spectral light-gray triangle with dark outline; preserve identities everywhere. Set body labels at least 8 pt and panel letters 10 pt at final size, thin charcoal axes, sparse light-gray gridlines, no outer frame.

Use verbatim text: `Figure 4 | Formal comparison — awaiting data`, `(a) Accuracy and correct-code AST diversity`, `(b) Budget and eligibility`, `pass@1 (%) ↑`, `D4AST ↑`, `Plain self-distillation`, `SSD`, `Hard spectral`, `SPECTRUM`, `AST diversity is an implementation proxy`, and the explicit missing placeholders above. Prohibit fabricated scores, plausible error bars, significance stars, inferred seed counts, unconfirmed dataset names, benchmark winner labels, causal language, trained-output filtering, truncated bars, dual y-axes, gradients, logos, and tiny rotated labels. Preserve exactly all verified values, comparison sets, metric directions, uncertainty definitions, transformations, selection rules, and missing-data placeholders.

### Caption and statistical disclosure

**Figure 4 (planned; no formal results available).** Matched-budget comparison of Plain self-distillation, SSD, Hard spectral, and SPECTRUM on `[MISSING: confirmed datasets]`. Both pass@1 (%) and D4AST are higher-is-better; D4AST measures expected AST coverage in four correct draws and is an implementation proxy. Formal outcome: `[MISSING: result]`. Aggregation, intervals, independent seed count, task universe, eligible-task cohort, exact budget, pairing, tests, correction, and tie rule: `[MISSING: confirmed protocol]`. No fitted, extrapolated, or observed result is shown by this prompt. All tasks enter correctness; the eventual diversity eligibility rule and counts must be disclosed.

## D. Option 2 — Joint Accuracy–Diversity Map

### Design rationale

Emphasize whether an apparent diversity difference accompanies an accuracy difference. Compress per-method detail into a supporting native-value ledger. This is a two-outcome map, not a compute Pareto frontier; its coordinates are valid only for aligned populations and runs.

### Standalone generation prompt

Design planned Figure 4 for “SPECTRUM: Preserving Correct-Code Diversity in Self-Distillation” as a 178 × 112 mm double-column scientific figure, white background, 4 mm gutters. No formal experiment observations have been supplied. Ask how Plain self-distillation, SSD, Hard spectral, and SPECTRUM jointly compare in accuracy and correct-code AST diversity at a confirmed matched budget. Make panel (a), dataset-faceted joint outcome maps, occupy 65% of usable area; reserve 35% below for panel (b), native values, sample eligibility, and budget metadata. The immediate relationship is two measured objectives per same evaluation run, with no result claim until verified data arrive.

For each confirmed dataset facet in (a), map pass@1 in percent to x, labeled `pass@1 (%) ↑`, and expected distinct normalized-AST fingerprints among four correct draws to y, labeled `D4AST ↑`. Required fields are dataset/revision, method, seed, native checkpoint ID, budget ID, task cohort ID, both metrics, and uncertainty metadata. Both coordinates must use the same declared run and compatible cohorts; if the primary correctness universe and conditional D4AST universe differ, disclose the two populations and show an additional cohort-matched correctness coordinate only after its definition is approved. Individual independent training seeds are small method-shaped points; only verified across-seed aggregates receive larger symbols. Connect method points with fine neutral lines only if a seed/task/budget pairing key is confirmed, and label them `Matched runs`; otherwise draw no connecting lines. Show separate horizontal/vertical documented intervals, not an invented joint confidence ellipse. Use no hulls, Pareto frontier, fitted trend, or best-method region. Missing coordinates yield no marks: display `[MISSING: joint formal observations]` and `[INSERT VERIFIED VALUE]` as text outside the quantitative plane. Use common scales across facets, bounds informed by metrics and actual data, and clear endpoint ticks. Do not add an arrow claiming improvement.

Panel (b) contains a compact table in confirmed dataset order with all four exact method names, raw pass@1 and D4AST values, independent seed count, total/eligible tasks, and budget ID. Every numeric cell is `[INSERT VERIFIED VALUE]` until supplied. Report `[MISSING: task/seed aggregation]`, `[MISSING: interval definition and level]`, `[MISSING: confirmed datasets and seeds]`, `[MISSING: matching rule and evaluation samples]`, and `[MISSING: tests, multiplicity correction, and tie criterion]`. Do not turn completion samples into training replicates. Calculate per-task pass@1 as c/n and D4AST as Σ_j[1−choose(c−n_j,4)/choose(c,4)] for complete AST labels and c≥4; final cross-method cohort handling is `[MISSING: eligibility protocol]`. Retain unavailable values explicitly and show all correctness tasks.

Evaluate final native merged checkpoints. SPECTRUM uses `C = (1/M) Σ_{i,u} g_{iu}g_{iu}ᵀ` from completion-masked reference-CE gradients at native K/V outputs over all nonpadding token positions, normalizes by λmax(C), and constructs `T = [I + τ(I−C̄)]⁻¹`, default τ=1. It temporarily folds W′=TᵀW and b′=Tᵀb for one raw completion per training prompt, restores the original parameters, trains ordinary LoRA on all raw outputs with all-token loss, and merges. No filtering, hooks, prompt ensembles, or inference adapters may be inserted into the interpretation.

Use SPECTRUM blue #0072B2 diamond, Plain dark-gray circle, SSD medium-gray square, Hard spectral light-gray triangle with dark outline. Use these same shapes in table keys; do not use color for datasets or performance sign. Keep labels at least 8 pt, panel letters 10 pt, and gridlines light and sparse. Exact required text is `Figure 4 | Joint outcomes — awaiting data`, `(a) Accuracy–diversity relationship`, `(b) Native values and matched conditions`, `pass@1 (%) ↑`, `D4AST ↑`, `Plain self-distillation`, `SSD`, `Hard spectral`, `SPECTRUM`, `AST diversity is an implementation proxy`, and every placeholder stated above. Prohibit fabricated points, trends, seed counts, confidence ellipses, significance, dominance claims, invented datasets, cohort substitution, misleading dual axes, gradients, and decorative charts. Preserve exactly all verified values, comparison sets, metric directions, uncertainty definitions, transformations, selection rules, and missing-data placeholders.

### Caption and statistical disclosure

**Figure 4 (planned; joint observations missing).** Each eventual coordinate compares pass@1 (%) and D4AST for one native checkpoint under `[MISSING: matched-budget and cohort protocol]`; larger values are better on both axes. Methods are Plain self-distillation, SSD, Hard spectral, and SPECTRUM. No winner or accuracy–diversity relationship is established. Dataset/seed count, task populations, point aggregation, interval meaning, pairing, tests, correction, and tie rule are `[MISSING]`. Lines, if later authorized, identify matched runs rather than trajectories or causal effects. D4AST is expected AST coverage in four correct draws, not semantic algorithm count.

## E. Option 3 — Contrast Forest With Native-Value Audit

### Design rationale

Emphasize method-specific gains and losses against a common baseline while retaining raw magnitudes. Compress absolute positions into aligned numeric columns. The risk is an apparently favorable delta created by different eligibility cohorts; contrast generation must confirm the task set before plotting.

### Standalone generation prompt

Create planned Figure 4 for “SPECTRUM: Preserving Correct-Code Diversity in Self-Distillation,” using a 178 × 118 mm double-column white canvas. This prompt contains no formal measurements. Ask whether each comparator differs from Plain self-distillation in both accuracy and correct-code AST diversity at a verified matched budget. Panel (a), a two-unit effect forest, must occupy 62% of usable area on the left. Panel (b), aligned native-value columns, occupies 26% on the right; panel (c), a full-width budget/eligibility footer, occupies 12%. The three-second visual relationship is signed effects around honest zero lines with both favorable and unfavorable changes equally visible.

In (a), group rows by `[MISSING: confirmed dataset name and revision]` in protocol order. Within each dataset order comparison rows `SSD − Plain`, `Hard spectral − Plain`, `SPECTRUM − Plain`. Use two separate x scales labeled `Δpass@1 (percentage points)` and `ΔD4AST (expected AST fingerprints)`, each centered on a clearly labeled zero reference. Define deltas as method minus Plain self-distillation; never combine unlike units. Use only verified paired contrasts on the declared common task cohort; if pairing is unconfirmed, retain `[MISSING: valid contrast inputs]` without drawing points or lines. For each row require method, dataset, independent training seed IDs, checkpoint IDs, budget ID, contrast cohort, raw scores, derived contrast, and interval metadata. Draw point/interval marks from those fields and print `[INSERT VERIFIED VALUE]` until they exist. Use symmetric display ranges where feasible, otherwise label every bound and retain all negative effects. An interval crossing zero does not automatically mean tie; do not label superiority, equivalence, or noninferiority without an approved decision rule.

Panel (b) lists raw pass@1 (%) and D4AST for all four methods, including Plain, aligned to corresponding dataset groups. Show aggregate values and n only when the actual aggregation and statistical unit are known. D4AST is expected AST coverage in four correct draws, computed as Σ_j[1−choose(c−n_j,4)/choose(c,4)] with complete normalized-AST labels and c≥4; it is an implementation proxy. Per-task pass@1 is c/n and retains zero-correct tasks. Panel (c) displays `[MISSING: formal datasets and training seeds]`, `[MISSING: task/seed aggregation and interval definition]`, `[MISSING: contrast cohort and eligibility counts]`, `[MISSING: matched training, calibration, compute, and evaluation budgets]`, and `[MISSING: test, multiplicity correction, tie or noninferiority rule]`. Do not import pilot uncertainty or a candidate margin into the formal figure. Include the raw metrics because baseline subtraction can hide scale.

The evaluated models are restored/merged native checkpoints. SPECTRUM constructs C=(1/M)Σ_{i,u}g_{iu}g_{iu}ᵀ using native K/V output gradients of completion-masked reference CE at every nonpadding token position, uses C̄=C/λmax(C), and applies T=[I+τ(I−C̄)]⁻¹ with default τ=1. Its W′=TᵀW and b′=Tᵀb are temporary for generating one raw completion per training prompt; restore before ordinary all-token LoRA on all raw outputs, then merge natively. No training-data filters, hooks, prompt ensembles, or inference adapters enter the figure. Baseline implementation details remain missing until documented.

Use SPECTRUM blue #0072B2 diamonds, Plain dark-gray circles, SSD medium-gray squares, Hard spectral light-gray triangles with dark outlines; maintain identities in all raw-value keys. Use 8 pt minimum labels, 10 pt panel letters, thin charcoal zero lines, light nonzero gridlines, no row ranking by unobserved effects, no commercial decoration. Exact text: `Figure 4 | Formal contrasts — awaiting data`, `(a) Difference from Plain self-distillation`, `(b) Native metrics`, `(c) Budget and statistical scope`, `Δpass@1 (percentage points)`, `ΔD4AST (expected AST fingerprints)`, `Plain self-distillation`, `SSD`, `Hard spectral`, `SPECTRUM`, `AST diversity is an implementation proxy`, and all missing placeholders above. Prohibit fabricated contrasts, pseudo-replicates, winner labels, significance stars, guessed seeds, unconfirmed datasets, hidden losses, unapproved margins, truncated bars, dual axes, and decorative heatmaps. Preserve exactly all verified values, comparison sets, metric directions, uncertainty definitions, transformations, selection rules, and missing-data placeholders.

### Caption and statistical disclosure

**Figure 4 (planned; formal contrasts missing).** Signed differences from Plain self-distillation are shown separately for pass@1 in percentage points and D4AST in expected distinct AST fingerprints, with positive values favorable. Comparators are SSD, Hard spectral, and SPECTRUM; raw values include all four methods. Result, datasets, seeds, matched-budget definition, common eligibility cohort, aggregation, intervals, pairing, tests, multiplicity correction, and tie/noninferiority rule are `[MISSING: verified formal protocol and results]`. Zero is a reference, not a decision threshold. This specification contains no observed, fitted, or extrapolated numerical result.

## F. Cross-option evidence-fidelity checklist

- Exactly three structurally distinct alternatives use the same future comparison set and both metrics.
- No formal scores, effect sizes, rankings, seed counts, dataset assignments, intervals, or statistical claims have been invented.
- One named dominant panel occupies at least half of every design; supporting material audits the same comparison.
- Every future mark requires verified fields; `MISSING` values remain text or unavailable entries, never plausible coordinates.
- Native pass@1 percentages and D4AST units/directions remain separate; derived deltas state their formulas.
- D4AST is conditional correct-code AST coverage, not semantic algorithm identity; per-method and common-cohort eligibility remain explicit.
- Sample units, independent training replication, pairing, intervals, tests, correction, and tie/noninferiority rules are unconfirmed until supplied.
- Matched-budget labels require complete accounting, including calibration and generation; one raw training completion is not the evaluation draw count.
- SPECTRUM method scope is exact, and native merged checkpoints have no inference adapter or generation intervention.
- No unconfirmed proposed protocol becomes a measured experiment; final captions cannot claim success before data arrive.
