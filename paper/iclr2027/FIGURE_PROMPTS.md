# SPECTRUM — Complete English figure production prompts

Four figures, each with three independent options. Every copyable prompt is below 5,000 characters. Quantitative figures use plotting code; no data image generation or prompt assembly is needed. Native LaTeX tables are in main.tex.

# Figure 1 — Can increasing correctness conceal contraction within correct outputs?

## A. Evidence Inventory

**Question:** Can increasing correctness conceal contraction within correct outputs?

**Supported answer:** In the saved five-round MBPP run, Plain and SPECTRUM increase pass@1 while losing AST richness; SPECTRUM loses less.

**Fact lock:** {"plain":{"pass1_percent":[37.925,38.425,39.15,39.65,40.7875,41.3],"C16":[4.016,3.808,3.634,3.372,3.19,3.09],"Simpson":[0.84297,0.802178,0.781279,0.738599,0.707753,0.691991],"paired_D4_change":[-0.138258,-0.220248,-0.376093,-0.500308,-0.574162],"paired_D4_ci95":[[-0.207978,-0.068049],[-0.293476,-0.14518],[-0.452677,-0.298745],[-0.573634,-0.429593],[-0.653711,-0.498749]],"paired_D4_n":[245,246,240,244,241]},"spectral_soft":{"pass1_percent":[37.925,37.8375,38.3625,39.05,39.775,40.175],"C16":[4.016,3.848,3.768,3.662,3.588,3.606],"Simpson":[0.84297,0.822225,0.809408,0.773249,0.75196,0.765747],"paired_D4_change":[-0.099678,-0.139992,-0.221023,-0.3163,-0.315297],"paired_D4_ci95":[[-0.166006,-0.035438],[-0.211323,-0.069725],[-0.304755,-0.145722],[-0.391983,-0.243946],[-0.394451,-0.239572]],"paired_D4_n":[242,236,244,242,245]}}

**Missing/boundary:** Independent training seeds and intermediate 64-sample pools; no global semantic diversity measurement.

**Design skill:** `designing-experiment-figures`. **Production:** `programmatic-figure-spec`.

## B. Three candidate designs

| Option | Reading path | Main risk |
|---|---|---|
| 1 | Phase trajectory with conditional checks | Misreading local/conditional evidence as a global guarantee. |
| 2 | Longitudinal retention with aligned diagnostics | Misreading local/conditional evidence as a global guarantee. |
| 3 | Conditional retention as the focal evidence | Misreading local/conditional evidence as a global guarantee. |

**Recommendation:** Option 1, used in the supplied manuscript, gives the principal relationship the largest area and matches the available evidence.

## C. Option 1 — Phase trajectory with conditional checks

**Rationale:** Place pass@1 (%) on x and C16 on y in the left 58% panel. Connect rounds 0 through 5 in order and label their numbers. Put paired D4 change from initialization versus rounds 1--5, including CI bars, in the middle 21%; place Simpson diversity versus rounds 0--5 in the right 21%. A shared legend maps plain to Plain and spectral_soft to SPECTRUM. Label panels (a) Accuracy and breadth, (b) Equal correct draws, (c) Concentration. This prioritizes the accuracy/breadth separation.

### Standalone English production prompt (3094 characters)

