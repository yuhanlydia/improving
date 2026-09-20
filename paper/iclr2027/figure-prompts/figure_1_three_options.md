# Figure 1 — Correctness and breadth separate

## A. Evidence inventory / scientific ground truth

**Principal question.** Can correctness improve while the distribution of correct implementations becomes narrower?

**Source-supported answer.** Both measured looped arms increase final pass@1 and decrease correct AST richness; SPECTRUM retains more breadth than Plain.

**Source.** `results/retention_5round_train16_eval16_seed43/report.json`; exact data also appear in `figures/figure_data.json`.

MEASURED: two six-point trajectories, 500 common MBPP tasks, n=16 sampled programs per task, one seed. CONCEPTUAL: a=.4, q uniform on four classes versus concentrated on one class. DERIVED: expected richness among four correct samples = sum_j[1-(1-q_j)^4], giving 2.734375 versus 1. MISSING: per-task program/class histograms, which must never be reconstructed from these aggregate means.

## B. Three candidates

| Option | Evidence organization / topology | Emphasis and main risk |
|---|---|---|
| 1 | Two-objective trajectory with probability inset | It directly reveals the two-objective movement; it compresses the x-as-round reading path. Risk: connecting temporal points must not imply an optimization frontier. |
| 2 | Round-indexed breadth with a correctness strip | The shared round index makes the recursive trajectory explicit; it compresses the direct trade-off view. Risk: keep metric axes separate and prohibit dual y axes. |
| 3 | Endpoint displacement with full trajectory microplot | The endpoint contrast is immediate and the small plot preserves the temporal evidence; it compresses intermediate correctness values, which remain numerically included in its production data. Risk: endpoint displacement alone must not suggest an independently repeated training sample. |

**Recommendation:** Option 1, which is supplied as the completed vector PDF. Every option preserves the same evidence and uses a dominant region of at least half the usable area.

## C. Option 1 — Two-objective trajectory with probability inset

### Design rationale
It directly reveals the two-objective movement; it compresses the x-as-round reading path. Risk: connecting temporal points must not imply an optimization frontier.

### Standalone production prompt

Create Figure 1 for an ICLR research paper at 6.7 × 2.25 inches, full text width, as a precise vector scientific figure. Scientific question: Can correctness improve while the distribution of correct implementations becomes narrower? The three-second takeaway is: Both measured looped arms increase final pass@1 and decrease correct AST richness; SPECTRUM retains more breadth than Plain.

Use 65% of the canvas for a direct two-objective scatter: x is pass@1 in percent and y is Correct AST richness@16. Connect rounds only within each method, label rounds 0 through 5, mark the shared initial point once, and emphasize both round-5 endpoints. Use the remaining 35% for grouped bars of the two illustrative q distributions, with classes A–D on x and conditional probability from zero to one on y. Mark the panel Analytic example, label Broad and Concentrated, and state Both: pass@1 = 40%.

Exact evidence and mathematical inputs to preserve:
Plain rounds 0–5: pass@1 (%) = [37.925, 38.425, 39.15, 39.65, 40.7875, 41.3]; Correct AST richness@16 = [4.016, 3.808, 3.634, 3.372, 3.19, 3.09]. SPECTRUM rounds 0–5: pass@1 (%) = [37.925, 37.8375, 38.3625, 39.05, 39.775, 40.175]; Correct AST richness@16 = [4.016, 3.848, 3.768, 3.662, 3.588, 3.606].

The probability panel is explicitly illustrative, not measured. Both distributions have a=0.4; their entire pass@k curves agree for every k, while their conditional distributions differ. Bars start at zero. Plot no uncertainty ellipses in the trajectory, no fabricated empirical class counts, and no unobserved histories. Round curves use the same 500 tasks, but they are one evolving run, not independent seeds.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Correct AST richness@16”, “pass@1 (%)”, “Plain”, “SPECTRUM”, “Initial”, “Analytic example”, “Broad”, “Concentrated”, “Correct implementation class”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Correctness does not determine correct-implementation breadth. (a) Over five rounds, Plain and SPECTRUM move toward higher pass@1 but lower correct AST richness@16 than the initial model; SPECTRUM retains more breadth. Points are task means over the same 500 MBPP tasks, with 16 samples per task and one training seed. Labels denote rounds, and connecting segments only indicate temporal order. Point estimates are shown here; task-bootstrap intervals are reported in Figure 4 and the tables. (b) An analytic example, not an empirical histogram: both distributions have correctness probability a=0.4, but conditional implementation probabilities q=(1/4,1/4,1/4,1/4) and q=(1,0,0,0), respectively. Their expected richness among four correct samples is 2.734375 and 1.

## D. Option 2 — Round-indexed breadth with a correctness strip

### Design rationale
The shared round index makes the recursive trajectory explicit; it compresses the direct trade-off view. Risk: keep metric axes separate and prohibit dual y axes.

### Standalone production prompt

Create Figure 1 for an ICLR research paper at 6.7 × 2.25 inches, full text width, as a precise vector scientific figure. Scientific question: Can correctness improve while the distribution of correct implementations becomes narrower? The three-second takeaway is: Both measured looped arms increase final pass@1 and decrease correct AST richness; SPECTRUM retains more breadth than Plain.

