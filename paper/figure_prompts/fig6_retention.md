# SPECTRUM — Figure 6: Future Repeated-Round Retention Evaluation

**Production status: future experiment prompts only. No repeated-round native-checkpoint retention measurements are available. Do not plot an assumed decline, a flat preservation curve, or a favorable SPECTRUM trajectory.**

## A. Evidence Inventory

### Principal scientific question

Across explicitly defined repeated self-distillation cycles, how do native merged checkpoints change in pass@1 and correct-code AST diversity relative to round 0, under confirmed seed/task pairing and cumulative-budget accounting?

### Source-supported answer

`MISSING`: no measured retention result is available. Repeated optimizer epochs are not self-distillation cycles. The availability of a cycle runner or a candidate multi-round configuration does not demonstrate retention. A D4AST ratio describes retention of the metric's magnitude, not persistence of particular algorithms or AST classes.

### Measurements and comparisons

| Status | Field | Meaning and required source |
|---|---|---|
| `MEASURED` | Repeated-round results | None supplied for this figure. No retention claim is permitted. |
| `CONCEPTUAL` | Candidate methods | `Plain self-distillation`, `SSD`, `Hard spectral`, `SPECTRUM`; actual repeated-round comparison set and baseline configurations are `[MISSING: confirmed run manifest]`. Never imply a control completed every round. |
| `CONCEPTUAL` | Round definition | Round 0 is a documented native starting checkpoint. Each subsequent self-distillation cycle regenerates training outputs from the current model, restores temporary intervention parameters, trains, and produces a merged native checkpoint. Epochs within that training phase do not increment the round axis. |
| `CONCEPTUAL` | SPECTRUM cycle | Recompute `C = (1/M) Σ_{i,u} g_{iu}g_{iu}ᵀ` each round at native K/V outputs using completion-masked reference CE and all nonpadding token positions; `C̄=C/λmax(C)`, `T=[I+τ(I−C̄)]⁻¹`, default `τ=1`. Temporarily fold `W′=TᵀW`, `b′=Tᵀb`; generate one raw completion per training prompt; restore originals; ordinary all-token LoRA on all raw outputs; merge natively. No filters, hooks, prompt ensembles, or inference adapters. |
| `MISSING` | Evaluation fields | Dataset/revision/split, task ID, seed, method, round, checkpoint hash, parent checkpoint hash, sample ID, correctness, AST fingerprint, verifier/decoding protocol, draw count, eligibility, and metric values. |
| `DERIVED` | pass@1 (%) ↑ | Per-task `100c/n`, where n includes all verified evaluation draws; unavailable when n=0. Final aggregation is unconfirmed. |
| `DERIVED` | D4AST ↑ | Expected normalized-AST coverage in four correct draws: `Σ_j[1−choose(c−n_j,4)/choose(c,4)]`; requires c≥4 and complete AST labels among correct draws. Unit: expected distinct fingerprints. Implementation proxy, not semantic algorithm count. |
| `MISSING` | Budget/round plan | `[MISSING: confirmed number of self-distillation cycles]`, per-round and cumulative calibration/generation/training compute, prompt allocation, evaluation draws, and matching rule. Do not hardcode a candidate cycle count or seed count. |
| `MISSING` | Pairing and cohort | `[MISSING: fixed dataset/task universe, seed lineage, round-0 checkpoint alignment, and diversity eligibility rule across methods/rounds]`. Missing round/task observations remain missing. |

### Statistics and uncertainty

Require `[MISSING: independent training seeds]`, `[MISSING: aggregation over tasks and seeds]`, `[MISSING: repeated-measure interval method and level]`, `[MISSING: confirmed pairing key]`, `[MISSING: tests and across-round multiplicity plan]`, and `[MISSING: tie or noninferiority rule]`. Pair only verified common tasks and seed lineages. Do not treat rounds as independent replicates; the checkpoint lineage induces dependence. Report eligible and total task counts by method/round; a changing D4AST cohort can mimic metric retention. A fixed common-eligible cohort may be useful but is not yet authorized as the primary estimator. Never replace an ineligible task's D4AST with zero.