```text
Create Figure 1 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: In the saved five-round MBPP run, Plain and SPECTRUM increase pass@1 while losing AST richness; SPECTRUM loses less. Place pass@1 (%) on x and C16 on y in the left 58% panel. Connect rounds 0 through 5 in order and label their numbers. Put paired D4 change from initialization versus rounds 1--5, including CI bars, in the middle 21%; place Simpson diversity versus rounds 0--5 in the right 21%. A shared legend maps plain to Plain and spectral_soft to SPECTRUM. Label panels (a) Accuracy and breadth, (b) Equal correct draws, (c) Concentration. This prioritizes the accuracy/breadth separation. Locked facts: All arrays below are saved measurements (six round-0--5 entries, or five round-1--5 paired changes). {"plain":{"pass1_percent":[37.925,38.425,39.15,39.65,40.7875,41.3],"C16":[4.016,3.808,3.634,3.372,3.19,3.09],"Simpson":[0.84297,0.802178,0.781279,0.738599,0.707753,0.691991],"paired_D4_change":[-0.138258,-0.220248,-0.376093,-0.500308,-0.574162],"paired_D4_ci95":[[-0.207978,-0.068049],[-0.293476,-0.14518],[-0.452677,-0.298745],[-0.573634,-0.429593],[-0.653711,-0.498749]],"paired_D4_n":[245,246,240,244,241]},"spectral_soft":{"pass1_percent":[37.925,37.8375,38.3625,39.05,39.775,40.175],"C16":[4.016,3.848,3.768,3.662,3.588,3.606],"Simpson":[0.84297,0.822225,0.809408,0.773249,0.75196,0.765747],"paired_D4_change":[-0.099678,-0.139992,-0.221023,-0.3163,-0.315297],"paired_D4_ci95":[[-0.166006,-0.035438],[-0.211323,-0.069725],[-0.304755,-0.145722],[-0.391983,-0.243946],[-0.394451,-0.239572]],"paired_D4_n":[242,236,244,242,245]}} Paired D4 intervals resample evaluation tasks 2,000 times; eligibility varies by contrast. Simpson uses tasks with at least two correct outputs. No uncertainty is plotted for phase or Simpson points. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies. Alt text: Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain. Boundary: Independent training seeds and intermediate 64-sample pools; no global semantic diversity measurement. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies.

**Alt text:** Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain.

## D. Option 2 — Longitudinal retention with aligned diagnostics

**Rationale:** Use the left 55% for C16 against rounds 0--5. In the right 45%, stack three aligned strips for pass@1 (%), paired D4 changes with CI bars, and Simpson diversity. Each strip has its own labeled y-axis and shares round order. Show all initial and final values beside their respective points. This emphasizes accumulation across rounds; do not add a fitted decay rate.

### Standalone English production prompt (2981 characters)

```text
Create Figure 1 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: In the saved five-round MBPP run, Plain and SPECTRUM increase pass@1 while losing AST richness; SPECTRUM loses less. Use the left 55% for C16 against rounds 0--5. In the right 45%, stack three aligned strips for pass@1 (%), paired D4 changes with CI bars, and Simpson diversity. Each strip has its own labeled y-axis and shares round order. Show all initial and final values beside their respective points. This emphasizes accumulation across rounds; do not add a fitted decay rate. Locked facts: All arrays below are saved measurements (six round-0--5 entries, or five round-1--5 paired changes). {"plain":{"pass1_percent":[37.925,38.425,39.15,39.65,40.7875,41.3],"C16":[4.016,3.808,3.634,3.372,3.19,3.09],"Simpson":[0.84297,0.802178,0.781279,0.738599,0.707753,0.691991],"paired_D4_change":[-0.138258,-0.220248,-0.376093,-0.500308,-0.574162],"paired_D4_ci95":[[-0.207978,-0.068049],[-0.293476,-0.14518],[-0.452677,-0.298745],[-0.573634,-0.429593],[-0.653711,-0.498749]],"paired_D4_n":[245,246,240,244,241]},"spectral_soft":{"pass1_percent":[37.925,37.8375,38.3625,39.05,39.775,40.175],"C16":[4.016,3.848,3.768,3.662,3.588,3.606],"Simpson":[0.84297,0.822225,0.809408,0.773249,0.75196,0.765747],"paired_D4_change":[-0.099678,-0.139992,-0.221023,-0.3163,-0.315297],"paired_D4_ci95":[[-0.166006,-0.035438],[-0.211323,-0.069725],[-0.304755,-0.145722],[-0.391983,-0.243946],[-0.394451,-0.239572]],"paired_D4_n":[242,236,244,242,245]}} Paired D4 intervals resample evaluation tasks 2,000 times; eligibility varies by contrast. Simpson uses tasks with at least two correct outputs. No uncertainty is plotted for phase or Simpson points. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies. Alt text: Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain. Boundary: Independent training seeds and intermediate 64-sample pools; no global semantic diversity measurement. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies.

**Alt text:** Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain.

## E. Option 3 — Conditional retention as the focal evidence

**Rationale:** Use the upper 55% for paired D4 change from initialization against rounds 1--5 with exact CI bars and zero reference. Below it, use 30% for the measured pass@1-versus-C16 trajectories and 15% for Simpson-versus-round. Keep each plot independent; no linking axes with arrows implying causality. This emphasizes the within-correct result while retaining every source series.

### Standalone English production prompt (2988 characters)

