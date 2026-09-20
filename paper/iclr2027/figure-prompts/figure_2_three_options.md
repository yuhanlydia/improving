# Figure 2 — General loop and concrete spectral modulation

## A. Evidence inventory / scientific ground truth

**Principal question.** Where does SPECTRUM change the data-generating loop, and what persists in the final student?

**Source-supported answer.** Every round re-estimates a temporary generation operator; raw synthetic data train one student whose native inference retains the learned result.

**Source.** `src/ and the committed retention experiment configuration; exact operator and learning schedule are specified in main.tex.`; exact data also appear in `figures/figure_data.json`.

CONFIRMED: recurrent student state, recalibration from each student, raw generation, one-LoRA update, temporary K/V modulation, restoration before SFT, native student evaluation, masked reference loss geometry. ILLUSTRATIVE: module boxes and one schematic scalar gain curve; they are not empirical activation heatmaps. TO CONFIRM: none needed for this completed diagram. Numerical strength choices belong to experiment tables, not this conceptual figure.

## B. Three candidates

| Option | Evidence organization / topology | Emphasis and main risk |
|---|---|---|
| 1 | Generic loop above a mechanism expansion | This is the implemented recommendation. It separates the reusable framework from the particular operator while preserving one loop. Risk: tiny text in the mechanism expansion. |
| 2 | Dual-lane generation and learning lifecycle | The restored learner and temporary generator cannot be confused. It compresses the algebra into an inset. Risk: the two lanes must not appear as two independently trained teachers. |
| 3 | Student-state hub with operator construction arc | The repeatedly updated student is the visual center. It compresses strict left-to-right sequence but highlights state. Risk: avoid a circular arrow that returns synthetic records directly to the geometry without the student update. |

**Recommendation:** Option 1, which is supplied as the completed vector PDF. Every option preserves the same evidence and uses a dominant region of at least half the usable area.

## C. Option 1 — Generic loop above a mechanism expansion

### Design rationale
This is the implemented recommendation. It separates the reusable framework from the particular operator while preserving one loop. Risk: tiny text in the mechanism expansion.

### Standalone production prompt

Create Figure 2 for an ICLR research paper at 6.7 × 2.6 inches, full text width, as a precise vector scientific figure. Scientific question: Where does SPECTRUM change the data-generating loop, and what persists in the final student? The three-second takeaway is: Every round re-estimates a temporary generation operator; raw synthetic data train one student whose native inference retains the learned result.

Use 55% of the canvas for a top recurrent backbone: Student theta_t → Generation operator A_t → Generate D_t → Learn from D_t / one LoRA → Next student theta_(t+1). Return one arrow from the next student to generation-operator recalibration. Print restore theta_t before SFT at the learner, 16 raw samples / prompt at D_t, and branch from theta_(t+1) with a dashed arrow to Native inference. Below, expand only the SPECTRUM operator with Reference loss → Loss-sensitive geometry → Proximal spectral modulation and a small analytic positive-gain plot. Use dotted or thin connector semantics for the expansion, not an additional learning path.

Exact evidence and mathematical inputs to preserve:
The general Looped Self-Distillation state is student theta_t. Recalibrate a generation operator A_t=A(theta_t); use the operator only to generate D_t on the fixed training prompts; restore the original student weights theta_t; fit one LoRA to D_t; merge to obtain theta_(t+1); the next round recalibrates A from that updated student. The completed experiment uses 16 raw generated records per training prompt; all raw records, including incorrect or duplicated records, are available to SFT rather than correctness filtering. Final evaluation uses the student's native inference without the generation operator. SPECTRUM instantiates A using masked reference-completion loss gradients g=grad_h ell_ref at selected K/V activations, the uncentered second moment C=mean(gg^T), normalized geometry Cbar=C/lambda_max(C), and T=[I+tau(I-Cbar)]^(-1). Its scalar gain is g_tau(mu)=1/[1+tau(1-mu)] for normalized eigenvalue mu in [0,1]. Fold T into K/V weights for generation, and restore before student learning. The representation geometry is recomputed every round. Reference supervision and generated training records are distinct roles.

