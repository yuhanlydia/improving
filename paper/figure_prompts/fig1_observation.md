# SPECTRUM — Figure 1: Pilot observation

## A. Evidence Inventory

### Principal scientific question
Does the ordering by single-draw correctness determine the ordering by diversity among correct programs?

### Source-supported answer
No in this exploratory pilot: SSD has the highest reported pass@1, while SPECTRUM has the highest expected AST coverage in four correct draws. The differences are small; these are not confirmatory multi-seed results and AST variation does not establish distinct semantic algorithms.

### Measurements and comparisons
`MEASURED`: Qwen2.5-Coder-1.5B-Instruct, 64 held-out MBPP tasks, 64 samples per task, seed 42, final checkpoints after one self-distillation cycle. The post hoc analysis extracts the first Python/py/untagged fenced block and uses local execution. Figure labels map Plain→Plain, SSD→SSD, SPD-hard→SPD-hard, Spectral-soft→SPECTRUM.

| Method | pass@1 (%) ↑ | Expected AST coverage in four correct draws, D4AST ↑ |
|---|---:|---:|
| Plain | 36.82 | 3.393 |
| SSD | 36.89 | 3.391 |
| SPD-hard | 36.87 | 3.409 |
| SPECTRUM | 36.65 | 3.422 |

Source: [immutable pilot report](https://github.com/yuhanlydia/improving/blob/d8a50903de671cdb7e5c23a28ff43de1c32c16b5/results/pilot_seed42_codecentric/README.md). Local source inspected at `improving-geometry-review/results/pilot_seed42_codecentric/README.md`.

### Statistics and uncertainty
`MEASURED`: paired final-checkpoint SPECTRUM−SSD D4AST difference +0.0312, reported pointwise 95% CI [0.0095, 0.0550]; pass@1 difference −0.244 percentage points, 95% CI [−0.854, 0.342]. These paired estimates use a common eligible cohort and must not be reconstructed by subtracting the independently reported per-arm coverage means. Intervals have no multiple-comparison correction. Per-arm intervals, replicate-level measurements, exact resampling implementation, and a confirmatory tie rule are `MISSING`. D4AST is conditional on available correct programs; its eligible-task denominator can differ across arms. No seeds beyond 42 are implied.

### Derived quantities
`DERIVED`: ordering of the supplied rounded means. For a task with c correct samples and AST-class counts n_j, coverage in four correct draws is sum_j[1−choose(c−n_j,4)/choose(c,4)], when eligibility and labels are complete. A plotted mean difference must specify its cohort; unpaired rounded-mean difference is not the reported paired effect. Do not interpret the 0.24 percentage-point rounded difference as the exact −0.244 point paired estimate.

### Missing information
`MISSING`: multi-seed confirmation; per-arm uncertainty; complete per-task data for scatter distributions; semantic-algorithm labels; a fixed future extractor and inference margin. No noninferiority or statistical-tie badge is authorized.

## B. Three Candidate Visualizations

| Option | Evidence narrative | Dominant panel | Supporting evidence | Data requirements | Main risk |
|---|---|---|---|---|---|
| 1 | Native metrics reveal rank reversal | D4AST dot plot, 60% plot width | Aligned pass@1 dot plot, 40% | Supplied eight means; available | Expanded dot axes can overstate small gaps |
| 2 | Accuracy–diversity relationship | Four-point two-objective scatter, 70% | Exact-value ledger, 30% | Supplied paired coordinates per method; available | Connecting methods would imply a trajectory |
| 3 | Paired uncertainty qualifies the observation | Two-unit paired-effect forest, 60% | Raw per-arm mean ledger, 40% | Two supplied effects and CIs; available | Paired cohort must not be confused with per-arm means |

**Recommendation:** Option 1 is the embedded figure. It exposes native magnitudes and the changed ordering with no unsupported per-arm error bars. Option 3 is useful when the paired interval disclosure is the primary argument.

## C. Option 1 — Aligned native-metric dot plots

### Design rationale
Make diversity the visual center and correctness its aligned qualifier. Emphasize the reversal; compress paired inference into the caption. Both raw measures remain readable and do not share an artificial normalized axis.

### Standalone generation prompt
Produce Figure 1 for a full-width ICLR paper as a precise vector scientific chart on white, approximately 7 × 2.25 inches. The three-second claim is “Correctness and correct-code diversity have different leaders” in a small, exploratory one-seed pilot. Use two aligned horizontal dot plots with identical method rows ordered Plain, SSD, SPD-hard, SPECTRUM from top to bottom. Give the right diversity panel 60% of usable plot width and the left correctness panel 40%; reserve a restrained top title and bottom provenance line. In panel “(a) Single-draw correctness”, plot pass@1 (%) ↑ at Plain 36.82, SSD 36.89, SPD-hard 36.87, SPECTRUM 36.65; x-axis 35.5 to 38.0 with clearly printed ticks. In panel “(b) Correct-code diversity”, plot “Expected AST coverage, D4AST ↑” at Plain 3.393, SSD 3.391, SPD-hard 3.409, SPECTRUM 3.422; x-axis 3.350 to 3.460 with sparse, honest ticks. Print each exact value beside its point. These are dots on labeled expanded axes, never truncated bars. Use gray circles for Plain, navy squares for SSD, ochre triangles for SPD-hard, and saturated teal diamonds for SPECTRUM, preserving identity across both panels; make the SPECTRUM row label bold. Use 8-point horizontal labels, 9-point panel titles, 10-point main title, thin light-gray vertical grids, no top/right spines, no shadows or gradients. Required text is “Correctness and correct-code diversity have different leaders”, “SSD has the highest pass@1; SPECTRUM has the highest AST coverage.”, both exact panel headings, both axis labels, all four method names, all eight numeric labels, and “Exploratory pilot · one cycle · seed 42 · 64 MBPP tasks × 64 samples per task”. No per-arm CIs are available: do not draw error bars or replicate points. No statistical tie rule, p-value, or confirmatory noninferiority claim is supplied. Do not connect different methods, draw distributions, equate AST classes with algorithms, add a significance star, or imply multiple seeds. Preserve every measured mean, direction, comparison identity, uncertainty limitation, and provenance disclosure exactly.

### Caption and statistical disclosure
Exploratory pilot after one self-distillation cycle with Qwen2.5-Coder-1.5B-Instruct (64 MBPP tasks, 64 samples per task, seed 42). SSD leads in pass@1, whereas SPECTRUM leads in expected AST coverage among four correct draws. Values are reported final-checkpoint means; no per-arm intervals are supplied. Coverage means can use different eligible-task cohorts. The separately reported paired SPECTRUM−SSD estimates are +0.0312 coverage units (pointwise 95% CI [0.0095, 0.0550]) and −0.244 percentage points in pass@1 ([−0.854, 0.342]); the paired coverage effect need not equal the difference of the displayed per-arm means. The first-fence extraction sensitivity analysis was post hoc, uses local execution, and does not apply multiple-comparison correction. AST coverage is an implementation proxy, not semantic algorithm coverage.

## D. Option 2 — Two-objective scatter with an exact-value ledger

### Design rationale
Emphasize the joint relationship: the accuracy leader and diversity leader are different points. Compress row-by-row comparisons into a ledger. Use no Pareto frontier, which would encourage a stronger optimization claim than the data support.

### Standalone generation prompt
Produce an alternate Figure 1 as a vector ICLR chart on white at 7 × 2.7 inches. The principal claim remains a small exploratory rank reversal between correctness and correct-code AST diversity. Allocate 70% of usable width to one dominant two-objective scatter and 30% to an exact-value table. In the scatter, x is “pass@1 (%) ↑”, range 35.5–38.0, and y is “Expected AST coverage, D4AST ↑”, range 3.35–3.46. Plot exactly four aggregate observations, with no connecting lines: Plain (36.82,3.393), SSD (36.89,3.391), SPD-hard (36.87,3.409), SPECTRUM (36.65,3.422). Place direct method labels with short non-crossing leader lines if needed. Use gray circle, navy square, ochre triangle, and teal diamond respectively; reinforce SPECTRUM with a bold label. The right ledger has columns “Method”, “pass@1 (%)”, “D4AST” and preserves all eight raw values to the supplied precision. Put a small conceptual annotation “Different leaders” between the SSD and SPECTRUM labels without an arrow implying causality. Exact text includes “Pilot: accuracy–diversity ordering”, all method and axis names, the ledger headings, “Different leaders”, and “One cycle · seed 42 · 64 MBPP tasks × 64 samples”. Use horizontal 8-point labels, 10-point title, thin gray gridlines and restrained print-safe colors. Marks are reported method-level means, not per-task measurements. State in the caption that per-arm intervals are missing, correct-code coverage means may use different eligible-task cohorts, and the separately reported paired SPECTRUM−SSD intervals are +0.0312 [0.0095,0.0550] coverage units and −0.244 [−0.854,0.342] percentage points, with pointwise 95% coverage and no multiplicity correction. Do not synthesize uncertainty ellipses, raw scatter clouds, a fitted line, a Pareto frontier, a trajectory, semantic algorithms, or any statistical tie or noninferiority badge. Preserve the exact observed coordinates and all missing-data and cohort disclosures.

### Caption and statistical disclosure
Joint method-level pilot means show that the highest pass@1 and highest fixed-four-correct AST coverage occur in different arms. All measurements, sample scope, cohort caveats, paired intervals, extraction limitations, and interpretation limits are identical to Option 1; points do not represent independent task-level samples and are deliberately unconnected.

## E. Option 3 — Paired-effect forest with raw-value audit

### Design rationale
Emphasize uncertainty on the specific SPECTRUM–SSD comparison while retaining the raw four-arm context. Compress the ranking view. The principal interpretation risk is confusing a paired common cohort with the displayed arm-specific means.

### Standalone generation prompt
Produce an alternate Figure 1 for a full-width ICLR paper at 7 × 2.8 inches on white. Explain the same pilot observation through a dominant paired-effect region occupying 60% of usable area, plus a four-arm raw-value ledger in the remaining 40%. The left region contains two stacked, independently scaled horizontal interval axes, both comparing “SPECTRUM − SSD”. The upper axis is “ΔD4AST (coverage units)”, x from −0.01 to 0.065, with a teal diamond at +0.0312 and a horizontal pointwise 95% CI from 0.0095 to 0.0550. The lower axis is “Δpass@1 (percentage points)”, x from −1.1 to 0.55, with a teal diamond at −0.244 and interval from −0.854 to 0.342. Draw a fine vertical zero line in each facet. Print both central estimates and both interval endpoints numerically; do not share a numeric axis between unlike units. The right table lists Plain 36.82 and 3.393, SSD 36.89 and 3.391, SPD-hard 36.87 and 3.409, and SPECTRUM 36.65 and 3.422 under “pass@1 (%) ↑” and “D4AST ↑”. Use the same gray circle, navy square, ochre triangle, and teal diamond identities in row swatches; no per-arm intervals. Required labels are “Pilot: paired effects and raw means”, “SPECTRUM − SSD”, both delta-axis names, “Raw per-arm means”, all four method names, every supplied value, “Pointwise 95% CIs; one seed”, and “Paired and per-arm coverage cohorts differ”. Use 8-point labels, 10-point title, thin grids and generous whitespace. State 64 MBPP tasks × 64 samples, one cycle, seed 42, Qwen2.5-Coder-1.5B-Instruct in the caption. Treat the exact paired coverage cohort and resampling implementation as missing details; preserve the reported interval meaning rather than naming an unsupported test. Do not subtract rounded arm means to relocate the paired point, impose a common standardized-effect scale, draw per-arm whiskers, add p-values or significance stars, or claim multi-seed confirmation, semantic algorithms, statistical equivalence, or a verified noninferiority margin. Preserve all measurements, cohort distinctions, pointwise uncertainty semantics, and missing information.

### Caption and statistical disclosure
Reported paired effects qualify the same rank-reversal observation. SPECTRUM−SSD is +0.0312 D4AST units (pointwise 95% CI [0.0095,0.0550]) and −0.244 pass@1 percentage points ([−0.854,0.342]); no multiplicity correction is applied. The raw per-arm means provide scale, but their eligible coverage cohorts differ from the paired common cohort. Remaining pilot and extraction limitations are identical to Option 1.

## F. Cross-option evidence-fidelity checklist

- Exactly three distinct reading paths: native metrics, joint relationship, paired uncertainty.
- Every quantitative mark maps to a supplied mean or interval; no pseudo-replicates.
- Diversity is expected AST coverage among four correct draws, not semantic algorithm count.
- The principal panel owns at least 50% of usable area.
- Four-arm means retain precision; paired values retain their separate cohort semantics.
- Correctness is in percent; paired correctness change is in percentage points.
- No per-arm uncertainty, significance, seeds, fitted relationships, or confirmatory result is invented.
- All labels are horizontal and readable at paper width; method identities are redundant with shape.