```text
Create Figure 1 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: In the saved five-round MBPP run, Plain and SPECTRUM increase pass@1 while losing AST richness; SPECTRUM loses less. Use the upper 55% for paired D4 change from initialization against rounds 1--5 with exact CI bars and zero reference. Below it, use 30% for the measured pass@1-versus-C16 trajectories and 15% for Simpson-versus-round. Keep each plot independent; no linking axes with arrows implying causality. This emphasizes the within-correct result while retaining every source series. Locked facts: All arrays below are saved measurements (six round-0--5 entries, or five round-1--5 paired changes). {"plain":{"pass1_percent":[37.925,38.425,39.15,39.65,40.7875,41.3],"C16":[4.016,3.808,3.634,3.372,3.19,3.09],"Simpson":[0.84297,0.802178,0.781279,0.738599,0.707753,0.691991],"paired_D4_change":[-0.138258,-0.220248,-0.376093,-0.500308,-0.574162],"paired_D4_ci95":[[-0.207978,-0.068049],[-0.293476,-0.14518],[-0.452677,-0.298745],[-0.573634,-0.429593],[-0.653711,-0.498749]],"paired_D4_n":[245,246,240,244,241]},"spectral_soft":{"pass1_percent":[37.925,37.8375,38.3625,39.05,39.775,40.175],"C16":[4.016,3.848,3.768,3.662,3.588,3.606],"Simpson":[0.84297,0.822225,0.809408,0.773249,0.75196,0.765747],"paired_D4_change":[-0.099678,-0.139992,-0.221023,-0.3163,-0.315297],"paired_D4_ci95":[[-0.166006,-0.035438],[-0.211323,-0.069725],[-0.304755,-0.145722],[-0.391983,-0.243946],[-0.394451,-0.239572]],"paired_D4_n":[242,236,244,242,245]}} Paired D4 intervals resample evaluation tasks 2,000 times; eligibility varies by contrast. Simpson uses tasks with at least two correct outputs. No uncertainty is plotted for phase or Simpson points. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies. Alt text: Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain. Boundary: Independent training seeds and intermediate 64-sample pools; no global semantic diversity measurement. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies.

**Alt text:** Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain.

## F. Fidelity and QA

- Exactly three designs encode the same facts; layout changes do not change evidence.
- Quantitative marks come from saved measurements or explicitly defined calculations.
- One dominant scientific panel owns at least half the usable canvas.
- Preserve single-seed scope, pairing, eligibility, and missing information.
- Check legibility, clipping, arrow/text collisions, units, and grayscale reproduction at final paper width.


---

# Figure 2 — How does fixed calibration information change each round without selecting generated samples?

## A. Scientific Ground Truth

**Question:** How does fixed calibration information change each round without selecting generated samples?

**Supported answer:** The anchor is fixed; K/V geometry is re-estimated on the evolving model, then temporarily folded for generation and removed before single-LoRA SFT.

**Fact lock:** CONFIRMED: native student theta_t; fixed reference anchor A={(x_i,y_i*)}; reference-completion mean NLL with prompt targets masked; all nonpadding K/V-output gradients; normalized second moment Cbar_t=C_t/lambda_max(C_t); T_t=[I+tau(I-Cbar_t)]^{-1}; temporary pre-RoPE K/V weight folding; all raw synthetic records D_t; restore native theta_t; one LoRA SFT on all nonpadding causal targets; merge theta_(t+1); recompute geometry next round; native final inference. Reference data are reused external supervision. No newly labeled anchor data, rollout grading, strategy assignment, sample rejection, adapter pool, or reward update.

**Missing/boundary:** No unresolved pipeline component is drawn. No semantic-diversity guarantee follows from local full rank.

**Design skill:** `designing-pipeline-figures`. **Production:** `vector-diagram-spec`.

## B. Three candidate designs

| Option | Reading path | Main risk |
|---|---|---|
| 1 | Two-lane learning loop | Misreading local/conditional evidence as a global guarantee. |
| 2 | Circular recurrence around the fixed anchor | Misreading local/conditional evidence as a global guarantee. |
| 3 | One transition expanded between successive students | Misreading local/conditional evidence as a global guarantee. |

**Recommendation:** Option 1, used in the supplied manuscript, gives the principal relationship the largest area and matches the available evidence.

## C. Option 1 — Two-lane learning loop

**Rationale:** Canvas 6.65 by 2.9 inches. Top lane: Fixed reference anchor -> Re-estimate K/V geometry -> Proximal spectral gain. Bottom lane: Current student theta_t -> Temporary K/V folding / Generate all raw samples -> Restore native weights / Single-LoRA SFT -> theta_(t+1). Draw a dashed current-student input to geometry, a solid gain input to temporary generation, and one bottom return arrow from theta_(t+1) to current student. The loop occupies 75% of usable area. Label the reference edge Reused each round and the data edge D_t. Do not let an arrow cross text.

### Standalone English production prompt (2683 characters)

```text
Create Figure 2 for an anonymous ICLR paper using vector-diagram-spec. The immediate takeaway is: The anchor is fixed; K/V geometry is re-estimated on the evolving model, then temporarily folded for generation and removed before single-LoRA SFT. Canvas 6.65 by 2.9 inches. Top lane: Fixed reference anchor -> Re-estimate K/V geometry -> Proximal spectral gain. Bottom lane: Current student theta_t -> Temporary K/V folding / Generate all raw samples -> Restore native weights / Single-LoRA SFT -> theta_(t+1). Draw a dashed current-student input to geometry, a solid gain input to temporary generation, and one bottom return arrow from theta_(t+1) to current student. The loop occupies 75% of usable area. Label the reference edge Reused each round and the data edge D_t. Do not let an arrow cross text. Locked facts: CONFIRMED: native student theta_t; fixed reference anchor A={(x_i,y_i*)}; reference-completion mean NLL with prompt targets masked; all nonpadding K/V-output gradients; normalized second moment Cbar_t=C_t/lambda_max(C_t); T_t=[I+tau(I-Cbar_t)]^{-1}; temporary pre-RoPE K/V weight folding; all raw synthetic records D_t; restore native theta_t; one LoRA SFT on all nonpadding causal targets; merge theta_(t+1); recompute geometry next round; native final inference. Reference data are reused external supervision. No newly labeled anchor data, rollout grading, strategy assignment, sample rejection, adapter pool, or reward update. Use an editable vector diagram, white background, black text, thin gray borders, and light-gray fills only for persistent information and the temporary generation module. Minimum label size 8 pt at paper width. Keep all text horizontal and connectors clear. Export PDF and PNG. Prohibit reward models, verification gates, strategy labels, model ensembles, adapter pools, extra losses, numerical result claims, or semantic guarantees not specified here.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform. Alt text: A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student. Boundary: No unresolved pipeline component is drawn. No semantic-diversity guarantee follows from local full rank. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform.