Use a dominant top-left panel occupying 55% of usable area: x is learning round 0–5, y is Correct AST richness@16. Below it put a short aligned pass@1-percent strip with the same rounds and method identities, occupying 20%. Allocate the remaining 25% to a compact two-row probability mosaic of q=(.25,.25,.25,.25) versus q=(1,0,0,0); each row must sum to one, with equal-width outlined class cells and no fake empirical image. Print the same-a statement and the two analytic richness values.

Exact evidence and mathematical inputs to preserve:
Plain rounds 0–5: pass@1 (%) = [37.925, 38.425, 39.15, 39.65, 40.7875, 41.3]; Correct AST richness@16 = [4.016, 3.808, 3.634, 3.372, 3.19, 3.09]. SPECTRUM rounds 0–5: pass@1 (%) = [37.925, 37.8375, 38.3625, 39.05, 39.775, 40.175]; Correct AST richness@16 = [4.016, 3.848, 3.768, 3.662, 3.588, 3.606].

The probability panel is explicitly illustrative, not measured. Both distributions have a=0.4; their entire pass@k curves agree for every k, while their conditional distributions differ. Bars start at zero. Plot no uncertainty ellipses in the trajectory, no fabricated empirical class counts, and no unobserved histories. Round curves use the same 500 tasks, but they are one evolving run, not independent seeds.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Correct AST richness@16”, “pass@1 (%)”, “Plain”, “SPECTRUM”, “Initial”, “Analytic example”, “Broad”, “Concentrated”, “Correct implementation class”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Correctness does not determine correct-implementation breadth. (a) Over five rounds, Plain and SPECTRUM move toward higher pass@1 but lower correct AST richness@16 than the initial model; SPECTRUM retains more breadth. Points are task means over the same 500 MBPP tasks, with 16 samples per task and one training seed. Labels denote rounds, and connecting segments only indicate temporal order. Point estimates are shown here; task-bootstrap intervals are reported in Figure 4 and the tables. (b) An analytic example, not an empirical histogram: both distributions have correctness probability a=0.4, but conditional implementation probabilities q=(1/4,1/4,1/4,1/4) and q=(1,0,0,0), respectively. Their expected richness among four correct samples is 2.734375 and 1.

## E. Option 3 — Endpoint displacement with full trajectory microplot

### Design rationale
The endpoint contrast is immediate and the small plot preserves the temporal evidence; it compresses intermediate correctness values, which remain numerically included in its production data. Risk: endpoint displacement alone must not suggest an independently repeated training sample.

### Standalone production prompt

Create Figure 1 for an ICLR research paper at 6.7 × 2.25 inches, full text width, as a precise vector scientific figure. Scientific question: Can correctness improve while the distribution of correct implementations becomes narrower? The three-second takeaway is: Both measured looped arms increase final pass@1 and decrease correct AST richness; SPECTRUM retains more breadth than Plain.

Use 60% for a paired initial-to-round-5 displacement view: two horizontal native-unit axes in aligned rows, pass@1 (%) and Correct AST richness@16, with Initial, Plain round5 and SPECTRUM round5 dots and numerical values. Inside this dominant block, a small round0–5 richness line plot retains all intermediate measurements. Use the remaining 40% for the analytic four-class conditional probability example, showing q exactly and expected richness values. Do not turn the endpoint result into a retention-identity or survival diagram.

Exact evidence and mathematical inputs to preserve:
Plain rounds 0–5: pass@1 (%) = [37.925, 38.425, 39.15, 39.65, 40.7875, 41.3]; Correct AST richness@16 = [4.016, 3.808, 3.634, 3.372, 3.19, 3.09]. SPECTRUM rounds 0–5: pass@1 (%) = [37.925, 37.8375, 38.3625, 39.05, 39.775, 40.175]; Correct AST richness@16 = [4.016, 3.848, 3.768, 3.662, 3.588, 3.606].

The probability panel is explicitly illustrative, not measured. Both distributions have a=0.4; their entire pass@k curves agree for every k, while their conditional distributions differ. Bars start at zero. Plot no uncertainty ellipses in the trajectory, no fabricated empirical class counts, and no unobserved histories. Round curves use the same 500 tasks, but they are one evolving run, not independent seeds.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Correct AST richness@16”, “pass@1 (%)”, “Plain”, “SPECTRUM”, “Initial”, “Analytic example”, “Broad”, “Concentrated”, “Correct implementation class”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Correctness does not determine correct-implementation breadth. (a) Over five rounds, Plain and SPECTRUM move toward higher pass@1 but lower correct AST richness@16 than the initial model; SPECTRUM retains more breadth. Points are task means over the same 500 MBPP tasks, with 16 samples per task and one training seed. Labels denote rounds, and connecting segments only indicate temporal order. Point estimates are shown here; task-bootstrap intervals are reported in Figure 4 and the tables. (b) An analytic example, not an empirical histogram: both distributions have correctness probability a=0.4, but conditional implementation probabilities q=(1/4,1/4,1/4,1/4) and q=(1,0,0,0), respectively. Their expected richness among four correct samples is 2.734375 and 1.

## F. Cross-option fidelity checklist

- Exactly three distinct evidence organizations or topologies, with the same source-supported content.
- One dominant region occupies at least half the usable area.
- Every numerical mark comes from the printed ledger or a labeled analytic example.
- Reported uncertainty is task uncertainty, not training-seed uncertainty.
- Measured aggregates are never reconstructed as fabricated empirical histograms.
- No projection comparator appears before the ablation experiment.
- Correct AST richness counts normalized syntax classes, not proven semantic strategies.
- Native student evaluation, raw-data learning and temporary generation modulation remain distinct.