### Derived quantities

For metric M on a confirmed common analysis cohort, define `ΔM_r = M_r − M_0`. Use percentage points for Δpass@1 and expected distinct fingerprints for ΔD4AST. Optional indexed retention is `R_M(r) = 100 × M_r/M_0`, labeled `% of round-0 metric`; it can exceed 100%. If M_0 is zero, missing, or based on an incompatible cohort, ratio is undefined and remains missing. Show raw M_0 and M_r alongside ratios. `[MISSING: aggregate-then-ratio versus mean-of-paired-ratios choice]` must be resolved; these are not interchangeable. Stable semantic strategy retention requires independently audited stable strategy IDs and a separate protocol, which are not supplied and are not part of this figure.

### Missing information

All round-wise native values, lineage records, seeds, task/sample counts, uncertainty, confirmed method/round plan, common eligibility policy, missing-run policy, and budget data are missing. No smoothing, fitted decay, extrapolation, “survival” curve, or monotonic assumption is justified. Preserve possible deterioration, improvement, crossing trajectories, missing rounds, and eligibility changes once measured.

## B. Three Candidate Visualizations

| Option | Evidence narrative | Dominant panel | Supporting evidence | Data requirements | Main risk |
|---|---|---|---|---|---|
| 1 | Native round trajectories | Aligned pass@1 and D4AST trajectories, 65% | Round-0 contrasts and budget/cohort ledger, 35% | Native round scores, lineage, uncertainty, confirmed round plan; all `MISSING` | Lines may imply independent rounds or fill missing checkpoints. |
| 2 | Retention and availability audit | Method/seed × round retention matrix, 60% | Raw-value and eligible-task matrices, 40% | Paired baseline/current scores, ratio definition, cohort counts; all `MISSING` | Indexing hides raw scale and changing eligibility. |
| 3 | Matched baseline-to-round comparison | Paired round-0/current slopes faceted by round, 62% | Per-round deltas and cumulative-budget ledger, 38% | Exact task/seed baseline pairing, raw values, contrast uncertainty; all `MISSING` | Pairing unaligned tasks or treating metric preservation as strategy survival. |

**Recommendation:** Option 1 after native checkpoint measurements arrive. It preserves round ordering and both native metrics without requiring an unconfirmed ratio estimator. Options 2 and 3 require additional verified baseline/cohort pairing; no option is currently a measured figure.

## C. Option 1 — Native Round Trajectories

### Design rationale

Emphasize the whole trajectory of each metric without presupposing decline or preservation. Compress normalized effects into a small audit strip. The risk is apparently continuous performance across unobserved checkpoints; the renderer must break lines at missing rounds.

### Standalone generation prompt

Create planned Figure 6 for “SPECTRUM: Preserving Correct-Code Diversity in Self-Distillation,” on a 178 × 112 mm white double-column ICLR-style canvas with 4 mm gutters. No repeated-round results exist in the supplied evidence. Ask how native merged checkpoints change in accuracy and correct-code AST diversity across true self-distillation cycles relative to round 0. Make panel (a), two aligned native-metric trajectory subplots, 65% of usable area; panel (b), round-0 contrasts and eligibility/budget ledger, 35%. The three-second relationship is two metrics evaluated at the same native checkpoint rounds, not an assumed retention success.

Panel (a) shares an x axis labeled `Self-distillation cycle`, beginning with `0 (native baseline)` and continuing only through `[MISSING: confirmed evaluated cycles]`. Use a top y axis `pass@1 (%) ↑` and lower y axis `D4AST ↑`. Methods are `Plain self-distillation`, `SSD`, `Hard spectral`, `SPECTRUM` only if their actual repeated-round runs are supplied. Require dataset/revision, method, seed lineage, integer cycle, native checkpoint and parent hashes, fixed evaluation task IDs, draw budget, per-task scores, aggregate, and interval metadata. Show small independent-seed observations and larger documented aggregates; connect only successive observed checkpoints within the same method/seed lineage. No interpolation through missing rounds, no smoothing, no fitted decay, and no extrapolation. Until these fields exist, draw no traces or intervals and show `[MISSING: native checkpoint round results]` and `[INSERT VERIFIED VALUE]` in the empty field. Use separate dataset facets in confirmed protocol order; never silently pool datasets. Pass@1 is per-task 100c/n; D4AST is expected normalized-AST coverage in four correct draws, not semantic algorithm count. Display honest native scales and disclose any nonzero y minimum; use no quantitative bars.