**Alt text:** A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student.

## D. Option 2 — Circular recurrence around the fixed anchor

**Rationale:** Canvas 6.65 by 3.3 inches. Put the persistent anchor in a small central outlined box (20% of area), and a clockwise ring occupying 80%: Current student -> Geometry -> Gain -> Raw generation -> Restore + single-LoRA SFT -> Next student. A radial dashed line from anchor ends at geometry only. Mark the return state theta_(t+1) to theta_t for the next round. Put the gain equation beside the gain node, not across connectors. No arrows from evaluation to the learning loop.

### Standalone English production prompt (2597 characters)

```text
Create Figure 2 for an anonymous ICLR paper using vector-diagram-spec. The immediate takeaway is: The anchor is fixed; K/V geometry is re-estimated on the evolving model, then temporarily folded for generation and removed before single-LoRA SFT. Canvas 6.65 by 3.3 inches. Put the persistent anchor in a small central outlined box (20% of area), and a clockwise ring occupying 80%: Current student -> Geometry -> Gain -> Raw generation -> Restore + single-LoRA SFT -> Next student. A radial dashed line from anchor ends at geometry only. Mark the return state theta_(t+1) to theta_t for the next round. Put the gain equation beside the gain node, not across connectors. No arrows from evaluation to the learning loop. Locked facts: CONFIRMED: native student theta_t; fixed reference anchor A={(x_i,y_i*)}; reference-completion mean NLL with prompt targets masked; all nonpadding K/V-output gradients; normalized second moment Cbar_t=C_t/lambda_max(C_t); T_t=[I+tau(I-Cbar_t)]^{-1}; temporary pre-RoPE K/V weight folding; all raw synthetic records D_t; restore native theta_t; one LoRA SFT on all nonpadding causal targets; merge theta_(t+1); recompute geometry next round; native final inference. Reference data are reused external supervision. No newly labeled anchor data, rollout grading, strategy assignment, sample rejection, adapter pool, or reward update. Use an editable vector diagram, white background, black text, thin gray borders, and light-gray fills only for persistent information and the temporary generation module. Minimum label size 8 pt at paper width. Keep all text horizontal and connectors clear. Export PDF and PNG. Prohibit reward models, verification gates, strategy labels, model ensembles, adapter pools, extra losses, numerical result claims, or semantic guarantees not specified here.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform. Alt text: A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student. Boundary: No unresolved pipeline component is drawn. No semantic-diversity guarantee follows from local full rank. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform.

**Alt text:** A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student.

## E. Option 3 — One transition expanded between successive students

**Rationale:** Canvas 6.65 by 3.0 inches. Place theta_t and theta_(t+1) at left and right; let their expanded middle transition occupy 65%. Above the transition, fixed anchor + current theta_t feed geometry then the exact proximal-gain equation. Beneath, temporary generator -> complete raw corpus D_t -> restored-weight single-LoRA learning. Draw a single outer feedback line from the right student to the left state labeled Repeat with same anchor. Put a separate small right-side label Native inference attached only to the new student.

### Standalone English production prompt (2650 characters)

```text
Create Figure 2 for an anonymous ICLR paper using vector-diagram-spec. The immediate takeaway is: The anchor is fixed; K/V geometry is re-estimated on the evolving model, then temporarily folded for generation and removed before single-LoRA SFT. Canvas 6.65 by 3.0 inches. Place theta_t and theta_(t+1) at left and right; let their expanded middle transition occupy 65%. Above the transition, fixed anchor + current theta_t feed geometry then the exact proximal-gain equation. Beneath, temporary generator -> complete raw corpus D_t -> restored-weight single-LoRA learning. Draw a single outer feedback line from the right student to the left state labeled Repeat with same anchor. Put a separate small right-side label Native inference attached only to the new student. Locked facts: CONFIRMED: native student theta_t; fixed reference anchor A={(x_i,y_i*)}; reference-completion mean NLL with prompt targets masked; all nonpadding K/V-output gradients; normalized second moment Cbar_t=C_t/lambda_max(C_t); T_t=[I+tau(I-Cbar_t)]^{-1}; temporary pre-RoPE K/V weight folding; all raw synthetic records D_t; restore native theta_t; one LoRA SFT on all nonpadding causal targets; merge theta_(t+1); recompute geometry next round; native final inference. Reference data are reused external supervision. No newly labeled anchor data, rollout grading, strategy assignment, sample rejection, adapter pool, or reward update. Use an editable vector diagram, white background, black text, thin gray borders, and light-gray fills only for persistent information and the temporary generation module. Minimum label size 8 pt at paper width. Keep all text horizontal and connectors clear. Export PDF and PNG. Prohibit reward models, verification gates, strategy labels, model ensembles, adapter pools, extra losses, numerical result claims, or semantic guarantees not specified here.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform. Alt text: A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student. Boundary: No unresolved pipeline component is drawn. No semantic-diversity guarantee follows from local full rank. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform.