Use solid arrows for the executed generation and learning path, a single return arrow for round recalibration, and a dashed outlet for native inference. There is no verifier-filtered training funnel, no strategy-specific adapter pool, no weight-SVD step, and no inference-time activation hook. Reference gradients are collected for operator construction, separately from student SFT. An analytic gain sketch may show its bounded positive shape, but must not be presented as a measured eigenspectrum or an experimentally selected tau.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Looped Self-Distillation”, “Student”, “Generation operator”, “Generate”, “Learn from D_t”, “one LoRA”, “Next student”, “Native inference”, “SPECTRUM instantiation”, “Reference loss”, “Loss-sensitive geometry”, “Proximal spectral modulation”, “restore theta_t before SFT”, “16 raw samples / prompt”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Looped Self-Distillation and its SPECTRUM instantiation. Each round constructs a generation operator from the current student, generates a synthetic corpus, and trains one student before repeating. In SPECTRUM, a reference-completion loss defines K/V gradient second moments. The normalized geometry yields a closed-form proximal modulation with positive gains in [1/(1+tau),1]. It is folded into the K/V weights during generation, then removed before student training. The completed loop uses 16 raw generated records per training prompt and one LoRA. The next student is evaluated under native inference. The small gain curve is an analytic illustration, not a measured spectrum or an experimental strength selection.

## D. Option 2 — Dual-lane generation and learning lifecycle

### Design rationale
The restored learner and temporary generator cannot be confused. It compresses the algebra into an inset. Risk: the two lanes must not appear as two independently trained teachers.

### Standalone production prompt

Create Figure 2 for an ICLR research paper at 6.7 × 2.6 inches, full text width, as a precise vector scientific figure. Scientific question: Where does SPECTRUM change the data-generating loop, and what persists in the final student? The three-second takeaway is: Every round re-estimates a temporary generation operator; raw synthetic data train one student whose native inference retains the learned result.

Use a dominant 65% central diagram with two aligned lanes. The upper Generation lane starts at theta_t, recalibrates A_t, and generates raw D_t. The lower Student learning lane starts from restored theta_t, receives D_t vertically, performs the one-LoRA update, and ends at theta_(t+1). A return loop takes theta_(t+1) to recalibration. Add a native-inference outlet to the new student. Use the remaining 35% for a right mechanism inset containing masked reference loss gradient, Cbar and the exact proximal inverse equation plus a positive-gain sketch.

Exact evidence and mathematical inputs to preserve:
The general Looped Self-Distillation state is student theta_t. Recalibrate a generation operator A_t=A(theta_t); use the operator only to generate D_t on the fixed training prompts; restore the original student weights theta_t; fit one LoRA to D_t; merge to obtain theta_(t+1); the next round recalibrates A from that updated student. The completed experiment uses 16 raw generated records per training prompt; all raw records, including incorrect or duplicated records, are available to SFT rather than correctness filtering. Final evaluation uses the student's native inference without the generation operator. SPECTRUM instantiates A using masked reference-completion loss gradients g=grad_h ell_ref at selected K/V activations, the uncentered second moment C=mean(gg^T), normalized geometry Cbar=C/lambda_max(C), and T=[I+tau(I-Cbar)]^(-1). Its scalar gain is g_tau(mu)=1/[1+tau(1-mu)] for normalized eigenvalue mu in [0,1]. Fold T into K/V weights for generation, and restore before student learning. The representation geometry is recomputed every round. Reference supervision and generated training records are distinct roles.

Use solid arrows for the executed generation and learning path, a single return arrow for round recalibration, and a dashed outlet for native inference. There is no verifier-filtered training funnel, no strategy-specific adapter pool, no weight-SVD step, and no inference-time activation hook. Reference gradients are collected for operator construction, separately from student SFT. An analytic gain sketch may show its bounded positive shape, but must not be presented as a measured eigenspectrum or an experimentally selected tau.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Looped Self-Distillation”, “Student”, “Generation operator”, “Generate”, “Learn from D_t”, “one LoRA”, “Next student”, “Native inference”, “SPECTRUM instantiation”, “Reference loss”, “Loss-sensitive geometry”, “Proximal spectral modulation”, “restore theta_t before SFT”, “16 raw samples / prompt”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Looped Self-Distillation and its SPECTRUM instantiation. Each round constructs a generation operator from the current student, generates a synthetic corpus, and trains one student before repeating. In SPECTRUM, a reference-completion loss defines K/V gradient second moments. The normalized geometry yields a closed-form proximal modulation with positive gains in [1/(1+tau),1]. It is folded into the K/V weights during generation, then removed before student training. The completed loop uses 16 raw generated records per training prompt and one LoRA. The next student is evaluated under native inference. The small gain curve is an analytic illustration, not a measured spectrum or an experimental strength selection.

## E. Option 3 — Student-state hub with operator construction arc

### Design rationale
The repeatedly updated student is the visual center. It compresses strict left-to-right sequence but highlights state. Risk: avoid a circular arrow that returns synthetic records directly to the geometry without the student update.

### Standalone production prompt