Panel (b) gives raw round-0 values and derived ΔM_r=M_r−M_0 on the same confirmed cohort, with `Δpass@1 (percentage points)` and `ΔD4AST (expected AST fingerprints)` in separate columns. Keep `[MISSING: baseline alignment and common eligibility cohort]` until confirmed. Print total and D4AST-eligible tasks at each round; ineligible diversity values are unavailable, not zero. Include `[MISSING: independent seeds]`, `[MISSING: task/seed aggregation and repeated-measure intervals]`, `[MISSING: test, across-round correction, and tie rule]`, and `[MISSING: per-round and cumulative budgets]`. Rounds are dependent repeated measures, not training replicates; epochs do not become cycles. No retention percentage is needed for this design.

SPECTRUM recalibrates C=(1/M)Σ_{i,u}g_{iu}g_{iu}ᵀ at native K/V outputs in every cycle from completion-masked reference CE over all nonpadding token positions. C̄=C/λmax(C), T=[I+τ(I−C̄)]⁻¹ with default τ=1. It temporarily folds W′=TᵀW and b′=Tᵀb, generates one raw completion per training prompt, restores originals, trains ordinary all-token LoRA on all raw outputs, and merges. Evaluate the resulting native checkpoint without filters, hooks, prompt ensembles, or inference adapters; one raw training completion is not the evaluation draw count.

Use SPECTRUM blue #0072B2 diamonds/solid line, Plain dark-gray circles/solid line, SSD medium-gray squares/dotted line, Hard spectral light-gray outlined triangles/dashed line, consistently across panels. Use 8 pt minimum text, 10 pt panel letters, thin axes and sparse grids. Exact text: `Figure 6 | Repeated-round evaluation — awaiting data`, `(a) Native checkpoint trajectories`, `(b) Change from round 0 and evaluation scope`, `Self-distillation cycle`, `0 (native baseline)`, `pass@1 (%) ↑`, `D4AST ↑`, `Δpass@1 (percentage points)`, `ΔD4AST (expected AST fingerprints)`, `AST metric retention is not strategy survival`, the four method names, and all placeholders above. Prohibit fabricated flat or falling curves, fake uncertainty, inferred seed/cycle counts, hidden missing rounds, epoch-as-round labels, best-only tasks, semantic retention claims, causality, dual axes, gradients, and significance stars. Preserve exactly all verified values, comparison sets, metric directions, uncertainty semantics, transformations, selection rules, and missing-data placeholders.

### Caption and statistical disclosure

**Figure 6 (planned; repeated-round data missing).** Native merged-checkpoint pass@1 (%) and D4AST, both higher-is-better, are to be measured across `[MISSING: confirmed self-distillation cycles]` for `[MISSING: confirmed method/run manifest]`. No retention outcome is known. ΔM is native metric minus its round-0 value on `[MISSING: confirmed common cohort]`. Dataset/task counts, independent seeds, lineage pairing, aggregation, repeated-measure intervals, eligibility, cumulative budgets, tests/correction/tie rules, and missing-run policy are `[MISSING]`. D4AST is an implementation proxy; its magnitude does not identify surviving strategies. No fitted or extrapolated trajectory is authorized.

## D. Option 2 — Retention and Availability Matrix

### Design rationale

Emphasize the breadth of repeated-round coverage and the distinction between a lower measured value and missing evidence. Compress native magnitudes into adjacent numeric matrices. The risk is a misleading ratio caused by a small or changing denominator; show the denominator and require a fixed cohort.