**Alt text:** A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student.

## F. Fidelity and QA

- Exactly three designs encode the same facts; layout changes do not change evidence.
- Quantitative marks come from saved measurements or explicitly defined calculations.
- One dominant scientific panel owns at least half the usable canvas.
- Preserve single-seed scope, pairing, eligibility, and missing information.
- Check legibility, clipping, arrow/text collisions, units, and grayscale reproduction at final paper width.


---

# Figure 3 — Does a broader learned distribution help at larger total and correct-sample budgets?

## A. Evidence Inventory

**Question:** Does a broader learned distribution help at larger total and correct-sample budgets?

**Supported answer:** SPECTRUM gains correct richness over Plain at displayed k>1 and retains positive paired richness gains at b=4,8,16; its pass@1 is lower.

**Fact lock:** {"base":{"Ck":[0.379437,1.266564,2.267013,4.039638,12.802],"passk_percent":[37.94375,55.076545,61.097433,65.692438,72.0]},"plain":{"Ck":[0.414469,1.166138,1.922874,3.159216,8.506],"passk_percent":[41.446875,56.541115,61.857231,65.636368,70.4]},"spectral_soft":{"Ck":[0.403313,1.243749,2.161081,3.758256,11.51],"passk_percent":[40.33125,56.214816,61.892824,66.225078,72.6]},"paired_D":{"4":{"mean":0.295425,"ci95":[0.248877,0.343169],"eligible_tasks":316},"8":{"mean":0.780096,"ci95":[0.665332,0.889468],"eligible_tasks":296},"16":{"mean":1.815723,"ci95":[1.581866,2.055081],"eligible_tasks":254}}}

**Missing/boundary:** No measured k=32 value or new generations; no seed uncertainty or scaling-law fit.

**Design skill:** `designing-experiment-figures`. **Production:** `programmatic-figure-spec`.

## B. Three candidate designs

| Option | Reading path | Main risk |
|---|---|---|
| 1 | Budget curves and matched-correct effects | Misreading local/conditional evidence as a global guarantee. |
| 2 | Exact-value budget matrix with an effect strip | Misreading local/conditional evidence as a global guarantee. |
| 3 | Paired-budget comparisons with a conditional footer | Misreading local/conditional evidence as a global guarantee. |

**Recommendation:** Option 1, used in the supplied manuscript, gives the principal relationship the largest area and matches the available evidence.

## C. Option 1 — Budget curves and matched-correct effects

**Rationale:** Use a 6.65 by 2.5-inch canvas. Allocate 56% to Ck curves versus k; 23% to pass@k (%) versus k; 21% to paired Delta Db versus b with CI bars and a zero line. Total budgets are [1,4,8,16,64], with base-2 log x axes and explicit ticks. Correct budgets are [4,8,16] categorical. Label (a) Correct AST richness, (b) Task success, (c) Matched-correct gain. Use separate y scales and give the paired n values 316,296,254 in the caption.

### Standalone English production prompt (2579 characters)