Create Figure 2 for an ICLR research paper at 6.7 × 2.6 inches, full text width, as a precise vector scientific figure. Scientific question: Where does SPECTRUM change the data-generating loop, and what persists in the final student? The three-second takeaway is: Every round re-estimates a temporary generation operator; raw synthetic data train one student whose native inference retains the learned result.

Place student state theta_t at the left of a dominant 60% closed loop. Above the loop, create the temporary generation operator A_t; at the right generate raw D_t; below the loop learn one LoRA starting from restored theta_t; close the loop at the next student theta_(t+1). Put a separate final native-inference outlet outside the loop. Use 40% of the rightmost area as a vertical mathematical expansion of A_t: g, then normalized uncentered second moment, then T and its positive bounded gain. Avoid separate adapter pools or task-specific subspaces.

Exact evidence and mathematical inputs to preserve:
The general Looped Self-Distillation state is student theta_t. Recalibrate a generation operator A_t=A(theta_t); use the operator only to generate D_t on the fixed training prompts; restore the original student weights theta_t; fit one LoRA to D_t; merge to obtain theta_(t+1); the next round recalibrates A from that updated student. The completed experiment uses 16 raw generated records per training prompt; all raw records, including incorrect or duplicated records, are available to SFT rather than correctness filtering. Final evaluation uses the student's native inference without the generation operator. SPECTRUM instantiates A using masked reference-completion loss gradients g=grad_h ell_ref at selected K/V activations, the uncentered second moment C=mean(gg^T), normalized geometry Cbar=C/lambda_max(C), and T=[I+tau(I-Cbar)]^(-1). Its scalar gain is g_tau(mu)=1/[1+tau(1-mu)] for normalized eigenvalue mu in [0,1]. Fold T into K/V weights for generation, and restore before student learning. The representation geometry is recomputed every round. Reference supervision and generated training records are distinct roles.

Use solid arrows for the executed generation and learning path, a single return arrow for round recalibration, and a dashed outlet for native inference. There is no verifier-filtered training funnel, no strategy-specific adapter pool, no weight-SVD step, and no inference-time activation hook. Reference gradients are collected for operator construction, separately from student SFT. An analytic gain sketch may show its bounded positive shape, but must not be presented as a measured eigenspectrum or an experimentally selected tau.

Use white background, flat vector marks, no shadows, 7–8 pt horizontal text at a 6.7-inch paper width. SPECTRUM is teal #147C80 with circle markers; Plain is restrained rust #A35E3C with square markers; Initial model is gray #687382 with diamonds and dashed lines where appropriate. Use light horizontal grid lines, no top/right spines, explicit axis units and readable ticks. Color must be reinforced by shapes and direct labels. Do not introduce SPD, a hard-projection comparator, UA-RL measurements, additional datasets, new runs, significance stars, smoothed curves, fitted laws, or invented values.

Exact text required: “Looped Self-Distillation”, “Student”, “Generation operator”, “Generate”, “Learn from D_t”, “one LoRA”, “Next student”, “Native inference”, “SPECTRUM instantiation”, “Reference loss”, “Loss-sensitive geometry”, “Proximal spectral modulation”, “restore theta_t before SFT”, “16 raw samples / prompt”.

Final fidelity requirement: preserve every measured value, comparison, metric direction, conditional cohort, uncertainty definition, conceptual-versus-measured distinction, and confirmed state-update dependency exactly; leave unavailable information unplotted.

### Caption and statistical disclosure

Looped Self-Distillation and its SPECTRUM instantiation. Each round constructs a generation operator from the current student, generates a synthetic corpus, and trains one student before repeating. In SPECTRUM, a reference-completion loss defines K/V gradient second moments. The normalized geometry yields a closed-form proximal modulation with positive gains in [1/(1+tau),1]. It is folded into the K/V weights during generation, then removed before student training. The completed loop uses 16 raw generated records per training prompt and one LoRA. The next student is evaluated under native inference. The small gain curve is an analytic illustration, not a measured spectrum or an experimental strength selection.

## F. Cross-option fidelity checklist

- Exactly three distinct evidence organizations or topologies, with the same source-supported content.
- One dominant region occupies at least half the usable area.
- Every numerical mark comes from the printed ledger or a labeled analytic example.
- Reported uncertainty is task uncertainty, not training-seed uncertainty.
- Measured aggregates are never reconstructed as fabricated empirical histograms.
- No projection comparator appears before the ablation experiment.
- Correct AST richness counts normalized syntax classes, not proven semantic strategies.
- Native student evaluation, raw-data learning and temporary generation modulation remain distinct.