### Standalone generation prompt

Design planned Figure 6 for “SPECTRUM: Preserving Correct-Code Diversity in Self-Distillation” as a 178 × 122 mm double-column white figure, 4 mm gutters. No empirical repeated-round retention table is supplied. Ask how measured native-checkpoint accuracy and correct-code AST diversity compare with round 0 across confirmed methods, datasets, and seed lineages. Panel (a), a two-metric indexed-retention matrix, occupies 60% of usable area; panel (b), raw native values, occupies 25%; panel (c), eligibility and budget audit, occupies 15%. The immediate message is which round-wise metric comparisons are measured, undefined, or absent, not that preservation has occurred.

For (a), rows are dataset blocks, method blocks, then independent seed lineages in confirmed manifest order; columns are actual `Self-distillation cycle` values from 0 through `[MISSING: confirmed evaluated cycles]`. Create separate matrices titled `pass@1 (% of round 0)` and `D4AST (% of round 0)`. Each numeric cell requires native baseline/current checkpoint hashes, seed, method, task cohort, and raw M_0 and M_r. Define indexed retention as R_M(r)=100×M_r/M_0 only on a confirmed common cohort. If baseline is zero, missing, or incomparable, mark the ratio `Undefined`; do not impute. The choice of ratio-of-aggregates or aggregate-of-ratios is `[MISSING: ratio aggregation rule]`. Keep matrices entirely unfilled until data arrive, with `[MISSING: paired round-wise native metrics]`. Later use a bounded-by-data diverging color scale centered at 100%, printed limits, and visible numeric values; values above 100% are allowed and must not be clipped. Use hatching plus `Missing` for absent observations so it cannot be read as poor retention. A 100% reference is an indexed baseline, not proof that any specific AST or algorithm persists.

Panel (b) lists exact raw `pass@1 (%) ↑` and `D4AST ↑` for round 0 and every evaluated round, keyed to the same rows. Per-task correctness is 100c/n; D4AST is expected normalized-AST coverage among four correct draws and is unavailable when c<4 or correct-sample AST labels are incomplete. Panel (c) lists total and eligible tasks, fixed-cohort rule, checkpoint availability, per-round and cumulative compute, and evaluation draw budget. Keep `[INSERT VERIFIED VALUE]`, `[MISSING: datasets, seeds, and lineages]`, `[MISSING: common eligibility cohort]`, `[MISSING: aggregation and repeated-measure uncertainty]`, `[MISSING: tests, across-round correction, and tie rule]`, and `[MISSING: budget matching and missing-run policy]`. Do not derive uncertainty from matrix row count or treat rounds/tasks/completions as independent training seeds. If uncertainty cannot fit in cells, put documented intervals in an aligned raw-value table; never discard their meaning.

Each round must be a fresh SPECTRUM cycle: compute C=(1/M)Σ_{i,u}g_{iu}g_{iu}ᵀ at native K/V outputs from completion-masked reference CE over all nonpadding positions; normalize C̄=C/λmax(C); form T=[I+τ(I−C̄)]⁻¹ with τ=1 by default; temporarily fold W′=TᵀW and b′=Tᵀb; generate one raw completion per training prompt; restore original parameters; ordinary all-token LoRA on all raw outputs; merge natively. Evaluation uses native merged checkpoints without filters, hooks, prompt ensembles, or inference adapters. Optimizer epochs are not self-distillation cycles.

Use SPECTRUM blue #0072B2 diamond row keys, Plain self-distillation dark-gray circle keys, SSD medium-gray square keys, Hard spectral light-gray outlined triangle keys. Use a separate clearly labeled retention colormap; method color never doubles as retention magnitude. Keep 8 pt minimum text, 10 pt panel letters, short horizontal row labels, and readable cell values. Exact text: `Figure 6 | Indexed metric retention — awaiting data`, `(a) Relative to round 0`, `(b) Raw native metrics`, `(c) Availability, eligibility, and budgets`, `Self-distillation cycle`, `pass@1 (% of round 0)`, `D4AST (% of round 0)`, `pass@1 (%) ↑`, `D4AST ↑`, `Missing`, `Undefined`, `AST metric retention is not strategy survival`, the four method names, and all placeholders above. Prohibit invented matrices, plausible survival patterns, undefined-ratio imputation, clipping above 100%, fabricated uncertainty, epoch-as-round labels, seed-count assumptions, semantic strategy survival, hidden eligibility changes, and decorative heatmaps. Preserve exactly all verified values, comparison sets, metric directions, uncertainty semantics, transformations, selection rules, and missing-data placeholders.