```text
Create Figure 3 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: SPECTRUM gains correct richness over Plain at displayed k>1 and retains positive paired richness gains at b=4,8,16; its pass@1 is lower. Use a 6.65 by 2.5-inch canvas. Allocate 56% to Ck curves versus k; 23% to pass@k (%) versus k; 21% to paired Delta Db versus b with CI bars and a zero line. Total budgets are [1,4,8,16,64], with base-2 log x axes and explicit ticks. Correct budgets are [4,8,16] categorical. Label (a) Correct AST richness, (b) Task success, (c) Matched-correct gain. Use separate y scales and give the paired n values 316,296,254 in the caption. Locked facts: Budget order k=[1,4,8,16,64]; paired correct budgets b=[4,8,16]. MEASURED arrays and archived intervals: {"base":{"Ck":[0.379437,1.266564,2.267013,4.039638,12.802],"passk_percent":[37.94375,55.076545,61.097433,65.692438,72.0]},"plain":{"Ck":[0.414469,1.166138,1.922874,3.159216,8.506],"passk_percent":[41.446875,56.541115,61.857231,65.636368,70.4]},"spectral_soft":{"Ck":[0.403313,1.243749,2.161081,3.758256,11.51],"passk_percent":[40.33125,56.214816,61.892824,66.225078,72.6]},"paired_D":{"4":{"mean":0.295425,"ci95":[0.248877,0.343169],"eligible_tasks":316},"8":{"mean":0.780096,"ci95":[0.665332,0.889468],"eligible_tasks":296},"16":{"mean":1.815723,"ci95":[1.581866,2.055081],"eligible_tasks":254}}} Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: The same final 64-sample pools on 500 MBPP tasks give Ck and pass@k for k=1,4,8,16,64. Paired SPECTRUM-minus-Plain Db contrasts use common eligible tasks at b=4,8,16 and archived 95% task-bootstrap intervals. One training seed. Alt text: SPECTRUM yields more correct structures than Plain as total budget increases, with positive richness gains when correct-sample counts are matched. Boundary: No measured k=32 value or new generations; no seed uncertainty or scaling-law fit. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** The same final 64-sample pools on 500 MBPP tasks give Ck and pass@k for k=1,4,8,16,64. Paired SPECTRUM-minus-Plain Db contrasts use common eligible tasks at b=4,8,16 and archived 95% task-bootstrap intervals. One training seed.

**Alt text:** SPECTRUM yields more correct structures than Plain as total budget increases, with positive richness gains when correct-sample counts are matched.

## D. Option 2 — Exact-value budget matrix with an effect strip

**Rationale:** Use a 6.65 by 3-inch canvas. In the left 60%, draw a native vector matrix with three method rows and five k columns, each cell displaying exact Ck values to three decimals and a zero-origin proportional horizontal mark. Label the raw budget columns 1,4,8,16,64. The right 40% contains pass@k curves above and paired Delta Db intervals below. Preserve the lower SPECTRUM k=1 entry; do not use winner coloring or turn the matrix into a significance heatmap.

### Standalone English production prompt (2605 characters)

```text
Create Figure 3 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: SPECTRUM gains correct richness over Plain at displayed k>1 and retains positive paired richness gains at b=4,8,16; its pass@1 is lower. Use a 6.65 by 3-inch canvas. In the left 60%, draw a native vector matrix with three method rows and five k columns, each cell displaying exact Ck values to three decimals and a zero-origin proportional horizontal mark. Label the raw budget columns 1,4,8,16,64. The right 40% contains pass@k curves above and paired Delta Db intervals below. Preserve the lower SPECTRUM k=1 entry; do not use winner coloring or turn the matrix into a significance heatmap. Locked facts: Budget order k=[1,4,8,16,64]; paired correct budgets b=[4,8,16]. MEASURED arrays and archived intervals: {"base":{"Ck":[0.379437,1.266564,2.267013,4.039638,12.802],"passk_percent":[37.94375,55.076545,61.097433,65.692438,72.0]},"plain":{"Ck":[0.414469,1.166138,1.922874,3.159216,8.506],"passk_percent":[41.446875,56.541115,61.857231,65.636368,70.4]},"spectral_soft":{"Ck":[0.403313,1.243749,2.161081,3.758256,11.51],"passk_percent":[40.33125,56.214816,61.892824,66.225078,72.6]},"paired_D":{"4":{"mean":0.295425,"ci95":[0.248877,0.343169],"eligible_tasks":316},"8":{"mean":0.780096,"ci95":[0.665332,0.889468],"eligible_tasks":296},"16":{"mean":1.815723,"ci95":[1.581866,2.055081],"eligible_tasks":254}}} Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: The same final 64-sample pools on 500 MBPP tasks give Ck and pass@k for k=1,4,8,16,64. Paired SPECTRUM-minus-Plain Db contrasts use common eligible tasks at b=4,8,16 and archived 95% task-bootstrap intervals. One training seed. Alt text: SPECTRUM yields more correct structures than Plain as total budget increases, with positive richness gains when correct-sample counts are matched. Boundary: No measured k=32 value or new generations; no seed uncertainty or scaling-law fit. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** The same final 64-sample pools on 500 MBPP tasks give Ck and pass@k for k=1,4,8,16,64. Paired SPECTRUM-minus-Plain Db contrasts use common eligible tasks at b=4,8,16 and archived 95% task-bootstrap intervals. One training seed.

**Alt text:** SPECTRUM yields more correct structures than Plain as total budget increases, with positive richness gains when correct-sample counts are matched.

## E. Option 3 — Paired-budget comparisons with a conditional footer

**Rationale:** Use a 6.65 by 3.1-inch canvas. Top-left 55%: for each k, place three method points on the common Ck axis in separate budget rows, with a thin gray within-row connector only. Upper-right 25%: the same budget rows with pass@k (%) points on an independent axis. Bottom 20%: paired Delta Db and CI bars for b=4,8,16. This emphasizes the crossover at k=1 and the growing absolute richness contrast without asserting a fitted law.

### Standalone English production prompt (2574 characters)

