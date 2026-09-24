# Nine-page manuscript blueprint

The main text has eight sections and ends on page 9. Statements and references start on page 10; appendices start on page 13. This revision expands the scientific explanation while keeping every experimental value and figure unchanged.

| Section | Question and argumentative purpose | Paragraph sequence | Evidence and visual anchors |
|---|---|---|---|
| 1. Introduction | Why must a self-improving model remain a useful generator for its future self? | Evolving teacher → multiple valid solutions → observed accuracy/breadth separation → prior work and narrower question → fixed-anchor method → supported contributions. | Figure 1; completed five-round MBPP endpoints; iterative-SD citations. |
| 2. What should a self-distillation loop retain? | What information is missing from correctness alone? | Factor correctness and conditional implementation probability → occupancy proposition and concrete example → estimators and task populations → retention profile. | Proposition 1; pass@k, C_k, D_b; Appendix A. |
| 3. Looped Self-Distillation with a fixed reference anchor | What repeats, what changes, and where does supervision enter? | Define generation/learning operators → explain the outer learning loop → identify fixed external reference information and unselected raw outputs. | Equation 3; Figure 2; exact information-flow appendix. |
| 4. SPECTRUM: proximal spectral modulation | How does an internal generation intervention become a native-student effect? | Reference geometry → continuous proximal gain → temporary folding and single-student objective. | Equations 4–8; Proposition 2; Appendix B proofs and Appendix C protocol. |
| 5. Experiments | What is retained, what explains it, and where does it transfer? | Protocol → RQ1 longitudinal/native endpoint → RQ2 matched-correct and sampling budget → RQ3 projection/SSD trade-offs → RQ4 frozen transfer. | Figures 1 and 3; Tables 1–3; all existing completed results. |
| 6. Related work | How does this study differ in loop, feedback, endpoint, and intervention? | Iterative self-training/SD → feedback sources → diversity in recursive learning → spectral control and retained behavior. | Existing 22 cited sources; detailed distinctions below. |
| 7. Limitations | What bounds the result and its interpretation? | Evidence/measurement scope → fixed supervision and unisolated mechanism factors → resource and transfer boundaries. | One backbone/seed; AST proxy; absent directional controls; resource table; APPS trade-off. |
| 8. Conclusion and future work | What principle follows, and which concrete questions remain? | Restate separation and retained 89.9% coverage → connect future experiments to current mechanisms and scope. | Existing MBPP endpoint; matched-correct/native-inference evidence; prospective controls clearly labeled. |

## Expanded method paragraphs

1. **Geometry construction.** Completion-only reference NLL generates nonpadding K/V-output gradients; the loss mask and gradient-position mask are distinguished.
2. **What sensitivity means.** A finite anchor measures squared directional response, without identifying algorithm labels or signed correctness improvements. Re-estimation tracks current parameters under a fixed information source.
3. **Proximal design.** A quadratic objective yields bounded continuous gains. The numerical example maps eigenvalues (1, 1/2, 0) to gains (1, 2/3, 1/2) at tau = 1; it is an algebraic illustration, not an experiment.
4. **Local guarantee.** Invertibility, distance from identity, and perturbation stability hold for the local map; output diversity is measured empirically.
5. **Generator-to-student learning.** Temporary folded weights generate every record. Native weights are restored, and one LoRA optimizes the explicit per-example CE objective over nonpadding causal targets, including prompt targets.
6. **Why the intervention can persist.** K/V changes modify attention computations; only the learned student is carried between rounds. Successive gains are not directly compounded into the base checkpoint. The corpus transmits the intervention into learning.

## Expanded Related Work paragraphs

- **Iterative learning:** STaR, ReST-EM, rationale/context self-distillation, and SCoder establish precedent. Recurrent-depth transformers concern repeated forward computation; this study tracks repeated parameter learning and corpus replacement.
- **Feedback source:** SD-Zero, CRISP, and SSD differ in reward-conditioned revision, instruction-conditioned token KL, and raw-output CE. SPECTRUM uses fixed reference calibration and raw-output CE; absence of rollout filtering is not claimed as a first.
- **Diversity and recursive data:** Sampled demonstrations can bias teacher feedback; UA-RL rewards rare strategies; synthetic-data recursion and accumulation address distributional degradation. Our measured conditional endpoint separates correct-output breadth from success frequency.
- **Spectral control:** Activation editing and reference-gradient subspaces precede this work. SPECTRUM's contribution is the bounded full-rank response within a recalibrated loop, assessed in subsequent native students.

## Change map and evidence lock

- Expanded Sections 4 and 6.
- Replaced the combined Discussion and conclusion with independent Sections 7 and 8.
- Added one learner-objective equation, one algebraic example, and explicit mechanism explanations.
- Added no result, experiment, dataset, model, seed, or figure.
- All future experiments remain prospective. Existing accuracy and transfer costs remain visible.