### Caption and statistical disclosure

**Figure 6 (planned; indexed values missing).** Indexed native-metric retention is `100×M_r/M_0` on `[MISSING: common cohort and ratio aggregation rule]`, with raw pass@1 and D4AST shown separately. Higher native values are better; 100% means equal metric magnitude to round 0 and does not identify persistent algorithms. Ratios with zero, missing, or incompatible baselines are undefined. Method/round manifest, datasets, seeds, task eligibility, lineage pairing, aggregation, intervals, tests/correction/tie rules, and cumulative budgets are `[MISSING]`. No measured retention pattern, fitted trend, or extrapolation is presented by this specification.

## E. Option 3 — Matched Baseline-to-Round Audit

### Design rationale

Emphasize how each matched seed/task population changes from its own native baseline at each later round. Compress the temporal path into repeated baseline comparisons. The risk is implying that identical aggregate diversity means identical underlying implementations; caption and axis labels must rule out that inference.

### Standalone generation prompt

Create planned Figure 6 for “SPECTRUM: Preserving Correct-Code Diversity in Self-Distillation” on a 178 × 118 mm white double-column canvas with 4 mm gutters. No repeated-round native-checkpoint observations are available. Ask how the same confirmed task populations and training-seed lineages change in accuracy and correct-code AST diversity from round 0 to each evaluated self-distillation cycle. Allocate 62% of usable area to panel (a), a faceted matched baseline-to-round slope field, 23% to panel (b), contrast intervals, and 15% to panel (c), lineage/eligibility/budget scope. The three-second relationship is explicit baseline pairing and two separate native outcomes, not a favorable retention claim.

Panel (a) is grouped by confirmed dataset and has one facet per `[MISSING: confirmed later cycle]`, in true cycle order. Every facet has two adjacent native-metric columns, `pass@1 (%) ↑` and `D4AST ↑`; within each show categorical endpoints `Round 0` and `Round r`. Plot the same verified method/seed/common-task cohort at those two endpoints, connecting only if the full pairing key is confirmed. Do not join unrelated seed IDs, datasets, or task cohorts; if pairing is absent, keep `[MISSING: verified baseline-to-round pairing]` and draw no slopes. Require seed lineage, method, native baseline/current checkpoint hashes, dataset/revision, fixed task IDs, per-task values, aggregate, and interval metadata. All absent coordinates remain `[INSERT VERIFIED VALUE]` text outside the axes. Use small seed marks and only documented aggregate/interval overlays; do not make each completion a replicate. The number of facets remains a placeholder, never a guessed cycle count. Include every confirmed round, adverse change, incomplete run, and missing checkpoint. Use consistent metric scales across facets, no smoothing, no mean trend pasted onto individual seeds.

Panel (b) uses separate zero-centered contrast strips titled `Δpass@1 (percentage points)` and `ΔD4AST (expected AST fingerprints)`, where ΔM_r=M_r−M_0 on the same confirmed analysis cohort. Pair each contrast to the corresponding native values above. Keep `[MISSING: contrast aggregation and repeated-measure interval definition]`; no tie, equivalence, noninferiority, or significance label follows merely from crossing zero. D4AST is expected normalized-AST coverage in four correct draws, not semantic algorithm count; require complete AST labels and at least four correct samples. Correctness includes all tasks under its declared task universe. Panel (c) lists `[MISSING: confirmed methods, datasets, independent seeds, and round plan]`, `[MISSING: task/seed pairing and eligibility policy]`, `[MISSING: tests, across-round correction, and tie rule]`, and `[MISSING: per-round/cumulative budgets and missing-run policy]`. Report the total/eligible task counts used in every contrast.