```text
Create Figure 3 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: SPECTRUM gains correct richness over Plain at displayed k>1 and retains positive paired richness gains at b=4,8,16; its pass@1 is lower. Use a 6.65 by 3.1-inch canvas. Top-left 55%: for each k, place three method points on the common Ck axis in separate budget rows, with a thin gray within-row connector only. Upper-right 25%: the same budget rows with pass@k (%) points on an independent axis. Bottom 20%: paired Delta Db and CI bars for b=4,8,16. This emphasizes the crossover at k=1 and the growing absolute richness contrast without asserting a fitted law. Locked facts: Budget order k=[1,4,8,16,64]; paired correct budgets b=[4,8,16]. MEASURED arrays and archived intervals: {"base":{"Ck":[0.379437,1.266564,2.267013,4.039638,12.802],"passk_percent":[37.94375,55.076545,61.097433,65.692438,72.0]},"plain":{"Ck":[0.414469,1.166138,1.922874,3.159216,8.506],"passk_percent":[41.446875,56.541115,61.857231,65.636368,70.4]},"spectral_soft":{"Ck":[0.403313,1.243749,2.161081,3.758256,11.51],"passk_percent":[40.33125,56.214816,61.892824,66.225078,72.6]},"paired_D":{"4":{"mean":0.295425,"ci95":[0.248877,0.343169],"eligible_tasks":316},"8":{"mean":0.780096,"ci95":[0.665332,0.889468],"eligible_tasks":296},"16":{"mean":1.815723,"ci95":[1.581866,2.055081],"eligible_tasks":254}}} Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: The same final 64-sample pools on 500 MBPP tasks give Ck and pass@k for k=1,4,8,16,64. Paired SPECTRUM-minus-Plain Db contrasts use common eligible tasks at b=4,8,16 and archived 95% task-bootstrap intervals. One training seed. Alt text: SPECTRUM yields more correct structures than Plain as total budget increases, with positive richness gains when correct-sample counts are matched. Boundary: No measured k=32 value or new generations; no seed uncertainty or scaling-law fit. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** The same final 64-sample pools on 500 MBPP tasks give Ck and pass@k for k=1,4,8,16,64. Paired SPECTRUM-minus-Plain Db contrasts use common eligible tasks at b=4,8,16 and archived 95% task-bootstrap intervals. One training seed.

**Alt text:** SPECTRUM yields more correct structures than Plain as total budget increases, with positive richness gains when correct-sample counts are matched.

## F. Fidelity and QA

- Exactly three designs encode the same facts; layout changes do not change evidence.
- Quantitative marks come from saved measurements or explicitly defined calculations.
- One dominant scientific panel owns at least half the usable canvas.
- Preserve single-seed scope, pairing, eligibility, and missing information.
- Check legibility, clipping, arrow/text collisions, units, and grayscale reproduction at final paper width.


---

# Figure 4 — Can actual samples have equal estimated pass curves but unequal correct AST counts?

## A. Evidence Inventory

**Question:** Can actual samples have equal estimated pass curves but unequal correct AST counts?

**Supported answer:** The saved HumanEval/3 example is broader under SPECTRUM, while HumanEval/2 shows the reverse at the same number of correct samples.

**Fact lock:** MEASURED: 16 samples per method at round five. HumanEval/3: 16 correct under both; Plain AST counts [16], SPECTRUM [15,1]. HumanEval/2: 12 correct under both; Plain counts [1,1,1,1,1,1,1,1,1,1,1,1], SPECTRUM [2,1,1,1,1,1,1,1,1,1,1]. DERIVED: D4 on HumanEval/3 is 1 versus 1.25; on HumanEval/2 it is 4 versus 3.909091. Formula D_b=sum_j[1-comb(m-m_j,b)/comb(m,b)]. Classes are ranked separately, with no cross-model identity matching. Selection: for each sign of SPECTRUM-minus-Plain AST-count difference, choose lowest numerical HumanEval ID among tasks with equal correct counts >=4. Selection is sign-conditioned; no prevalence claim.

**Missing/boundary:** Program text was removed from the compact archive; do not invent code, algorithm names, prompt text, or semantic labels.

**Design skill:** `designing-experiment-figures`. **Production:** `programmatic-figure-spec`.

## B. Three candidate designs

| Option | Reading path | Main risk |
|---|---|---|
| 1 | Two frequency-rank panels | Misreading local/conditional evidence as a global guarantee. |
| 2 | Sample occupancy blocks | Misreading local/conditional evidence as a global guarantee. |
| 3 | Conditional rarefaction with observed-count evidence | Misreading local/conditional evidence as a global guarantee. |

**Recommendation:** Option 1, used in the supplied manuscript, gives the principal relationship the largest area and matches the available evidence.

## C. Option 1 — Two frequency-rank panels

**Rationale:** Canvas 6.65 by 2.35 inches. Allocate 58% to HumanEval/3 and 42% to HumanEval/2. In each panel, plot zero-baseline paired bars of counts against within-model frequency rank, with Plain gray and SPECTRUM black. Fill absent ranks with zero only for layout. Print Both: 16/16 correct or Both: 12/16 correct. Use y ranges 0--18 and 0--3 respectively and label them; different scales must be obvious.

### Standalone English production prompt (2571 characters)

```text
Create Figure 4 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: The saved HumanEval/3 example is broader under SPECTRUM, while HumanEval/2 shows the reverse at the same number of correct samples. Canvas 6.65 by 2.35 inches. Allocate 58% to HumanEval/3 and 42% to HumanEval/2. In each panel, plot zero-baseline paired bars of counts against within-model frequency rank, with Plain gray and SPECTRUM black. Fill absent ranks with zero only for layout. Print Both: 16/16 correct or Both: 12/16 correct. Use y ranges 0--18 and 0--3 respectively and label them; different scales must be obvious. Locked facts: MEASURED: 16 samples per method at round five. HumanEval/3: 16 correct under both; Plain AST counts [16], SPECTRUM [15,1]. HumanEval/2: 12 correct under both; Plain counts [1,1,1,1,1,1,1,1,1,1,1,1], SPECTRUM [2,1,1,1,1,1,1,1,1,1,1]. DERIVED: D4 on HumanEval/3 is 1 versus 1.25; on HumanEval/2 it is 4 versus 3.909091. Formula D_b=sum_j[1-comb(m-m_j,b)/comb(m,b)]. Classes are ranked separately, with no cross-model identity matching. Selection: for each sign of SPECTRUM-minus-Plain AST-count difference, choose lowest numerical HumanEval ID among tasks with equal correct counts >=4. Selection is sign-conditioned; no prevalence claim. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities. Alt text: HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs. Boundary: Program text was removed from the compact archive; do not invent code, algorithm names, prompt text, or semantic labels. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities.