In each SPECTRUM cycle, recompute C=(1/M)Σ_{i,u}g_{iu}g_{iu}ᵀ at native K/V outputs from completion-masked reference CE over all nonpadding token positions, normalize C̄=C/λmax(C), and use T=[I+τ(I−C̄)]⁻¹ with default τ=1. Temporarily fold W′=TᵀW and b′=Tᵀb for one raw completion per training prompt, restore originals, train ordinary all-token LoRA on all raw outputs, and merge into native weights. Evaluate native checkpoints without filters, hooks, prompt ensembles, or inference adapters. Round 0 is the documented initial native checkpoint; an optimizer epoch does not constitute a cycle.

Use SPECTRUM blue #0072B2 diamonds/solid connectors, Plain self-distillation dark-gray circles, SSD medium-gray squares/dotted connectors, Hard spectral light-gray outlined triangles/dashed connectors. Do not encode method and change sign with the same color. Set minimum labels 8 pt, panel letters 10 pt, thin charcoal axes and zero references, sparse grids, no gradients or rotated labels. Exact text: `Figure 6 | Matched round-0 comparisons — awaiting data`, `(a) Paired native checkpoint changes`, `(b) Difference from round 0`, `(c) Lineage and evaluation scope`, `Round 0`, `Round r`, `pass@1 (%) ↑`, `D4AST ↑`, `Δpass@1 (percentage points)`, `ΔD4AST (expected AST fingerprints)`, `AST metric retention is not strategy survival`, the four method names, and all placeholders above. Prohibit fabricated slopes, assumed seed/round counts, unmatched pairing, imputed unavailable diversity, hidden adverse results, epochs labeled cycles, inferred semantic survival, causal claims, fabricated intervals, and significance stars. Preserve exactly all verified values, comparison sets, metric directions, uncertainty semantics, transformations, selection rules, and missing-data placeholders.

### Caption and statistical disclosure

**Figure 6 (planned; paired changes missing).** Round-0 and later native checkpoints would be compared on `[MISSING: confirmed matched seed/task cohorts]` for pass@1 (%) and D4AST, both higher-is-better. ΔM is later value minus baseline in native units. Main result and retention conclusion are unavailable. Confirmed methods/cycles, datasets, independent seeds, lineage pairing, task eligibility, aggregation, repeated-measure intervals, tests/correction/tie criteria, cumulative budgets, and missing-run rules are `[MISSING]`. Slopes identify paired measurements only; equal D4AST does not imply retention of particular implementations or algorithms. No fitted or extrapolated values are part of this design.

## F. Cross-option evidence-fidelity checklist

- Exactly three distinct evidence organizations share the same future round-wise accuracy/diversity requirements.
- Every option names a dominant field of at least 50%; supporting panels audit baseline change, eligibility, or budget.
- No retention values, trajectories, cycle counts, seed counts, error bars, or claims have been invented.
- A round is a complete regenerate–restore–train–merge cycle, not an optimizer epoch; the gradient second moment is recomputed each cycle.
- Evaluations refer to native merged checkpoints with explicit lineage, dataset/task, verifier, and decoding identities.
- Both raw pass@1 and D4AST remain visible; the latter is correct-code AST coverage, not semantic strategy survival.
- Missing or ineligible D4AST values are not zero; task eligibility and pairing across rounds remain required protocol inputs.
- Deltas and optional ratios disclose formulas, units, denominators, aggregation order, and zero/missing handling.
- Rounds are dependent repeated measures, never extra independent training seeds; intervals and multiplicity remain unconfirmed.
- Per-round/cumulative budgets, common-cohort rules, and failed/missing runs are disclosed before interpreting retention.
- Temporary generation folding/restoration, one raw training output per prompt, all-token LoRA on all raw outputs, native merging, and the exclusion of filters/hooks/prompt ensembles/inference adapters remain exact.