**Alt text:** HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs.

## D. Option 2 — Sample occupancy blocks

**Rationale:** Canvas 6.65 by 2.8 inches. Use an upper 55% HumanEval/3 panel with two method lanes of 16 correct-sample tiles, grouped by AST frequency class. In the lower 45% show the 12 correct tiles for HumanEval/2 and a separate four-failed-draw block for each method. Assign local class labels j1,j2,... within each model, never aligned semantic labels. Print class counts and exact D4 beside lanes. Group borders and text distinguish classes without relying on color.

### Standalone English production prompt (2635 characters)

```text
Create Figure 4 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: The saved HumanEval/3 example is broader under SPECTRUM, while HumanEval/2 shows the reverse at the same number of correct samples. Canvas 6.65 by 2.8 inches. Use an upper 55% HumanEval/3 panel with two method lanes of 16 correct-sample tiles, grouped by AST frequency class. In the lower 45% show the 12 correct tiles for HumanEval/2 and a separate four-failed-draw block for each method. Assign local class labels j1,j2,... within each model, never aligned semantic labels. Print class counts and exact D4 beside lanes. Group borders and text distinguish classes without relying on color. Locked facts: MEASURED: 16 samples per method at round five. HumanEval/3: 16 correct under both; Plain AST counts [16], SPECTRUM [15,1]. HumanEval/2: 12 correct under both; Plain counts [1,1,1,1,1,1,1,1,1,1,1,1], SPECTRUM [2,1,1,1,1,1,1,1,1,1,1]. DERIVED: D4 on HumanEval/3 is 1 versus 1.25; on HumanEval/2 it is 4 versus 3.909091. Formula D_b=sum_j[1-comb(m-m_j,b)/comb(m,b)]. Classes are ranked separately, with no cross-model identity matching. Selection: for each sign of SPECTRUM-minus-Plain AST-count difference, choose lowest numerical HumanEval ID among tasks with equal correct counts >=4. Selection is sign-conditioned; no prevalence claim. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities. Alt text: HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs. Boundary: Program text was removed from the compact archive; do not invent code, algorithm names, prompt text, or semantic labels. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities.

**Alt text:** HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs.

## E. Option 3 — Conditional rarefaction with observed-count evidence

**Rationale:** Canvas 6.65 by 2.8 inches. Use 55% for two clearly separated per-task D_b curves for integer b=1,2,3,4 computed exactly from the supplied class counts. Put the measured class-count vectors in a 45% adjacent table with correct counts and task IDs. All curves are DERIVED rarefaction of the existing samples, not new model runs. Mark the opposite signs at b=4 without generalizing their frequency.

### Standalone English production prompt (2572 characters)

```text
Create Figure 4 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: The saved HumanEval/3 example is broader under SPECTRUM, while HumanEval/2 shows the reverse at the same number of correct samples. Canvas 6.65 by 2.8 inches. Use 55% for two clearly separated per-task D_b curves for integer b=1,2,3,4 computed exactly from the supplied class counts. Put the measured class-count vectors in a 45% adjacent table with correct counts and task IDs. All curves are DERIVED rarefaction of the existing samples, not new model runs. Mark the opposite signs at b=4 without generalizing their frequency. Locked facts: MEASURED: 16 samples per method at round five. HumanEval/3: 16 correct under both; Plain AST counts [16], SPECTRUM [15,1]. HumanEval/2: 12 correct under both; Plain counts [1,1,1,1,1,1,1,1,1,1,1,1], SPECTRUM [2,1,1,1,1,1,1,1,1,1,1]. DERIVED: D4 on HumanEval/3 is 1 versus 1.25; on HumanEval/2 it is 4 versus 3.909091. Formula D_b=sum_j[1-comb(m-m_j,b)/comb(m,b)]. Classes are ranked separately, with no cross-model identity matching. Selection: for each sign of SPECTRUM-minus-Plain AST-count difference, choose lowest numerical HumanEval ID among tasks with equal correct counts >=4. Selection is sign-conditioned; no prevalence claim. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities. Alt text: HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs. Boundary: Program text was removed from the compact archive; do not invent code, algorithm names, prompt text, or semantic labels. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities.

**Alt text:** HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs.

## F. Fidelity and QA

- Exactly three designs encode the same facts; layout changes do not change evidence.
- Quantitative marks come from saved measurements or explicitly defined calculations.
- One dominant scientific panel owns at least half the usable canvas.
- Preserve single-seed scope, pairing, eligibility, and missing information.
- Check legibility, clipping, arrow/text collisions, units, and grayscale reproduction at final paper width.
